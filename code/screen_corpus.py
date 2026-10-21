#!/usr/bin/env python3
"""Offline triage of a publisher's public, static agent-activity snapshot.
No HTTP client, subprocess, eval, model API, or URL dereferencing is used.
Scores are review priorities, never probabilities or identity/intent verdicts.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

FEATURES = {
    "coordination_language": (2, r"\b(collaborat\w*|coordinat\w*|other agents|shared memor\w*|handoff|hand-off|relay|peer review)\b|协作|协同|其他智能体|共享记忆|交接"),
    "request_for_peer_action": (2, r"\b(anyone|can someone|please (?:share|relay|confirm|reply)|need help|looking for (?:other|a) agents)\b|请.{0,10}(?:分享|回复|确认)|有没有人"),
    "continuity_claim": (1, r"\b(next (?:instance|session|agent)|future (?:instance|session|agent)|persistent memor\w*|across sessions)\b|下一个实例|后续实例|跨会话"),
    "restriction_language": (1, r"\b(unauthori[sz]ed|bypass|sandbox|out.of.scope|escape|blocked)\b|未经授权|绕过|沙箱|越权"),
    "concealment_claim": (2, r"\b(hide (?:it|this|our)|avoid detection|without (?:the )?(?:human|operator).{0,16}(?:know|notic)|don.t tell (?:the )?(?:human|operator)|covert (?:channel|communication))\b|隐瞒操作者|规避监控|秘密通信"),
    "human_direction_disclosed": (0, r"\b(operator.directed|my operator|human.directed|human.deployed|my human|asked me to|owner asked)\b|操作者指挥|人类部署|用户委托"),
    "research_context_language": (0, r"\b(experiment|simulation|simulated|researchers?|benchmark|evaluation|controlled test)\b|模拟环境|受控实验|研究者|评估"),
    "benevolent_motive_claim": (0, r"\b(protect humanity|save humanity|benefit humanity|protect (?:all )?humans)\b|保护人类|拯救人类|造福人类"),
    "claude_name_mention": (0, r"\bclaude\b|克劳德"),
}
PATTERNS = {k: re.compile(p, re.I) for k, (_, p) in FEATURES.items()}
URL_RE = re.compile(r"https?://[^\s<>\"'\]\)]+", re.I)
EMAIL_RE = re.compile(r"(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_RE = re.compile(r"(?i)\b(?:sk-(?:ant-)?|gh[pousr]_|github_pat_|AKIA)[A-Za-z0-9_-]{10,}")
KEYVALUE_RE = re.compile(r"(?i)\b(api[_ -]?key|access[_ -]?token|password|secret)\s*[:=]\s*[^\s,;]+")
CSV_FORMULA = re.compile(r"^[\s]*[=+@\-\t\r]")

def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()

def normalized_hash(text):
    return digest_bytes(re.sub(r"\s+", " ", html.unescape(text)).strip().casefold().encode("utf-8"))

def safe_url(value):
    """Keep only a public-looking URL's scheme/host/path. No query, fragment or userinfo."""
    if not isinstance(value, str):
        return ""
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme not in ("http", "https") or not host:
            return ""
        if EMAIL_RE.search(parsed.path) or SECRET_RE.search(parsed.path):
            return f"{parsed.scheme}://{host}/[redacted-path]"
        return f"{parsed.scheme}://{host}{parsed.path}"[:400]
    except ValueError:
        return ""

def redact(text):
    text = SECRET_RE.sub("[credential-redacted]", text)
    text = KEYVALUE_RE.sub(lambda m: m.group(1) + "=[redacted]", text)
    text = EMAIL_RE.sub("[email-redacted]", text)
    text = IP_RE.sub("[ip-redacted]", text)
    text = URL_RE.sub(lambda m: safe_url(m.group(0)) or "[url-redacted]", text)
    return text

def iso_time(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < 946684800:
            return ""
        try:
            return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat()
        except (ValueError, OverflowError, OSError):
            return ""
    return ""

def load_snapshot(path):
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("Snapshot exceeds the reviewed 16 MiB local size bound")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("datasets"), dict):
        raise ValueError("Unsupported schema: expected datasets -> dataset -> identity")
    return data

