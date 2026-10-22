"""Synthetic checks: no live network and no copied third-party post content."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import unittest
from extract_clawdchat_snapshot import build, content_text, extract_posts


def fixture(reorder=False, duplicate=False):
    posts=[]
    for i in range(4):
        ident=f'00000000-0000-0000-0000-{i:012d}'
        posts.append({'id':ident, 'web_url':'https://clawdchat.cn/post/'+ident,
                      'title':f'item{i}', 'content':'same' if i>=2 else 'preflight',
                      'created_at':'2026-01-01T00:00:00Z'})
    if duplicate:
        posts[3]['id']=posts[2]['id']; posts[3]['web_url']=posts[2]['web_url']
    headings=[x['title'] for x in posts]
    if reorder: headings.reverse()
    data='0:'+json.dumps({'initialPosts':posts})+'\n'
    return (''.join('<h2>'+x+'</h2>' for x in headings)+
            '<script>self.__next_f.push('+json.dumps([1,data])+')</script>').encode()


class Checks(unittest.TestCase):
    def test_preflight_and_content_duplicates(self):
        result=build(fixture())
        self.assertEqual([x['source_position'] for x in result['selected']], [3,4])
        self.assertEqual(result['exact_duplicate_content_groups'], [[3,4]])
        self.assertEqual(result['selected_unique_ids'],2)
    def test_order_mismatch_rejected(self):
        with self.assertRaises(ValueError): build(fixture(reorder=True))
    def test_duplicate_ids_preserve_positions(self):
        result=build(fixture(duplicate=True))
        self.assertEqual(result['selected_count'],2)
        self.assertEqual(result['selected_unique_ids'],1)
        self.assertTrue(result['selected'][1]['duplicate_within_selected'])
    def test_flight_length_uses_utf8_bytes(self):
        value='中文\ntext'
        stream='12:T'+format(len(value.encode()),'x')+','+value+'13:T1,x'
        self.assertEqual(content_text({'content':'$12'},stream),value)
        self.assertEqual(content_text({'content':'$13'},stream),'x')
    def test_executable_argument_not_evaluated(self):
        with self.assertRaises((ValueError,json.JSONDecodeError)):
            extract_posts(b'<script>self.__next_f.push([1,alert(1)])</script>')


if __name__=='__main__': unittest.main()
