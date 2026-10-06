"""Owner-history Kindred snapshots and interruptible conditional effects."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck

class CastKindredTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
            p.previous_schools=set();p.played_schools=set()
        return g
    def cast(self,g,cid,owner=0):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False))
    def test_cryosleep_uses_matching_previous_school(self):
        for school,count in [('FROST',2),('FIRE',1)]:
            with self.subTest(school=school):
                g=self.game();g.players[0].previous_schools={school};self.cast(g,'TLC_440')
                self.assertEqual(len(g.players[0].hand),count)
    def test_current_turn_school_does_not_activate_kindred(self):
        g=self.game();g.players[0].played_schools={'FROST'};self.cast(g,'TLC_440')
        self.assertEqual(len(g.players[0].hand),1)
    def test_offturn_cast_uses_owners_just_finished_turn(self):
        g=self.game();g.players[1].played_schools={'FROST'};self.cast(g,'TLC_440',1)
        self.assertEqual(len(g.players[1].hand),2);self.assertEqual(g.current,0)
    def test_offturn_cast_does_not_use_owners_older_turn(self):
        g=self.game();g.players[1].previous_schools={'FROST'};self.cast(g,'TLC_440',1)
        self.assertEqual(len(g.players[1].hand),1)
    def test_opponent_history_does_not_activate_kindred(self):
        g=self.game();g.players[1].previous_schools={'FROST'};self.cast(g,'TLC_440')
        self.assertEqual(len(g.players[0].hand),1)
    def test_cast_does_not_publish_played_school(self):
        g=self.game();self.cast(g,'TLC_440');self.assertFalse(g.players[0].played_schools)
        self.assertFalse(g.players[0].played_history)
    def test_ambush_summons_conditional_second_spitter(self):
        for active in (False,True):
            with self.subTest(active=active):
                g=self.game();g.players[0].previous_schools={'SHADOW'} if active else set()
                self.cast(g,'TLC_519');self.assertEqual(len(g.players[0].minions),2 if active else 1)
    def test_caustic_fumes_hits_deathrattle_summon_after_destroy(self):
        g=self.game();g.players[0].previous_schools={'FEL'};g._summon(1,'DINO_130')
        self.cast(g,'TLC_447');m=g.players[1].minions[0]
        self.assertEqual((m.card_id,m.health),('DINO_130t',2))
    def test_hybridization_waits_between_costs_with_snapshot_bonus(self):
        g=self.game();p=g.players[0];p.previous_schools={'NATURE'}
        p.deck=['TLC_249','DINO_130','TLC_233','EDR_492','CORE_CS2_029']
        dispatch=g._dispatch_effect;seen=[]
        def effect(op,ctx):
            dispatch(op,ctx)
            if op[0]=='kindred_cost_draw_one':
                seen.append(op)
                if len(seen)==1:g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
        with patch.object(g,'_dispatch_effect',side_effect=effect):
            self.cast(g,'TLC_236');self.assertEqual(len(p.hand),1);p.previous_schools.clear()
            g.step(g.legal_actions()[0])
        self.assertEqual([op[1] for op in seen],[1,2,3,4])
        self.assertEqual(sorted(g._cost(c,0) for c in p.hand),[0,1,2,3])
    def test_inactive_hybridization_still_draws_without_discount(self):
        g=self.game();p=g.players[0];p.deck=['TLC_249','DINO_130','TLC_233','EDR_492']
        self.cast(g,'TLC_236');self.assertEqual(sorted(g._cost(c,0) for c in p.hand),[1,2,3,4])
    def test_unknown_kindred_child_rejected(self):
        g=self.game();self.assertFalse(g._supports_internal_operations([('kindred',[('unknown_effect',)])]))
