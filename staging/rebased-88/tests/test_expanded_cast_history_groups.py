"""Integration of shared history, recruitment and tribal internal spell effects."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck

class CastHistoryGroupsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def interrupt(self,g,opcode):
        original=g._dispatch_effect;seen=[]
        def effect(op,ctx):
            original(op,ctx)
            if op[0]==opcode:
                seen.append(op)
                if len(seen)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        return patch.object(g,'_dispatch_effect',side_effect=effect),seen
    def test_history_summons_wait_and_keep_original_history_snapshot(self):
        g=self.game();p=g.players[0]
        p.played_history=[dict(cost=1,card_id='AT_037t'),dict(cost=1,card_id='CS2_101t')]
        hook,seen=self.interrupt(g,'summon')
        with hook:
            self.cast(g,'CATA_560');self.assertEqual(len(p.minions),1)
            p.played_history.append(dict(cost=1,card_id='AT_037t'))
            g.step(g.legal_actions()[0]);self.assertEqual(len(seen),2)
        self.assertEqual([m.card_id for m in p.minions],['AT_037t','AT_037t','CS2_101t'])
    def test_history_uses_played_cost_and_ignores_spells(self):
        g=self.game();p=g.players[0]
        p.played_history=[dict(cost=1,card_id='CS3_020'),dict(cost=2,card_id='AT_037t'),dict(cost=1,card_id='CORE_CS2_029')]
        self.cast(g,'CATA_560');self.assertEqual([m.card_id for m in p.minions],['CS3_020'])
    def test_empty_history_does_not_leave_a_frame(self):
        g=self.game();self.cast(g,'CATA_560');self.assertFalse(g.players[0].minions);self.assertIsNone(g.pending_frame)
    def test_resurrection_waits_between_costs_and_grants_reborn(self):
        g=self.game();p=g.players[0];p.death_history=['AT_037t','CORE_EX1_012','CATA_304']
        hook,seen=self.interrupt(g,'resurrect_costs_reborn')
        with hook:
            self.cast(g,'TLC_818');self.assertEqual(len(p.minions),1)
            self.assertIn('REBORN',p.minions[0].keywords)
            g.step(g.legal_actions()[0]);self.assertEqual(len(seen),3)
        actual=[m for m in p.minions if 'REBORN' in m.keywords]
        self.assertEqual([g.cards[m.card_id]['cost'] for m in actual],[1,2,3])
    def test_highest_undead_ignores_more_expensive_other_tribe(self):
        g=self.game();g.players[0].death_history=['CORE_EX1_012','CORE_CATA_002','CS3_020']
        self.cast(g,'TIME_616');self.assertEqual([m.card_id for m in g.players[0].minions],['CORE_CATA_002'])
    def test_shield_recruits_wait_between_summons(self):
        g=self.game();hook,seen=self.interrupt(g,'one_shield_recruit')
        with hook:
            self.cast(g,'MEND_802');self.assertEqual(len(g.players[0].minions),1)
            self.assertIn('DIVINE_SHIELD',g.players[0].minions[0].keywords)
            g.step(g.legal_actions()[0]);self.assertEqual(len(seen),2)
        self.assertEqual(sum('DIVINE_SHIELD' in m.keywords for m in g.players[0].minions),2)
    def test_annihilation_recruits_only_bottom_three_demons(self):
        g=self.game();p=g.players[0];p.deck=['CATA_200','CORE_CS2_029','CORE_BT_351','CS3_020']
        g._summon(0,'AT_037t');g._summon(1,'AT_037t');self.cast(g,'JAIL_510')
        self.assertEqual([m.card_id for m in p.minions],['CATA_200','CORE_BT_351'])
        self.assertEqual([g._card_data(c)['id'] for c in p.deck],['CORE_CS2_029','CS3_020'])
        self.assertFalse(g.players[1].minions)
    def test_tribal_damage_reaches_both_sides_not_unrelated_minions(self):
        g=self.game();a=g._summon(0,'CS3_020');b=g._summon(1,'CS3_020');c=g._summon(1,'CORE_EX1_110')
        before=(a.health,b.health,c.health)
        with patch.object(g.rng,'choice',side_effect=lambda choices: next((x for x in choices if x==a.uid),choices[0])):
            self.cast(g,'TLC_901')
        self.assertEqual((a.health,b.health,c.health),(before[0]-3,before[1]-3,before[2]))
