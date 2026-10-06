"""60-card release: observable outcomes and cross-system regression checks."""
import json
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.batch60_cards import RULES,MOON_TRANSFORMS,DRAGON_TRANSFORMS

class Batch60Tests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play_card(self,g,c,target=None,choice=None):
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target) and (choice is None or a.choices==(choice,))]
        self.assertTrue(actions,(c.card_id,target,choice));first=actions[0];g.step(max((a for a in actions if a.target==first.target and a.choices==first.choices),key=lambda a:a.position));return c
    def play(self,g,cid,target=None,choice=None):return self.play_card(g,self.put(g,cid,g.current),target,choice)
    def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def attack(self,g,m,target):
        m.summoned_turn=g.turn-1
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==target))
    def test_sixty_collectibles(self):self.assertEqual(len(RULES),60)
    def test_striker_transforms_on_dragon_only(self):
        g=self.game();c=self.put(g,'CATA_551');self.play(g,'EDR_851t');self.assertEqual(c.card_id,'CATA_551')
        self.play(g,'CATA_551t');self.assertEqual(c.card_id,'CATA_551t');self.play_card(g,c)
        m=g.players[0].minions[-1];self.assertEqual((m.attack,m.health),(6,6));self.assertIn('TAUNT',m.keywords)
    def test_scout_uses_transformed_attack(self):
        g=self.game();c=self.put(g,'CATA_552');self.play(g,'CATA_551t');self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[1].health,22)
    def test_ebyssian_persistent_rush(self):
        g=self.game();c=self.put(g,'CATA_553');self.play(g,'CATA_551t');self.play_card(g,c)
        self.assertEqual(g.players[0].minions[-1].attack,12)
        dragon=g._summon(0,'CATA_551t');self.assertIn('RUSH',g._effective_keywords(dragon));g._silence(dragon);self.assertIn('RUSH',g._effective_keywords(dragon))
        self.assertNotIn('RUSH',g._effective_keywords(g._summon(1,'CATA_551t')))
    def test_overseer_nature_held_positive_and_negative(self):
        for active in (False,True):
            g=self.game();c=self.put(g,'TIME_213')
            if active:self.play(g,'TIME_702',g.hero_id(1))
            self.play_card(g,c);m=g.players[0].minions[-1]
            self.assertEqual((m.attack,m.health),(3,4) if active else (2,3));self.assertEqual(len(g.players[0].hand),int(active))
    def test_ebb_flow_requires_minion_while_held(self):
        g=self.game();self.play(g,'EDR_851t');c=self.put(g,'TIME_702');self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[0].armor,0)
        c=self.put(g,'TIME_702');self.play(g,'EDR_851t');self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[0].armor,5)
    def moon(self,cid):
        g=self.game();c=self.put(g,cid)
        for n in range(3):
            self.play(g,'TOKEN_COIN');self.assertEqual(c.card_id,cid if n<2 else MOON_TRANSFORMS[cid])
        return g,c
    def test_wish_moon_lifesteal(self):
        g,c=self.moon('EDR_460');g.players[0].health=20;m=g._summon(1,'EDR_851t');self.play_card(g,c,m.uid);self.assertEqual(g.players[0].health,26)
    def test_light_moon_returns_unupgraded_copy(self):
        g,c=self.moon('FIR_918');m=g._summon(0,'EDR_851t');self.play_card(g,c,m.uid);self.assertEqual(g.players[0].hand[-1].card_id,'FIR_918');self.assertEqual(m.attack,4)
    def test_molten_gold_elemental(self):
        g,c=self.moon('JAIL_801');self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[1].health,26);self.assertEqual(g.players[0].minions[-1].attack,3)
    def test_frostshatter_elemental(self):
        g,c=self.moon('JAIL_803');self.play_card(g,c,g.hero_id(1));self.assertEqual(len(g.players[0].hand),2);self.assertGreaterEqual(g.players[1].frozen_until,g.turn)
    def test_stormfury_elemental_lifesteal(self):
        g,c=self.moon('JAIL_805');g.players[0].health=20;g._summon(1,'EDR_851t');g._summon(1,'EDR_851t');self.play_card(g,c);self.assertEqual(g.players[0].health,24)
    def test_reforestation_age_and_combined_draw(self):
        g=self.game();c=self.put(g,'EDR_843')
        for _ in range(2):self.cycle(g);self.assertEqual(c.card_id,'EDR_843')
        self.cycle(g);self.assertEqual(c.card_id,'EDR_843t1');g.players[0].hand=[c];g.players[0].deck=['EDR_851t','CORE_CS2_029'];self.play_card(g,c)
        self.assertEqual({v.card_id for v in g.players[0].hand},{'EDR_851t','CORE_CS2_029'})
    def test_reforestation_unupgraded_choice(self):
        g=self.game();g.players[0].deck=['EDR_851t','CORE_CS2_029'];self.play(g,'EDR_843',choice=1);self.assertEqual(g.players[0].hand[0].card_id,'EDR_851t')
    def test_delayed_fire_next_own_turn(self):
        g=self.game();self.play(g,'FIR_902');self.assertEqual(g.players[1].health,30);self.cycle(g);self.assertEqual(g.players[1].health,24)
    def test_crystalspine_last_mana(self):
        g=self.game();m=g._summon(0,'CATA_130');c=self.put(g,'CORE_CS2_029');g.players[0].mana=4
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==g.hero_id(1)))
        self.assertEqual((m.attack,m.health),(g.cards[m.card_id]['attack']+1,g.cards[m.card_id]['health']+1))
    def test_troublemaker_progress_in_deck_and_hand(self):
        g=self.game();g.players[0].deck=['JAIL_470'];self.play(g,'TIME_702',g.hero_id(1));c=g._draw(0);self.play(g,'CORE_CS2_029',g.hero_id(1));self.play_card(g,c)
        self.assertEqual(g.players[1].health,19)
    def test_twilight_egg_grows_whelp_only(self):
        g=self.game();m=g._summon(0,'CATA_210');self.cycle(g);self.assertEqual(m.health,2);self.kill(g,m)
        w=g.players[0].minions[0];self.assertEqual((w.card_id,w.attack,w.health),('CATA_210t',3,2))
    def test_stegodon_all_three_zones(self):
        g=self.game();c=self.put(g,'TLC_827');g.players[0].deck=['TLC_827'];m=g._summon(0,'TLC_827');g.step(Action('end'))
        self.assertEqual((c.attack_bonus,m.attack,g.players[0].deck[0].attack_bonus),(1,1,1))
    def test_shadow_changes_repeatedly(self):
        g=self.game();c=self.put(g,'CORE_RLK_567');self.play(g,'TOKEN_COIN');self.assertEqual(c.card_id,'TOKEN_COIN')
        self.play(g,'CORE_CS2_029',g.hero_id(1));self.assertEqual(c.card_id,'CORE_CS2_029');self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[1].health,18)
    def test_mirrex_latest_opponent_and_three_cost(self):
        g=self.game();g.players[1].last_minion_played='CATA_551t';c=self.put(g,'DINO_407');g.legal_actions()
        self.assertEqual((c.card_id,g._cost(c,0),g._card_stat(c,'attack',0),g._card_stat(c,'health',0)),('CATA_551t',3,3,4))
        g._queue_event('minion_played',owner=1,card_id='EDR_851t',source=0,cost=1);self.assertEqual(c.card_id,'EDR_851t')
    def test_shapeshifter_repeats_owner_turn(self):
        g=self.game();c=self.put(g,'TIME_876');self.put(g,'EDR_851t',1);self.cycle(g);self.assertEqual(c.card_id,'EDR_851t')
        g.players[1].hand=[];self.put(g,'CATA_551t',1);self.cycle(g);self.assertEqual(c.card_id,'CATA_551t')
    def test_slayer_buffs_before_stealth_removed(self):
        g=self.game();m=g._summon(0,'CAP_000');self.attack(g,m,g.hero_id(1));self.assertEqual(g.players[1].health,27);self.assertEqual((m.attack,m.health),(3,4));self.assertNotIn('STEALTH',m.keywords)
    def test_shaw_discount(self):
        g=self.game();m=g._summon(0,'CAP_005');c=self.put(g,'CORE_CS2_029');self.attack(g,m,g.hero_id(1));self.assertEqual(g._cost(c,0),1)
    def test_tricks_tracks_stealth_attack(self):
        g=self.game();c=self.put(g,'CAP_006');m=g._summon(0,'TLC_247');self.attack(g,m,g.hero_id(1));self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[1].health,22)
    def test_silent_strike_stealth_positive_negative(self):
        for stealth in (False,True):
            g=self.game();m=g._summon(0,'EDR_851t');v=g._summon(1,'CATA_551t')
            if stealth:m.keywords.add('STEALTH')
            before=v.health;self.play(g,'CAP_001',m.uid);self.assertEqual(v.health,before-4 if stealth else before)
    def test_rehgar_adjacent_attack(self):
        g=self.game();a=g._summon(0,'EDR_851t');g._summon(0,'CORE_CATA_004');self.attack(g,a,g.hero_id(1));self.assertEqual(g.players[0].hand[0].card_id,'CORE_EX1_238')
    def test_thresher_cleave_shield(self):
        g=self.game();a=g._summon(0,'CORE_SCH_605');vs=[g._summon(1,'EDR_851t') for _ in range(3)];vs[0].keywords.add('DIVINE_SHIELD');self.attack(g,a,vs[1].uid)
        self.assertEqual([m.uid for m in g.players[1].minions],[vs[0].uid]);self.assertNotIn('DIVINE_SHIELD',vs[0].keywords)
    def test_dracorex_damage_other_enemies(self):
        g=self.game();a=g._summon(0,'DINO_401');v=g._summon(1,'EDR_851t');g._summon(1,'EDR_851t');self.attack(g,a,v.uid);self.assertEqual(g.players[1].minions,[])
    def test_omen_last_attack_increases_deathrattle(self):
        g=self.game();a=g._summon(0,'EDR_421');a.health=1;v=g._summon(1,'EDR_851t');self.attack(g,a,v.uid);self.assertEqual(g.players[1].health,28)
    def test_hound_survives_attacks_minion(self):
        g=self.game();a=g._summon(0,'FIR_953');v=g._summon(1,'EDR_851t');self.attack(g,a,v.uid);self.assertEqual(g.players[1].health,25)
    def test_escape_draw_no_death(self):
        g=self.game();a=g._summon(0,'JAIL_030');self.attack(g,a,g.hero_id(1));self.assertEqual(len(g.players[0].hand),1);self.assertNotIn(a,g.players[0].board);self.assertEqual(g.players[0].death_history,[])
    def test_raincaller_first_spell_damage_each_turn(self):
        g=self.game();m=g._summon(0,'CATA_487');attack=m.attack
        self.play(g,'CORE_CS2_029',g.hero_id(1));self.assertEqual(m.attack,attack+2)
        self.play(g,'CORE_CS2_029',g.hero_id(1));self.assertEqual(m.attack,attack+2)
        self.cycle(g);self.play(g,'CORE_CS2_029',g.hero_id(1));self.assertEqual(m.attack,attack+4)
    def test_archaios_sets_attacker_health(self):
        g=self.game();a=g._summon(0,'EDR_851t');g._summon(0,'TLC_811');self.attack(g,a,g.hero_id(1));self.assertEqual(a.health,6)
    def test_sabretooth_kill_copy(self):
        g=self.game();a=g._summon(0,'TLC_247');v=g._summon(1,'EDR_851t');self.attack(g,a,v.uid);self.assertEqual(g.players[0].hand[0].card_id,'EDR_851t')
    def test_finja_kill_recruits_two(self):
        g=self.game();g.players[0].deck=['CORE_EX1_507']*2;a=g._summon(0,'CORE_CFM_344');v=g._summon(1,'EDR_851t');self.attack(g,a,v.uid);self.assertEqual(len(g.players[0].minions),3)
    def test_spear_last_durability_uses_attack_snapshot(self):
        g=self.game();self.play(g,'EDR_842');g.players[0].weapon['durability']=1;v=g._summon(1,'CATA_551t');v.keywords.discard('TAUNT');health=v.health
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==g.hero_id(0) and a.target==g.hero_id(1)))
        self.assertEqual(v.health,health-2);self.assertIsNone(g.players[0].weapon)
    def test_acolyte_undead_only(self):
        g=self.game();g._summon(0,'CORE_RLK_121');self.kill(g,g._summon(0,'CS2_033'));self.assertFalse(g.players[0].hand)
        self.kill(g,g._summon(0,'CAP_803'));self.assertEqual(len(g.players[0].hand),1)
    def test_flytrap_both_owners_death_attack(self):
        g=self.game();m=g._summon(0,'EDR_484');self.kill(g,g._summon(1,'EDR_851t'));self.assertEqual(m.attack,3)
    def test_direhorn_payment_only_when_missing_reborn(self):
        g=self.game();m=g._summon(0,'DINO_416');g.players[0].corpses=2;self.kill(g,g._summon(0,'EDR_851t'));self.assertIn('REBORN',m.keywords);self.assertEqual(g.players[0].corpses,0)
        self.kill(g,g._summon(0,'EDR_851t'));self.assertEqual(g.players[0].corpses,1)
    def test_platysaur_exact_physical_card(self):
        g=self.game();old=self.put(g,'CORE_CS2_029');self.play(g,'TLC_603');drawn=g.players[0].hand[-1];self.kill(g,g.players[0].minions[0]);self.assertIn(old,g.players[0].hand);self.assertNotIn(drawn,g.players[0].hand)
    def test_ooze_one_bones_with_both_stats(self):
        g=self.game();v=g._summon(0,'EDR_851t');g._buff(v,3,4);self.play(g,'TLC_252',v.uid);c=g.players[0].hand[0];self.assertEqual(len(g.players[0].hand),1)
        m=g.players[0].minions[0];self.play_card(g,c,m.uid);self.assertEqual((m.attack,m.health),(7,8))
    def test_blackwing_breath_damage_payload(self):
        g=self.game();m=g._summon(0,'CATA_464');g._buff(m,4,0);self.kill(g,m);c=g.players[0].hand[0];self.play_card(g,c,g.hero_id(1));self.assertEqual(g.players[1].health,23)
    def test_augur_private_choice_and_exact_discard(self):
        g=self.game();a=self.put(g,'CORE_CS2_029',1);b=self.put(g,'CORE_CS2_029',1);self.play(g,'JAIL_303')
        selected=g.pending_choice['options'][0]['uid'];self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True});self.choose(g)
        board=g.observe(1)['players'][0]['board'][0];self.assertNotIn('secret_discard',board);self.kill(g,g.players[0].minions[0]);self.assertEqual(len(g.players[1].hand),1);self.assertNotEqual(g.players[1].hand[0].uid,selected)
    def test_epoch_played_previous_turn_not_summoned(self):
        g=self.game();g.step(Action('end'));self.play(g,'EDR_851t');summoned=g._summon(1,'EDR_851t');g.step(Action('end'));self.play(g,'TIME_714');self.assertEqual(g.players[1].minions,[summoned])
    def test_chromie_draws_one_each_played_identity(self):
        g=self.game();g.players[0].played_history=[dict(card_id='EDR_851t',cost=1)]*2+[dict(card_id='CORE_CS2_029',cost=4)];g.players[0].deck=['EDR_851t']*2+['CORE_CS2_029'];self.kill(g,g._summon(0,'TIME_103'));self.assertEqual(len(g.players[0].hand),2)
    def test_earthen_roar_second_different_target(self):
        g=self.game();self.put(g,'CATA_551t');a=g._summon(1,'CATA_551t');b=g._summon(1,'CATA_551t');self.play(g,'CATA_554',a.uid)
        self.assertEqual([o['uid'] for o in g.pending_choice['options']],[b.uid]);self.choose(g);self.assertEqual((a.health,b.health),(1,1))
    def test_morchok_excess_discount(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029']*3;self.play(g,'CATA_570');self.assertEqual([g._cost(c,0) for c in g.players[0].hand],[0,0,2])
    def test_glider_next_murloc_discount_and_shield(self):
        g=self.game();g.players[0].previous_tribes={'MURLOC'};self.play(g,'TLC_428');c=self.put(g,'CORE_EX1_507');self.assertEqual(g._cost(c,0),2);self.play_card(g,c);self.assertIn('DIVINE_SHIELD',g.players[0].minions[-1].keywords);self.assertFalse(g.players[0].cost_effects)
    def test_loh_future_minions_cost_five(self):
        g=self.game();self.play(g,'TLC_257');c=self.put(g,'EDR_851t');self.assertEqual(g._cost(c,0),5);self.assertEqual(g._cost(self.put(g,'CORE_CS2_029'),0),4)
    def test_naralex_first_dragon_resets(self):
        g=self.game();g._summon(0,'EDR_844');c=self.put(g,'CATA_551t');self.assertEqual(g._cost(c,0),1);self.play_card(g,c);d=self.put(g,'CATA_551t');self.assertEqual(g._cost(d,0),g.cards[d.card_id]['cost']);self.cycle(g);self.assertEqual(g._cost(d,0),1)
    def test_keeper_destruction_follows_to_board(self):
        g=self.game();c=self.put(g,'EDR_851t');self.play(g,'FIR_928');self.play_card(g,c);m=g.players[0].minions[-1];self.assertEqual(m.attack,4)
        self.cycle(g);self.cycle(g);self.assertIn(m,g.players[0].board);self.cycle(g);self.assertNotIn(m,g.players[0].board)
    def test_last_stand_recruits_from_hand(self):
        g=self.game();c=self.put(g,'EDR_851t');m=g._summon(0,'EDR_851t');self.play(g,'CATA_610',m.uid);self.kill(g,m);self.assertNotIn(c,g.players[0].hand);self.assertEqual(len(g.players[0].minions),1)
    def test_amphibian_passes_deathrattle(self):
        g=self.game();a=g._summon(0,'EDR_851t');b=g._summon(0,'EDR_851t');self.play(g,'EDR_261',a.uid);self.kill(g,a);self.assertEqual((b.attack,b.health),(3,3));self.assertTrue(b.attached_death_effects)
    def test_pterrordax_health_steal(self):
        g=self.game();v=g._summon(1,'EDR_851t');self.kill(g,g._summon(0,'TLC_831'));m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(3,4));self.assertNotIn(v,g.players[1].board)
    def test_sinful_steed_full_enchanted_reborn(self):
        g=self.game();m=g._summon(0,'CAP_800');g._buff(m,2,4);self.kill(g,m);n=g.players[0].minions[0];self.assertEqual((n.attack,n.health,n.max_health),(4,7,7));self.assertNotIn('REBORN',n.keywords)
    def test_lingering_spirit_excess_healing(self):
        g=self.game();g.players[0].health=29;self.kill(g,g._summon(0,'CAP_803'));self.assertEqual((g.players[0].health,g.players[1].health),(30,28))
    def test_typhoon_no_deaths_or_copied_buffs(self):
        g=self.game();a=g._summon(0,'EDR_851t');g._buff(a,5,5);g._summon(1,'EDR_851t');before=sum(len(p.deck) for p in g.players);self.play(g,'EDR_232')
        self.assertFalse(any(p.board for p in g.players));self.assertEqual(sum(len(p.deck) for p in g.players),before+2);self.assertFalse(any(p.death_history for p in g.players))
    def test_triumph_excess_discount(self):
        g=self.game();c=self.put(g,'CORE_CS2_029');m=g._summon(1,'EDR_851t');self.play(g,'CATA_978',m.uid);self.assertEqual(g._cost(c,0),0)
    def test_torch_return_excess_no_spell_damage(self):
        g=self.game();m=g._summon(1,'CATA_551t');m.health=2;g._summon(0,'CORE_EX1_012');self.assertGreater(g._spell_damage(0),0);self.play(g,'CATA_585',m.uid);c=g.players[0].hand[-1];self.assertEqual(c.rule_state['damage'],6)
    def test_bone_flurry_extra_damage(self):
        for died in (False,True):
            g=self.game()
            if died:self.kill(g,g._summon(0,'EDR_851t'))
            self.play(g,'JAIL_445');self.assertEqual(g.players[1].health,24 if died else 27)
    def test_vanguard_repeats_if_missile_kills(self):
        g=self.game();g._summon(1,'EDR_851t')
        with patch.object(g.rng,'choice',side_effect=lambda xs:xs[-1]):self.play(g,'MEND_302')
        self.assertEqual(g.players[1].health,25)
    def test_lightning_rod_friendly_then_enemy(self):
        g=self.game();a=g._summon(0,'CATA_551t');b=g._summon(1,'CATA_551t');ha,hb=a.health,b.health;self.play(g,'TIME_212',a.uid);self.assertEqual((a.health,b.health),(ha-2,hb-4))
    def test_shield_stops_overkill_bonus(self):
        g=self.game();c=self.put(g,'CORE_CS2_029');m=g._summon(1,'EDR_851t');m.keywords.add('DIVINE_SHIELD');self.play(g,'CATA_978',m.uid);self.assertEqual(g._cost(c,0),4)
    def test_silence_clears_attached_and_progress(self):
        g=self.game();m=g._summon(0,'CATA_210');m.rule_state['egg_bonus']=5;m.attached_death_effects=[('b60_infest',)];g._silence(m);self.kill(g,m);self.assertFalse(g.players[0].minions)
    def test_private_hand_progress_not_observed(self):
        g=self.game();c=self.put(g,'EDR_460');self.play(g,'TOKEN_COIN');own=g.observe(0);other=g.observe(1)
        self.assertEqual(own['players'][0]['hand'][0]['rule_state']['spells'],1);self.assertNotIn('hand',other['players'][0]);json.dumps(other)
    def test_step_rollback_restores_hand_progress(self):
        g=self.game();self.put(g,'EDR_460');c=self.put(g,'TOKEN_COIN');actions=g.legal_actions();before=deepcopy(g.__dict__);original=g._b60_event
        def fail(kind,data):
            original(kind,data)
            if kind=='spell_cast':raise RuntimeError('injected')
        with patch.object(g,'_b60_event',side_effect=fail):
            with self.assertRaises(RuntimeError):g.step(next(a for a in actions if a.kind=='play' and a.source==c.uid))
        self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())
    def test_dead_acolyte_does_not_draw_own_death(self):
        g=self.game();self.kill(g,g._summon(0,'CORE_RLK_121'));self.assertFalse(g.players[0].hand)
    def test_generated_moon_starts_fresh(self):
        g=self.game();g._queue_event('spell_cast',owner=0,card_id='TOKEN_COIN',cost=0);g._add(0,'EDR_460');c=g.players[0].hand[-1];self.play(g,'TOKEN_COIN');self.assertEqual(c.rule_state['spells'],1)
    def test_no_enemy_hand_progress_on_own_spell(self):
        g=self.game();c=self.put(g,'EDR_460',1);self.play(g,'TOKEN_COIN');self.assertEqual(c.card_id,'EDR_460');self.assertFalse(getattr(c,'rule_state',{}).get('spells',0))
    def test_health_setting_removes_existing_damage(self):
        g=self.game();a=g._summon(1,'CATA_551t');a.health=3;a.keywords.discard('TAUNT');self.play(g,'CATA_554',a.uid)
        self.assertEqual((a.health,a.max_health),(1,1))
        b=g._summon(0,'CS2_033');b.health=2;g._summon(0,'TLC_811');self.attack(g,b,g.hero_id(1));self.assertEqual((b.health,b.max_health),(6,6))
    def test_crystalspine_spending_extra_mana_inside_effect(self):
        g=self.game();m=g._summon(0,'CATA_130');before=m.attack;self.play(g,'CATA_135');self.assertEqual(m.attack,before+1)
    def test_morchok_full_hand_burn_keeps_repeating(self):
        g=self.game();g.players[0].deck=['EDR_851t']*3+['CORE_CS2_029']
        for _ in range(9):self.put(g,'TOKEN_COIN')
        self.play(g,'CATA_570');self.assertEqual(len(g.players[0].hand),10);self.assertEqual(g.players[0].deck,[]);self.assertEqual(g.players[0].fatigue,1)
    def test_raincaller_does_not_ignore_prior_spell_damage(self):
        g=self.game();self.play(g,'CORE_CS2_029',g.hero_id(1));m=g._summon(0,'CATA_487');before=m.attack
        self.play(g,'CORE_CS2_029',g.hero_id(1));self.assertEqual(m.attack,before)
    def test_finja_surviving_target_no_recruit(self):
        g=self.game();g.players[0].deck=['CORE_EX1_507']*2;a=g._summon(0,'CORE_CFM_344');v=g._summon(1,'CS2_033');self.attack(g,a,v.uid);self.assertEqual(len(g.players[0].minions),1)
    def test_silenced_steed_loses_special_reborn(self):
        g=self.game();m=g._summon(0,'CAP_800');g._buff(m,2,4);g._silence(m);m.keywords.add('REBORN');self.kill(g,m);self.assertEqual(g.players[0].minions[0].health,1)
    def test_shadow_untransformed_unplayable(self):
        g=self.game();c=self.put(g,'CORE_RLK_567');self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
    def test_shadow_exact_parameterized_spell_copy(self):
        g=self.game();shadow=self.put(g,'CORE_RLK_567');c=self.put(g,'CATA_464t');c.rule_state={'damage':7};c.spell_damage_bonus=1;c.cost_delta=-1
        self.play_card(g,c,g.hero_id(1));self.assertEqual(shadow.card_id,'CATA_464t');self.assertEqual(shadow.rule_state['damage'],7);self.assertEqual(shadow.spell_damage_bonus,1);self.assertEqual(g._cost(shadow,0),1)
        self.play_card(g,shadow,g.hero_id(1));self.assertEqual(g.players[1].health,14)

if __name__=='__main__':unittest.main()
