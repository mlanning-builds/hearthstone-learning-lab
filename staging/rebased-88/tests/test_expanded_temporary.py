"""Temporary expiry, selected deck draws, and resumable Follow chains."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card

class TemporaryTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def put(self,g,cid,owner=0,temporary=False):
        c=g._enter_hand(owner,Card(g._new_id(),cid))
        if temporary:g._make_temporary(c)
        return c
    def play(self,g,c,target=None):
        choices=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(choices,(c.card_id,target));g.step(max(choices,key=lambda a:a.position))
    def attach(self,g,c,cid='CAP_802'):
        c._follow_effects=[dict(card_id=cid,end=g.turn)]
    def follow(self,c):return getattr(c,'_follow_effects',[])
    def test_temporary_discards_only_owner_end(self):
        g=self.game();a=self.put(g,'TOKEN_COIN',temporary=True);b=self.put(g,'TOKEN_COIN',1,True);g.step(Action('end'))
        self.assertNotIn(a,g.players[0].hand);self.assertIn(b,g.players[1].hand);g.step(Action('end'));self.assertNotIn(b,g.players[1].hand)
    def test_opponent_turn_generated_temporary_survives_until_owner_end(self):
        g=self.game();g.step(Action('end'));c=self.put(g,'TOKEN_COIN',temporary=True);g.step(Action('end'));self.assertIn(c,g.players[0].hand)
        g.step(Action('end'));self.assertNotIn(c,g.players[0].hand)
    def test_ordinary_cards_survive_cleanup(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');g.step(Action('end'));self.assertIn(c,g.players[0].hand)
    def test_played_temporary_is_not_discarded(self):
        g=self.game();c=self.put(g,'EDR_851t',temporary=True);self.play(g,c);g.step(Action('end'))
        self.assertNotIn(c.card_id,g.players[0].discard_history);self.assertTrue(g.players[0].minions)
    def test_expiry_publishes_discard_listener(self):
        g=self.game();self.put(g,'TOKEN_COIN',temporary=True)
        with patch.object(g,'_event_frame',wraps=g._event_frame) as frames:
            g.step(Action('end'));self.assertTrue(any(c.args[0][0]=='discard' for c in frames.call_args_list))
    def test_expiry_discards_whole_batch(self):
        g=self.game();self.put(g,'TOKEN_COIN',temporary=True);self.put(g,'EDR_851t',temporary=True);g.step(Action('end'))
        self.assertEqual(g.players[0].discard_history,['TOKEN_COIN','EDR_851t'])
    def test_copied_card_retains_temporary(self):
        g=self.game();c=self.put(g,'TOKEN_COIN',temporary=True);clone=g._clone_hand_card(0,c);self.assertTrue(g._is_temporary(clone));g.step(Action('end'))
        self.assertEqual(g.players[0].discard_history.count('TOKEN_COIN'),2)
    def test_shuffle_resets_temporary_enchantment(self):
        g=self.game();c=self.put(g,'TOKEN_COIN',temporary=True);clean=g._shuffle_hand_card(0,c);self.assertFalse(g._is_temporary(clean))
    def test_return_from_board_resets_temporary(self):
        g=self.game();c=self.put(g,'EDR_851t',temporary=True);self.play(g,c);g._bounce(g.players[0].minions[-1]);self.assertFalse(g._is_temporary(g.players[0].hand[-1]))
    def test_spelunker_only_discounts_temporary(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));a=self.put(g,'CORE_CS2_029');b=self.put(g,'CORE_CS2_029',temporary=True)
        self.assertEqual((g._cost(a,0),g._cost(b,0)),(4,2))
    def test_spelunker_survives_ordinary_play(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));self.play(g,self.put(g,'EDR_851t'));c=self.put(g,'CORE_CS2_029',temporary=True);self.assertEqual(g._cost(c,0),2)
    def test_spelunker_consumed_by_first_temporary_play(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));a=self.put(g,'CORE_CS2_029',temporary=True);b=self.put(g,'CORE_CS2_029',temporary=True);self.play(g,a,g.hero_id(1));self.assertEqual(g._cost(b,0),4)
    def test_spelunker_stacks_and_floors_cost(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));self.play(g,self.put(g,'TLC_450'));c=self.put(g,'CORE_CS2_029',temporary=True);self.assertEqual(g._cost(c,0),0)
    def test_discount_not_consumed_by_discard(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));c=self.put(g,'TOKEN_COIN',temporary=True);g._discard_card(0,c);next_card=self.put(g,'CORE_CS2_029',temporary=True);self.assertEqual(g._cost(next_card,0),2)
    def test_catacombs_excludes_all_copies_of_itself(self):
        g=self.game();g.players[0].deck=['TLC_451','TLC_451','EDR_851t'];self.play(g,self.put(g,'TLC_451'))
        self.assertEqual([o['card_id'] for o in g.pending_choice['options']],['EDR_851t'])
    def test_catacombs_no_eligible_card_no_fatigue(self):
        g=self.game();g.players[0].deck=['TLC_451'];self.play(g,self.put(g,'TLC_451'));self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].fatigue,0)
    def test_catacombs_moves_actual_card_without_draw_event(self):
        g=self.game();c=Card(g._new_id(),'CORE_CS2_029');c.attack_bonus=2;g.players[0].deck=[c];self.play(g,self.put(g,'TLC_451'))
        with patch.object(g,'_queue_event',wraps=g._queue_event) as events:
            g.step(Action('choose',choices=(0,)));draws=[e.kwargs['card'] for e in events.call_args_list if e.args[0]=='card_drawn'];self.assertEqual(draws,[]);self.assertTrue(g._is_temporary(c))
        self.assertIs(g.players[0].hand[-1],c);self.assertFalse(g.players[0].deck)
    def test_catacombs_offers_distinct_identities(self):
        g=self.game();g.players[0].deck=['EDR_851t']*5+['CORE_CS2_029']*5;self.play(g,self.put(g,'TLC_451'));self.assertEqual(len(g.pending_choice['options']),2)
    def test_catacombs_choice_is_private(self):
        g=self.game();self.play(g,self.put(g,'TLC_451'));self.assertIn('options',g.observe(0)['pending_choice']);self.assertNotIn('options',g.observe(1)['pending_choice'])
    def test_ghosts_summon_reborn_and_attach_to_coin(self):
        g=self.game();coin=self.put(g,'TOKEN_COIN');self.play(g,self.put(g,'CAP_802'));m=g.players[0].minions[-1]
        self.assertEqual((m.attack,m.health),(2,1));self.assertIn('REBORN',m.keywords);self.assertEqual(self.follow(coin)[0]['card_id'],'CAP_802')
    def test_ghosts_chain_through_spell_once_and_transfer(self):
        g=self.game();coin=self.put(g,'TOKEN_COIN');self.attach(g,coin);self.play(g,coin);self.assertEqual(len(g.players[0].minions),1)
        self.assertIsNone(g._pending_follow)
    def test_ghosts_chain_through_minion_once(self):
        g=self.game();c=self.put(g,'EDR_851t');self.attach(g,c);self.play(g,c);self.assertEqual([m.card_id for m in g.players[0].minions],['EDR_851t','CAP_802t'])
    def test_ghosts_chain_after_battlecry_choice(self):
        g=self.game();c=self.put(g,'TLC_246');self.attach(g,c);self.play(g,c);self.assertEqual(g.phase,'choice');self.assertEqual(len(g.players[0].minions),1)
        g.step(Action('choose',choices=(0,)));self.assertEqual(len(g.players[0].minions),2);self.assertIsNone(g._pending_follow)
    def test_ghosts_chain_after_spell_choice(self):
        g=self.game();g.players[0].deck=['TOKEN_COIN'];c=self.put(g,'TLC_451');self.attach(g,c);self.play(g,c);g.step(Action('choose',choices=(0,)))
        self.assertEqual(len(g.players[0].minions),1);self.assertEqual(self.follow(g.players[0].hand[-1])[0]['card_id'],'CAP_802')
    def test_ghosts_chain_through_weapon(self):
        g=self.game();c=self.put(g,'JAIL_380');self.attach(g,c);self.play(g,c);self.assertEqual(len(g.players[0].minions),1)
    def test_ghosts_chain_through_location(self):
        g=self.game();c=self.put(g,'CORE_REV_990');self.attach(g,c);self.play(g,c);self.assertEqual(len(g.players[0].minions),1);self.assertEqual(len(g.players[0].locations),1)
    def test_countered_attached_spell_still_publishes_attachment(self):
        g=self.game();g._effect(('secret','CORE_EX1_287'),dict(owner=1));c=self.put(g,'TOKEN_COIN');self.attach(g,c);self.play(g,c);self.assertEqual(len(g.players[0].minions),1)
    def test_follow_attachment_expires_without_discard(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');self.attach(g,c);g.step(Action('end'));self.assertIn(c,g.players[0].hand);self.assertFalse(self.follow(c));self.assertFalse(g.players[0].discard_history)
    def test_follow_ignores_unaffordable_cards(self):
        g=self.game();c=self.put(g,'CORE_CS2_029');g.players[0].mana=2;self.play(g,self.put(g,'CAP_802'));self.assertFalse(self.follow(c))
    def test_follow_ignores_spell_without_valid_target(self):
        g=self.game();c=self.put(g,'JAIL_433');g._effect(('follow_attach','CAP_802'),dict(owner=0));self.assertFalse(self.follow(c))
    def test_follow_respects_full_board(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        c=self.put(g,'EDR_851t');g._effect(('follow_attach','CAP_802'),dict(owner=0));self.assertFalse(self.follow(c))
    def test_fuse_requires_pirate(self):
        g=self.game();pirate=self.put(g,'CORE_NEW1_027');other=self.put(g,'EDR_851t');self.play(g,self.put(g,'CAP_101'))
        self.assertEqual(self.follow(pirate)[0]['card_id'],'CAP_101');self.assertFalse(self.follow(other));self.assertEqual(g.players[1].health,28)
    def test_fuse_attached_minion_damage_no_spell_damage(self):
        g=self.game();g._summon(0,'CORE_EX1_012');c=self.put(g,'CORE_NEW1_027');self.attach(g,c,'CAP_101');self.play(g,c);self.assertEqual(g.players[1].health,28)
    def test_original_fuse_spell_damage_applies(self):
        g=self.game();g._summon(0,'CORE_EX1_012');self.play(g,self.put(g,'CAP_101'));self.assertEqual(g.players[1].health,27)
    def test_multiple_attachments_resolve_independently(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');self.attach(g,c);c._follow_effects*=2;self.play(g,c);self.assertEqual(len(g.players[0].minions),2)
    def test_copies_preserve_attachment_without_aliasing(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');self.attach(g,c);clone=g._clone_hand_card(0,c);clone._follow_effects.clear();self.assertTrue(self.follow(c))
    def test_follow_visible_only_to_owner(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');self.attach(g,c);self.assertEqual(len(g.observe(0)['players'][0]['hand'][0]['follow_effects']),1);self.assertNotIn('hand',g.observe(1)['players'][0])
    def test_follow_failure_rolls_back_everything(self):
        g=self.game();c=self.put(g,'TOKEN_COIN');self.attach(g,c);rng=g.rng.getstate()
        with patch.object(g,'_temporary_effect',side_effect=RuntimeError('test rollback')):
            with self.assertRaises(RuntimeError):self.play(g,c)
        self.assertEqual(g.players[0].hand[0].uid,c.uid);self.assertFalse(g.players[0].board);self.assertEqual(g.rng.getstate(),rng)
    def test_spelunker_consumed_even_when_temporary_spell_countered(self):
        g=self.game();self.play(g,self.put(g,'TLC_450'));g._effect(('secret','CORE_EX1_287'),dict(owner=1));self.play(g,self.put(g,'TOKEN_COIN',temporary=True))
        self.assertFalse(g.players[0].cost_effects)
    def test_end_turn_generated_temporary_is_cleaned_up(self):
        g=self.game();card=Card(g._new_id(),'TOKEN_COIN');g._make_temporary(card);g.players[0].deck=[card];g._summon(0,'CORE_ULD_133');g.step(Action('end'))
        self.assertNotIn(card,g.players[0].hand);self.assertIn('TOKEN_COIN',g.players[0].discard_history)
    def test_temporary_expiry_follows_new_controller(self):
        g=self.game();c=self.put(g,'TOKEN_COIN',temporary=True);g.players[0].hand.remove(c);g._enter_hand(1,c);g.step(Action('end'))
        self.assertIn(c,g.players[1].hand);g.step(Action('end'));self.assertNotIn(c,g.players[1].hand)
    def test_catacombs_full_hand_burns_selected_draw(self):
        g=self.game();g.players[0].deck=['EDR_851t'];self.play(g,self.put(g,'TLC_451'))
        for _ in range(10):self.put(g,'TOKEN_COIN')
        g.step(Action('choose',choices=(0,)));self.assertFalse(g.players[0].deck);self.assertEqual(len(g.players[0].hand),10)
        self.assertFalse(any(g._is_temporary(c) for c in g.players[0].hand))
    def test_full_board_ghost_still_passes_to_playable_spell(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        c=self.put(g,'TOKEN_COIN');self.play(g,self.put(g,'CAP_802'));self.assertEqual(len(g.players[0].board),7);self.assertTrue(self.follow(c))
    def test_no_pirate_still_deals_original_fuse_damage(self):
        g=self.game();self.play(g,self.put(g,'CAP_101'));self.assertEqual(g.players[1].health,28)
    def test_follow_does_not_activate_on_summon_without_play(self):
        g=self.game();c=self.put(g,'EDR_851t');self.attach(g,c);g.players[0].hand.remove(c);g._summon(0,c.card_id,entry_origin='recruit',entry_zone='hand',entry_source=c);g._settle()
        self.assertEqual(len(g.players[0].minions),1)
    def test_two_step_ghost_chain_selects_new_recipient(self):
        g=self.game();first=self.put(g,'TOKEN_COIN');self.attach(g,first);second=self.put(g,'EDR_851t');self.play(g,first);self.assertTrue(self.follow(second));self.play(g,second)
        self.assertEqual(sum(m.card_id=='CAP_802t' for m in g.players[0].minions),2)
