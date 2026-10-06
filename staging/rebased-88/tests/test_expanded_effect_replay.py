"""Captured contexts, live/dead Deathrattles and recruited payloads."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card

class ReplayTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid,target=0):
        c=g._enter_hand(0,Card(g._new_id(),cid));g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def die(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def test_swimmer_triggers_without_killing_subject(self):
        g=self.game();m=g._summon(0,'CORE_EX1_096');n=len(g.players[0].deck);self.play(g,'JAIL_395',m.uid)
        self.assertIn(m,g.players[0].minions);self.assertEqual(len(g.players[0].deck),n-1);self.assertEqual(g.players[0].corpses,0)
    def test_swimmer_attached_effect_uses_subject_as_source(self):
        g=self.game();m=g._summon(0,'EDR_851t');m.attached_death_effects=[('buff_self',2,3)];a,h=m.attack,m.health
        self.play(g,'JAIL_395',m.uid);self.assertEqual((m.attack,m.health),(a+2,h+3))
    def test_swimmer_rejects_non_deathrattle_target(self):
        g=self.game();m=g._summon(0,'EDR_851t');c=g._enter_hand(0,Card(g._new_id(),'JAIL_395'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid and a.target==m.uid for a in g.legal_actions()))
    def test_swimmer_silenced_printed_deathrattle_not_eligible(self):
        g=self.game();m=g._summon(0,'CORE_EX1_096');g._silence(m);self.assertEqual(g._targets_for('JAIL_395',0),[0])
    def test_sentence_replays_friendly_death(self):
        g=self.game();self.die(g,g._summon(0,'CORE_EX1_096'));n=len(g.players[0].deck);self.play(g,'JAIL_940');self.assertEqual(len(g.players[0].deck),n-1)
    def test_sentence_ignores_enemy_history(self):
        g=self.game();self.die(g,g._summon(1,'CORE_EX1_096'));n=len(g.players[0].deck);self.play(g,'JAIL_940');self.assertEqual(len(g.players[0].deck),n)
    def test_umbra_replays_up_to_five_records(self):
        g=self.game()
        for _ in range(6):self.die(g,g._summon(0,'CORE_LOOT_413'))
        before=g.players[0].armor;self.play(g,'TLC_106');self.assertEqual(g.players[0].armor,before+15)
    def test_sawbones_rewards_destroyed_other_minions(self):
        g=self.game()
        for _ in range(3):g._summon(0,'EDR_851t')
        cost=g.cards['JAIL_444']['cost'];n=len(g.players[0].deck);self.play(g,'JAIL_444')
        self.assertEqual(len(g.players[0].deck),n-3);self.assertEqual(g.players[0].mana,min(10,10-cost+3));self.assertEqual([m.card_id for m in g.players[0].minions],['JAIL_444'])
    def test_sawbones_ignores_enemy(self):
        g=self.game();m=g._summon(1,'EDR_851t');n=len(g.players[0].deck);self.play(g,'JAIL_444');self.assertIn(m,g.players[1].minions);self.assertEqual(len(g.players[0].deck),n)
    def test_sawbones_reborn_survives_but_counts_destroyed(self):
        g=self.game();m=g._summon(0,'EDR_851t');m.keywords.add('REBORN');n=len(g.players[0].deck);self.play(g,'JAIL_444')
        self.assertEqual(len(g.players[0].deck),n-1);self.assertEqual(len(g.players[0].minions),2)
    def test_moragg_recruits_and_adds_reciprocal_deathrattle(self):
        g=self.game();c=Card(g._new_id(),'CORE_EX1_319');c.attack_bonus=2;g.players[0].deck=[c]
        self.die(g,g._summon(0,'JAIL_906'));m=g.players[0].minions[0];self.assertEqual(m.attack,g.cards[c.card_id]['attack']+2)
        self.die(g,m);self.assertEqual([m.card_id for m in g.players[0].minions],['JAIL_906'])
    def test_moragg_does_not_draw_non_demon(self):
        g=self.game();self.die(g,g._summon(0,'JAIL_906'));self.assertFalse(g.players[0].minions);self.assertEqual(len(g.players[0].deck),20)
    def test_parasite_gains_friendly_demon_stats(self):
        g=self.game();m=g._summon(0,'JAIL_721');a,h=m.attack,m.health;d=g._summon(0,'CORE_EX1_319');g._settle();self.assertEqual((m.attack,m.health),(a+d.attack,h+d.health))
    def test_parasite_ignores_enemy_and_non_demon(self):
        g=self.game();m=g._summon(0,'JAIL_721');a,h=m.attack,m.health;g._summon(1,'CORE_EX1_319');g._summon(0,'EDR_851t');g._settle();self.assertEqual((m.attack,m.health),(a,h))
    def test_maul_triggers_end_effect(self):
        g=self.game();g._summon(0,'TIME_054');g._equip(0,'CATA_472');g._break_weapon(0);g._settle(allow_event_choices=True)
        self.assertEqual([c.card_id for c in g.players[0].hand],['TOKEN_COIN'])
    def test_maul_does_not_trigger_silenced_end_effect(self):
        g=self.game();m=g._summon(0,'TIME_054');g._silence(m);g._equip(0,'CATA_472');g._break_weapon(0);g._settle(allow_event_choices=True)
        self.assertFalse(g.players[0].hand)
