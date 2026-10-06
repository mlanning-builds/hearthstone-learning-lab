"""Shared staged choices against controlled contracts, not Standard admission."""
import json,unittest
from copy import deepcopy
from unittest.mock import patch
from pathlib import Path
import test_expanded_generation as fixtures
from expanded import Action
from expanded.game import Card
from expanded import cards
from expanded import choice_generators as cg
from expanded.generation_cards import pool,discover,random_cards
from expanded.generation import request_matches
from expanded.pools import GenerationPool
from expanded.features import encode_decision,SCHEMA
from engine.cards import UnsupportedCard

class ChoiceGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.GenerationTests();self.g=self.helper.game()
        catalog={d['id']:d for d in json.loads(Path('data/standard/cards.json').read_text())}
        self.g.cards.update({cid:catalog[cid] for cid in cg.RULES})
        for table,added in ((cards.RULES,cg.RULES),(cards.CHOICES,cg.CHOICES),(cards.DEATH_EFFECTS,cg.DEATH_EFFECTS),(cards.WEAPON_TRIGGERS,cg.WEAPON_TRIGGERS),(cards.LOCATION_RULES,{'JAIL_987':'none'})):
            p=patch.dict(table,added);p.start();self.addCleanup(p.stop)
    @property
    def p(self):return self.g.players[0]
    def install(self,request,ids):self.helper.install(self.g,request,ids)
    def synthetic(self,cid,kind='MINION',cost=1,hero='MAGE',**extra):
        self.g.cards[cid]=dict(id=cid,name=cid,type=kind,cost=cost,cardClass=hero,attack=1,health=1,rarity='COMMON',mechanics=[],**extra)
        return cid
    def offers(self,request):
        ids=[]
        for n in range(3):
            cid='fixture'+str(len(self.g.cards))
            hero=request.classes if request.classes not in ('any','own','own_or_neutral','other') else 'DRUID' if request.classes=='other' else 'MAGE'
            d=dict(id=cid,name=cid,type=request.card_type or 'SPELL',cardClass=hero,cost=request.minimum,
                   attack=1,health=1,rarity=request.rarity or 'COMMON',mechanics=[request.mechanic] if request.mechanic else [])
            if request.tribe:d.update(race=request.tribe,races=[request.tribe])
            if request.rune:d['runeCost']={request.rune:1}
            self.g.cards[cid]=d;ids.append(cid)
        self.install(request,ids);return ids
    def all_pools(self,cid):
        for request in sorted(cg.requests_for(cid),key=repr):self.offers(request)
    def run_body(self,cid,**ctx):
        self.helper.run_ops(self.g,cg.RULES[cid][1],card_id=cid,**ctx)
    def play(self,cid,choice=None,target=0):
        c=self.g._enter_hand(0,Card(self.g._new_id(),cid))
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target and (choice is None or a.choices==(choice,)))
        self.g.step(action);return c
    def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
    def test_all_33_definitions_remain_staged(self):
        self.assertEqual(len(cg.RULES),33);self.assertFalse(set(cg.RULES)&cards.COLLECTIBLE_IDS)
    def test_rune_selector_requires_requested_rune_without_deck_rune_filter(self):
        for rune in ('blood','frost','unholy'):
            self.assertTrue(request_matches(pool(rune=rune),dict(cost=1,runeCost={rune:2}),'MAGE'))
            self.assertFalse(request_matches(pool(rune=rune),dict(cost=1,runeCost={}),'DEATHKNIGHT'))
        with self.assertRaises(ValueError):pool(rune='shadow')
    def test_hematurge_spends_one_and_discovers(self):
        self.all_pools('CORE_RLK_066');self.p.corpses=2;self.play('CORE_RLK_066')
        self.assertEqual(self.p.corpses,1);self.choose();self.assertEqual(len(self.p.hand),1)
    def test_hematurge_without_corpse_needs_no_pool(self):
        self.play('CORE_RLK_066');self.assertIsNone(self.g.pending_choice)
    def test_hematurge_missing_pool_rolls_back_payment_and_corpse(self):
        self.p.corpses=1;c=self.g._enter_hand(0,Card(self.g._new_id(),'CORE_RLK_066'));before=self.g.observe(0)
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):self.g.step(next(a for a in self.g.legal_actions() if a.source==c.uid and a.kind=='play'))
        self.assertEqual(self.g.observe(0),before)
    def test_mortician_requires_recent_friendly_undead(self):
        self.all_pools('CORE_RLK_116');self.p.last_turn_ended=self.g.turn-1
        m=self.g._summon(0,'CORE_EX1_012');m.health=0;self.g._settle()
        self.run_body('CORE_RLK_116');self.assertIsNotNone(self.g.pending_choice)
    def test_mortician_ignores_deaths_during_previous_own_turn(self):
        m=self.g._summon(0,'CORE_EX1_012');m.health=0;self.g._settle();self.p.last_turn_ended=self.g.turn
        self.run_body('CORE_RLK_116');self.assertIsNone(self.g.pending_choice)
    def test_mortician_ignores_enemy_undead(self):
        m=self.g._summon(1,'CORE_EX1_012');m.health=0;self.g._settle()
        self.run_body('CORE_RLK_116');self.assertIsNone(self.g.pending_choice)
    def test_death_window_resets_at_end_of_owner_turn(self):
        m=self.g._summon(0,'CORE_EX1_012');m.health=0;self.g._settle();self.assertTrue(self.g._choicegen_undead_died(0))
        self.g.step(Action('end'));self.assertFalse(self.g._choicegen_undead_died(0))
    def test_rune_strike_discovers_only_when_target_dies(self):
        self.all_pools('RLK_025');m=self.g._summon(1,'AT_037t');self.play('RLK_025',target=m.uid)
        self.assertIsNotNone(self.g.pending_choice);self.choose();self.assertEqual(len(self.p.hand),1)
    def test_rune_strike_shield_or_survival_does_not_discover(self):
        for cid,shield in (('EX1_tk34',False),('AT_037t',True)):
            m=self.g._summon(1,cid)
            if shield:m.keywords.add('DIVINE_SHIELD')
            self.run_body('RLK_025',target=m.uid);self.assertIsNone(self.g.pending_choice)
    def test_hook_heave_summons_after_choice(self):
        self.all_pools('CAP_105');self.play('CAP_105');self.assertFalse(self.p.minions)
        self.choose();self.assertEqual([m.card_id for m in self.p.minions],['CAP_107t','CAP_107t'])
    def test_wanted_poster_grants_prepare_to_physical_card(self):
        request=next(iter(cg.requests_for('CAP_407')));self.install(request,['CORE_CS2_222'])
        self.play('CAP_407');self.choose();c=self.p.hand[0]
        self.assertIn(Action('prepare',source=c.uid),self.g.legal_actions())
        self.g.step(Action('prepare',source=c.uid));self.assertTrue(c.rule_state['prepared'])
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
    def test_illidari_studies_discount_is_next_outcast(self):
        self.all_pools('CORE_YOP_001');self.play('CORE_YOP_001');self.choose()
        outcast=Card(self.g._new_id(),'CORE_BT_480');other=Card(self.g._new_id(),'CORE_CS2_029')
        self.assertEqual(self.g._cost(outcast,0),0);self.assertEqual(self.g._cost(other,0),4)
    def test_all_choose_one_branches_suspend_correctly(self):
        for cid in ('Core_LOE_115','EDR_872'):
            for branch in (0,1):
                self.p.mana=10;self.all_pools(cid);self.play(cid,choice=branch)
                self.assertIsNotNone(self.g.pending_choice);self.choose()
    def test_secret_ingredient_both_branches(self):
        self.play('JAIL_201',choice=0);self.assertEqual(self.g._hero_attack(0),2)
        self.all_pools('JAIL_201');self.play('JAIL_201',choice=1);self.assertEqual(len(self.p.hand),1)
    def test_symbiosis_other_class_choice(self):
        self.all_pools('EDR_273');self.play('EDR_273');self.choose()
        self.assertEqual(self.g.cards[self.p.hand[0].card_id]['cardClass'],'DRUID')
    def test_qonzu_two_steps_only_one_discover(self):
        self.all_pools('EDR_517');self.play('EDR_517');cid=self.g.pending_choice['options'][0]['card_id']
        self.choose();self.assertEqual(self.p.discoveries_total,1);self.assertFalse(self.p.hand)
        self.choose(1);self.assertEqual(self.g._card_data(self.g.players[1].deck[-1])['id'],cid)
        self.assertEqual(self.p.discoveries_total,1);self.assertFalse(self.p.hand)
    def test_qonzu_keep_puts_selected_spell_in_hand(self):
        self.all_pools('EDR_517');self.play('EDR_517');self.choose();self.choose()
        self.assertEqual(len(self.p.hand),1)
    def test_whelp_next_turn_crystal_then_expires(self):
        self.all_pools('FIR_927');self.p.max_mana=5;self.play('FIR_927');self.choose()
        self.assertEqual(self.p.max_mana,5);self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual(self.p.max_mana,7);self.g.step(Action('end'));self.assertEqual(self.p.max_mana,6)
    def test_whelp_at_cap_does_not_remove_real_crystal(self):
        self.all_pools('FIR_927');self.play('FIR_927');self.choose()
        for _ in range(3):self.g.step(Action('end'))
        self.assertEqual(self.p.max_mana,10)
    def test_breakout_architect_selected_spell_repeats(self):
        request=next(iter(cg.requests_for('JAIL_123')));self.install(request,['CORE_CS2_032'])
        self.play('JAIL_123');self.choose();c=self.p.hand[0];self.assertTrue(c.rule_state['repeat_spell'])
        self.p.mana=10;m=self.g._summon(1,'EX1_tk34')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertFalse(self.g.players[1].minions)
    def test_blood_clone_spends_corpses_and_summons_without_battlecry(self):
        self.all_pools('JAIL_451');self.p.corpses=5;self.play('JAIL_451');self.choose()
        self.assertEqual(self.p.corpses,0);self.assertEqual(self.p.minions[0].card_id,self.p.hand[0].card_id)
    def test_blood_clone_four_corpses_only_adds_hand_card(self):
        self.all_pools('JAIL_451');self.p.corpses=4;self.play('JAIL_451');self.choose()
        self.assertEqual(self.p.corpses,4);self.assertFalse(self.p.minions)
    def test_jade_uses_paid_cost_history_and_two_physical_cards(self):
        self.all_pools('JAIL_474');self.p.played_history=[dict(card_id='CORE_CS2_029',cost=n) for n in (2,2,4)]
        self.play('JAIL_474');self.assertEqual([c.cost_delta for c in self.p.hand],[-2,-2]);self.assertEqual(len({c.uid for c in self.p.hand}),2)
    def test_code_violet_three_previous_spells_summons_twice(self):
        self.all_pools('JAIL_735');self.p.spells_turn=['TOKEN_COIN']*3;self.play('JAIL_735')
        self.assertEqual(len(self.p.minions),2)
    def test_code_violet_two_previous_spells_summons_once(self):
        self.all_pools('JAIL_735');self.p.spells_turn=['TOKEN_COIN']*2;self.play('JAIL_735')
        self.assertEqual(len(self.p.minions),1)
    def test_hexmarshal_uses_starting_deck_not_current_deck(self):
        self.all_pools('JAIL_806');self.p.starting_deck=['AT_037t'];self.run_body('JAIL_806')
        self.assertEqual(self.p.hand[0].cost_delta,-5)
        self.p.starting_deck=['CORE_CS2_029'];self.p.deck=[];self.run_body('JAIL_806')
        self.assertEqual(self.p.hand[-1].cost_delta,0)
    def test_scarlet_bruiser_no_neutral_checks_current_deck(self):
        self.all_pools('JAIL_328');self.helper.run_ops(self.g,cg.DEATH_EFFECTS['JAIL_328']);self.assertEqual(self.p.hand[0].cost_delta,-2)
        self.p.deck=['CORE_EX1_012'];self.helper.run_ops(self.g,cg.DEATH_EFFECTS['JAIL_328']);self.assertEqual(len(self.p.hand),1)
    def test_noxious_bribe_combines_only_owner_copy(self):
        self.p.hero_class='DRUID';self.install(cg.CHOOSE,['CORE_AT_037']);self.play('JAIL_861');self.choose()
        c=self.p.hand[0];enemy=self.g.players[1].hand[0]
        self.assertTrue(c.rule_state['choose_both']);self.assertFalse(getattr(enemy,'rule_state',{}).get('choose_both'))
        self.assertTrue(all(a.choices==(-1,) for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def test_staff_discount_uses_hero_attack(self):
        self.all_pools('JAIL_875');self.p.temporary_attack=3;self.g._equip(0,'JAIL_875')
        attack=self.g._hero_attack(0);self.helper.run_ops(self.g,cg.WEAPON_TRIGGERS['JAIL_875']);self.choose()
        self.assertEqual(self.p.hand[0].cost_delta,-attack)
    def test_cosmic_manifestations_outcast_repeats_damage_and_shuffle(self):
        self.all_pools('JAIL_892');self.play('JAIL_892',target=-2)
        self.assertEqual(self.g.players[1].health,26);self.assertEqual(len(self.p.deck),14)
    def test_forger_only_affordable_temporary_spells(self):
        request=next(iter(cg.requests_for('JAIL_986')));self.install(request,['TOKEN_COIN','CORE_CS2_032']);self.p.mana=3
        self.play('JAIL_986');self.assertEqual(self.p.hand[0].card_id,'TOKEN_COIN');self.assertTrue(self.g._is_temporary(self.p.hand[0]))
    def test_wing_unlocks_after_another_play_across_turns(self):
        self.install(next(iter(cg.requests_for('JAIL_987'))),['CORE_AT_052']);self.play('JAIL_987');self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'));c=self.p.hand[0]
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
        self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
        self.play('TOKEN_COIN');self.assertTrue(any(a.kind=='play' and a.source==c.uid for a in self.g.legal_actions()))
    def test_circadiamancer_tracks_generated_card_across_turns(self):
        self.all_pools('TIME_102');self.run_body('TIME_102');c=self.p.hand[0]
        self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(c.cost_delta,-1)
    def test_solitude_finishes_two_choices_then_discounts_all_hand_minions(self):
        self.all_pools('TIME_448');existing=self.g._enter_hand(0,Card(self.g._new_id(),'CORE_EX1_012'))
        self.play('TIME_448');self.choose();self.assertEqual(getattr(existing,'cost_delta',0),0);self.choose()
        self.assertTrue(all(c.cost_delta==-2 for c in self.p.hand));self.assertEqual(self.p.discoveries_total,2)
    def test_cultivator_places_two_buffed_beasts_on_bottom(self):
        self.all_pools('TIME_730');self.play('TIME_730');self.choose();self.choose()
        self.assertFalse(self.p.hand);self.assertEqual(len(self.p.deck),14)
        self.assertEqual([(c.attack_bonus,c.health_bonus) for c in self.p.deck[:2]],[(5,5),(5,5)])
        self.assertEqual(self.p.deck[-1],'CORE_CS2_029')
    def test_champion_fills_only_opponent_free_slots(self):
        self.all_pools('TIME_872');self.g._summon(1,'AT_037t');self.play('TIME_872')
        self.assertEqual(len(self.g.players[1].minions),7);self.assertEqual(len(self.p.minions),1)
    def test_relic_miner_destroys_top_and_uses_rarity(self):
        self.all_pools('TLC_109');top='CORE_EX1_012';self.p.deck.append(top);self.play('TLC_109')
        self.assertEqual(len(self.p.deck),12);self.assertFalse(any(c.card_id==top for c in self.p.hand))
        rarity=self.g.cards[top]['rarity'];self.assertTrue(all(self.g.cards[o['card_id']]['rarity']==rarity for o in self.g.pending_choice['options']))
    def test_relic_empty_deck_does_not_fatigue(self):
        self.p.deck=[];self.play('TLC_109');self.assertIsNone(self.g.pending_choice);self.assertEqual(self.p.fatigue,0)
    def test_paleomancy_keeps_three_for_five_corpses(self):
        self.all_pools('TLC_434');self.p.corpses=5;self.play('TLC_434');self.choose()
        self.assertEqual(len(self.p.hand),3);self.assertEqual(self.p.corpses,0);self.assertEqual(self.p.discoveries_total,1)
    def test_paleomancy_without_corpses_keeps_one(self):
        self.all_pools('TLC_434');self.p.corpses=4;self.play('TLC_434');self.choose()
        self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.corpses,4)
    def test_scavenger_uses_mana_after_card_payment(self):
        self.offers(pool(minimum=9,maximum=9,classes=cg.OWN));self.play('TLC_461')
        self.assertTrue(all(self.g.cards[o['card_id']]['cost']==9 for o in self.g.pending_choice['options']))
    def test_artifacts_uses_discovery_history(self):
        self.all_pools('TLC_462');self.run_body('TLC_462');self.assertEqual(self.g.cards[self.p.minions[-1].card_id]['cost'],2)
        self.p.discoveries_this_turn=1;self.run_body('TLC_462');self.assertEqual(self.g.cards[self.p.minions[-1].card_id]['cost'],4)
    def test_voidbulb_kindred_produces_two_taunts(self):
        self.all_pools('TLC_815');self.run_body('TLC_815',kindred=True)
        self.assertEqual(len(self.p.minions),2);self.assertTrue(all('TAUNT' in m.keywords for m in self.p.minions))
    def test_follow_footsteps_attaches_to_selected_card(self):
        self.install(cg.STEALTH,['CORE_EX1_010']);self.play('CAP_002');self.choose();c=self.p.hand[0]
        self.assertEqual(c._follow_effects,[dict(card_id='CAP_002',end=self.g.turn)])
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertIsNotNone(self.g.pending_choice);self.choose();self.assertEqual(len(self.p.hand),1)
    def test_follow_expires_without_playing_card(self):
        self.install(cg.STEALTH,['CORE_EX1_010']);self.play('CAP_002');self.choose();c=self.p.hand[0]
        self.g.step(Action('end'));self.assertEqual(c._follow_effects,[])
    def test_choices_and_death_window_visible_without_leaking_options(self):
        self.all_pools('TLC_434');self.play('TLC_434');view=self.g.observe(0)
        self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertIn('undead_died_since_last_turn',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_source_and_canonical_alias_cannot_discover_themselves(self):
        source='TLC_434';self.g.cards['alias']=dict(self.g.cards[source],id='alias',countAsCopyOfDbfId=self.g.cards[source]['dbfId'])
        r=pool();self.install(r,[source]);self.helper.run_ops(self.g,[discover(r)],card_id='alias')
        self.assertIsNone(self.g.pending_choice)
    def test_private_choice_clone_resumes_same_outcome(self):
        self.all_pools('JAIL_451');self.play('JAIL_451');clone=deepcopy(self.g)
        self.choose();clone.step(Action('choose',choices=(0,)));self.assertEqual(self.g.observe(0),clone.observe(0))
    def test_low_wing_placement_does_not_generate_until_activated(self):
        self.play('JAIL_987');self.assertFalse(self.p.hand);self.assertEqual(self.p.locations[0].durability,3)
    def test_low_wing_missing_pool_restores_charge_and_cooldown(self):
        self.play('JAIL_987');before=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):
            self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'))
        self.assertEqual(self.g.observe(0),before);self.assertEqual(self.g.rng.getstate(),rng)
    def test_locked_card_exposes_relative_unlock_progress(self):
        self.install(next(iter(cg.requests_for('JAIL_987'))),['CORE_AT_052']);self.play('JAIL_987')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='activate'));c=self.p.hand[0]
        row=next(c for c in self.g.observe(0)['players'][0]['hand'] if c['card_id']=='CORE_AT_052')
        self.assertEqual(row['plays_until_unlocked'],1)
        self.play('TOKEN_COIN');row=next(c for c in self.g.observe(0)['players'][0]['hand'] if c['card_id']=='CORE_AT_052')
        self.assertEqual(row['plays_until_unlocked'],0)
    def test_generated_prepare_does_not_bypass_play_lock(self):
        c=self.g._generation_place('CORE_CS2_222','hand',(('prepare',True),('locked_until_play',True)),dict(owner=0))
        self.assertFalse(self.g._can_prepare(c,0));self.play('TOKEN_COIN');self.assertTrue(self.g._can_prepare(c,0))
    def test_paleomancy_full_hand_still_spends_corpses(self):
        self.all_pools('TLC_434');self.p.corpses=5
        self.p.hand=[Card(self.g._new_id(),'TOKEN_COIN') for _ in range(9)]
        self.play('TLC_434');self.choose();self.assertEqual(len(self.p.hand),10);self.assertEqual(self.p.corpses,0)
    def test_blood_clone_full_board_still_spends_corpses(self):
        self.all_pools('JAIL_451');self.p.corpses=5
        for _ in range(7):self.g._summon(0,'AT_037t')
        self.play('JAIL_451');self.choose();self.assertEqual(len(self.p.minions),7);self.assertEqual(self.p.corpses,0)
    def test_relic_missing_contract_does_not_destroy_top_or_pay(self):
        self.p.deck.append('CORE_EX1_012');c=self.g._enter_hand(0,Card(self.g._new_id(),'TLC_109'));before=self.g.observe(0)
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):
            self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.g.observe(0),before);self.assertEqual(self.p.deck[-1],'CORE_EX1_012')
    def test_solitude_with_deck_minion_leaves_hand_costs_unchanged(self):
        self.all_pools('TIME_448');self.p.deck.append('AT_037t');self.play('TIME_448');self.choose();self.choose()
        self.assertTrue(all(c.cost_delta==0 for c in self.p.hand))
    def test_both_raven_branches_offer_two_sequential_discovers(self):
        self.all_pools('Core_LOE_115');c=self.g._enter_hand(0,Card(self.g._new_id(),'Core_LOE_115'));self.g._b60_state(c)['choose_both']=True
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid));self.choose();self.choose()
        self.assertEqual(self.p.discoveries_total,2);self.assertEqual(len(self.p.hand),2)
    def test_failed_qonzu_destination_keeps_suspended_choice(self):
        from expanded import Game
        self.all_pools('EDR_517');self.play('EDR_517');self.choose();before=self.g.observe(0)
        with patch.object(Game,'_generation_place',side_effect=UnsupportedCard('injected destination error')):
            with self.assertRaisesRegex(UnsupportedCard,'injected'):self.choose(1)
        self.assertEqual(self.g.observe(0),before);self.choose();self.assertEqual(len(self.p.hand),1)
    def test_code_violet_pending_summon_choice_does_not_count_itself(self):
        from expanded import Game
        self.all_pools('JAIL_735');self.offers(cg.SPELL);self.p.spells_turn=['TOKEN_COIN']*2
        original=Game._generation_place
        def with_choice(game,cid,destination,mods,ctx,**kw):
            result=original(game,cid,destination,mods,ctx,**kw)
            if destination=='board':game._generation_effect(discover(cg.SPELL),ctx)
            return result
        with patch.object(Game,'_generation_place',with_choice):
            self.play('JAIL_735');self.choose()
        self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.minions),1)
    def test_cultivator_bottom_insertion_is_not_a_shuffle(self):
        self.all_pools('TIME_730');before=len(self.p.shuffle_history);self.play('TIME_730');self.choose();self.choose()
        self.assertEqual(len(self.p.shuffle_history),before)
