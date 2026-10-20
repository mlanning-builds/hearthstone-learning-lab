"""Internally cast generation spells own their choices and preserve pool gates."""
import unittest
from unittest.mock import patch
from engine.cards import UnsupportedCard
from expanded import cards
from expanded.generation_cards import pool,discover
from expanded.dark_gift_generators import request,discover as dark_discover
from expanded.pools import GenerationPool
import test_expanded_generation as fixtures


class InternalGenerationTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p=self.g.players[0]
        self.rules={};context=patch.dict(cards.RULES,self.rules)
        context.start();self.addCleanup(context.stop)

    def spell(self,operations,cid='FIX_INTERNAL_GENERATOR'):
        self.g.cards[cid]=dict(id=cid,name=cid,type='SPELL',cardClass='MAGE',cost=4,mechanics=[])
        cards.RULES[cid]=('none',operations)
        return cid

    def install(self,request,ids=('CORE_CS2_188',),owner=0):
        if not hasattr(self.g,'_generation_pools'):self.g._generation_pools={}
        self.g._generation_pools[(request,self.g.players[owner].hero_class)]=GenerationPool('controlled internal generation',tuple(ids),'Fixture; not production approval')

    def cast(self,cid,owner=0):self.fx.run_ops(self.g,[('cast_fixed_spell',cid,'random')],owner=owner)

    def test_plain_discover_is_automatically_selected_without_paid_play(self):
        req=pool(card_type='MINION');self.install(req)
        cid=self.spell([discover(req)]);self.assertTrue(self.g._supports_internal_spell(cid,0))
        mana=self.p.mana;self.cast(cid)
        self.assertIsNone(self.g.pending_choice);self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_188'])
        self.assertEqual(self.p.discoveries_total,1);self.assertEqual(self.p.cards_played,0)
        self.assertEqual(self.p.mana,mana);self.assertEqual(self.p.spells_turn,[])

    def test_two_discovers_resume_after_each_automatic_choice(self):
        req=pool(card_type='MINION');self.install(req);self.cast(self.spell([discover(req),discover(req)]))
        self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.hand),2)
        self.assertEqual(self.p.discoveries_total,2)

    def test_off_turn_owner_receives_own_card_and_discover_credit(self):
        req=pool(card_type='MINION');self.install(req,owner=1)
        self.cast(self.spell([discover(req)]),owner=1)
        self.assertEqual(self.p.hand,[]);self.assertEqual(self.p.discoveries_total,0)
        self.assertEqual([c.card_id for c in self.g.players[1].hand],['CORE_CS2_188'])
        self.assertEqual(self.g.players[1].discoveries_total,1)

    def test_choicegen_discover_uses_same_automatic_owner(self):
        req=pool(card_type='MINION');self.install(req)
        self.cast(self.spell([('choicegen_discover',req,'plain',())]))
        self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.hand),1)
        self.assertEqual(self.p.discoveries_total,1)

    def test_choicegen_destination_child_retains_automatic_policy(self):
        req=pool(card_type='MINION');self.install(req)
        self.cast(self.spell([('choicegen_discover',req,'destination',())]))
        self.assertIsNone(self.g.pending_choice)
        self.assertEqual(self.p.discoveries_total,1)
        events=[e for e in self.g.events if e['event']=='automatic_choice']
        self.assertEqual([e['kind'] for e in events],['choicegen_discover','choicegen_destination'])

    def test_dark_gift_discover_is_automatic_and_keeps_enchantment(self):
        req=request(minimum=1,maximum=1);self.install(req.alternatives[0])
        self.cast(self.spell([dark_discover(req)]))
        self.assertIsNone(self.g.pending_choice);self.assertEqual(len(self.p.hand)+len(self.p.deck),13)
        generated=[c for c in self.p.hand+self.p.deck if getattr(c,'rule_state',{}).get('dark_gifts')]
        self.assertEqual(len(generated),1);self.assertEqual(self.p.discoveries_total,1)

    @patch('expanded.generation_families.reviewed_contract',return_value=None)
    @patch('expanded.generation_catalog.standard_contract',return_value=None)
    def test_missing_pool_does_not_become_supported_only_fallback(self,*contracts):
        req=pool(card_type='MINION');cid=self.spell([discover(req)]);before=self.g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.cast(cid)
        self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(self.p.hand,[])

    def test_unsupported_pool_member_rejected_before_rng(self):
        req=pool(card_type='MINION');self.install(req,('CORE_CS2_188','UNKNOWN'))
        cid=self.spell([discover(req)]);before=self.g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.cast(cid)
        self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(self.p.hand,[])

    def test_unknown_nested_operation_is_not_admitted(self):
        for operation in [('generation_attach',('UNKNOWN',)),('generation_if_holding','DRAGON',('UNKNOWN',)),('generation_mana_branch',10,('draw',1),('UNKNOWN',))]:
            self.assertFalse(self.g._supports_internal_operations([operation]))
        self.assertFalse(self.g._supports_internal_operations([None]))
        self.assertFalse(self.g._supports_internal_operations([()]))

    def test_known_nested_operation_is_admitted(self):
        req=pool(card_type='MINION')
        self.assertTrue(self.g._supports_internal_operations([('generation_attach',('generate_random',req,1,'board',()))]))
        self.assertTrue(self.g._supports_internal_operations([('generation_mana_branch',10,('draw',1),discover(req))]))

    def test_unknown_choose_one_branch_is_rejected_without_sampling(self):
        cid=self.spell([('draw',1)])
        branches=[('valid','none',[('draw',1)]),('missing','none',[('UNKNOWN',)])]
        with patch.dict(cards.CHOICES,{cid:branches}):
            self.assertFalse(self.g._supports_internal_spell(cid,0));state=self.g.rng.getstate()
            with self.assertRaises(UnsupportedCard):self.cast(cid)
            self.assertEqual(self.g.rng.getstate(),state);self.assertEqual(self.p.hand,[])
