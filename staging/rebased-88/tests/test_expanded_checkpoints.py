import json
from pathlib import Path
import tempfile
import unittest
from expanded.checkpoints import save_policy,load_policy
from expanded.learning import SparsePolicy

class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'policy.json'
    def save(self):
        p=SparsePolicy(seed=33,weights={'a':0.4,'b':-0.3})
        p.choose([{'a':1},{'b':1}]);receipt=save_policy(self.path,p,completed_episodes=7)
        return p,receipt
    def test_exact_sampling_and_weights_resume(self):
        p,r=self.save();q,m=load_policy(self.path,expected_sha256=r['sha256'])
        self.assertEqual(p.weights,q.weights);self.assertEqual(m['completed_episodes'],7)
        rows=[{'a':1},{'b':1}]
        self.assertEqual([p.choose(rows) for _ in range(100)],[q.choose(rows) for _ in range(100)])
    def test_no_overwrite_or_temporary_files(self):
        p,r=self.save();before=self.path.read_bytes()
        with self.assertRaises(FileExistsError):save_policy(self.path,p,completed_episodes=8)
        self.assertEqual(before,self.path.read_bytes());self.assertEqual(list(self.path.parent.iterdir()),[self.path])
    def test_checksum_detects_changed_snapshot(self):
        p,r=self.save();self.path.write_bytes(self.path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'checksum'):load_policy(self.path,expected_sha256=r['sha256'])
    def test_reject_version_and_engine_mismatches(self):
        self.save();original=json.loads(self.path.read_text())
        for field in ('schema','feature_schema','engine_fingerprint'):
            data=dict(original);data[field]='wrong';self.path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_policy(self.path)
    def test_reject_malformed_rng_and_weights(self):
        self.save();original=json.loads(self.path.read_text())
        for field,value in [('rng_state',[3,[1],None]),('weights',{'a':'bad'}),('completed_episodes',True)]:
            data=dict(original);data[field]=value;self.path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):load_policy(self.path)
    def test_invalid_weights_never_publish(self):
        p=SparsePolicy(seed=2);p.weights['bad']=float('nan')
        with self.assertRaises(ValueError):save_policy(self.path,p,completed_episodes=0)
        self.assertFalse(self.path.exists())
