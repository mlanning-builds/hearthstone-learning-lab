"""Candidate Tyrande/Niri activation; disputed attribution stays in fidelity gaps."""
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.features import encode_decision,SCHEMA

class RepeatConsumerTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PRIEST',31),random_deck('HUNTER',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:p.hand=[];p.board=[];p.deck=[];p.health=p.max_health=100;p.mana=p.max_mana=10;p.cards_played=0
        return g
    def play(self,g,cid,target=0,cost=None,choices=None):
        g.players[0].mana=10;c=g._add(0,cid)
        if cost is not None:c.set_cost=cost
        a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target and (choices is None or a.choices==choices))
        g.step(a);return c
    def tyrande(self,g):
        self.play(g,'EDR_464');return next(m for m in g.players[0].minions if m.card_id=='EDR_464')
    def test_tyrande_three_spells_then_normal(self):
        g=self.game();self.tyrande(g)
        for _ in range(3):self.play(g,'CORE_CS2_029',-2)
        self.assertEqual(g.players[1].health,64);self.assertEqual(g.players[0].spell_repeat_charges,0)
        self.play(g,'CORE_CS2_029',-2);self.assertEqual(g.players[1].health,58)
    def test_charges_survive_minion_silence_and_death(self):
        g=self.game();m=self.tyrande(g);g._silence(m);m.health=0;g._settle()
        self.play(g,'CORE_CS2_029',-2);self.assertEqual(g.players[1].health,88)
    def test_minions_and_powers_do_not_spend_charges(self):
        g=self.game();self.tyrande(g);self.play(g,'AT_037t');g.players[0].health=90
        g.step(Action('power',target=-1));self.assertEqual(g.players[0].spell_repeat_charges,3)
    def test_internal_cast_does_not_spend_tyrande_charge(self):
        g=self.game();self.tyrande(g)
        g._start_play_effects([('cast_fixed_spell','CORE_CS2_029','enemies')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertEqual(g.players[1].health,94);self.assertEqual(g.players[0].spell_repeat_charges,3)
    def test_repetition_has_one_payment_and_history_entry(self):
        g=self.game();self.tyrande(g);before=g.players[0].cards_played
        self.play(g,'CORE_CS2_029',-2)
        self.assertEqual(g.players[0].mana,6);self.assertEqual(g.players[0].cards_played,before+1)
        self.assertEqual(g.players[0].spells_turn,['CORE_CS2_029'])
    def test_tyrande_retains_choose_one_branch(self):
        g=self.game();self.tyrande(g);g.players[0].deck=['CORE_CS2_029']*4
        m=g._summon(1,'AT_037t');m.health=m.max_health=10
        self.play(g,'CORE_EX1_154',m.uid,choices=(1,))
        self.assertEqual(m.health,8);self.assertEqual(len(g.players[0].hand),2)
    def test_discover_consumes_one_charge_across_two_choices(self):
        g=self.game();self.tyrande(g);g.players[0].deck=['CORE_CS2_029','CORE_CS2_024']
        self.play(g,'CORE_DS1_184');self.assertEqual(g.players[0].spell_repeat_charges,2)
        g.step(Action('choose',choices=(0,)));g.step(Action('choose',choices=(0,)))
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g.players[0].spell_repeat_charges,2)
    def test_niri_uses_paid_cost_for_hand_spell(self):
        g=self.game();g._summon(0,'TLC_836');self.play(g,'CORE_CS2_029',-2,cost=1)
        self.assertEqual(g.players[1].health,88);self.assertEqual(g.players[0].mana,9)
    def test_niri_does_not_double_zero_or_two_cost_spell(self):
        for cost in (0,2):
            with self.subTest(cost=cost):
                g=self.game();g._summon(0,'TLC_836');self.play(g,'CORE_CS2_029',-2,cost=cost)
                self.assertEqual(g.players[1].health,94)
    def test_silenced_or_enemy_niri_does_not_double(self):
        for owner in (0,1):
            g=self.game();m=g._summon(owner,'TLC_836')
            if owner==0:g._silence(m)
            self.play(g,'CORE_CS2_029',-2,cost=1);self.assertEqual(g.players[1].health,94)
    def test_niri_doubles_played_discounted_minion(self):
        g=self.game();g._summon(0,'TLC_836');self.play(g,'AT_037t',cost=1)
        m=next(m for m in g.players[0].minions if m.card_id=='AT_037t')
        self.assertEqual((m.attack,m.health),(2,2))
    def test_niri_does_not_double_summoned_minion(self):
        g=self.game();g._summon(0,'TLC_836');m=g._summon(0,'AT_037t');g._settle()
        self.assertEqual((m.attack,m.health),(1,1))
    def test_niri_internal_physical_spell_uses_card_cost(self):
        g=self.game();g._summon(0,'TLC_836');c=Card(g._new_id(),'CORE_CS2_029');c.set_cost=1
        g._start_play_effects([('cast_physical_spell',c,'enemies')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertEqual(g.players[1].health,88)
    def test_overlapping_doublers_do_not_multiply(self):
        g=self.game();self.tyrande(g);g._summon(0,'TLC_836');g._summon(0,'TLC_836')
        self.play(g,'CORE_CS2_029',-2,cost=1);self.assertEqual(g.players[1].health,88)
        self.assertEqual(g.players[0].spell_repeat_charges,2)
    def test_charges_are_visible_and_encoded(self):
        g=self.game();self.tyrande(g);view=g.observe(0)
        self.assertEqual(view['players'][0]['spell_repeat_charges'],3)
        self.assertEqual(g.observe(1)['players'][0]['spell_repeat_charges'],3)
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertIn('spell_repeat_charges',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
