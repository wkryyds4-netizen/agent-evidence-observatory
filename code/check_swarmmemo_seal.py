#!/usr/bin/env python3
"""Offline synthetic checks of one pinned, model-reviewed upstream module.

Research harness by QiuZheng; MIT. Upstream files stay separately Apache-2.0.
No package installation, remote requests, or real conversation data are needed.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import sys

COMMIT = "135974f468ec5bb39aa0f275b43e54a763306d77"
EXPECTED = {
    "swarmmemo_seal.py": "fe9c256f6807e7339733ea273ff2a1bf15b55bf3d33b0bac97d1fb6acfebea0c",
    "seal-vector.json": "e688a6037c03756174b16531b0bfe4d477e6a21b033998370cf9e158d1259144",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    for filename, expected in EXPECTED.items():
        actual = hashlib.sha256((args.source_dir / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit("Refusing unreviewed source: SHA256 mismatch for " + filename)
    attempts = []

    def offline_guard(event, arguments):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.bind", "subprocess.Popen", "os.system"}:
            attempts.append(event)
            raise RuntimeError("Offline harness blocked: " + event)

    sys.addaudithook(offline_guard)
    spec = importlib.util.spec_from_file_location("reviewed_seal", args.source_dir / "swarmmemo_seal.py")
    seal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seal)
    import cryptography
    vector = json.loads((args.source_dir / "seal-vector.json").read_text(encoding="utf-8"))
    checks = []

    def expect(name, condition, boundary):
        checks.append({"name": name, "passed": bool(condition), "boundary": boundary})

    def rejected(name, function, boundary):
        try:
            function()
        except seal.SealError:
            expect(name, True, boundary)
        else:
            expect(name, False, boundary)

    v = vector["hpke_a1"]
    h = bytes.fromhex
    enc, ct = seal.hpke_seal(h(v["pkRm"]), h(v["info"]), h(v["aad"]), h(v["pt"]), ephemeral=h(v["skEm"]))
    expect("upstream_hpke_vector", enc.hex() == v["enc"] and ct.hex() == v["ct"], "Matches upstream fixture labelled RFC 9180 A.1; independent RFC byte verification is outside this run.")
    v = vector["envelope"]
    actual = seal.seal(seal.unb64(v["epoch_key"]), v["service"], v["room"], v["epoch"], v["author"], v["plaintext"].encode(), nonce=seal.unb64(v["nonce"]))
    expect("upstream_envelope_vector", actual == v["envelope"], "Matches upstream deterministic envelope fixture.")
    private, public = seal.generate_keypair()
    wrong_private, _ = seal.generate_keypair()
    key = seal.new_epoch_key()
    service, room, epoch, author = "offline.example", "~synthetic-room", 7, "a" * 64
    wrapped = seal.wrap(public, key, room, epoch)
    expect("recipient_unwrap", seal.unwrap(private, wrapped, room, epoch) == key, "Synthetic recipient unwraps synthetic epoch key.")
    rejected("wrong_recipient", lambda: seal.unwrap(wrong_private, wrapped, room, epoch), "Other synthetic private key cannot unwrap.")
    rejected("wrap_wrong_room", lambda: seal.unwrap(private, wrapped, room + "x", epoch), "HPKE info binds room.")
    rejected("wrap_wrong_epoch", lambda: seal.unwrap(private, wrapped, room, epoch + 1), "HPKE info binds epoch.")
    damaged = dict(wrapped)
    raw = bytearray(seal.unb64(damaged["ct"]))
    raw[-1] ^= 1
    damaged["ct"] = seal.b64(bytes(raw))
    rejected("wrap_ciphertext_tamper", lambda: seal.unwrap(private, damaged, room, epoch), "Authentication rejects modified key wrap.")
    relabelled = {**wrapped, "kid": "0" * 32}
    expect("unwrap_kid_boundary", seal.unwrap(private, relabelled, room, epoch) == key, "Low-level unwrap ignores kid; authenticated wrap selection belongs to verify_epoch_key and calling client.")
    body = seal.plaintext("Synthetic offline message: 合成离线数据", format="markdown")
    envelope = seal.seal(key, service, room, epoch, author, body)
    opened = lambda s=service, r=room, a=author, e=envelope, k=key: seal.open_envelope({epoch: k}, s, r, a, e)
    expect("message_roundtrip", opened() == json.loads(body), "Synthetic message roundtrip.")
    rejected("message_wrong_key", lambda: opened(k=seal.new_epoch_key()), "Wrong epoch key rejected.")
    for field, changes in (("service", {"s": "other.example"}), ("room", {"r": room + "x"}), ("author", {"a": "b" * 64})):
        rejected("message_aad_" + field, lambda changes=changes: opened(**changes), "AAD binds " + field + ".")
    parts = envelope.split(".")
    altered_epoch = ".".join([parts[0], str(epoch + 1), parts[2], parts[3]])
    rejected("message_aad_epoch", lambda: seal.open_envelope({epoch + 1: key}, service, room, author, altered_epoch), "Same key under changed epoch still fails authentication.")
    for part, name in ((2, "nonce"), (3, "ciphertext")):
        modified = parts.copy()
        raw = bytearray(seal.unb64(modified[part]))
        raw[-1] ^= 1
        modified[part] = seal.b64(bytes(raw))
        rejected("message_tamper_" + name, lambda e=".".join(modified): opened(e=e), "Modified " + name + " is rejected.")
    expect("replay_boundary", opened() == opened(), "Primitive accepts same valid envelope twice; replay control needs external state.")
    outer = {"timestamp": "synthetic-t1", "id": "synthetic-1", "reply_to": "synthetic-root", "envelope": envelope}
    changed = {**outer, "timestamp": "synthetic-t2", "id": "synthetic-2", "reply_to": "synthetic-other"}
    expect("outer_metadata_boundary", opened(e=outer["envelope"]) == opened(e=changed["envelope"]), "timestamp/id/reply_to are not parameters of this primitive; this is not a test of outer signed-post validation.")
    other_author = "b" * 64
    new_envelope = seal.seal(key, service, room, epoch, other_author, body)
    expect("shared_key_author_boundary", opened(a=other_author, e=new_envelope) == json.loads(body), "An epoch-key holder can create an envelope naming another author; author authenticity additionally requires the outer signature.")
    file_bytes = b"synthetic file\x00\x01"
    blob, entry = seal.encrypt_file(file_bytes)
    expect("file_roundtrip", seal.decrypt_file(blob, entry) == file_bytes, "Synthetic attachment roundtrip.")
    tampered = blob[:-1] + bytes([blob[-1] ^ 1])
    rejected("file_tamper", lambda: seal.decrypt_file(tampered, entry), "Modified file rejected.")
    rejected("file_hash_mismatch", lambda: seal.decrypt_file(blob, {**entry, "sha256": "0" * 64}), "Plaintext hash checked after decryption.")
    # Exercise signed identity and rotation helpers with a synthetic Ed25519 key.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    signing = Ed25519PrivateKey.generate()
    signing_public = seal.b64(signing.public_key().public_bytes_raw())
    def signed(command):
        payload = json.dumps({"service": service, "command": {**command, "public_key": signing_public}}, sort_keys=True, separators=(",", ":"))
        return {"public_key": signing_public, "signature": seal.b64(signing.sign(payload.encode())), "signed_payload": payload}
    link = signed({"operation": "identity.link", "data": json.dumps({"schema": 1, "kind": "x25519", "value": seal.b64(public)})})
    agent = {"public_key": signing_public, "seal_key": {**link, "x25519": seal.b64(public), "kid": seal.kid(public)}}
    expect("signed_identity_link", seal.verify_seal_key(agent, service) == public, "Valid synthetic signing key binds sealing key.")
    replaced = copy.deepcopy(agent)
    _, replacement = seal.generate_keypair()
    replaced["seal_key"].update(x25519=seal.b64(replacement), kid=seal.kid(replacement))
    rejected("identity_key_substitution", lambda: seal.verify_seal_key(replaced, service), "Substitution without a new signature rejected.")
    rotation = signed({"operation": "conversation.seal", "room": room, "data": json.dumps({"schema": 1, "epoch": epoch, "wraps": [wrapped]})})
    signed_entry = {**rotation, **wrapped, "epoch": epoch}
    accepted = {seal.fingerprint(signing_public)}
    expect("signed_member_rotation", seal.verify_epoch_key(signed_entry, room, service, accepted) == wrapped, "Valid rotation from accepted synthetic member verifies.")
    rejected("rotation_nonmember", lambda: seal.verify_epoch_key(signed_entry, room, service, {"f" * 64}), "Caller-supplied membership set excludes signer.")
    rejected("rotation_wrap_tamper", lambda: seal.verify_epoch_key({**signed_entry, **damaged}, room, service, accepted), "Returned wrap must match signed rotation.")
    expect("offline_guard_no_attempts", not attempts, "No guarded network/process actions attempted during module import and tests.")
    result = {"commit": COMMIT, "upstream_sha256": EXPECTED, "python": platform.python_version(), "cryptography": cryptography.__version__, "check_count": len(checks), "passed": sum(c["passed"] for c in checks), "checks": checks, "network_or_process_attempts": attempts, "limitations": ["Synthetic offline sample, not a cryptographic security audit or production deployment test.", "No proof of actual private conversations, autonomous groups, model identity, or operator independence.", "Main swarmmemo.py, browser implementation, backend, client pinning/persistence and full upstream test suite were not run.", "This harness uses upstream fixture bytes; it does not establish independent RFC conformance."]}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"checks": len(checks), "passed": result["passed"], "blocked_attempts": len(attempts)}))
    return 0 if result["passed"] == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
