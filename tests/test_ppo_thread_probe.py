"""Tiny numerical probe checks, without optimizer steps or game collection."""
import unittest
import torch
from tools.benchmark_ppo_threads import targets,compute,tensor_hash
from hearthstone_sim.neural.model import ModelConfig,TransformerPolicyValue

class ThreadProbeTests(unittest.TestCase):
    def test_computation_preserves_weights_and_finite_gradient(self):
        torch.set_num_threads(1)
        model=TransformerPolicyValue(ModelConfig(buckets=256,width=16,heads=2,layers=1,feedforward=32)).eval()
        item=dict(state=[[(1,1.)],[(2,1.)]],actions=[[(3,1.)],[(4,1.)]])
        batch=[item]*4;fixed=targets(model,batch);before=tensor_hash(model)
        result=compute(model,batch,fixed)
        self.assertTrue(all(torch.isfinite(torch.tensor(v)) for v in result));self.assertEqual(before,tensor_hash(model))
        gradients=[p.grad.clone() for p in model.parameters() if p.grad is not None]
        again=compute(model,batch,fixed)
        self.assertEqual(result,again)
        self.assertTrue(all(torch.equal(a,b.grad) for a,b in zip(gradients,[p for p in model.parameters() if p.grad is not None])))
    def test_no_optimizer_steps_exist_in_probe(self):
        import ast,inspect
        from tools import benchmark_ppo_threads as probe
        tree=ast.parse(inspect.getsource(probe))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr=='step' and not (isinstance(n.func.value,ast.Name) and n.func.value.id=='game') for n in calls))
if __name__=='__main__':unittest.main()
