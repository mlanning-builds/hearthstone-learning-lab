import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck


class LifestealBatchTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=10
        return g
    def context(self,owner=0):
        return dict(owner=owner,source=None,target=0,bonus=0,spell=True,lifesteal=True)
    def test_simultaneous_hits_heal_once_after_all_damage(self):
        g=self.game();a=g._summon(1,'CS2_033');b=g._summon(1,'CS2_033');calls=[];original=Game._heal
        def heal(game,target,amount,**kwargs):
            calls.append((amount,a.health,b.health));return original(game,target,amount,**kwargs)
        with patch.object(Game,'_heal',heal):
            with g._damage_batch():
                g._deal_effect(a.uid,2,self.context());g._deal_effect(b.uid,2,self.context())
        self.assertEqual(calls,[(4,4,4)]);self.assertEqual(g.players[0].health,14)
    def test_separate_hits_keep_separate_heals(self):
        g=self.game();a=g._summon(1,'CS2_033');calls=[];original=Game._heal
        def heal(game,target,amount,**kwargs):
            calls.append(amount);return original(game,target,amount,**kwargs)
        with patch.object(Game,'_heal',heal):
            g._deal_effect(a.uid,1,self.context());g._deal_effect(a.uid,1,self.context())
        self.assertEqual(calls,[1,1])
    def test_prevented_damage_does_not_add_healing(self):
        g=self.game();a=g._summon(1,'CS2_033');a.keywords.add('DIVINE_SHIELD')
        with patch.object(Game,'_heal') as heal:
            with g._damage_batch():g._deal_effect(a.uid,3,self.context())
            heal.assert_not_called()
        self.assertEqual(g.players[0].health,10)
    def test_exception_clears_batch_without_healing(self):
        g=self.game();a=g._summon(1,'CS2_033')
        with self.assertRaises(RuntimeError):
            with g._damage_batch():
                g._deal_effect(a.uid,1,self.context());raise RuntimeError('injected')
        self.assertEqual(g.players[0].health,10);self.assertEqual(g._lifesteal_batches,[])
        self.assertEqual(g._damage_batch_depth,0)
    def test_nested_batches_do_not_duplicate_healing(self):
        g=self.game();a=g._summon(1,'CS2_033');calls=[];original=Game._heal
        def heal(game,target,amount,**kwargs):
            calls.append(amount);return original(game,target,amount,**kwargs)
        with patch.object(Game,'_heal',heal):
            with g._damage_batch():
                g._deal_effect(a.uid,1,self.context())
                with g._damage_batch():g._deal_effect(a.uid,2,self.context())
        self.assertEqual(calls,[2,1]);self.assertEqual(g.players[0].health,13)
