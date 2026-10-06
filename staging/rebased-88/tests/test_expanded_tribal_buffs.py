import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class TribalBuffTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid,target):
        c=self.give(cid);self.g.step(Action('play',c.uid,target))
    def test_untyped_target_only_buffs_itself(self):
        a=self.g._summon(0,'Core_CS2_200');b=self.g._summon(0,'Core_CS2_200')
        self.play('TLC_441',a.uid);self.assertEqual((a.attack,a.max_health),(7,9))
        self.assertEqual((b.attack,b.max_health),(6,7))
    def test_dual_type_and_all_match_without_buffing_opponent(self):
        a=self.g._summon(0,'RLK_708');b=self.g._summon(0,'DINO_435');c=self.g._summon(1,'RLK_708')
        before=[m.attack for m in (a,b,c)]
        self.play('TLC_441',a.uid)
        self.assertEqual([m.attack for m in (a,b,c)],[before[0]+1,before[1]+1,before[2]])
    def test_all_target_matches_typed_but_not_untyped(self):
        a=self.g._summon(0,'DINO_435');b=self.g._summon(0,'RLK_708');c=self.g._summon(0,'Core_CS2_200')
        before=[m.attack for m in (a,b,c)];self.play('TLC_441',a.uid)
        self.assertEqual([m.attack for m in (a,b,c)],[before[0]+1,before[1]+1,before[2]])
    def test_nurturing_buffs_board_beast_and_one_eligible_hand_card(self):
        m=self.g._summon(0,'DINO_130t');before=(m.attack,m.max_health)
        a=self.give('DINO_435');b=self.give('Core_CS2_200')
        self.play('MEND_305',m.uid)
        self.assertEqual((m.attack,m.max_health),(before[0]+2,before[1]+2))
        self.assertEqual((a.attack_bonus,a.health_bonus),(2,2));self.assertEqual(b.attack_bonus,0)
    def test_nurturing_requires_friendly_beast_and_allows_empty_hand(self):
        spell=self.give('MEND_305');other=self.g._summon(1,'DINO_130t')
        self.assertFalse(any(a.kind=='play' and a.source==spell.uid for a in self.g.legal_actions()))
        own=self.g._summon(0,'DINO_130t');before=own.attack
        self.g.step(Action('play',spell.uid,own.uid));self.assertEqual(own.attack,before+2)
