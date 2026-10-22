#!/usr/bin/env python3
"""MIT: QiuZheng's offline checks of reviewed, AST-selected client paths.

Does not import the complete client, read user state, or open network sessions.
Mock boundaries and excluded paths are explicit in the generated result.
"""
import argparse
import ast
import base64
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import re
import sys
import time
from types import SimpleNamespace

COMMIT = "135974f468ec5bb39aa0f275b43e54a763306d77"
HASHES = {
    "swarmmemo.py": "7bb66027cfd170c3f508ed4ada782022a1860461f509848005909ee9767c093f",
    "swarmmemo_seal.py": "fe9c256f6807e7339733ea273ff2a1bf15b55bf3d33b0bac97d1fb6acfebea0c",
}
FUNCTIONS = {"strict_json", "b64", "unb64", "crypto", "printable", "created_sealed", "inbound_view", "inbound_threshold"}
METHODS = {"say", "header", "fetch", "show"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name, expected in HASHES.items():
        if hashlib.sha256((args.source_dir / name).read_bytes()).hexdigest() != expected:
            raise SystemExit("Refusing source hash mismatch: " + name)
    sys.dont_write_bytecode = True
    attempts = []
    def guard(event, arguments):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.bind", "subprocess.Popen", "os.system"}:
            attempts.append(event)
            raise RuntimeError("Offline check blocked " + event)
    sys.addaudithook(guard)
    spec = importlib.util.spec_from_file_location("reviewed_seal", args.source_dir / "swarmmemo_seal.py")
    seal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seal)
    tree = ast.parse((args.source_dir / "swarmmemo.py").read_text(encoding="utf-8"))
    selected, spans = [], []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS:
            selected.append(node)
            spans.append({"name": node.name, "start": node.lineno, "end": node.end_lineno})
        elif isinstance(node, ast.ClassDef) and node.name in {"ChatStop", "SealedRoom"}:
            selected.append(node)
            spans.append({"name": node.name, "start": node.lineno, "end": node.end_lineno})
        elif isinstance(node, ast.ClassDef) and node.name == "Chat":
            kept = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name in METHODS]
            spans.extend({"name": "Chat." + n.name, "start": n.lineno, "end": n.end_lineno} for n in kept)
            node.body = kept
            selected.append(node)
    namespace = {"__builtins__": __builtins__, "__name__": "reviewed_client_paths", "json": json, "base64": base64,
                 "re": re, "sys": sys, "time": time, "_ED25519": None, "PLAIN_ED25519": None,
                 "BASE64URL_RULE": "invalid base64url", "CHAT_FRAME": "Synthetic offline display boundary"}
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])), "reviewed-client-paths", "exec"), namespace)
    assert namespace["crypto"]() is not None, "This run requires cryptography; fallback was not loaded."
    import cryptography
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    signing = Ed25519PrivateKey.generate()
    public = seal.b64(signing.public_key().public_bytes_raw())
    author = seal.fingerprint(public)
    service, room, epoch = "offline.example", "~" + "a" * 26, 1
    def sign(command, service_name=service):
        payload = json.dumps({"version": 1, "service": service_name, "command": {"public_key": public, **command}}, separators=(",", ":"))
        return {"public_key": public, "signed_payload": payload, "signature": seal.b64(signing.sign(payload.encode()))}
    creation = sign({"operation": "conversation.open", "room": room, "data": json.dumps({"schema": 1, "kind": "group", "sealed": True})})
    checks = []
    def record(name, passed, observed):
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
    def creation_rejected(name, value, requested_room=room, requested_service=service):
        try:
            namespace["created_sealed"](value, requested_room, requested_service)
        except namespace["ChatStop"]:
            record(name, True, "Creation rejected before determining sealed status.")
        else:
            record(name, False, "Creation unexpectedly accepted.")
    record("creation_valid", namespace["created_sealed"](creation, room, service), "Synthetic signed creation accepted.")
    creation_rejected("creation_bad_signature", {**creation, "signature": seal.b64(bytes(64))})
    creation_rejected("creation_wrong_room", creation, room + "x")
    creation_rejected("creation_wrong_service", creation, requested_service="other.example")
    other_public = seal.b64(Ed25519PrivateKey.generate().public_key().public_bytes_raw())
    mismatch = sign({"operation": "conversation.open", "room": room, "public_key": other_public, "data": '{"sealed":true}'})
    creation_rejected("creation_public_key_mismatch", mismatch)
    private_x, public_x = seal.generate_keypair()
    epoch_key = seal.new_epoch_key()
    wrap = seal.wrap(public_x, epoch_key, room, epoch)
    wrap["agent"] = author
    rotation = sign({"operation": "conversation.seal", "room": room, "data": json.dumps({"schema": 1, "epoch": epoch, "wraps": [wrap]})})
    entry = {**rotation, **wrap, "epoch": epoch}
    conv = {"room": room, "created": creation, "members": [{"agent": author}], "my_state": "member"}
    # External key loading is replaced with synthetic in-memory key material only.
    namespace["seal_module"] = lambda: seal
    namespace["load_seal_keys"] = lambda _: [{"kid": seal.kid(public_x), "private_key": seal.b64(private_x)}]
    chat = namespace["Chat"].__new__(namespace["Chat"])
    chat.client = SimpleNamespace(service=service)
    chat.me = "f" * 64
    sealed_room = namespace["SealedRoom"](chat, conv)
    sealed_room.learn([entry])
    record("rotation_learned", sealed_room.keys.get(epoch) == epoch_key, "Original learn method accepted synthetic member-signed wrap.")
    text = "SYNTHETIC_MESSAGE_SENTINEL"
    envelope = seal.seal(epoch_key, service, room, epoch, author, seal.plaintext(text))
    message = {"id": "1" * 32, "author": author, "room": room, "text": envelope, "format": "sealed", "created_at": 1,
               **sign({"operation": "post", "room": room, "text": envelope, "data": '{"schema":1,"format":"sealed"}'})}
    record("message_valid", sealed_room.open(message) == (text, None), "Original open method returns synthetic plaintext.")
    bad_signature = {**message, "signature": seal.b64(bytes(64))}
    record("message_bad_signature_accepted", sealed_room.open(bad_signature) == (text, None), "Message signature is not checked by SealedRoom.open/body.")
    missing = {k: v for k, v in message.items() if k not in {"public_key", "signature", "signed_payload"}}
    record("message_missing_signature_accepted", sealed_room.open(missing) == (text, None), "Removing all outer signature material does not stop this helper.")
    record("message_public_key_substitution_accepted", sealed_room.open({**message, "public_key": other_public}) == (text, None), "Displayed author fingerprint is not bound to message public_key by this helper.")
    record("message_author_relabel_rejected", sealed_room.open({**message, "author": "b" * 64})[0] is None, "Existing envelope cannot simply change its AAD author.")
    # Preserve exact fetch control flow, replacing only its external get method.
    page = {"sealed": True, "data": {"conversation": conv, "seal": {"keys": [entry]}, "has_more": False},
            "messages": [bad_signature, copy.deepcopy(bad_signature)], "next_cursor": "synthetic-cursor"}
    chat.get = lambda *a, **k: copy.deepcopy(page)
    got = chat.fetch(room, "start", mark_read=False)
    record("fetch_bad_signature_reaches_opened", got["opened"].get(message["id"]) == (text, None), "Exact fetch path accepts synthetic get response with invalid outer message signature; transport/get gates mocked.")
    record("fetch_duplicate_ids_retained", len(got["messages"]) == 2, "Two identical IDs remain in messages; opened/pages mappings have one key.")
    # Original inbound_view runs its sealed, non-remote branch. Notices/member
    # announcements and disk saving are excluded. member_lines can fetch/verify
    # a member's sealing-key record; that separate check is not exercised here.
    chat.out, chat.err = io.StringIO(), io.StringIO()
    chat.settings = {"inbound.mode": "withhold", "inbound.threshold": 0.6, "inbound.fail_closed": True,
                     "inbound.categories": [], "inbound.remote_screen_rooms": []}
    chat.sources = {}
    chat.member_lines = lambda *a: None
    namespace["announce"] = lambda *a: None
    namespace["weakened"] = lambda *a: []
    saves = []
    namespace["save_chat"] = lambda state: saves.append(copy.deepcopy(state))
    state = {"room": room, "cursor": "start"}
    status = chat.show(state, got)
    record("show_duplicates_twice", status == 0 and chat.out.getvalue().count(text) == 2, "Original show loop prints identical supplied ID twice under sealed/non-remote screening; no tool action tested.")
    record("show_cursor_saved", state["cursor"] == "synthetic-cursor" and len(saves) == 1, "Acknowledged show updates cursor via mocked in-memory persistence.")
    before = chat.out.getvalue().count(text)
    chat.show(state, got, acknowledge=False)
    record("show_repeated_batch_again", chat.out.getvalue().count(text) == before + 2 and len(saves) == 1, "Supplying same batch again shows it again; peek does not save cursor.")
    result = {"commit": COMMIT, "sha256": HASHES, "python": platform.python_version(), "cryptography": cryptography.__version__,
              "check_count": len(checks), "passed": sum(c["passed"] for c in checks), "checks": checks,
              "check_semantics": "passed counts reproduced expected observations, including acceptance of bad/missing outer signatures; it does not mean product security checks passed.",
              "selected_source_ranges": spans, "guarded_attempts": attempts,
              "method": "Hash-pinned AST extraction of reviewed definitions/methods, not complete client import or end-to-end deployment test.",
              "mocks": ["Chat.get: synthetic response, bypassing transport and get/pin gates (creation signature checked separately).", "load_seal_keys: newly generated synthetic key.", "member_lines: omitted member state notices and agent.get/verify_seal_key checks; not per-message author-signature verification.", "announce and weakened: omitted settings notices.", "save_chat: in-memory capture, no persistence.", "Chat constructor not run; synthetic attributes supplied."],
              "limits": ["No server ingress checks or deployed service was tested.", "Replay findings concern supplied batches, display and local cursor only; not server delivery or tool execution.", "Absence of per-message verification in this read path does not mean server accepts forged posts.", "Keys and signatures do not authenticate model provenance, independent operators or autonomous social groups."]}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"checks": len(checks), "passed": result["passed"], "guarded_attempts": len(attempts)}))
    return 0 if result["passed"] == len(checks) and not attempts else 1


if __name__ == "__main__":
    raise SystemExit(main())
