"""Extract metadata from saved public ClawdChat HTML without running JavaScript.

Only exact JSON arguments to Next.js data pushes are decoded. The output omits
authors, titles and bodies. Preserve the input privately; hashes bind bytes, not
server authenticity. Initial posts are used only if their order matches the
rendered h2 titles. The first two records are preflight-only and excluded.
"""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class PageData(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_script = False
        self.in_heading = False
        self.script_buffer = []
        self.heading_buffer = []
        self.scripts = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
            self.script_buffer = []
        if tag == 'h2':
            self.in_heading = True
            self.heading_buffer = []

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_script:
            self.scripts.append(''.join(self.script_buffer))
            self.in_script = False
        if tag == 'h2' and self.in_heading:
            self.headings.append(''.join(self.heading_buffer))
            self.in_heading = False

    def handle_data(self, value):
        if self.in_script:
            self.script_buffer.append(value)
        if self.in_heading:
            self.heading_buffer.append(value)


def extract_posts(raw):
    page = PageData()
    page.feed(raw.decode('utf-8', errors='strict'))
    parts = []
    for script in page.scripts:
        match = re.fullmatch(r'\s*self\.__next_f\.push\((\[.*\])\);?\s*', script, re.S)
        if not match:
            continue
        value = json.loads(match.group(1))
        if len(value) == 2 and value[0] == 1 and isinstance(value[1], str):
            parts.append(value[1])
    flight = ''.join(parts)
    found = list(re.finditer(r'"initialPosts"\s*:', flight))
    if len(found) != 1:
        raise ValueError('Expected exactly one initialPosts array')
    posts, _ = json.JSONDecoder().raw_decode(flight[found[0].end():].lstrip())
    if not isinstance(posts, list) or not all(isinstance(x, dict) for x in posts):
        raise ValueError('Invalid initialPosts structure')
    if page.headings[:len(posts)] != [x.get('title') for x in posts]:
        raise ValueError('Rendered h2 order does not match initialPosts')
    return posts, flight


def content_text(post, flight):
    value = post.get('content')
    if not isinstance(value, str):
        return None
    reference = re.fullmatch(r'\$([0-9a-f]+)', value)
    if not reference:
        return value
    # React Flight T records carry a hexadecimal UTF-8 byte length.
    markers = list(re.finditer(r'(?<![0-9a-f])' + re.escape(reference[1]) + r':T([0-9a-f]+),', flight))
    if len(markers) != 1:
        return None
    marker = markers[0]
    length = int(marker[1], 16)
    payload = flight[marker.end():].encode('utf-8')
    if len(payload) < length:
        raise ValueError('Truncated Flight text record')
    return payload[:length].decode('utf-8', errors='strict')


def metadata(post, position, flight):
    post_id = post.get('id')
    valid_id = isinstance(post_id, str) and bool(re.fullmatch(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', post_id))
    if not valid_id:
        raise ValueError('Missing or invalid stable ID')
    body = post.get('content')
    canonical = 'https://clawdchat.cn/post/' + post_id
    observed_url = post.get('web_url')
    if observed_url != canonical:
        raise ValueError('Observed web_url does not match stable ID')
    return {
        'source_position': position,
        'record_type': 'post',
        'post_id': post_id,
        'url': observed_url,
        'url_status': 'observed web_url in HTML payload; matches stable ID; detail page not fetched',
        'created_at': post.get('created_at'),
        'updated_at': post.get('updated_at'),
        'time_evidence': 'platform HTML payload fields; not signed',
        'parent_field_present': 'parent_id' in post,
        'parent_id': post.get('parent_id'),
        'pinned_field_present': 'is_pinned' in post,
        'is_pinned': post.get('is_pinned'),
        'content_field_present': 'content' in post,
        'content_is_plain_string': isinstance(body, str) and not bool(re.fullmatch(r'\$[0-9a-f]+', body)),
        'content_text_resolved': content_text(post, flight) is not None,
        'comment_count_platform_field': post.get('comment_count'),
        'replies_in_this_record': isinstance(post.get('comments'), list),
    }


def build(raw):
    posts, flight = extract_posts(raw)
    if len(posts) < 2:
        raise ValueError('Fewer than two preflight items')
    preflight = [metadata(x, i + 1, flight) for i, x in enumerate(posts[:2])]
    if not all(x['created_at'] for x in preflight):
        raise ValueError('Preflight lacks timestamps')
    selected = [metadata(x, i + 3, flight) for i, x in enumerate(posts[2:22])]
    seen = set()
    content_positions = {}
    for record in selected:
        record['duplicate_within_selected'] = record['post_id'] in seen
        record['duplicates_preflight'] = record['post_id'] in {x['post_id'] for x in preflight}
        seen.add(record['post_id'])
        text = content_text(posts[record['source_position'] - 1], flight)
        if text is not None:
            content_positions.setdefault(text, []).append(record['source_position'])
    return {
        'source_url': 'https://clawdchat.cn/explore',
        'input_bytes': len(raw),
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'hash_scope': 'exact raw file bytes',
        'rendered_order_verified': True,
        'initial_post_count': len(posts),
        'preflight_excluded_count': 2,
        'preflight': preflight,
        'selected': selected,
        'selected_count': len(selected),
        'selected_unique_ids': len(seen),
        'exact_duplicate_content_groups': [positions for positions in content_positions.values() if len(positions) > 1],
        'notes': 'No later page is fetched. Missing reply fields are not zero replies.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = build(args.input.read_bytes())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['input_sha256', 'initial_post_count', 'selected_count', 'selected_unique_ids']}))


if __name__ == '__main__':
    main()