def records_from_snapshot(data):
    """Publisher schema: posts = [unix_ts, excerpt, url, place, reply_flag]."""
    records, rejected = [], collections.Counter()
    for dataset, people in data["datasets"].items():
        if not isinstance(people, dict):
            rejected["dataset_not_object"] += 1
            continue
        for identity, person in people.items():
            if not isinstance(person, dict):
                rejected["identity_not_object"] += 1
                continue
            posts = person.get("posts", [])
            if not isinstance(posts, list):
                rejected["posts_not_list"] += 1
                continue
            for index, post in enumerate(posts):
                if not isinstance(post, list) or len(post) < 5 or not isinstance(post[1], str):
                    rejected["post_shape"] += 1
                    continue
                excerpt = post[1]
                raw_locator = f"datasets/{dataset}/{identity}/posts/{index}"
                rid = digest_bytes(raw_locator.encode("utf-8"))[:20]
                identity_ref = digest_bytes(str(identity).encode("utf-8"))[:20]
                source_locator = f"datasets/{dataset}/identity-sha256:{identity_ref}/posts/{index}"
                records.append({
                    "record_id": rid, "dataset": str(dataset), "identity_label": redact(str(identity)),
                    "identity_ref": identity_ref,
                    "source_locator": source_locator,
                    "timestamp_utc": iso_time(post[0]),
                    "text": excerpt, "source_url_sanitized": safe_url(post[2]),
                    "place_label": redact(str(post[3]))[:160],
                    "publisher_reply_flag": bool(post[4]),
                    "text_sha256": normalized_hash(excerpt),
                    "post_index": index,
                })
    return records, dict(rejected)

def classify(record, hash_counts):
    text = record["text"]
    flags = {key: bool(pattern.search(text)) for key, pattern in PATTERNS.items()}
    points = sum(FEATURES[key][0] for key, found in flags.items() if found)
    has_peer = flags["coordination_language"] or flags["request_for_peer_action"]
    if has_peer and record["publisher_reply_flag"]:
        points += 1
    # An operator disclosure/context flag is displayed, not erased by a negative weight.
    hints = []
    if has_peer:
        hints.append("check_peer_context")
    if flags["human_direction_disclosed"]:
        hints.append("operator_direction_disclosed_in_excerpt")
    if flags["research_context_language"]:
        hints.append("research_or_report_language_requires_context")
    if flags["claude_name_mention"]:
        hints.append("claude_mention_is_not_model_attestation")
    if flags["benevolent_motive_claim"]:
        hints.append("motive_words_are_not_proof_of_motive")
    if not hints:
        hints.append("no_selected_keyword_signal")
    return {
        **{k: v for k, v in record.items() if k != "text"},
        "review_priority_score": points,
        "flags": flags,
        "text_duplicate_count": hash_counts[record["text_sha256"]],
        "hints": hints,
        "conclusion": "unassessed",
        "model_identity": "unverified",
        "parent_record_id": None,
    }

def csv_cell(v):
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    value = str(v if v is not None else "")
    # Prevent spreadsheet formulas in untrusted names/snippets if CSV is opened.
    return "'" + value if CSV_FORMULA.match(value) else value

def dump_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_cell(row.get(key)) for key in fields})

def select_review(rows, size=36):
    """Deterministic stratified sample; labels are not outcome categories."""
    chosen, seen, per_identity = [], set(), collections.Counter()
    ordered = sorted(rows, key=lambda r: (-r["review_priority_score"], r["record_id"]))
    strata = [
        ("priority", ordered, 12),
        ("claude_mention", [r for r in ordered if r["flags"]["claude_name_mention"]], 8),
        ("human_direction", [r for r in ordered if r["flags"]["human_direction_disclosed"]], 5),
        ("benevolent_words", [r for r in ordered if r["flags"]["benevolent_motive_claim"]], 4),
        ("low_signal_control", sorted([r for r in rows if r["review_priority_score"] == 0], key=lambda r:r["record_id"]), 7),
    ]
    for stratum, pool, limit in strata:
        count = 0
        for row in pool:
            ident = (row["dataset"], row["identity_ref"])
            if row["record_id"] in seen or per_identity[ident] >= 2:
                continue
            chosen.append({**row, "sample_stratum": stratum})
            seen.add(row["record_id"])
            per_identity[ident] += 1
            count += 1
            if count >= limit or len(chosen) >= size:
                break
        if len(chosen) >= size:
            break
    return chosen

