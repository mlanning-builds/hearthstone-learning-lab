"""Finite construction and physical payload behavior, with explicit review gates."""
import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded import Action,cards,locations
from expanded import reviewed_complex_bindings as bindings
from expanded import custom_builders,learned_spells,tiny_pal,hand_investigations,exceptional_finish
from expanded.pools import GenerationPool
import test_expanded_generation as fixtures


class ReviewedComplexPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as stream:
            cls.records={c['id']:c for c in json.load(stream)}

    def setUp(self):
        self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
        self.g.cards.update({cid:self.records[cid] for cid in set(bindings.RULES)|bindings.TOKEN_IDS})
        for table,values in ((cards.RULES,bindings.RULES),(cards.RULES,bindings.TOKEN_RULES),
            (cards.DEATH_EFFECTS,bindings.DEATH_EFFECTS),(cards.WEAPON_TRIGGERS,bindings.WEAPON_TRIGGERS),
            (locations.LOCATION_RULES,bindings.LOCATION_RULES)):
            context=patch.dict(table,values);context.start();self.addCleanup(context.stop)

    def ops(self,*operations,**context):self.fx.run_ops(self.g,operations,**context)
    def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
    def contract(self,request,ids,owner=0):
        if not hasattr(self.g,'_generation_pools'):self.g._generation_pools={}
        self.g._generation_pools[(request,self.g.players[owner].hero_class)]=GenerationPool('fixture',tuple(ids),'Controlled mechanics fixture')

    def test_bindings_have_nine_explicit_root_definitions(self):
        self.assertEqual(set(bindings.RULES),{'CAP_405','TLC_100','MEND_046','MEND_100','TIME_704','TIME_041','TIME_861','JAIL_458','JAIL_EVENT_100'})
        self.assertTrue(bindings.TOKEN_IDS<=self.records.keys())
        self.assertFalse(bindings.OPTION_IDS&bindings.PLAYABLE_TOKEN_IDS)

    def test_kazakus_selects_two_different_parts_and_physical_duration(self):
        self.ops(('craft_trial',));first=self.g.pending_choice['options'][0]['card_id']
        self.choose();self.assertNotIn(first,[o['card_id'] for o in self.g.pending_choice['options']])
        self.choose();self.choose(2);card=self.p.hand[0]
        self.assertEqual(card.card_id,'CAP_405tb3');self.assertEqual(card.rule_state['crafted_ops'][0][1],4)
        self.assertEqual(self.p.discoveries_total,0)

    def test_pending_construction_choice_cannot_be_overwritten(self):
        self.ops(('craft_trial',));choice=self.g.pending_choice
        with self.assertRaises(UnsupportedCard):self.g._craft_offer(0,'craft_trial_length',custom_builders.TRIAL_IDS)
        self.assertIs(self.g.pending_choice,choice)

    def test_elise_copy_stats_are_initialized_before_summon_notification(self):
        model=self.g._summon(0,'CORE_EX1_012');self.g._buff(model,7,9)
        original=self.g._log;seen=[]
        def log(event,**data):
            if event=='summon':
                m=self.g._force_live(data['entity']);seen.append((m.attack,m.max_health,m.health))
            return original(event,**data)
        with patch.object(self.g,'_log',side_effect=log):
            self.g._craft_choice(dict(kind='location_copy',owner=0,size=3),dict(card_id=model.card_id,uid=model.uid))
        self.assertEqual(seen,[(3,3,3)]);self.assertEqual((model.attack,model.max_health),(8,10))

    def test_unbound_custom_location_fails_and_paid_play_rolls_back(self):
        card=self.g._add(0,'TLC_100t1');mana=self.p.mana
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid)
        with self.assertRaises(UnsupportedCard):self.g.step(action)
        self.assertEqual(self.g.players[0].mana,mana);self.assertEqual(self.g.players[0].locations,[])
        self.assertIn(card.uid,[c.uid for c in self.g.players[0].hand])

    def test_bashana_approximation_retains_all_three_spell_payloads(self):
        self.contract(learned_spells.NATURE,['CORE_EX1_169']);self.ops(('learned_carve',))
        self.assertEqual(len(self.p.hand),3)
        self.assertTrue(all(c._learned_spell=='CORE_EX1_169' for c in self.p.hand))

    def test_invalid_carve_distribution_does_not_sample(self):
        self.contract(learned_spells.NATURE,['CORE_EX1_169'])
        self.g.carve_allocation_contract=dict(source='fixture',outcomes_by_count={3:((1,('UNKNOWN',)*3),)})
        state=self.g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.ops(('learned_carve',))
        self.assertEqual(self.g.rng.getstate(),state);self.assertEqual(self.p.hand,[])

    def test_unbound_learned_minion_is_not_fake_noop(self):
        card=Card(self.g._new_id(),'MEND_046t')
        with self.assertRaisesRegex(UnsupportedCard,'bound spell payload'):self.ops(('learned_cast',),physical_card=card)

    def test_bulb_created_and_copy_upgrade_independently(self):
        self.ops(('learned_bulb',));card=self.p.hand[0];copy=self.g._clone_hand_card(0,card)
        self.ops(('learned_bulb_tick',card.uid))
        self.assertEqual(card.rule_state['bulb_level'],2);self.assertEqual(copy.rule_state['bulb_level'],1)

    def test_tiny_pal_stale_choice_cannot_change_replacement_weapon(self):
        self.g._equip(0,'JAIL_458');self.ops(('tiny_choose',None));choice=self.g.pending_choice
        self.g._equip(0,'CS2_082');uid=self.p.equipped_card.uid
        self.choose();self.assertEqual(self.p.weapon['card_id'],'CS2_082');self.assertEqual(self.p.equipped_card.uid,uid)

    def test_tiny_pal_frost_excludes_actual_attack_target(self):
        enemy=self.g._summon(1,'CORE_EX1_012');self.g._summon(1,'CORE_CS2_188')
        self.ops(('tiny_freeze',enemy.uid))
        self.assertLessEqual(enemy.frozen_until,self.g.turn);self.assertGreater(self.q.frozen_until,self.g.turn)
        self.assertGreater(self.q.minions[1].frozen_until,self.g.turn)

    def test_forefather_uses_enemy_class_pool_and_private_correct_identity(self):
        self.g._add(1,'CORE_CS2_029');self.contract(hand_investigations.DECOYS,['CORE_EX1_162','CORE_CS2_188'],owner=1)
        source=self.g._summon(0,'TIME_041');before=source.max_health
        self.ops(('guess_hand',),source=source)
        own=self.g.observe(0)['pending_choice'];other=self.g.observe(1)['pending_choice']
        self.assertNotIn('correct',own);self.assertTrue(other['waiting'])
        index=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='CORE_CS2_029')
        self.choose(index);self.assertEqual(source.max_health,before+4);self.assertEqual(self.p.discoveries_total,0)

    def test_watfin_default_approximation_offers_a_physical_card(self):
        self.contract(exceptional_finish.MINIONS,['CORE_CS2_188']);self.ops(('suspicious_discover',))
        self.assertEqual(self.g.pending_choice['kind'],'suspicious_discover')
        self.assertEqual(len(self.g.pending_choice['cards']),1)
