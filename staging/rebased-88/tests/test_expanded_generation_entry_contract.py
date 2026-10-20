"""Creation modifiers are visible at entry and survive repeated summons."""
import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Game
from engine.game import Card
from engine.cards import UnsupportedCard

class GenerationEntryContractTests(unittest.TestCase):
    def setUp(self):
        self.g=fixtures.GenerationTests().game()
        self.ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)

    def test_stats_keywords_and_freeze_exist_at_summon_notification(self):
        seen=[]
        original=Game._capture_summon_event
        def capture(game,minion,origin):
            seen.append((minion.attack,minion.max_health,minion.health,
                         'TAUNT' in minion.keywords,minion.frozen_until>=0))
            return original(game,minion,origin)
        self.g.players[0].crystal_core=True
        with patch.object(Game,'_capture_summon_event',capture):
            self.g._generation_place('EDR_851t','board',
                (('stats',(2,3)),('keyword','TAUNT'),('freeze',True)),self.ctx)
        self.assertEqual(seen,[(2,3,3,True,True)])

    def test_every_repeated_summon_receives_creation_modifiers(self):
        with patch.object(Game,'_card_summon_repetitions',return_value=2):
            self.g._generation_place('EDR_851t','board',
                (('stats',(10,10)),('keyword','TAUNT'),('freeze',True)),self.ctx)
        minions=self.g.players[0].minions
        self.assertEqual(len(minions),2)
        self.assertTrue(all((m.attack,m.max_health,m.health)==(10,10,10)
                            and 'TAUNT' in m.keywords and m.frozen_until>=0 for m in minions))
        self.assertNotEqual(minions[0].uid,minions[1].uid)

    def test_fixed_cost_overrides_dynamic_base_cost(self):
        self.g.cards['FIXTURE_DYNAMIC']=dict(id='FIXTURE_DYNAMIC',name='fixture',
            type='MINION',cost=8,attack=1,health=1,cardClass='MAGE',races=['DRAGON'])
        with patch.object(Game,'_active',side_effect=lambda cid,owner:cid=='EDR_844'):
            result=self.g._generation_place('FIXTURE_DYNAMIC','hand',(('set_cost',3),),self.ctx)
            self.assertEqual(self.g._cost(result,0),3)
        self.assertEqual(result.set_cost,3)
        self.assertEqual(result.cost_delta,0)

    def test_invalid_entry_stats_do_not_create_body(self):
        before=self.g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'entry stats'):
            self.g._generation_place('EDR_851t','board',(('stats',(2,0)),),self.ctx)
        self.assertEqual(self.g.rng.getstate(),before)
        self.assertFalse(self.g.players[0].board)
