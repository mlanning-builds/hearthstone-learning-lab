"""Dormant isolation, awakening schedules, and connected card scenarios."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.features import encode_decision, SCHEMA

class DormantTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play(self,g,cid,target=None,choice=None):
        c=self.put(g,cid,g.current);g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target) and (choice is None or a.choices==(choice,))]
        self.assertTrue(actions,(cid,target,choice));g.step(max(actions,key=lambda a:a.position))
        return next((m for m in reversed(g.players[g.current].all_minions) if m.card_id==cid),None)
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def test_dormant_occupies_slot_and_is_not_active_minion(self):
        g=self.game();m=self.play(g,'CORE_BT_156')
        self.assertIn(m,g.players[0].board);self.assertNotIn(m,g.players[0].minions);self.assertEqual(m.dormant,2)
    def test_dormant_full_board_blocks_minion_plays(self):
        g=self.game()
        for _ in range(7):g._summon(0,'CORE_BT_156')
        c=self.put(g,'EDR_851t');self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_no_dormant_target_or_attack_actions(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');e=g._summon(1,'TIME_046');self.put(g,'CORE_CS2_029');self.put(g,'TLC_444')
        self.assertFalse(any(a.target in (m.uid,e.uid) or a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
    def test_two_owner_turns_not_two_half_turns(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g.step(Action('end'));self.assertEqual(m.dormant,2)
        g.step(Action('end'));self.assertEqual(m.dormant,1);self.cycle(g);self.assertFalse(m.dormant)
    def test_rush_on_awakening_cannot_attack_hero(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');e=g._summon(1,'CS2_033');self.cycle(g);self.cycle(g)
        actions=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid]
        self.assertEqual([a.target for a in actions],[e.uid])
    def test_no_rush_wakes_exhausted(self):
        g=self.game();m=g._summon(0,'EDR_416t');self.cycle(g);self.cycle(g)
        self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
        self.cycle(g);self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
    def test_dormant_immune_to_area_damage_and_destroy(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g._summon(1,'EDR_851t')
        g._effect(('area_damage','all_minions',100),dict(owner=0,source=None,bonus=0));g._settle()
        self.assertEqual(m.health,5);self.assertFalse(g.players[1].minions)
        self.assertEqual(g._damage(m.uid,10),0)
    def test_direct_generic_buff_heal_silence_bounce_transform_noop(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g._buff(m,5,5);g._heal(m.uid,5);g._silence(m);g._bounce(m);g._transform(m,'EDR_851t');g._freeze(m.uid)
        self.assertEqual((m.attack,m.health,m.dormant),(3,5,2));self.assertIn(m,g.players[0].board);self.assertFalse(m.silenced)
    def test_aura_source_suppressed_and_restored(self):
        g=self.game();a=g._summon(0,'CORE_CS2_122');m=g._summon(0,'EDR_851t');self.assertEqual(m.attack,2)
        g._sleep_minion(a,1);self.assertEqual(m.attack,1);g._awaken(a);self.assertEqual(m.attack,2)
    def test_aura_recipient_suppressed(self):
        g=self.game();g._summon(0,'CORE_CS2_122');m=g._summon(0,'CORE_BT_156');self.assertEqual(m.attack,3)
        g._awaken(m);self.assertEqual(m.attack,4)
    def test_buff_damage_preserved_across_imprisonment(self):
        g=self.game();m=g._summon(0,'CS2_033');g._buff(m,2,3);g._damage(m.uid,2)
        stats=(m.attack,m.health,m.max_health);g._sleep_minion(m,2);self.cycle(g);self.cycle(g)
        self.assertEqual((m.attack,m.health,m.max_health),stats)
    def test_sprite_own_power_only(self):
        g=self.game();m=g._summon(0,'EDR_469');g._queue_event('hero_power_used',owner=1);g._settle();self.assertTrue(m.dormant)
        g.step(next(a for a in g.legal_actions() if a.kind=='power'));self.assertFalse(m.dormant)
    def test_yore_armor_draw_only_while_dormant(self):
        g=self.game();m=g._summon(0,'EDR_979');g.step(Action('end'));self.assertEqual(g.players[0].armor,3);self.assertEqual(len(g.players[0].hand),1)
        g.step(Action('end'));g.step(Action('end'));self.assertEqual(g.players[0].armor,6)
        g.step(Action('end'));self.assertFalse(m.dormant);g.step(Action('end'));self.assertEqual(g.players[0].armor,6)
    def test_maiev_buffs_and_sleeps_other_played_minion(self):
        g=self.game();a=self.play(g,'JAIL_850');self.assertFalse(a.dormant)
        m=self.play(g,'EDR_851t');self.assertEqual((m.attack,m.health,m.dormant),(4,4,1));self.cycle(g);self.assertFalse(m.dormant)
    def test_maiev_does_not_buff_already_dormant_or_summoned(self):
        g=self.game();self.play(g,'JAIL_850');m=self.play(g,'CORE_BT_156');self.assertEqual((m.attack,m.dormant),(3,2))
        n=g._summon(0,'EDR_851t');g._settle();self.assertEqual((n.attack,n.dormant),(1,0))
    def test_confinement_friendly_demon_buffs_instead(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g._awaken(m);self.play(g,'JAIL_997',m.uid)
        self.assertFalse(m.dormant);self.assertEqual((m.attack,m.health),(6,8))
    def test_confinement_enemy_or_non_demon_sleeps(self):
        for owner in (0,1):
            g=self.game();m=g._summon(owner,'EDR_851t');self.play(g,'JAIL_997',m.uid);self.assertEqual(m.dormant,2)
    def test_ash_worm_full_board_including_locations(self):
        g=self.game();m=g._summon(0,'MEND_040')
        for _ in range(5):g._summon(0,'EDR_851t')
        g._settle();self.assertTrue(m.dormant)
        g._place_location(0,'CORE_REV_990');g._settle();self.assertFalse(m.dormant)
    def test_serpent_discount_checks_either_board(self):
        g=self.game();c=self.put(g,'TIME_022');self.assertEqual(g._cost(c,0),8)
        m=g._summon(1,'TIME_046');self.assertEqual(g._cost(c,0),4);g._awaken(m);self.assertEqual(g._cost(c,0),8)
    def test_patriarch_taunt_inactive_until_third_turn(self):
        g=self.game();m=g._summon(0,'TIME_046');self.assertNotIn('TAUNT',g._effective_keywords(m))
        self.cycle(g);self.cycle(g);self.assertEqual(m.dormant,1);self.cycle(g);self.assertIn('TAUNT',g._effective_keywords(m))
    def test_nozdormu_counts_pinned_newest_minion_and_spell(self):
        g=self.game();m=g._summon(0,'TIME_063');self.play(g,'EDR_851t');self.assertEqual(m.dormant,5)
        self.play(g,'JAIL_101');self.assertEqual(m.dormant,4);self.play(g,'JAIL_307');self.assertEqual(m.dormant,3)
    def test_nozdormu_counts_weapon(self):
        g=self.game();m=g._summon(0,'TIME_063');self.play(g,'JAIL_329');self.assertEqual(m.dormant,4)
    def test_warden_death_releases_exact_entity(self):
        g=self.game();m=g._summon(1,'CS2_033');warden=self.play(g,'TIME_442',m.uid)
        self.assertEqual(m.dormant,10000);warden.health=0;g._settle(allow_event_choices=True);self.assertFalse(m.dormant)
    def test_silenced_warden_does_not_release(self):
        g=self.game();m=g._summon(1,'CS2_033');warden=self.play(g,'TIME_442',m.uid)
        g._silence(warden);warden.health=0;g._settle();self.assertEqual(m.dormant,10000)
    def test_ogre_grows_or_wakes(self):
        g=self.game();m=g._summon(0,'TLC_253')
        with patch.object(g.rng,'randrange',return_value=1):self.cycle(g)
        self.assertEqual((m.attack,m.health,m.dormant),(7,7,-1))
        with patch.object(g.rng,'randrange',return_value=0):self.cycle(g)
        self.assertEqual((m.attack,m.health,m.dormant),(7,7,0))
    def test_grim_harvest_fixed_seed_and_draw(self):
        g=self.game();self.play(g,'EDR_840');self.assertEqual(len(g.players[0].hand),1)
        m=g.players[0].all_minions[0];self.assertIn(m.card_id,('EDR_840t','EDR_840t1','EDR_840t2'));self.assertTrue(m.dormant)
    def test_wyvern_both_choices(self):
        g=self.game();self.play(g,'EDR_820',choice=0);self.assertEqual(len(g.players[0].all_minions),2)
        e=g._summon(1,'CS2_033');self.play(g,'EDR_820',choice=1);self.assertEqual(e.health,4);self.assertEqual(len(g.players[0].all_minions),2)
    def test_corrupter_battlecry_and_deathrattle(self):
        g=self.game();m=self.play(g,'EDR_841');self.assertEqual(len(g.players[0].all_minions),2)
        m.health=0;g._settle(allow_event_choices=True);self.assertEqual(len(g.players[0].all_minions),2);self.assertTrue(all(m.dormant for m in g.players[0].all_minions))
    def test_hound_awakening_attack_only_current_turn(self):
        g=self.game();m=g._summon(0,'EDR_840t');self.cycle(g);self.cycle(g);self.assertEqual(g._hero_attack(0),3)
        g.step(Action('end'));self.assertEqual(g._hero_attack(0),0)
    def test_shepherd_weapon_summons_dormant_sheep(self):
        g=self.game();self.play(g,'EDR_416');g.step(next(a for a in g.legal_actions() if a.kind=='attack'))
        m=g.players[0].all_minions[0];self.assertEqual((m.card_id,m.dormant),('EDR_416t',2))
    def test_dormant_does_not_emit_ordinary_triggers(self):
        g=self.game();r=g._summon(0,'EDR_849');g._sleep_minion(r,2);m=self.play(g,'EDR_851t');self.assertEqual(m.keywords,set(g.cards[m.card_id].get('mechanics',[])))
    def test_public_dormant_state_and_version(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');view=g.observe(1)
        entity=view['players'][0]['board'][0];self.assertEqual((entity['type'],entity['dormant']),('DORMANT',2));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_silenced_minion_still_completes_external_dormancy(self):
        g=self.game();m=g._summon(0,'CS2_033');g._silence(m);g._sleep_minion(m,1);self.cycle(g)
        self.assertFalse(m.dormant);self.assertTrue(m.silenced)
    def test_temporary_attack_expires_while_dormant(self):
        g=self.game();m=g._summon(0,'CS2_033');g._effect(('temporary_attack_buff',2),dict(owner=0,source=None,target=m.uid));g._sleep_minion(m,2)
        g.step(Action('end'));self.assertEqual(m.attack,3)
    def test_ogre_imprisonment_retains_while_dormant_trigger(self):
        g=self.game();m=g._summon(0,'TLC_253');g._awaken(m);g._sleep_minion(m,10000)
        with patch.object(g.rng,'randrange',return_value=0):self.cycle(g)
        self.assertFalse(m.dormant)
    def test_hound_awaken_trigger_repeats_after_second_sleep(self):
        g=self.game();m=g._summon(0,'EDR_840t');g._awaken(m);g._sleep_minion(m,1);self.cycle(g)
        self.assertEqual(g._hero_attack(0),3)
    def test_dormant_space_prevents_summon_and_does_not_die(self):
        g=self.game()
        for _ in range(7):g._summon(0,'TIME_046')
        self.assertIsNone(g._summon(0,'EDR_851t'));g._settle();self.assertEqual(g.players[0].corpses,0)
    def test_dreadseed_pool_at_full_board_does_not_overfill(self):
        g=self.game()
        for _ in range(6):g._summon(0,'TIME_046')
        self.play(g,'EDR_820',choice=0);self.assertEqual(len(g.players[0].board),7)
    def test_granted_reborn_not_applied_to_dormant_resurrection(self):
        g=self.game();g.players[0].death_history=['CORE_BT_156']
        g._effect(('resurrect_costs_reborn',[2]),dict(owner=0,source=None))
        self.assertNotIn('REBORN',g.players[0].all_minions[0].keywords)
    def test_invalid_target_rolls_back_state(self):
        g=self.game();m=g._summon(1,'TIME_046');c=self.put(g,'JAIL_997');before=g.observe(0)
        with self.assertRaises(Exception):g.step(Action('play',c.uid,m.uid))
        self.assertEqual(g.observe(0),before)
    def test_opponent_hound_attack_expires_at_current_turn_end(self):
        g=self.game();m=g._summon(1,'EDR_840t');g._awaken(m)
        self.assertEqual(g._hero_attack(1),3);g.step(Action('end'));self.assertEqual(g._hero_attack(1),0)
    def test_imprisoned_link_features_ignore_arbitrary_entity_numbers(self):
        from copy import deepcopy
        g=self.game();m=g._summon(1,'CS2_033');self.play(g,'TIME_442',m.uid)
        view=g.observe(0);decision=dict(actor=0,observation=view,actions=view['legal_actions']);before=encode_decision(decision)
        changed=deepcopy(decision)
        for p in changed['observation']['players']:
            for entity in p.get('board',[])+p.get('hand',[]):
                entity['uid']+=500
                if 'imprisoned_entity' in entity.get('rule_state',{}):entity['rule_state']['imprisoned_entity']+=500
        for action in changed['actions']:
            for key in ('source','target'):
                if action.get(key,0)>0:action[key]+=500
        self.assertEqual(encode_decision(changed),before)
    def test_copy_of_awakened_minion_remains_active(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g._awaken(m);g._buff(m,2,2)
        copy=g._summon(0,m.card_id,copy_from=m,entry_origin='copy');self.assertFalse(copy.dormant);self.assertEqual(copy.attack,5)
    def test_fresh_resurrection_restarts_dormancy(self):
        g=self.game();m=g._summon(0,'CORE_BT_156');g._awaken(m);m.health=0;g._settle()
        new=g._summon(0,m.card_id,entry_origin='resurrection');self.assertEqual(new.dormant,2)
