#!/usr/bin/env python3
"""Aggregate static wiki metadata without following source_refs or exporting IPs."""
import argparse, collections, hashlib, json, sys
from pathlib import Path

def records(path):
    with path.open(encoding="utf-8-sig") as stream:
        for lineno, line in enumerate(stream, 1):
            if line.strip():
                row=json.loads(line)
                if not isinstance(row,dict):
                    raise ValueError(f"{path.name}:{lineno}: not an object")
                yield row

def span(items, key):
    dates=[r[key] for r in items if isinstance(r.get(key),str) and r[key]]
    return {"min":min(dates) if dates else None,"max":max(dates) if dates else None}

def aggregate(root):
    pages=list(records(root/"pages.jsonl"))
    events=list(records(root/"events.jsonl"))
    labels=list(records(root/"labels.jsonl"))
    counts=lambda rows,key:dict(collections.Counter(str(r.get(key,"[missing]")) for r in rows))
    return {
        "scope":"Author-published deidentified metadata only; no revision bodies.",
        "files":{name:{"bytes":(root/name).stat().st_size,"sha256":hashlib.sha256((root/name).read_bytes()).hexdigest()} for name in ("pages.jsonl","events.jsonl","labels.jsonl")},
        "page_count":len(pages),
        "event_count":len(events),
        "label_record_count":len(labels),
        "nonempty_label_count":sum(bool(r.get("label")) for r in labels),
        "human_marked_label_records":sum(r.get("is_human_handle") is True for r in labels),
        "stored_page_revision_sum":sum(r.get("n_revs",0) for r in pages),
        "wiki_page_counts":counts(pages,"wiki"),
        "page_family_counts":counts(pages,"page_family"),
        "event_type_counts":counts(events,"event_type"),
        "event_time_grade_counts":counts(events,"time_grade"),
        "success_observed_field_counts":counts(events,"success_observed"),
        "success_observed_by_event_type":{kind:counts([r for r in events if r.get("event_type")==kind],"success_observed") for kind in sorted({r.get("event_type","") for r in events})},
        "first_page_write_span":span(pages,"first_write"),
        "last_page_write_span":span(pages,"last_write"),
        "event_time_span":span(events,"time"),
        "pages_with_more_than_one_label":sum(isinstance(r.get("n_labels"),int) and r["n_labels"]>1 for r in pages),
        "limits":[
            "A label count is not an independent-agent count.",
            "Page co-presence is not a reply edge, coordination, or common operator.",
            "success_observed=False means no success recorded by that field, not proof of failure.",
            "A request timestamp and revision timestamp are different event types.",
            "Publisher metadata and classification fields were not independently re-created.",
            "No IP, raw request, payload, or source_ref contents are exported.",
        ],
    }

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    out=aggregate(args.data)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

