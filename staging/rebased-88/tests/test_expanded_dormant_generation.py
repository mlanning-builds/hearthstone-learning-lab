import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded import dormant_generation as dg
from engine.cards import UnsupportedCard

class DormantGenerationTests(unittest.TestCase):
    def setUp(self):
        self.helper=fixtures.GenerationTests();self.g=self.helper.game()
    def generate(self,**mods):
        return self.g._generation_place('CS3_025','board',tuple(mods.items()),dict(owner=0))
    def test_staged_declaration_requires_pool(self):
        self.assertNotIn('TIME_058',cards.COLLECTIBLE_IDS)
        with self.assertRaises(UnsupportedCard):self.helper.run_ops(self.g,dg.DEATH_EFFECTS['TIME_058'])
    def test_inactive_before_summon_event(self):
        seen=[]
        with patch.object(self.g,'_capture_summon_event',side_effect=lambda m,origin:seen.append(m.dormant)):
            m=self.generate(dormant_turns=2)
        self.assertEqual(seen,[2]);self.assertNotIn(m,self.g.players[0].minions)
    def test_inactive_before_first_aura_refresh(self):
        seen=[];original=self.g._refresh_auras
        def refresh():
            seen.extend(m.dormant for m in self.g.players[0].all_minions);return original()
        with patch.object(self.g,'_refresh_auras',side_effect=refresh):self.generate(dormant_turns=2)
        self.assertTrue(seen);self.assertTrue(all(n==2 for n in seen))
    def test_two_owner_turns(self):
        m=self.generate(dormant_turns=2)
        self.g.step(Action('end'));self.assertEqual(m.dormant,2)
        self.g.step(Action('end'));self.assertEqual(m.dormant,1)
        self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual(m.dormant,0)
    def test_invalid_duration_does_not_create_entity(self):
        for duration in (0,-1,True,1.5,'2'):
            with self.assertRaises(UnsupportedCard):self.generate(dormant_turns=duration)
        self.assertFalse(self.g.players[0].board)
    def test_hand_destination_rejected(self):
        with self.assertRaises(UnsupportedCard):self.g._generation_place('CS3_025','hand',(('dormant_turns',2),),dict(owner=0))
        self.assertFalse(self.g.players[0].hand)
    def test_full_board_remains_full(self):
        for _ in range(7):self.generate(dormant_turns=2)
        self.assertIsNone(self.generate(dormant_turns=2));self.assertEqual(len(self.g.players[0].board),7)
    def test_existing_normal_summon_stays_active(self):
        self.assertEqual(self.generate().dormant,0)
    def test_flutterwing_death_uses_dormant_generation(self):
        import json
        from pathlib import Path
        from copy import deepcopy
        self.g.cards['TIME_058']=next(d for d in json.loads(Path('data/standard/cards.json').read_text()) if d['id']=='TIME_058')
        outcome=deepcopy(self.g.cards['CS3_025']);outcome.update(id='DORMANT_TEST_OUTCOME',cost=2,dbfId=-98001)
        self.g.cards[outcome['id']]=outcome
        self.helper.install(self.g,dg.TWO,[outcome['id']])
        with patch.dict(cards.DEATH_EFFECTS,dg.DEATH_EFFECTS):
            source=self.g._summon(0,'TIME_058');self.g._damage(source.uid,99);self.g._settle(allow_event_choices=True)
        board=self.g.players[0].all_minions
        self.assertEqual(len(board),1);self.assertEqual(board[0].card_id,outcome['id']);self.assertEqual(board[0].dormant,2)
