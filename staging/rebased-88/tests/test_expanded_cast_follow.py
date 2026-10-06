"""Owner-scoped Follow eligibility during automatic and interrupted effects."""
import unittest
from expanded import Game,Action,random_deck

class CastFollowTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10
        return g
    def cast(self,g,cid,owner=0):
        g._start_play_effects([('cast_fixed_spell',cid,'random')],dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False))
    def follow(self,c):return getattr(c,'_follow_effects',[])
    def test_ghosts_attaches_and_runs_after_subsequent_hand_play(self):
        g=self.game();c=g._add(0,'TOKEN_COIN');self.cast(g,'CAP_802')
        self.assertEqual(self.follow(c)[0]['card_id'],'CAP_802')
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(len(g.players[0].minions),2)
    def test_noncurrent_owner_is_used_without_changing_turn(self):
        g=self.game();c=g._add(1,'TOKEN_COIN');other=g._add(0,'TOKEN_COIN');turn=(g.current,g.turn)
        self.cast(g,'CAP_802',1)
        self.assertTrue(self.follow(c));self.assertFalse(self.follow(other));self.assertEqual((g.current,g.turn),turn)
        self.assertEqual(len(g.players[1].minions),1)
    def test_choice_phase_does_not_erase_owner_eligibility(self):
        g=self.game();c=g._add(0,'TOKEN_COIN');g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=1,source=None))
        choice=g.pending_choice
        g._effect(('follow_attach','CAP_802'),dict(owner=0,source=None))
        self.assertTrue(self.follow(c));self.assertIs(g.pending_choice,choice);self.assertEqual(g.phase,'choice')
    def test_owner_cost_and_lock_still_apply(self):
        g=self.game();c=g._add(1,'CORE_CS2_029');g.players[1].mana=0
        self.cast(g,'CAP_802',1);self.assertFalse(self.follow(c))
        g.players[1].mana=10;c.play_lock={'owner':1,'until':g.players[1].turns_taken+1}
        self.cast(g,'CAP_802',1);self.assertFalse(self.follow(c))
    def test_missing_target_still_blocks_attachment(self):
        g=self.game();c=g._add(1,'JAIL_433');g._effect(('follow_attach','CAP_802'),dict(owner=1,source=None))
        self.assertFalse(self.follow(c))
    def test_full_board_blocks_minion_but_not_spell(self):
        g=self.game()
        for _ in range(7):g._summon(1,'AT_037t')
        c=g._add(1,'AT_037t');spell=g._add(1,'TOKEN_COIN');self.cast(g,'CAP_802',1)
        self.assertFalse(self.follow(c));self.assertTrue(self.follow(spell))
    def test_evidence_attaches_and_shuffles_complete_dependency(self):
        g=self.game();c=g._add(0,'TOKEN_COIN');self.cast(g,'CAP_402')
        self.assertEqual(self.follow(c)[0]['card_id'],'CAP_402')
        self.assertEqual(sum(g._card_data(v)['id']=='CAP_400t2t' for v in g.players[1].deck),1)
    def test_hand_helper_does_not_offer_opponent_actions_to_player(self):
        g=self.game();c=g._add(1,'TOKEN_COIN')
        self.assertTrue(any(a.kind=='play' and a.source==c.uid for a in g._hand_actions(1)))
        self.assertFalse(any(a.source==c.uid for a in g.legal_actions()))
    def test_fuse_attaches_only_to_owner_pirate(self):
        g=self.game();pirate=g._add(1,'CORE_NEW1_027');other=g._add(1,'AT_037t')
        self.cast(g,'CAP_101',1)
        self.assertEqual(self.follow(pirate)[0]['card_id'],'CAP_101');self.assertFalse(self.follow(other))
        self.assertEqual(g.players[0].health,28)
