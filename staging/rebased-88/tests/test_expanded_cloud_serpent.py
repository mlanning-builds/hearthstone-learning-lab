import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.selectors import has_tribe

class CloudSerpentTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*10;p.mana=p.max_mana=10
    def give(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g.players[owner].hand.append(c);return c
    def play(self):
        c=self.give('TLC_888');self.g.step(Action('play',c.uid,position=len(self.p.board)));return c
    def test_played_serpent_cannot_copy_itself(self):
        self.play();self.assertEqual(self.p.hand,[])
    def test_each_tribe_can_be_copied(self):
        for tribe in ('ELEMENTAL','DRAGON'):
            with self.subTest(tribe=tribe):
                self.p.hand=[];self.p.mana=10
                cid=next(cid for cid,d in self.g.cards.items() if d['type']=='MINION' and has_tribe(d,tribe))
                original=self.give(cid);self.play()
                self.assertEqual([c.card_id for c in self.p.hand],[cid,cid]);self.assertNotEqual(original.uid,self.p.hand[-1].uid)
    def test_copy_preserves_modifiers_without_aliasing(self):
        original=self.give('TLC_888');original.attack_bonus=3;original.health_bonus=4;original.cost_delta=-2
        self.play();clone=self.p.hand[-1]
        self.assertEqual((clone.attack_bonus,clone.health_bonus,clone.cost_delta),(3,4,-2))
        clone.attack_bonus=9;clone.cost_delta=-5
        self.assertEqual((original.attack_bonus,original.cost_delta),(3,-2))
    def test_union_does_not_duplicate_dual_tribe_card(self):
        original=self.give('TLC_888');self.give('CORE_CS2_029');self.give('TLC_888',1)
        with patch.object(self.g.rng,'choice',wraps=self.g.rng.choice) as choose:self.play()
        self.assertEqual(len(choose.call_args_list),1)
        self.assertEqual([c.uid for c in choose.call_args.args[0]],[original.uid])
    def test_summoning_does_not_trigger_battlecry(self):
        original=self.give('TLC_888');self.g._summon(0,'TLC_888');self.assertEqual(self.p.hand,[original])
    def test_full_hand_does_not_overflow(self):
        for _ in range(10):self.give('TLC_888')
        self.g._effect(('copy_random_hand_any',((('tribe','eq','DRAGON'),),)),dict(owner=0,target=0,source=None))
        self.assertEqual(len(self.p.hand),10)
