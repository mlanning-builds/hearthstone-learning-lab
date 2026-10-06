import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class HeldSpellTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players;self.p.hand=[];self.p.mana=self.p.max_mana=10
        self.p.deck=['CORE_CS2_029','CORE_EX1_506']
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def play(self,cid,target=0):
        c=self.give(cid);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def test_strike_draws_minion_only(self):
        self.give('EDR_471');self.play('TIME_750',-2)
        self.assertEqual(self.q.health,27);self.assertEqual(self.p.hand[-1].card_id,'CORE_EX1_506')
        self.assertEqual(self.p.deck,['CORE_CS2_029'])
    def test_strike_does_not_count_expensive_spell(self):
        self.give('CORE_OG_211');self.play('TIME_750',-2);self.assertEqual(len(self.p.hand),1)
    def test_strike_discounted_minion_below_threshold(self):
        c=self.give('EDR_471');c.cost_delta=-6;self.play('TIME_750',-2)
        self.assertEqual(len(self.p.hand),1)
    def test_strike_no_matching_draw_does_not_draw_spell(self):
        self.give('EDR_471');self.p.deck=['CORE_CS2_029'];self.play('TIME_750',-2)
        self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.deck,['CORE_CS2_029'])
    def test_firelord_base_damage(self):
        m=self.g._summon(1,'EDR_471');self.play('FIR_923');self.assertEqual(m.health,26)
    def test_firelord_bonus_damage(self):
        self.give('CORE_OG_211');m=self.g._summon(1,'EDR_471');self.play('FIR_923')
        self.assertEqual(m.health,22)
    def test_firelord_discount_disables_bonus(self):
        c=self.give('CORE_OG_211');c.cost_delta=-1
        m=self.g._summon(1,'EDR_471');self.play('FIR_923');self.assertEqual(m.health,26)
    def test_firelord_spell_damage_and_enemy_only(self):
        self.g._summon(0,'TIME_856');self.give('EDR_471')
        m=self.g._summon(1,'EDR_471');self.play('FIR_923')
        self.assertEqual(m.health,20);self.assertEqual(self.q.health,30)
