import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ThassarianDoveTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid):
        c=self.give(cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in self.p.minions if m.card_id==cid)
    def test_battlecry_deathrattle_reborn_and_second_death(self):
        m=self.play('RLK_223');self.assertEqual(self.q.health,28)
        m.health=0;self.g._settle();self.assertEqual(self.q.health,26)
        reborn=next(m for m in self.p.minions if m.card_id=='RLK_223')
        self.assertEqual(reborn.health,1);self.assertNotIn('REBORN',reborn.keywords)
        reborn.health=0;self.g._settle();self.assertEqual(self.q.health,24)
        self.assertEqual(self.p.minions,[])
    def test_silence_removes_deathrattle_and_reborn(self):
        m=self.play('RLK_223');self.g._silence(m);m.health=0;self.g._settle()
        self.assertEqual(self.q.health,28);self.assertEqual(self.p.minions,[])
    def test_summon_does_not_run_battlecry(self):
        self.g._summon(0,'RLK_223');self.assertEqual(self.q.health,30)
    def test_dove_buffs_existing_and_drawn_minions_only(self):
        held=self.give('CORE_EX1_506');spell=self.give('CORE_CS2_029')
        self.p.deck=['CORE_CS2_029','CORE_EX1_506'];dove=self.play('TIME_037')
        self.assertEqual([c.health_bonus for c in self.p.hand],[2,0,2])
        self.assertEqual(dove.health,2);self.assertEqual(self.p.deck,['CORE_CS2_029'])
    def test_dove_buffs_hand_when_deck_has_no_minions(self):
        held=self.give('CORE_EX1_506');self.p.deck=['CORE_CS2_029'];self.play('TIME_037')
        self.assertEqual(held.health_bonus,2);self.assertEqual(len(self.p.hand),1)
    def test_dove_buff_survives_play(self):
        held=self.give('CORE_EX1_506');self.p.deck=[];self.play('TIME_037')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==held.uid))
        m=next(m for m in self.p.minions if m.card_id=='CORE_EX1_506')
        self.assertEqual(m.health,3)
