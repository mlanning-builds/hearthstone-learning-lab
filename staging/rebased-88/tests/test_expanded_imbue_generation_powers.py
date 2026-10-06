"""Synthetic contracts exercise power semantics, never certify Standard pools."""
import json
import unittest
from copy import deepcopy
import test_expanded_imbue_bodies as fixtures
from expanded import Action
from expanded.game import Card
from expanded.generation_cards import pool
from expanded.pools import GenerationPool
from expanded.features import encode_decision
from engine.cards import UnsupportedCard

class ImbueGenerationPowerTests(unittest.TestCase):
    def game(self,hero,level=1):return fixtures.ImbueBodyTests().game(hero,level)
    def contract(self,g,request,ids,owner=0):
        if not hasattr(g,'_generation_pools'):g._generation_pools={}
        g._generation_pools[request,g.players[owner].hero_class]=GenerationPool('Synthetic fixture',tuple(ids),'Tests only; not a complete Standard pool')
    def card(self,g,cid,kind='MINION',cost=1,hero='PRIEST',tribe=None):
        g.cards[cid]=dict(id=cid,name=cid,type=kind,cost=cost,cardClass=hero,attack=1,health=1,mechanics=[])
        if tribe:g.cards[cid]['race']=tribe
        return cid
    def priest(self,level=1,mana=10):
        g=self.game('PRIEST',level);g.players[0].mana=mana
        for kind in ('MINION','SPELL'):
            ids=[self.card(g,kind+str(n),kind,n) for n in (1,5,9,12)]
            self.contract(g,pool(card_type=kind,classes='PRIEST'),ids)
        return g
    def rogue(self,level=1):
        g=self.game('ROGUE',level)
        ids=[self.card(g,'R'+str(n),cost=n,hero='MAGE') for n in (1,3,5)]
        self.contract(g,pool(card_type='MINION',classes='other'),ids)
        return g
    def portal(self,g,cost,owner=0,empty=False):
        cid=self.card(g,'DRAGON'+str(cost),cost=cost,hero='NEUTRAL',tribe='DRAGON')
        self.contract(g,pool(card_type='MINION',tribe='DRAGON',minimum=cost,maximum=cost),() if empty else (cid,),owner)
    def draw_portal(self,g,owner=0):
        g.players[owner].deck.append('EDR_445pt3');g._draw(owner);g._settle(allow_event_choices=True)
    def test_paladin_shuffles_two_physical_portals_and_pays_once(self):
        g=self.game('PALADIN',4);old=len(g.players[0].deck);g.step(Action('power'))
        portals=[c for c in g.players[0].deck if g._card_data(c)['id']=='EDR_445pt3']
        self.assertEqual(len(portals),2);self.assertNotEqual(portals[0].uid,portals[1].uid)
        self.assertEqual(len(g.players[0].deck),old+2);self.assertEqual(g.players[0].mana,9)
        self.assertEqual(g.players[0].hero_power_uses,1)
    def test_portal_uses_latest_imbue_not_creation_level(self):
        g=self.game('PALADIN');g.step(Action('power'));g._imbue(0,3);self.portal(g,4)
        g.players[0].deck=['AT_037t','EDR_445pt3'];g._draw(0);g._settle()
        self.assertEqual(g.players[0].minions[0].card_id,'DRAGON4')
        self.assertEqual([c.card_id for c in g.players[0].hand],['AT_037t'])
    def test_stolen_portal_uses_recipient_progress(self):
        g=self.game('PALADIN',6);g._imbue(1,2);self.portal(g,2,1);self.draw_portal(g,1)
        self.assertEqual(g.players[1].minions[0].card_id,'DRAGON2');self.assertFalse(g.players[0].minions)
    def test_zero_imbues_uses_reviewed_empty_zero_pool(self):
        g=self.game('PALADIN');self.portal(g,0,1,empty=True);self.draw_portal(g,1)
        self.assertFalse(g.players[1].minions);self.assertEqual(len(g.players[1].hand),1)
    def test_portal_full_hand_burns_without_effect_or_replacement(self):
        g=self.game('PALADIN');g.players[0].hand=[Card(g._new_id(),'AT_037t') for _ in range(10)]
        self.draw_portal(g);self.assertFalse(g.players[0].minions);self.assertEqual(len(g.players[0].deck),10)
    def test_portal_full_board_still_replaces_draw(self):
        g=self.game('PALADIN');self.portal(g,1)
        for _ in range(7):g._summon(0,'AT_037t')
        self.draw_portal(g);self.assertEqual(len(g.players[0].minions),7);self.assertEqual(len(g.players[0].hand),1)
    def test_portal_chain_draws_only_one_ordinary_card(self):
        g=self.game('PALADIN');self.portal(g,1);g.players[0].deck=['AT_037t','EDR_445pt3','EDR_445pt3']
        g._draw(0);g._settle();self.assertEqual(len(g.players[0].minions),2);self.assertEqual(len(g.players[0].hand),1)
    def test_portal_manual_cast_has_no_replacement_draw(self):
        g=self.game('PALADIN');self.portal(g,1);c=g._enter_hand(0,Card(g._new_id(),'EDR_445pt3'))
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(len(g.players[0].minions),1);self.assertFalse(g.players[0].hand)
    def test_portal_missing_pool_rolls_back_paid_draw(self):
        g=self.game('PALADIN');g.players[0].deck=['EDR_445pt3'];c=g._enter_hand(0,Card(g._new_id(),'CORE_CS2_023'))
        before=g.observe(0);rng=g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):
            g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
    def test_priest_offers_one_of_each_type_after_payment(self):
        g=self.priest(level=3,mana=7);g.step(Action('power'))
        ids=[o['card_id'] for o in g.pending_choice['options']]
        self.assertEqual([g.cards[c]['type'] for c in ids],['MINION','SPELL'])
        self.assertTrue(all(g.cards[c]['cost']<=8 for c in ids));self.assertEqual(g.players[0].mana,5)
        self.assertEqual(g.players[0].hero_power_uses,0)
    def test_priest_choice_is_temporary_discounted_and_not_discover(self):
        g=self.priest(3);g.step(Action('power'));cid=g.pending_choice['options'][1]['card_id']
        g.step(Action('choose',choices=(1,)));c=g.players[0].hand[0]
        self.assertEqual(c.card_id,cid);self.assertEqual(c.cost_delta,-3);self.assertTrue(g._is_temporary(c))
        self.assertEqual(g.players[0].discoveries_total,0);self.assertEqual(g.players[0].hero_power_uses,1)
        g.step(Action('end'));self.assertFalse(g.players[0].hand)
    def test_priest_no_affordable_options_finishes_power(self):
        g=self.priest(mana=2)
        for cid in list(g.cards):
            if cid.startswith(('MINION','SPELL')):g.cards[cid]['cost']=12
        g.step(Action('power'));self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].hero_power_uses,1)
    def test_priest_single_nonempty_group(self):
        g=self.priest();self.contract(g,pool(card_type='SPELL',classes='PRIEST'),())
        g.step(Action('power'));self.assertEqual(len(g.pending_choice['options']),1)
    def test_priest_checks_both_contracts_before_random(self):
        g=self.priest();del g._generation_pools[pool(card_type='SPELL',classes='PRIEST'),'PRIEST']
        before=g.observe(0);rng=g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):g.step(Action('power'))
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
    def test_priest_choices_private_and_feature_encodable(self):
        g=self.priest();g.step(Action('power'));view=g.observe(0)
        self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
        self.assertNotIn('snapshot',json.dumps(view))
        self.assertTrue(encode_decision(dict(actor=0,observation=view,actions=view['legal_actions'])))
    def test_priest_full_hand_choice_burns_result(self):
        g=self.priest();g.players[0].hand=[Card(g._new_id(),'AT_037t') for _ in range(10)]
        g.step(Action('power'));g.step(Action('choose',choices=(0,)))
        self.assertEqual(len(g.players[0].hand),10);self.assertEqual(g.players[0].hero_power_uses,1)
    def test_rogue_keep_commits_one_payment_one_card_one_use(self):
        g=self.rogue(3);g.step(Action('power'));cid=g.players[0].hand[0].card_id
        self.assertEqual(g.pending_choice['kind'],'rewind');self.assertEqual(g.players[0].hero_power_uses,0)
        g.step(Action('choose',choices=(0,)));p=g.players[0]
        self.assertEqual((p.mana,len(p.hand),p.hero_power_uses),(9,1,1));self.assertEqual(p.hand[0].card_id,cid)
        self.assertEqual(p.hand[0].cost_delta,-3);self.assertTrue(p.power_used);self.assertIsNone(g._power_frame)
    def test_rogue_reroll_restores_zones_but_advances_random(self):
        g=self.rogue(3);g.step(Action('power'));rng=g.rng.getstate()
        g.step(Action('choose',choices=(1,)));p=g.players[0]
        self.assertNotEqual(g.rng.getstate(),rng);self.assertEqual((p.mana,len(p.hand),p.hero_power_uses),(9,1,1))
        self.assertEqual(p.hand[0].cost_delta,-3);self.assertIsNone(g.pending_choice);self.assertIsNone(g._power_frame)
        self.assertEqual(g._power_sequence_depth,0);self.assertNotIn(Action('power'),g.legal_actions())
    def test_rogue_reroll_does_not_remove_existing_hand(self):
        g=self.rogue();old=g._enter_hand(0,Card(g._new_id(),'AT_037t'))
        g.step(Action('power'));g.step(Action('choose',choices=(1,)))
        self.assertEqual(len(g.players[0].hand),2);self.assertEqual(g.players[0].hand[0].uid,old.uid)
    def test_rogue_reroll_preserves_one_shot_power_discount(self):
        g=self.rogue();g.players[0].next_power_cost_effects=[dict(kind='set',amount=0)]
        g.step(Action('power'));g.step(Action('choose',choices=(1,)))
        self.assertEqual(g.players[0].mana,10);self.assertEqual(g.players[0].next_power_cost_effects,[])
    def test_rogue_full_hand_can_rewind_without_duplicate_use(self):
        g=self.rogue();g.players[0].hand=[Card(g._new_id(),'AT_037t') for _ in range(10)]
        g.step(Action('power'));g.step(Action('choose',choices=(1,)))
        self.assertEqual(len(g.players[0].hand),10);self.assertEqual(g.players[0].hero_power_uses,1)
    def test_rogue_missing_pool_is_atomic(self):
        g=self.game('ROGUE');before=g.observe(0);rng=g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):g.step(Action('power'))
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
    def test_rogue_refresh_starts_new_rewind_budget(self):
        g=self.rogue();g.step(Action('power'));g.step(Action('choose',choices=(1,)))
        g.players[0].power_used=False;g.step(Action('power'));self.assertEqual(g.pending_choice['remaining'],1)
        g.step(Action('choose',choices=(0,)));self.assertEqual(g.players[0].hero_power_uses,2)
    def test_rogue_snapshot_is_not_observed(self):
        g=self.rogue();g.step(Action('power'));view=g.observe(0)
        self.assertNotIn('snapshot',json.dumps(view));self.assertNotIn('options',g.observe(1)['pending_choice'])
        self.assertTrue(encode_decision(dict(actor=0,observation=view,actions=view['legal_actions'])))
    def test_rogue_free_trigger_rejects_unverified_timing(self):
        g=self.rogue()
        with self.assertRaisesRegex(UnsupportedCard,'conformance'):
            g._imbue_consumer_split(('imbue_trigger_power',),dict(owner=0))
    def test_rogue_after_use_listener_runs_once_after_either_choice(self):
        for choice in (0,1):
            g=self.rogue();g._summon(0,'EDR_470');hp=g.players[0].minions[0].max_health
            g.step(Action('power'));self.assertEqual(g.players[0].minions[0].max_health,hp)
            g.step(Action('choose',choices=(choice,)))
            self.assertEqual(g.players[0].minions[0].max_health,hp+2)
    def test_rogue_after_use_nested_choice_resumes_without_another_rewind(self):
        from unittest.mock import patch
        from expanded.cards import TRIGGERS
        for choice in (0,1):
            g=self.rogue();g._summon(0,'EDR_470')
            with patch.dict(TRIGGERS,{'EDR_470':('hero_power_used',[('discover_deck',),('armor',7)])}):
                g.step(Action('power'));g.step(Action('choose',choices=(choice,)))
                self.assertNotEqual(g.pending_choice['kind'],'rewind')
                g.step(Action('choose',choices=(0,)))
            self.assertEqual(g.players[0].armor,7);self.assertEqual(g.players[0].hero_power_uses,1)
            self.assertIsNone(g._power_frame);self.assertIsNone(g.pending_choice)
    def test_rogue_clone_can_finish_same_reroll(self):
        g=self.rogue();g.step(Action('power'));other=deepcopy(g)
        for state in (g,other):state.step(Action('choose',choices=(1,)))
        self.assertEqual(g.observe(0),other.observe(0));self.assertEqual(g.rng.getstate(),other.rng.getstate())
    def test_rogue_failed_reroll_restores_pending_decision(self):
        from unittest.mock import patch
        from expanded import Game
        g=self.rogue();g.step(Action('power'));before=g.observe(0);rng=g.rng.getstate()
        with patch.object(Game,'_imbue_power_operations',side_effect=UnsupportedCard('injected replay failure')):
            with self.assertRaisesRegex(UnsupportedCard,'injected'):g.step(Action('choose',choices=(1,)))
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
        g.step(Action('choose',choices=(0,)));self.assertEqual(g.players[0].hero_power_uses,1)
    def test_priest_power_cost_modifier_changes_offer_budget(self):
        g=self.priest(level=1,mana=4);g.players[0].next_power_cost_effects=[dict(kind='set',amount=0)]
        for kind in ('MINION','SPELL'):
            self.contract(g,pool(card_type=kind,classes='PRIEST'),(kind+'5',))
        g.step(Action('power'));self.assertEqual(len(g.pending_choice['options']),2)
        self.assertEqual(g.players[0].mana,4)
    def test_priest_empty_mana_can_offer_zero_after_discount(self):
        g=self.priest(mana=2);g.step(Action('power'))
        self.assertEqual([o['card_id'] for o in g.pending_choice['options']],['MINION1','SPELL1'])
        g.step(Action('choose',choices=(0,)));self.assertEqual(g._cost(g.players[0].hand[0],0),0)
