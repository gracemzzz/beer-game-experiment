import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_agent_page_exposure_v5 import displayed_states, verify


class ExposureTests(unittest.TestCase):
    def test_nested_public_tool_output_decodes_without_evaluation(self):
        state={'batch_id':'x','decision':{'inventory':12,'phase':'initial'}}
        wrapped=repr([{'type':'input_text','text':json.dumps({'output':json.dumps(state)})}])
        self.assertEqual(displayed_states(wrapped),[state])
        self.assertEqual(displayed_states("__import__('os').remove('file')"),[])

    def scenario(self, filtered=False):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder=Path(tmp.name);(folder/'steps').mkdir()
        before={'batch_id':'x','decision':{'phase':'initial','inventory':12}}
        after={'batch_id':'x','phase':'complete'}
        choices={'c001':[4,4,4,4]}
        (folder/'steps/0001.json').write_text(json.dumps(dict(action='submit',index=1,
            choices=choices,display_before=before,display_after=after)))
        def call(cid,cmd):return dict(type='custom_tool_call',record=cid,call_id=str(cid),input='text(await tools.exec_command('+json.dumps({'cmd':cmd})+'));')
        def output(cid,obj):return dict(type='custom_tool_call_output',call_id=str(cid),output=json.dumps(obj))
        command="@'\n"+json.dumps(choices)+"\n'@ | python driver.py submit --run local"
        shown={'batch_id':'x','decision':{'phase':'initial'}} if filtered else before
        public=[call(1,'python driver.py show --run local'),output(1,shown),
            call(2,command),output(2,{'output':'FileNotFoundError: typo'}),
            call(3,command),output(3,after)]
        (folder/'PUBLIC_TRANSCRIPT.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in public))
        return verify(folder)

    def test_rejected_identical_input_does_not_take_accepted_mapping(self):
        result=self.scenario()
        self.assertTrue(result['mechanical_full_page_exposure_passed'])
        self.assertEqual(result['accepted_mapping'][0]['public_record'],3)
        self.assertEqual(result['failed_or_unmatched_attempts'][0]['record'],2)

    def test_filtered_state_is_not_full_exposure(self):
        result=self.scenario(filtered=True)
        self.assertFalse(result['mechanical_full_page_exposure_passed'])
        self.assertEqual(result['full_before_count'],0)


if __name__=='__main__':unittest.main()
