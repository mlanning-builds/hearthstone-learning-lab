"""Bonus Effect eligibility and live card interactions."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.bonus_effects import BONUS_EFFECTS

class BonusEffectTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def play(self,g,cid,target=None):
        c=Card(g._new_id(),cid);g.players[g.current].hand.append(c)
        choices=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(choices);g.step(max(choices,key=lambda a:a.position))
        return next((m for m in g.players[g.current].minions if m.card_id==cid),None)
    def test_pool_is_constructed_post_30_2(self):
        self.assertEqual(len(BONUS_EFFECTS),8);self.assertIn('ELUSIVE',BONUS_EFFECTS);self.assertNotIn('STEALTH',BONUS_EFFECTS)
    def test_new_minion_can_receive_rush(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.assertIn('RUSH',g._bonus_pool(m))
    def test_ready_attacked_and_enemy_minions_cannot_receive_rush(self):
        for case in ('ready','attacked','enemy'):
            with self.subTest(case=case):
                g=self.game();m=g._summon(1 if case=='enemy' else 0,'EDR_851t')
                if case=='ready':m.summoned_turn=g.turn-1
                if case=='attacked':m.attacks=1
                self.assertNotIn('RUSH',g._bonus_pool(m))
    def test_existing_keywords_excluded_and_pool_exhaustion(self):
        g=self.game();m=g._summon(0,'EDR_851t');m.keywords.update(BONUS_EFFECTS-{'TAUNT'})
        self.assertEqual(g._bonus_pool(m),['TAUNT']);g._grant_bonus_effects(m,3)
        self.assertEqual(g._bonus_pool(m),[])
    def test_consumed_shield_can_be_granted_again(self):
        g=self.game();m=g._summon(0,'EDR_851t');m.keywords.add('DIVINE_SHIELD')
        g._damage(m.uid,1);self.assertIn('DIVINE_SHIELD',g._bonus_pool(m))
    def test_galvadon_grants_three_distinct_keywords(self):
        g=self.game();m=g._summon(0,'EDR_851t');self.play(g,'TLC_444',m.uid)
        self.assertEqual(len(m.keywords & BONUS_EFFECTS),3)
    def test_raptor_triggers_only_on_other_play(self):
        g=self.game();raptor=self.play(g,'EDR_849');self.assertFalse(raptor.keywords & BONUS_EFFECTS)
        summoned=g._summon(0,'EDR_851t');self.assertFalse(summoned.keywords & BONUS_EFFECTS)
        other=self.play(g,'CORE_EX1_011');self.assertEqual(len(other.keywords & BONUS_EFFECTS),1)
    def test_silenced_raptor_does_not_grant(self):
        g=self.game();r=self.play(g,'EDR_849');g._silence(r)
        other=self.play(g,'CORE_EX1_011');self.assertFalse(other.keywords & BONUS_EFFECTS)
    def test_punisher_steals_current_not_consumed_keywords(self):
        g=self.game();m=g._summon(1,'EDR_851t');m.keywords.update({'TAUNT','DIVINE_SHIELD','STEALTH'})
        m.keywords.remove('STEALTH');g._damage(m.uid,1)
        punisher=self.play(g,'JAIL_101',m.uid)
        self.assertNotIn('TAUNT',m.keywords);self.assertIn('TAUNT',punisher.keywords)
        self.assertEqual((punisher.attack,punisher.health),(5,4))
    def test_punisher_counts_stolen_even_if_already_present(self):
        g=self.game();m=g._summon(1,'EDR_851t');m.keywords.add('TAUNT');source=g._summon(0,'JAIL_101');source.keywords.add('TAUNT')
        g._effect(('bonus_steal',),dict(owner=0,target=m.uid,source=source));self.assertEqual(source.attack,5)
    def test_tyrannogill_summons_three_distinct_token_records(self):
        g=self.game();m=g._summon(0,'TLC_240');m.health=0;g._settle(allow_event_choices=True)
        self.assertEqual([m.card_id for m in g.players[0].minions],['TLC_240t','TLC_240t2','TLC_240t3'])
        self.assertTrue(all(len(m.keywords & BONUS_EFFECTS)==1 for m in g.players[0].minions))
    def test_tyrannogill_board_limit(self):
        g=self.game();m=g._summon(0,'TLC_240')
        for _ in range(6):g._summon(0,'EDR_851t')
        m.health=0;g._settle(allow_event_choices=True)
        self.assertEqual(len(g.players[0].minions),7)
        self.assertEqual(sum(m.card_id.startswith('TLC_240t') for m in g.players[0].minions),1)
    def test_stranglevine_deathrattle_passes_repeatedly(self):
        g=self.game();v=g._summon(0,'TLC_465');first=g._summon(0,'EDR_851t')
        v.health=0;g._settle(allow_event_choices=True)
        self.assertIn(('bonus_pass_deathrattle',),first.attached_death_effects)
        second=g._summon(0,'EDR_851t');first.health=0;g._settle(allow_event_choices=True)
        self.assertIn(('bonus_pass_deathrattle',),second.attached_death_effects)
    def test_empty_board_stranglevine_noop(self):
        g=self.game();v=g._summon(0,'TLC_465');v.health=0;g._settle(allow_event_choices=True)
        self.assertFalse(g.players[0].minions)
