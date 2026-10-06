import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ConditionalCostCardTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('PRIEST',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.mana=p.max_mana=10
    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c
    def test_slitherdrake_does_not_count_itself(self):
        c=self.give('END_033');self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
    def test_another_dragon_discount_appears_and_disappears(self):
        c=self.give('END_033');other=self.give('END_033');base=self.g.cards[c.card_id]['cost']
        self.assertEqual(self.g._cost(c,0),max(0,base-3))
        self.g._discard_card(0,other);self.assertEqual(self.g._cost(c,0),base)
    def test_board_dragon_does_not_qualify(self):
        c=self.give('END_033');self.g._summon(0,'END_033')
        self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
    def test_siren_needs_both_schools_this_turn(self):
        c=self.give('TLC_819')
        holy=next(cid for cid,d in self.g.cards.items() if d.get('spellSchool')=='HOLY')
        shadow=next(cid for cid,d in self.g.cards.items() if d.get('spellSchool')=='SHADOW')
        self.p.spells_turn=[holy];self.p.spell_schools_this_turn={'HOLY'};self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
        self.p.spells_turn.append(shadow);self.p.spell_schools_this_turn.add('SHADOW');self.assertEqual(self.g._cost(c,0),1)
        self.p.spells_turn=[];self.p.spell_schools_this_turn.clear();self.p.spells_previous=[holy,shadow]
        self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
    def test_siren_still_receives_explicit_cost_modifiers(self):
        c=self.give('TLC_819')
        self.p.spells_turn=[next(cid for cid,d in self.g.cards.items() if d.get('spellSchool')==school) for school in ('HOLY','SHADOW')]
        self.p.spell_schools_this_turn={'HOLY','SHADOW'}
        c.cost_delta=2;self.assertEqual(self.g._cost(c,0),3)
    def test_lure_counts_actual_power_uses_not_healing(self):
        c=self.give('EDR_477');base=self.g._cost(c,0)
        self.g.step(Action('power',target=-1))
        self.assertEqual(self.p.hero_power_uses,1);self.assertEqual(self.g._cost(c,0),max(0,base-1))
        self.assertEqual(self.g.observe(1)['players'][0]['hero_power_uses'],1)
    def test_illegal_power_does_not_increment_counter(self):
        self.p.mana=0
        with self.assertRaises(ValueError):self.g.step(Action('power',target=-1))
        self.assertEqual(self.g.players[0].hero_power_uses,0)
    def test_lure_count_is_owner_specific_and_cost_floored(self):
        c=self.give('EDR_477');base=self.g._cost(c,0);self.q.hero_power_uses=50
        self.assertEqual(self.g._cost(c,0),base);self.p.hero_power_uses=50
        self.assertEqual(self.g._cost(c,0),0)
    def test_discounted_cost_controls_legality_and_payment(self):
        c=self.give('END_033');self.give('END_033')
        cost=self.g._cost(c,0);self.p.mana=cost
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        self.g.step(action);self.assertEqual(self.p.mana,0)

    def test_school_condition_resets_on_opponents_turn(self):
        c=self.give('TLC_819');self.p.spell_schools_this_turn={'HOLY','SHADOW'}
        self.g.step(Action('end'))
        self.assertEqual(self.p.spell_schools_this_turn,set())
        self.assertEqual(self.g._cost(c,0),self.g.cards[c.card_id]['cost'])
