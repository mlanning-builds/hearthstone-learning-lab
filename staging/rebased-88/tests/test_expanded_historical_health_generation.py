"""Explicit historical contracts and physical Health-cost cards remain staged."""
import json,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action
from expanded.game import Card
from expanded import cards
from expanded import historical_generation as hg,health_generation as hp
from expanded.generation_cards import pool,discover,random_cards
from expanded.generation import request_matches
from expanded.features import encode_decision,SCHEMA
from engine.cards import UnsupportedCard

class HistoricalHealthGenerationTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.GenerationTests();self.g=self.helper.game()
        catalog={d['id']:d for d in json.loads(Path('data/standard/cards.json').read_text())}
        self.g.cards.update({cid:catalog[cid] for cid in hg.RULES.keys()|hp.RULES.keys()})
        for table,values in ((cards.RULES,{**hg.RULES,**hp.RULES}),
                             (cards.DEATH_EFFECTS,{**hg.DEATH_EFFECTS,**hp.DEATH_EFFECTS}),
                             (cards.TRIGGERS,hg.TRIGGERS)):
            p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
    @property
    def p(self):return self.g.players[0]
    def install(self,request,ids):self.helper.install(self.g,request,ids)
    def past(self,request,**overrides):
        cid='PAST_FIXTURE_'+str(len(self.g.cards))
        d=dict(id=cid,name=cid,dbfId=-len(self.g.cards),collectible=True,set='GILNEAS',type=request.card_type or 'MINION',
               cardClass=request.classes if request.classes not in ('any','own','own_or_neutral','other') else 'MAGE',
               cost=request.minimum,attack=2,health=3,mechanics=[request.mechanic] if request.mechanic else [])
        if request.tribe:d.update(race=request.tribe,races=[request.tribe])
        if request.school:d['spellSchool']=request.school
        d.update(overrides);self.g.cards[cid]=d;self.install(request,[cid]);return cid
    def play(self,cid,target=0):
        c=self.g._enter_hand(0,Card(self.g._new_id(),cid))
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
    def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
    def body(self,ops,**ctx):self.helper.run_ops(self.g,ops,**ctx)
    def test_eleven_new_collectibles_stay_outside_live_registration(self):
        self.assertEqual(len(hg.RULES)+len(hp.RULES),11)
        self.assertFalse((hg.RULES.keys()|hp.RULES.keys())&cards.COLLECTIBLE_IDS)
    def test_era_is_explicit_and_rejects_unknown_values(self):
        self.assertNotEqual(pool(era='past'),pool())
        with self.assertRaises(ValueError):pool(era='future')
    def test_standard_contract_cannot_fulfill_historical_request(self):
        self.install(pool(card_type='MINION'),['CORE_EX1_012']);rng=self.g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):self.g._generation_candidates(hg.MINION,0)
        self.assertEqual(self.g.rng.getstate(),rng)
    def test_historical_rejects_current_standard_identity(self):
        self.install(hg.MINION,['CORE_EX1_012'])
        with self.assertRaisesRegex(UnsupportedCard,'Standard'):self.g._generation_candidates(hg.MINION,0)
    def test_historical_rejects_original_printing_of_core_card(self):
        d=self.g.cards['CORE_EX1_012'];cid=self.past(hg.MINION,set='LEGACY',countAsCopyOfDbfId=d.get('countAsCopyOfDbfId',d['dbfId']))
        with self.assertRaisesRegex(UnsupportedCard,'Standard'):self.g._generation_candidates(hg.MINION,0)
    def test_historical_rejects_tokens(self):
        self.past(hg.MINION,collectible=False)
        with self.assertRaisesRegex(UnsupportedCard,'tokens'):self.g._generation_candidates(hg.MINION,0)
    def test_historical_rejects_other_modes_and_future_sets(self):
        for name in ('LETTUCE','BATTLEGROUNDS','VANILLA','CORE_HIDDEN','HERO_SKINS','UNRELEASED'):
            self.past(hg.MINION,set=name)
            with self.subTest(name=name),self.assertRaises(UnsupportedCard):self.g._generation_candidates(hg.MINION,0)
    def test_historical_rejects_ineligible_school_without_filtering(self):
        self.past(hg.NATURE,spellSchool='FIRE')
        with self.assertRaisesRegex(UnsupportedCard,'ineligible'):self.g._generation_candidates(hg.NATURE,0)
    def test_historical_rejects_duplicate_canonical_printings(self):
        cid=self.past(hg.MINION);alias='OLD_ALIAS';self.g.cards[alias]=dict(self.g.cards[cid],id=alias)
        self.install(hg.MINION,[cid,alias])
        with self.assertRaisesRegex(UnsupportedCard,'duplicate canonical'):self.g._generation_candidates(hg.MINION,0)
    def test_historical_does_not_omit_unsupported_outcome(self):
        cid=self.past(hg.MINION);self.install(hg.MINION,[cid,'UNIMPLEMENTED_PAST_CARD'])
        with self.assertRaisesRegex(UnsupportedCard,'missing card data'):self.g._generation_candidates(hg.MINION,0)
    def test_neon_innovation_buffs_selected_physical_mech(self):
        cid=self.past(hg.MECH,cost=3);self.play('TIME_016');self.choose();c=self.p.hand[0]
        self.assertEqual((c.card_id,c.attack_bonus,c.health_bonus),(cid,5,5))
    def test_alter_time_two_choices_two_discoveries_with_discounts(self):
        self.past(hg.ARCANE,cost=4);self.play('TIME_857');self.choose()
        self.assertIsNotNone(self.g.pending_choice);self.choose()
        self.assertEqual(len(self.p.hand),2);self.assertEqual(self.p.discoveries_total,2)
        self.assertTrue(all(c.cost_delta==-2 for c in self.p.hand));self.assertNotEqual(self.p.hand[0].uid,self.p.hand[1].uid)
    def test_alter_time_choice_options_private(self):
        self.past(hg.ARCANE,cost=4);self.play('TIME_857');v=self.g.observe(0)
        self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        self.assertTrue(encode_decision(dict(actor=0,observation=v,actions=v['legal_actions'])))
    def test_historical_missing_contract_rolls_back_paid_spell(self):
        c=self.g._enter_hand(0,Card(self.g._new_id(),'TIME_016'));v=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):
            self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.g.observe(0),v);self.assertEqual(self.g.rng.getstate(),rng)
    def test_flashback_summons_two_without_combo_bonus(self):
        cid=self.past(hg.ONE);self.play('TIME_711')
        self.assertEqual([m.card_id for m in self.p.minions],[cid,cid]);self.assertEqual([m.attack for m in self.p.minions],[2,2])
    def test_flashback_combo_buffs_both(self):
        self.past(hg.ONE);self.play('TOKEN_COIN');self.play('TIME_711')
        self.assertEqual([(m.attack,m.health) for m in self.p.minions],[(3,3),(3,3)])
    def test_flashback_respects_one_remaining_slot(self):
        self.past(hg.ONE)
        for _ in range(6):self.g._summon(0,'AT_037t')
        self.play('TIME_711');self.assertEqual(len(self.p.minions),7)
    def test_fading_memory_death_adds_one_five_cost(self):
        cid=self.past(hg.FIVE);m=self.g._summon(0,'TIME_040');m.health=0;self.g._settle()
        self.assertEqual([c.card_id for c in self.p.hand],[cid])
    def test_amber_warden_death_summons_random_old_minion(self):
        cid=self.past(hg.MINION);m=self.g._summon(0,'TIME_052');m.health=0;self.g._settle()
        self.assertEqual([m.card_id for m in self.p.minions],[cid])
    def test_silence_suppresses_historical_death_generation(self):
        m=self.g._summon(0,'TIME_040');self.g._silence(m);m.health=0;self.g._settle();self.assertFalse(self.p.hand)
    def test_time_lost_glaive_replacement_triggers_weapon_death(self):
        cid=self.past(hg.DEMON);self.play('TIME_444');self.g._equip(0,'CS2_082')
        self.assertEqual([c.card_id for c in self.p.hand],[cid]);self.assertEqual(self.p.weapon['card_id'],'CS2_082')
    def test_primordial_lord_generates_colossal_without_summoning_it(self):
        cid=self.past(hg.COLOSSAL,cost=8);self.play('CATA_EVENT_000')
        self.assertEqual(self.p.hand[0].card_id,cid);self.assertEqual(len(self.p.minions),1)
    def test_farseer_triggers_on_owner_paid_spell(self):
        cid=self.past(hg.NATURE);self.g._summon(0,'TIME_013');self.play('TOKEN_COIN');self.choose()
        self.assertEqual(self.p.hand[0].card_id,cid)
    def test_farseer_ignores_opponent_spell_event(self):
        self.g._summon(0,'TIME_013');self.g._queue_event('spell_cast',owner=1,card_id='TOKEN_COIN',cost=0);self.g._settle(allow_event_choices=True)
        self.assertIsNone(self.g.pending_choice)
    def test_blood_draw_pays_health_and_discovers(self):
        self.install(hp.SPELL,['CORE_CS2_029']);cost=self.g.cards['TIME_612']['cost'];self.p.mana=0
        self.play('TIME_612');self.assertEqual(self.p.health,30-cost);self.assertEqual(self.p.mana,0);self.choose()
        self.assertEqual(self.p.hand[0].card_id,'CORE_CS2_029')
    def test_blood_draw_missing_pool_rolls_back_health(self):
        c=self.g._enter_hand(0,Card(self.g._new_id(),'TIME_612'));before=self.g.observe(0)
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):
            self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.g.observe(0),before)
    def test_blood_draw_generated_spell_does_not_inherit_health_payment(self):
        self.install(hp.SPELL,['CORE_CS2_029']);self.play('TIME_612');self.choose()
        self.assertEqual(self.g._payment_kind(self.p.hand[0],0),'mana')
    def test_blood_draw_health_cost_respects_discount(self):
        self.install(hp.SPELL,['CORE_CS2_029']);c=self.g._enter_hand(0,Card(self.g._new_id(),'TIME_612'));c.cost_delta=-1
        cost=self.g._cost(c,0);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(self.p.health,30-cost)
    def test_physical_health_payment_cannot_kill_own_hero(self):
        c=self.g._generation_place('CORE_CS2_029','hand',(('health_payment','permanent'),),dict(owner=0));self.p.health=4
        self.assertFalse(self.g._can_pay(c,0));self.p.health=5;self.assertTrue(self.g._can_pay(c,0))
    def test_health_payment_is_not_damage_and_ignores_armor(self):
        c=self.g._generation_place('CORE_CS2_029','hand',(('health_payment','permanent'),),dict(owner=0));self.p.armor=9;self.p.mana=0
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==-2))
        self.assertEqual((self.p.health,self.p.armor,self.p.mana,self.p.hero_damage_events_turn),(26,9,0,0))
    def test_whispering_stone_death_grants_two_permanent_health_spells(self):
        self.install(hp.FEL,['CORE_BT_035']);m=self.g._summon(0,'TLC_467');m.health=0;self.g._settle()
        self.assertEqual(len(self.p.hand),2);self.assertTrue(all(self.g._payment_kind(c,0)=='health' for c in self.p.hand))
        copies=list(self.p.hand);self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertTrue(all(self.g._payment_kind(c,0)=='health' for c in copies))
    def test_forgotten_millennium_fills_only_free_slots(self):
        self.install(hp.UNDEAD,['CORE_EX1_012']);self.g._add(0,'TOKEN_COIN');self.play('TIME_615')
        self.assertEqual(len(self.p.hand),10);generated=[c for c in self.p.hand if c.card_id=='CORE_EX1_012']
        self.assertEqual(len(generated),9);self.assertTrue(all(self.g._payment_kind(c,0)=='health' for c in generated))
    def test_millennium_discount_expires_but_cards_stay(self):
        self.install(hp.UNDEAD,['CORE_EX1_012']);self.play('TIME_615');generated=list(self.p.hand)
        self.g.step(Action('end'));self.assertEqual(len(self.p.hand),10)
        self.assertTrue(all(self.g._payment_kind(c,0)=='mana' for c in generated))
    def test_full_hand_does_not_skip_pool_validation(self):
        self.p.hand=[Card(self.g._new_id(),'TOKEN_COIN') for _ in range(10)]
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed'):self.body(hp.RULES['TIME_615'][1])
    def test_reviewed_empty_pool_produces_nothing(self):
        self.install(hp.UNDEAD,[]);self.play('TIME_615');self.assertFalse(self.p.hand)
    def test_unknown_health_duration_rejected_before_creating_entity(self):
        with self.assertRaisesRegex(UnsupportedCard,'duration'):
            self.g._generation_place('CORE_CS2_029','hand',(('health_payment','unknown'),),dict(owner=0))
        self.assertFalse(self.p.hand)
    def test_health_payment_copy_is_independent(self):
        c=self.g._generation_place('CORE_CS2_029','hand',(('health_payment','turn'),),dict(owner=0));clone=self.g._copy_card(c)
        self.assertEqual(self.g._payment_kind(clone,0),'health');clone.rule_state['health_payment']=False
        self.assertEqual(self.g._payment_kind(c,0),'health')
    def test_health_payment_moves_with_physical_card_to_new_controller(self):
        c=self.g._generation_place('CORE_CS2_029','hand',(('health_payment','permanent'),),dict(owner=0));self.p.hand.remove(c);self.g._enter_hand(1,c)
        self.assertEqual(self.g._payment_kind(c,1),'health');self.assertEqual(self.g._payment_kind(Card(0,c.card_id),0),'mana')
    def test_health_payment_visible_only_in_owner_hand(self):
        self.g._generation_place('CORE_CS2_029','hand',(('health_payment','turn'),),dict(owner=0));v=self.g.observe(0)
        self.assertEqual(v['players'][0]['hand'][0]['payment_kind'],'health');self.assertNotIn('hand',self.g.observe(1)['players'][0])
        rows=encode_decision(dict(actor=0,observation=v,actions=v['legal_actions']))
        self.assertIn('health_payment',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_pending_historical_choice_clone_resolves_identically(self):
        self.past(hg.MECH,cost=3);self.play('TIME_016');other=deepcopy(self.g)
        self.choose();other.step(Action('choose',choices=(0,)));self.assertEqual(self.g.observe(0),other.observe(0))
