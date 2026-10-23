"""Scripted rule checks only; no policies, games, evaluations or learning."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from hearthstone_sim.neural.runner import prepare
prepare()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'staging/rebased-88/tests'))
from test_expanded_generation import GenerationTests
from engine.game import Card
from engine.cards import UnsupportedCard


class RarityRepairTests(unittest.TestCase):
    def game(self):
        g=GenerationTests().game()
        for p in g.players:p.hand=[];p.deck=[];p.mana=10
        return g

    def destroy(self,g,cid):
        card=Card(g._new_id(),cid);g.players[g.current].deck=[card]
        g._choicegen_effect(('choicegen_destroy_top_rarity',),dict(owner=g.current,source=None,target=0))
        return card

    def test_retiring_reviewed_signature_preserves_excess_and_totals(self):
        from tools.long_training_campaign import retire_reviewed_rarity_failures
        safety=dict(attempted=12724,failed=32,signatures={'UnsupportedCard:_choicegen_effect':8,'unrelated':4})
        retire_reviewed_rarity_failures(safety)
        self.assertEqual(safety,dict(attempted=12724,failed=32,signatures={'UnsupportedCard:_choicegen_effect':2,'unrelated':4}))
        safety['signatures']['UnsupportedCard:_choicegen_effect']=6
        retire_reviewed_rarity_failures(safety)
        self.assertEqual(safety['signatures'],{'unrelated':4})

    def test_unrated_token_destroys_without_substituting_common_pool(self):
        g=self.game()
        self.assertFalse(g.cards['TOKEN_COIN'].get('rarity'))
        self.destroy(g,'TOKEN_COIN')
        self.assertFalse(g.players[g.current].deck)
        self.assertIsNone(g.pending_choice)

    def test_existing_legendary_rarity_remains_exact(self):
        g=self.game();self.destroy(g,'CORE_EX1_100')
        self.assertFalse(g.players[g.current].deck)
        self.assertTrue(g.pending_choice['options'])
        self.assertTrue(all(g.cards[o['card_id']]['rarity']=='LEGENDARY' for o in g.pending_choice['options']))

    def test_missing_collectible_metadata_still_fails_before_destruction(self):
        g=self.game();cid='CORE_EX1_100';broken=dict(g.cards[cid]);broken.pop('rarity')
        with patch.dict(g.cards,{cid:broken}):
            with self.assertRaisesRegex(UnsupportedCard,'Collectible destroyed top card'):
                self.destroy(g,cid)
        self.assertEqual(len(g.players[g.current].deck),1)


if __name__=='__main__':unittest.main()
