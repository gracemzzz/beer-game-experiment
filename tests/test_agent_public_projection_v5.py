"""Protect the boundary between public evidence and private model records."""
from pathlib import Path
import importlib.util
import json
import unittest

spec=importlib.util.spec_from_file_location('agent_trace',Path(__file__).resolve().parents[1]/'scripts/audit_agent_public_trace_v5.py')
trace=importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class ProjectionTests(unittest.TestCase):
    def test_projection_excludes_private_records_and_internal_metadata(self):
        events=[
            {'type':'response_item','payload':{'type':'reasoning','text':'PRIVATE_REASONING'}},
            {'type':'response_item','payload':{'type':'message','role':'developer','content':[{'type':'input_text','text':'PRIVATE_INSTRUCTION'}]}},
            {'type':'response_item','payload':{'type':'message','role':'assistant','channel':'analysis','content':[{'type':'output_text','text':'PRIVATE_ANALYSIS'}]}},
            {'type':'turn_context','payload':{'model':'example','effort':'high','instructions':'PRIVATE_CONTEXT'}},
            {'type':'response_item','payload':{'type':'custom_tool_call','call_id':'1','name':'exec','input':'PUBLIC_COMMAND','internal_chat_message_metadata_passthrough':'PRIVATE_METADATA'}},
            {'type':'response_item','payload':{'type':'message','role':'assistant','channel':'final','content':[{'type':'output_text','text':'PUBLIC_STATUS'}]}},
        ]
        public,settings,_=trace.project('\n'.join(json.dumps(e) for e in events).encode())
        result=json.dumps(public)
        self.assertNotIn('PRIVATE_',result)
        self.assertIn('PUBLIC_COMMAND',result)
        self.assertIn('PUBLIC_STATUS',result)
        self.assertEqual(settings,[{'model':'example','effort':'high'}])

    def test_encrypted_parent_body_remains_an_explicit_gap(self):
        event={'type':'response_item','payload':{'type':'agent_message','author':'/root','recipient':'/root/test','content':[
            {'type':'input_text','text':'Message header'}, {'type':'encrypted_content','encrypted_content':'CIPHERTEXT'}]}}
        public,_,_=trace.project(json.dumps(event).encode())
        self.assertTrue(public[0]['encrypted_body_present'])
        self.assertNotIn('CIPHERTEXT',json.dumps(public))
        self.assertEqual(public[0]['visible_text'],'Message header')


if __name__=='__main__':
    unittest.main()
