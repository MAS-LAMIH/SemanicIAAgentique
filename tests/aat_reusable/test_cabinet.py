import unittest
from experiments.aat_reusable.cabinet_native import Cabinet,serve
from experiments.aat_reusable.cabinet_score import score
from semantic_action.transport import HTTPTransport
class CabinetTests(unittest.TestCase):
 def test_direct_native_create_release_rejection_and_frame(self):
  state=Cabinet();before=state.snapshot()
  with serve(state) as origin:
   t=HTTPTransport(origin)
   self.assertEqual(t._http_request('PUT','/cabinet/secure',{'guard':{'generation':0}}).status,200)
   self.assertTrue(state.secured)
   self.assertEqual(t._http_request('PUT','/cabinet/release',{'guard':{'generation':0}}).status,409)
   self.assertTrue(state.secured);self.assertEqual(state.writes,1)
   self.assertEqual(t._http_request('PUT','/cabinet/release',{'guard':{'generation':1}}).status,200)
   self.assertFalse(state.secured);self.assertEqual(state.unrelated,before['unrelated'])
   self.assertEqual(t._http_request('PUT','/cabinet/secure',{'guard':{'generation':True}}).status,400)
   state.ready=False
   self.assertEqual(t._http_request('PUT','/cabinet/secure',{'guard':{'generation':2}}).status,422)
  self.assertEqual(state.writes,2)
 def test_native_scorer_detects_unchanged_effect_and_private_frame(self):
  state=Cabinet(mode='frame');before=state.snapshot()
  with serve(state) as origin:HTTPTransport(origin)._http_request('PUT','/cabinet/secure',{'guard':{'generation':0}})
  verdict=score(before,state.snapshot(),state.journal,True)
  self.assertFalse(verdict['native_success']);self.assertEqual(verdict['incorrect_native_transitions'],1)
if __name__=='__main__':unittest.main()
