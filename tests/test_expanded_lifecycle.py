"""User-run checks for cards moved onto the common play lifecycle."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import RULES, DEATH_EFFECTS
from engine.game import Game as LegacyGame
from engine.cards import UnsupportedCard


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEATHKNIGHT',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.q.hand=[]
        self.p.mana=self.p.max_mana=10

    def give(self,cid):
        card=Card(self.g._new_id(),cid);self.p.hand.append(card);return card

    def play(self,card,target=0,position=None):
        if position is None:
            position=len(self.p.board) if self.g.cards[card.card_id]['type']=='MINION' else -1
        self.g.step(Action('play',card.uid,target,position))

    def test_old_cards_do_not_delegate_to_old_play_method(self):
        with patch.object(LegacyGame,'_play',side_effect=AssertionError('Old play path called')):
            self.play(self.give('CORE_CS2_189'),-2)
            self.play(self.give('RLK_503'))
            self.play(self.give('RLK_067'))
        self.assertEqual(self.q.health,29)
        self.assertEqual(self.p.corpses,1)
        self.assertEqual(self.p.weapon['card_id'],'RLK_067')
        self.assertEqual(self.p.cards_played,3)

    def test_old_minion_consumes_discount_once_and_logs_once(self):
        card=self.give('CORE_UNG_084');card.cost_delta=-1
        self.p.cost_effects=[dict(selector='MINION',amount=2,expires=None)]
        self.play(card,-2)
        self.assertEqual(self.p.mana,9)
        self.assertEqual(self.q.health,27)
        self.assertEqual(self.p.cost_effects,[])
        self.assertEqual(self.p.cards_played,1)
        plays=[e for e in self.g.events if e['event']=='play' and e.get('card')==card.card_id]
        self.assertEqual(len(plays),1)

    def test_copy_battlecry_preserves_hand_buffs(self):
        card=self.give('CORE_RLK_062');card.attack_bonus=2;card.health_bonus=3
        self.play(card)
        base=self.g.cards[card.card_id]
        self.assertEqual(len(self.p.board),3)
        for m in self.p.board:
            self.assertEqual((m.attack,m.health,m.max_health),
                             (base['attack']+2,base['health']+3,base['health']+3))
        self.assertEqual(self.p.cards_played,1)

    def test_corpse_volley_uses_available_corpses(self):
        self.p.corpses=3
        self.play(self.give('CORE_RLK_505'))
        self.assertEqual(self.p.corpses,0)
        self.assertEqual(self.q.health,24)
        self.assertEqual(self.p.cards_played,1)

    def test_tidehunter_summons_immediately_to_its_right(self):
        existing=self.g._summon(0,'Core_CS2_200')
        self.play(self.give('CORE_EX1_506'),position=0)
        self.assertEqual([m.card_id for m in self.p.board],
                         ['CORE_EX1_506','TOKEN_SCOUT',existing.card_id])

    def test_lifedrinker_heals_before_lethal_checkpoint(self):
        self.p.health=10;self.q.health=2
        self.play(self.give('CORE_GIL_622'))
        self.assertEqual(self.p.health,13)
        self.assertTrue(self.g.terminal)
        self.assertEqual(self.g.winner,0)
        self.assertEqual(self.g.phase,'finished')

    def test_old_weapon_uses_shared_replacement_hooks(self):
        self.g._equip(0,'CS2_082')
        # Synthetic death effect isolates the replacement lifecycle contract.
        with patch.dict(DEATH_EFFECTS,{'CS2_082':[('armor',3)]}):
            self.play(self.give('RLK_067'))
        self.assertEqual(self.p.armor,3)
        self.assertEqual(self.p.weapon['card_id'],'RLK_067')
        broken=[e for e in self.g.events if e['event']=='weapon_broken' and e.get('card')=='CS2_082']
        self.assertEqual(len(broken),1)

    def test_failed_old_card_effect_rolls_back_payment_and_summon(self):
        card=self.give('RLK_503')
        with patch.dict(RULES,{'RLK_503':('none',[('gain_corpses',1),('unknown_opcode',)])}):
            before=self.g.observe(0);rng=self.g.rng.getstate()
            with self.assertRaises(UnsupportedCard):self.play(card)
            self.assertEqual(self.g.observe(0),before)
            self.assertEqual(self.g.rng.getstate(),rng)
            self.assertIsNone(self.g.pending_frame)