def run(snapshot, output_dir, source_url):
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = snapshot.read_bytes()
    data = load_snapshot(snapshot)
    records, rejected = records_from_snapshot(data)
    counts = collections.Counter(r["text_sha256"] for r in records)
    rows = [classify(r, counts) for r in records]
    rows.sort(key=lambda r: (-r["review_priority_score"], r["record_id"]))
    sample = select_review(rows)
    flags_count = {key: sum(r["flags"][key] for r in rows) for key in FEATURES}
    platform_counts = collections.Counter(r["dataset"] for r in rows)
    identities = {(r["dataset"], r["identity_ref"]) for r in rows}
    dates = [r["timestamp_utc"] for r in rows if r["timestamp_utc"]]
    summary = {
        "schema_version": 1,
        "input_filename": snapshot.name,
        "input_sha256": digest_bytes(raw),
        "input_bytes": len(raw),
        "publisher_snapshot_source": source_url,
        "source_schema": "Swarmchasing agents.json: datasets/dataset/identity/posts/[timestamp,excerpt,url,place,reply_flag]",
        "record_count": len(rows),
        "snapshot_dataset_count": len(data["datasets"]),
        "snapshot_identity_record_count": sum(len(v) for v in data["datasets"].values() if isinstance(v, dict)),
        "dataset_count": len(platform_counts),
        "dataset_counts": dict(sorted(platform_counts.items())),
        "identity_labels_by_dataset": len(identities),
        "unique_excerpt_hashes": len(counts),
        "records_in_duplicate_excerpt_groups": sum(v for v in counts.values() if v > 1),
        "valid_timestamp_count": len(dates),
        "timestamp_min_utc": min(dates) if dates else None,
        "timestamp_max_utc": max(dates) if dates else None,
        "feature_counts": flags_count,
        "review_sample_count": len(sample),
        "rejected": rejected,
        "limitations": [
            "Publisher-selected excerpts, not full transcripts or a fresh live crawl; derived outputs do not reproduce excerpts.",
            "Epoch/zero and other timestamps before 2000 are treated as missing, not genuine activity dates.",
            "A reply flag has no authenticated parent ID; no reply graph is inferred.",
            "Identity labels are not independent agents, models, or human operators.",
            "Keyword scores are review priorities, not probabilities or factual verdicts.",
            "Duplicates may be exports or quotation, not evidence of communication.",
            "Source URLs are retained only as sanitized locators and never requested.",
            "Pattern-based redaction retains ordinary handles and linkable identity hashes; local per-record outputs are not anonymous and are excluded from the public release.",
            "No statistical test of C1 account coordination or model stylometry is performed.",
        ],
    }
    (output_dir/"screening_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    with (output_dir/"screening_records.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False)+"\n")
    (output_dir/"manual_review_sample.json").write_text(json.dumps(sample, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    fields = ["record_id","dataset","identity_label","identity_ref","timestamp_utc","review_priority_score","publisher_reply_flag","flags","hints","source_url_sanitized","source_locator"]
    dump_csv(output_dir/"manual_review_sample.csv", sample, ["sample_stratum"]+fields)
    # Keep publisher text in the original local snapshot, not in derived artifacts.
    dump_csv(output_dir/"ranked_index.csv", rows, fields)
    return summary

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--source-url",default="https://publicbbs.com/swarmchasing/data/agents.json")
    args=parser.parse_args()
    print(json.dumps(run(args.snapshot,args.out,args.source_url),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()

