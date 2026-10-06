"""Persistent spell effects and closed generated dependencies in internal casts."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.dreams import DREAMS,CORRUPTED
from expanded.bonus_effects import BONUS_EFFECTS

class CastPersistentStatesTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid,policy='random',card=None):
        op=('cast_physical_spell',card,policy) if card else ('cast_fixed_spell',cid,policy)
        g._start_play_effects([op],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def test_star_replacement_then_upgrade(self):
        g=self.game();self.cast(g,'JAIL_EVENT_101');p=g.players[0];uid=p.primary_power['uid']
        self.assertEqual(p.primary_power['damage'],2);self.cast(g,'JAIL_EVENT_101')
        self.assertEqual(p.primary_power['damage'],3);self.assertEqual(p.primary_power['uid'],uid)
    def test_temporary_power_retains_previous_replacement(self):
        g=self.game();self.cast(g,'JAIL_EVENT_101');self.cast(g,'TLC_632')
        power=g.players[0].primary_power;self.assertEqual(power['card_id'],'TLC_632t')
        self.assertEqual(power['remaining'],2);self.assertEqual(power['restore']['card_id'],'JAIL_EVENT_101hp')
    def test_refresh_resets_both_power_usage_flags(self):
        g=self.game();p=g.players[0];p.power_used=True;p.secondary_power={'card_id':'JAIL_446hp','used':True}
        g._summon(1,'CS3_020');self.cast(g,'JAIL_441')
        self.assertFalse(p.power_used);self.assertFalse(p.secondary_power['used'])
    def test_friendly_demon_buff_does_not_sleep(self):
        g=self.game();m=g._summon(0,'CS3_020');before=(m.attack,m.health);self.cast(g,'JAIL_997')
        self.assertEqual((m.attack,m.health),(before[0]+3,before[1]+3));self.assertFalse(m.dormant)
    def test_enemy_demon_sleeps_instead_of_buff(self):
        g=self.game();m=g._summon(1,'CS3_020');attack=m.attack;self.cast(g,'JAIL_997')
        self.assertEqual(m.dormant,2);self.assertEqual(m.attack,attack)
    def test_judgment_sets_both_boards_from_friendly_target(self):
        g=self.game();a=g._summon(0,'AT_037t');b=g._summon(1,'CS3_020');self.cast(g,'JAIL_326')
        self.assertEqual((a.attack,a.health,b.attack,b.health),(1,1,1,1))
    def test_bonus_effects_are_distinct_and_from_complete_pool(self):
        g=self.game();m=g._summon(0,'AT_037t');self.cast(g,'TLC_444')
        self.assertEqual(len(m.keywords & BONUS_EFFECTS),3)
    def test_dead_dragon_choice_is_automatic_and_owner_scoped(self):
        g=self.game();g.players[0].death_history=['CATA_551t'];g.players[1].death_history=['CATA_553t']
        self.cast(g,'EDR_455');self.assertIsNone(g.pending_choice)
        self.assertEqual([m.card_id for m in g.players[0].minions],['CATA_551t'])
    def test_gladiatorial_summons_for_both_controllers(self):
        g=self.game();g.players[0].deck=['CAP_107'];self.cast(g,'TIME_870')
        self.assertEqual(g.players[0].minions[0].card_id,'CAP_107')
        self.assertEqual(g.players[1].minions[0].card_id,'TIME_870t');self.assertFalse(g.players[0].hand)
    def test_opponent_summons_pause_between_entries(self):
        g=self.game();dispatch=g._dispatch_effect;seen=[]
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]=='summon_opponent':
                seen.append(op)
                if len(seen)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        with patch.object(g,'_dispatch_effect',side_effect=effect):
            self.cast(g,'TIME_873');self.assertEqual(len(g.players[1].minions),1)
            g.step(g.legal_actions()[0])
        self.assertEqual(len(g.players[1].minions),2);self.assertEqual(g.players[0].armor,10)
    def test_dream_rewards_keep_corrupted_physical_state(self):
        for corrupted in (False,True):
            with self.subTest(corrupted=corrupted):
                g=self.game();c=Card(g._new_id(),'EDR_846');c.rule_state={'dream_corrupted':corrupted}
                self.cast(g,c.card_id,card=c)
                self.assertEqual(set(c.card_id for c in g.players[0].hand),set(CORRUPTED if corrupted else DREAMS))
    def test_all_generated_dream_spells_admitted(self):
        g=self.game()
        for cid in DREAMS+CORRUPTED:
            if g.cards[cid]['type']=='SPELL':self.assertTrue(g._supports_internal_spell(cid),cid)
    def test_replayed_dead_minion_effect_uses_own_history(self):
        g=self.game();m=g._summon(0,'CORE_EX1_110');m.health=0;g._settle();g.players[0].board=[]
        self.cast(g,'JAIL_940');self.assertEqual([m.card_id for m in g.players[0].minions],['TOKEN_BAINE'])
    def test_attached_recruit_runs_when_enchanted_minion_dies(self):
        g=self.game();m=g._summon(0,'AT_037t');held=g._add(0,'CS3_020');self.cast(g,'CATA_610')
        m.health=0;g._settle();self.assertNotIn(held,g.players[0].hand)
        self.assertEqual([m.card_id for m in g.players[0].minions],['CS3_020'])
    def test_unknown_attached_effect_not_admitted(self):
        g=self.game();self.assertFalse(g._supports_internal_operations([('b60_attach',('unknown_effect',))]))
