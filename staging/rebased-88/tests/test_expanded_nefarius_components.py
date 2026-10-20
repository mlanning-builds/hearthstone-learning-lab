"""Standalone bodies required by the observed Nefarius component pool."""
import unittest
import test_expanded_choice_continuation as fixtures
from engine.game import Card
from expanded import Action


class NefariusComponentTests(unittest.TestCase):
    def setUp(self):
        self.game=fixtures.ChoiceContinuationTests().game()
        self.player=self.game.players[0]
        self.player.mana=10

    def play(self,cid):
        card=self.game._enter_hand(0,Card(self.game._new_id(),cid))
        action=next(a for a in self.game.legal_actions() if a.kind=='play' and a.source==card.uid)
        self.game.step(action)
        return self.player.minions[-1]

    def test_one_hit_wonder_rush_without_combo(self):
        minion=self.play('JAM_021')
        self.assertIn('RUSH',self.game._effective_keywords(minion))
        self.assertNotIn('POISONOUS',self.game._effective_keywords(minion))

    def test_one_hit_wonder_combo_grants_poisonous(self):
        self.player.cards_played=1
        self.assertIn('POISONOUS',self.game._effective_keywords(self.play('JAM_021')))

    def test_happy_ghoul_requires_actual_hero_healing_and_resets(self):
        card=Card(self.game._new_id(),'ICC_700')
        self.assertEqual(self.game._cost(card,0),3)
        self.game._heal(self.game.hero_id(0),1,healer=0)
        self.assertEqual(self.game._cost(card,0),3)
        self.player.health-=2
        self.game._heal(self.game.hero_id(0),1,healer=0)
        self.assertEqual(self.game._cost(card,0),0)
        self.game.step(Action('end'))
        self.assertEqual(self.game._cost(card,0),3)

    def test_razorscale_floor_applies_to_both_players_and_set_costs(self):
        scale=self.game._summon(0,'TTN_924')
        for owner in (0,1):
            card=Card(self.game._new_id(),'CORE_CS2_029')
            card.set_cost=0;card.cost_delta=-5
            self.assertEqual(self.game._cost(card,owner),2)
        self.game._silence(scale)
        self.assertEqual(self.game._cost(card,0),0)

    def test_razorscale_floor_survives_removal_of_one_source(self):
        first=self.game._summon(0,'TTN_924')
        second=self.game._summon(1,'TTN_924')
        card=Card(self.game._new_id(),'ICC_700');self.player.hero_healed_turn=True
        first.health=0;self.game._settle()
        self.assertEqual(self.game._cost(card,0),2)
        second.health=0;self.game._settle()
        self.assertEqual(self.game._cost(card,0),0)
