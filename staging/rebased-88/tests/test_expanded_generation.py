"""Generation contracts, choice privacy, physical cards, and fail-closed staging."""
import copy
import json
import unittest
from pathlib import Path
from expanded import Game, Action, random_deck
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.cards import COLLECTIBLE_IDS
from expanded.generation_cards import RULES, DEATH_EFFECTS, END_EFFECTS, TRIGGERS, pool, random_cards, discover, requests_for
from expanded.generation import request_matches
from expanded.pools import GenerationPool
from expanded.generation_audit import build_report
from standard.catalog import load_catalog


class GenerationTests(unittest.TestCase):
    def game(self):
        g = Game([random_deck('MAGE', 1), random_deck('HUNTER', 2)], seed=97)
        g.step(Action('mulligan')); g.step(Action('mulligan'))
        g.current = 0
        for p in g.players:
            p.hand = []; p.board = []; p.deck = ['CORE_CS2_029']*12
            p.mana = p.max_mana = 10; p.health = 30; p.armor = 0
        return g

    def install(self, g, request, ids):
        if not hasattr(g, '_generation_pools'):
            g._generation_pools = {}
        g._generation_pools[(request, g.players[0].hero_class)] = GenerationPool('fixture only', tuple(ids), 'Synthetic unit-test membership; not a Standard policy')

    def run_ops(self, g, ops, **context):
        ctx = dict(owner=0, source=None, target=0, bonus=0, lifesteal=False)
        ctx.update(context)
        g._start_play_effects(ops, ctx)
        g._settle(allow_event_choices=True)

    def test_sixty_unregistered_recipes(self):
        self.assertEqual(len(RULES), 60)
        self.assertFalse(set(RULES) & COLLECTIBLE_IDS)
        self.assertTrue(all(requests_for(cid) for cid in RULES))

    def test_every_record_is_in_pinned_standard(self):
        records={c['id']:c for c in load_catalog()}
        self.assertTrue(set(RULES) <= records.keys())
        self.assertTrue(all(records[cid]['collectible'] for cid in RULES))

    def test_missing_contract_preserves_rng_and_zones(self):
        g=self.game(); before=g.rng.getstate(); hand=copy.deepcopy(g.players[0].hand)
        with self.assertRaisesRegex(UnsupportedCard, 'no reviewed'):
            self.run_ops(g, [random_cards(pool())])
        self.assertEqual(g.rng.getstate(), before);self.assertEqual(g.players[0].hand, hand)

    def test_missing_outcome_is_not_filtered(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','unsupported'])
        before=g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.run_ops(g,[random_cards(r)])
        self.assertEqual(g.rng.getstate(),before);self.assertFalse(g.players[0].hand)

    def test_invalid_member_rejected_before_sampling(self):
        g=self.game();r=pool(card_type='MINION');self.install(g,r,['TOKEN_COIN'])
        with self.assertRaisesRegex(UnsupportedCard,'ineligible'):self.run_ops(g,[random_cards(r)])
        self.assertFalse(g.players[0].hand)

    def test_zero_count_still_requires_closure(self):
        g=self.game()
        with self.assertRaises(UnsupportedCard):self.run_ops(g,[random_cards(pool(),0)])

    def test_negative_count_rejected(self):
        g=self.game()
        with self.assertRaises(ValueError):self.run_ops(g,[random_cards(pool(),-1)])

    def test_zero_count_valid_contract_no_rng(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);before=g.rng.getstate()
        self.run_ops(g,[random_cards(r,0)]);self.assertEqual(g.rng.getstate(),before)

    def test_empty_contract_no_choice_or_card(self):
        g=self.game();r=pool();self.install(g,r,[])
        self.run_ops(g,[random_cards(r,3),discover(r)])
        self.assertFalse(g.players[0].hand);self.assertIsNone(g.pending_choice)

    def test_random_with_replacement_creates_distinct_physical_cards(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[random_cards(r,3)])
        self.assertEqual([c.card_id for c in g.players[0].hand],['TOKEN_COIN']*3)
        self.assertEqual(len({c.uid for c in g.players[0].hand}),3)

    def test_generation_does_not_draw_or_fatigue(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);g.players[0].deck=[]
        self.run_ops(g,[random_cards(r,2)])
        self.assertEqual(g.players[0].fatigue,0);self.assertFalse(g.players[0].deck)

    def test_full_hand_burns_without_overflow(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN'])
        for _ in range(9):g._add(0,'TOKEN_COIN')
        self.run_ops(g,[random_cards(r,3)])
        self.assertEqual(len(g.players[0].hand),10)

    def test_hand_discount_is_physical(self):
        g=self.game();r=pool();self.install(g,r,['CORE_CS2_029'])
        self.run_ops(g,[random_cards(r,2,cost_delta=-2)])
        self.assertEqual([g._cost(c,0) for c in g.players[0].hand],[2,2])
        self.assertEqual(g.cards['CORE_CS2_029']['cost'],4)

    def test_fixed_cost_modifier(self):
        g=self.game();r=pool();self.install(g,r,['CORE_CS2_029'])
        self.run_ops(g,[random_cards(r,set_cost=1)])
        self.assertEqual(g._cost(g.players[0].hand[0],0),1)

    def test_board_summon_never_fires_battlecry(self):
        g=self.game();r=pool();self.install(g,r,['CORE_CS2_189'])
        self.run_ops(g,[random_cards(r,destination='board')])
        self.assertEqual(len(g.players[0].minions),1);self.assertEqual(g.players[1].health,30)

    def test_full_board_preserved(self):
        g=self.game();r=pool();self.install(g,r,['EDR_851t'])
        for _ in range(7):g._summon(0,'EDR_851t')
        before=[m.uid for m in g.players[0].board]
        self.run_ops(g,[random_cards(r,2,'board')]);self.assertEqual([m.uid for m in g.players[0].board],before)

    def test_summon_stats_and_taunt(self):
        g=self.game();r=pool();self.install(g,r,['EDR_851t'])
        self.run_ops(g,[random_cards(r,destination='board',stats=(2,3),keyword='TAUNT')])
        m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(2,3));self.assertIn('TAUNT',g._effective_keywords(m))

    def test_generated_summon_can_freeze(self):
        g=self.game();r=pool();self.install(g,r,['EDR_851t'])
        self.run_ops(g,[random_cards(r,destination='board',freeze=True)])
        self.assertGreaterEqual(g.players[0].minions[0].frozen_until,0)

    def test_shuffle_preserves_existing_deck_order(self):
        g=self.game();r=pool();self.install(g,r,['EDR_851t']);g.players[0].deck=['TOKEN_COIN','CORE_CS2_029']
        self.run_ops(g,[random_cards(r,3,'deck',double_stats=True)])
        self.assertEqual([x for x in g.players[0].deck if isinstance(x,str)],['TOKEN_COIN','CORE_CS2_029'])
        added=[x for x in g.players[0].deck if isinstance(x,Card)]
        self.assertEqual(len(added),3);self.assertTrue(all((c.attack_bonus,c.health_bonus)==(1,1) for c in added))
        self.assertEqual(sum(e['count'] for e in g.players[0].shuffle_history),3);self.assertEqual(len(g.players[0].shuffle_history),1)

    def test_enemy_top_draws_generated_card_next(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN'])
        self.run_ops(g,[random_cards(r,destination='enemy_top')])
        self.assertEqual(g._draw(1).card_id,'TOKEN_COIN');self.assertFalse(g.players[1].shuffle_history)

    def test_discover_options_are_unique_and_do_not_autoselect(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','CORE_CS2_029','EDR_851t'])
        self.run_ops(g,[discover(r)])
        self.assertEqual(len({o['card_id'] for o in g.pending_choice['options']}),3)
        self.assertFalse(g.players[0].hand);self.assertEqual(g.phase,'choice')

    def test_discover_small_pool_has_no_duplicates(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[discover(r)])
        self.assertEqual(g.pending_choice['options'],[{'card_id':'TOKEN_COIN'}])

    def test_discover_options_private_to_owner(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','CORE_CS2_029']);self.run_ops(g,[discover(r)])
        self.assertIn('options',g.observe(0)['pending_choice'])
        self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        self.assertNotIn('context',g.observe(0)['pending_choice'])

    def test_selected_discover_resumes_following_effect(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[discover(r),('armor',4)])
        self.assertEqual(g.players[0].armor,0)
        g.step(Action('choose',choices=(0,)))
        self.assertEqual(g.players[0].hand[0].card_id,'TOKEN_COIN');self.assertEqual(g.players[0].armor,4)
        self.assertFalse(hasattr(g,'_generation_choice_context'))

    def test_consecutive_discover_pauses_twice(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[discover(r),discover(r)])
        g.step(Action('choose',choices=(0,)));self.assertEqual(g.phase,'choice');self.assertEqual(len(g.players[0].hand),1)
        g.step(Action('choose',choices=(0,)));self.assertEqual(len(g.players[0].hand),2)

    def test_discover_heals_even_if_hand_full(self):
        g=self.game();r=pool();self.install(g,r,['CORE_CS2_029']);g.players[0].health=10
        for _ in range(10):g._add(0,'TOKEN_COIN')
        self.run_ops(g,[discover(r,heal_cost=True)]);g.step(Action('choose',choices=(0,)))
        self.assertEqual(g.players[0].health,14);self.assertEqual(len(g.players[0].hand),10)

    def test_unchosen_options_shuffled_once_each(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','CORE_CS2_029','EDR_851t']);g.players[0].deck=[]
        self.run_ops(g,[discover(r,shuffle_unchosen=True)]);selected=g.pending_choice['options'][0]['card_id']
        g.step(Action('choose',choices=(0,)))
        self.assertEqual(g.players[0].hand[0].card_id,selected)
        self.assertEqual({c.card_id for c in g.players[0].deck},{'TOKEN_COIN','CORE_CS2_029','EDR_851t'}-{selected})

    def test_other_class_excludes_neutral_and_own_multiclass(self):
        r=pool(classes='other')
        self.assertFalse(request_matches(r,dict(cost=1,classes=['MAGE','ROGUE']),'MAGE'))
        self.assertFalse(request_matches(r,dict(cost=1,cardClass='NEUTRAL'),'MAGE'))
        self.assertTrue(request_matches(r,dict(cost=1,cardClass='ROGUE'),'MAGE'))

    def test_all_type_minions_match_beast_request(self):
        self.assertTrue(request_matches(pool(tribe='BEAST'),dict(type='MINION',race='ALL',cost=2),'MAGE'))

    def test_class_context_contract_is_not_reused_after_class_change(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);g.players[0].hero_class='HUNTER'
        with self.assertRaises(UnsupportedCard):self.run_ops(g,[random_cards(r)])

    def test_conditional_no_dragon_does_not_generate(self):
        g=self.game();self.run_ops(g,RULES['CORE_KAR_062'][1]);self.assertIsNone(g.pending_choice)

    def test_other_mech_excludes_self(self):
        g=self.game();source=g._summon(0,'EDR_851t');g.cards=dict(g.cards);g.cards['EDR_851t']=dict(g.cards['EDR_851t'],race='MECHANICAL',races=['MECHANICAL'])
        self.run_ops(g,RULES['CORE_LOE_039'][1],source=source);self.assertIsNone(g.pending_choice)

    def test_conditional_dragon_opens_discover(self):
        g=self.game();cid=next(cid for cid,d in g.cards.items() if d.get('race')=='DRAGON');g._add(0,cid)
        r=next(iter(requests_for('CORE_KAR_062')))
        eligible=[cid for cid,d in g.cards.items() if request_matches(r,d,'MAGE')]
        self.install(g,r,eligible[:1]);self.run_ops(g,RULES['CORE_KAR_062'][1]);self.assertEqual(g.phase,'choice')

    def test_attached_effect_executes_on_death(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);m=g._summon(0,'EDR_851t')
        self.run_ops(g,[('generation_attach',random_cards(r))],target=m.uid)
        m.health=0;g._settle(allow_event_choices=True)
        self.assertEqual([c.card_id for c in g.players[0].hand],['TOKEN_COIN'])

    def test_silence_removes_attached_generation(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);m=g._summon(0,'EDR_851t')
        self.run_ops(g,[('generation_attach',random_cards(r))],target=m.uid);g._silence(m);m.health=0;g._settle()
        self.assertFalse(g.players[0].hand)

    def test_board_attachment_friendly_only(self):
        g=self.game();a=g._summon(0,'EDR_851t');b=g._summon(1,'EDR_851t')
        self.run_ops(g,[('generation_attach_board',random_cards(pool()))])
        self.assertEqual(len(a.attached_death_effects),1);self.assertFalse(b.attached_death_effects)

    def test_preflight_includes_death_effects(self):
        g=self.game()
        with self.assertRaises(UnsupportedCard):g._generation_preflight('MEND_045',0)

    def test_webspinner_dependency_request_included(self):
        self.assertEqual(requests_for('CORE_AT_062'),{pool(card_type='MINION',tribe='BEAST')})

    def test_report_is_conservative_and_does_not_change_coverage(self):
        report=build_report(load_catalog(),COLLECTIBLE_IDS)
        self.assertEqual(report['staged_cards'],60);self.assertEqual(report['newly_playable_cards'],0)
        self.assertEqual(report['playable_catalog_cards'],len(COLLECTIBLE_IDS));self.assertFalse(report['membership_reviewed'])
        self.assertTrue(report['blockers_by_affected_generators'])
        self.assertTrue(all(not c['membership_reviewed'] for row in report['cards'] for c in row['pool_contexts']))

    def test_audit_written_status_matches_index(self):
        root=Path(__file__).resolve().parents[1]
        audit=json.loads((root/'expanded/catalog_audit.json').read_text())
        written={c['id'] for c in audit['cards'] if c['implementation']=='written_unverified'}
        self.assertEqual(written,set(COLLECTIBLE_IDS))

    def test_unknown_modifier_fails_before_adding_card(self):
        g=self.game();before=g.next_uid if hasattr(g,'next_uid') else None
        with self.assertRaisesRegex(UnsupportedCard,'Unknown generation modifiers'):
            g._generation_place('TOKEN_COIN','hand',(('typo',2),),dict(owner=0))
        self.assertFalse(g.players[0].hand)

    def test_spell_cannot_be_generated_onto_board(self):
        g=self.game()
        with self.assertRaisesRegex(UnsupportedCard,'requires a minion'):
            g._generation_place('TOKEN_COIN','board',(),dict(owner=0))
        self.assertFalse(g.players[0].board)

    def test_invalid_pool_request_rejected(self):
        for kwargs in [dict(minimum=-1),dict(minimum=3,maximum=1),dict(classes='MERCENARY'),dict(tribe='UNKNOWN'),dict(card_type='HERO_POWER')]:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):pool(**kwargs)

    def test_choice_failure_rolls_back_state_and_pending_context(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[discover(r,'board')])
        before=g.rng.getstate();pending=copy.deepcopy(g.pending_choice)
        with self.assertRaises(UnsupportedCard):g.step(Action('choose',choices=(0,)))
        self.assertEqual(g.pending_choice,pending);self.assertEqual(g.rng.getstate(),before)
        self.assertTrue(hasattr(g,'_generation_choice_context'));self.assertFalse(g.players[0].board)

    def test_combo_weapon_buff_is_not_applied_without_combo(self):
        g=self.game();r=pool(card_type='WEAPON');self.install(g,r,['CS2_082'])
        self.run_ops(g,[random_cards(r,combo_attack=2)],combo=False)
        self.run_ops(g,[random_cards(r,combo_attack=2)],combo=True)
        self.assertEqual([c.attack_bonus for c in g.players[0].hand],[0,2])

    def test_discovered_spell_included_in_following_school_discount(self):
        g=self.game();r=pool(card_type='SPELL',school='FEL')
        cid=next(cid for cid,d in g.cards.items() if d.get('type')=='SPELL' and d.get('spellSchool')=='FEL')
        self.install(g,r,[cid]);self.run_ops(g,[discover(r),('generation_discount_school','FEL',1)])
        g.step(Action('choose',choices=(0,)));self.assertEqual(g.players[0].hand[0].cost_delta,-1)

    def test_random_generation_is_seed_reproducible(self):
        outcomes=[]
        for _ in range(2):
            g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','CORE_CS2_029','EDR_851t'])
            self.run_ops(g,[random_cards(r,8)]);outcomes.append([c.card_id for c in g.players[0].hand])
        self.assertEqual(*outcomes)

    def test_generated_hand_card_does_not_gain_starting_deck_origin(self):
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN']);self.run_ops(g,[random_cards(r)])
        self.assertFalse(g._started_in_deck(g.players[0].hand[0],0))

    def test_duplicate_canonical_identity_contract_rejected(self):
        g=self.game();g.cards=dict(g.cards);g.cards['TOKEN_COIN']=dict(g.cards['TOKEN_COIN'],dbfId=999999);g.cards['duplicate']=dict(g.cards['TOKEN_COIN'],id='duplicate')
        r=pool();self.install(g,r,['TOKEN_COIN','duplicate'])
        with self.assertRaisesRegex(UnsupportedCard,'duplicate canonical'):self.run_ops(g,[discover(r)])

    def test_choice_feature_encoding_uses_only_visible_options(self):
        from expanded.features import encode_decision
        g=self.game();r=pool();self.install(g,r,['TOKEN_COIN','CORE_CS2_029']);self.run_ops(g,[discover(r)])
        observation=g.observe(0,include_events=False)
        rows=encode_decision(dict(actor=0,observation=observation,actions=observation['legal_actions']))
        self.assertEqual(len(rows),2)
        self.assertNotIn('_generation_choice_context',json.dumps(observation))
