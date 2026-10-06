"""Physical recruits followed by one friendly combat, through shared checkpoints."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.cards import TRIGGERS

class HerennTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEATHKNIGHT',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10
    def card(self,cid,attack=0,health=0):
        c=Card(self.g._new_id(),cid,attack_bonus=attack,health_bonus=health)
        return c
    def play(self):
        c=self.g._add(0,'TLC_810')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def pair(self,cid='CORE_LOOT_413'):
        self.p.deck=[self.card(cid),self.card(cid)]
    def recruits(self):return [m for m in self.p.minions if m.card_id!='TLC_810']

    def test_two_recruits_fight_each_other_once(self):
        self.pair();self.play();ms=self.recruits()
        self.assertEqual(len(ms),2);self.assertEqual([m.health for m in ms],[1,1])
        self.assertEqual(self.p.friendly_attacks,1);self.assertEqual(self.p.deck,[])
        self.assertEqual((self.p.health,self.q.health),(30,30))
        self.assertTrue(all(m.attacks==0 for m in ms))

    def test_eligible_cards_only_and_unselected_identity_preserved(self):
        self.pair();other=self.card('CORE_EX1_506');spell=self.card('CORE_CS2_029')
        self.p.deck.extend([other,spell]);self.play()
        self.assertEqual(self.p.deck,[other,spell]);self.assertEqual(len(self.recruits()),2)

    def test_empty_deck_has_no_fight_or_fatigue(self):
        self.play();self.assertEqual(self.recruits(),[]);self.assertEqual(self.p.fatigue,0)
        self.assertEqual(self.p.friendly_attacks,0)

    def test_one_match_is_summoned_without_fighting_existing_minion(self):
        old=self.g._summon(0,'CORE_EX1_110')
        self.p.deck=[self.card('CORE_LOOT_413')];self.play()
        self.assertEqual(old.health,5);self.assertEqual(self.p.friendly_attacks,0)
        self.assertEqual(self.recruits()[-1].health,3)

    def test_one_free_slot_recruits_only_one_card(self):
        for _ in range(5):self.g._summon(0,'EDR_851t')
        self.pair();self.play();self.assertEqual(len(self.p.board),7)
        self.assertEqual(len(self.p.deck),1);self.assertEqual(self.p.friendly_attacks,0)

    def test_full_board_after_herenn_does_not_consume_cards_or_rng(self):
        for _ in range(6):self.g._summon(0,'EDR_851t')
        self.pair();before=self.g.rng.getstate();self.play()
        self.assertEqual(len(self.p.deck),2);self.assertEqual(self.g.rng.getstate(),before)

    def test_recruits_preserve_deck_buffs_and_physical_origin(self):
        self.p.deck=[self.card('CORE_LOOT_413',health=4),self.card('CORE_LOOT_413',health=4)]
        for c in self.p.deck:c._starting_owner=0;c._starting_identity=self.g.cards[c.card_id]['dbfId']
        self.play();ms=self.recruits()
        self.assertEqual([m.health for m in ms],[5,5])
        self.g._bounce(ms[0]);self.assertTrue(self.g._started_in_deck(self.p.hand[0],0))

    def test_recruit_does_not_execute_battlecry_or_draw(self):
        self.p.deck=[self.card('RLK_708',health=4),self.card('RLK_708',health=4)]
        self.play();self.assertEqual(self.p.hand,[]);self.assertEqual(self.p.fatigue,0)
        self.assertEqual([m.health for m in self.recruits()],[4,4])

    def test_combat_deaths_resolve_both_deathrattles(self):
        self.pair('CORE_SW_068');self.play()
        self.assertEqual(self.recruits(),[]);self.assertEqual(self.p.armor,16)
        self.assertEqual(self.p.corpses,2)

    def test_deathrattle_draws_are_ordinary_draws(self):
        self.pair('CORE_EX1_096');self.play()
        self.assertEqual(self.recruits(),[]);self.assertEqual(self.p.fatigue,2)
        self.assertEqual(self.p.health,27)

    def test_first_recruit_lost_before_second_does_not_retarget_fight(self):
        self.g._summon(1,'EDR_815');self.q.corpses=4;self.pair()
        self.play();self.assertEqual(self.p.friendly_attacks,0)
        self.assertEqual(self.recruits(),[]);self.assertEqual(self.p.armor,6)

    def test_summon_choices_finish_before_fight(self):
        self.g._summon(0,'CORE_EX1_509');self.pair('CORE_SW_068')
        rule=(('summon','friendly','DEMON'),[('choose_fixed_summon',('EDR_851t',))])
        with patch.dict(TRIGGERS,{'CORE_EX1_509':rule}):
            self.play();self.assertEqual(len(self.p.deck),1);self.assertEqual(self.p.friendly_attacks,0)
            self.g.step(Action('choose',choices=(0,)))
            self.assertEqual(self.p.deck,[]);self.assertEqual(self.p.friendly_attacks,0)
            self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.p.friendly_attacks,1);self.assertEqual(self.p.armor,16)
        self.assertIsNone(self.g.pending_frame)

    def test_failed_combat_rolls_back_recruitment_and_rng(self):
        self.pair();c=self.g._add(0,'TLC_810');before=copy.deepcopy(self.g.__dict__)
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        with patch.object(Game,'_force_attack',side_effect=UnsupportedCard('injected combat failure')):
            with self.assertRaises(UnsupportedCard):self.g.step(action)
        self.assertEqual(self.g.players,before['players']);self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())
        self.assertIsNone(self.g.pending_frame)

    def test_bonus_applies_before_recruits_fight(self):
        self.p.murloc_summon_bonus=1;self.pair('TLC_240');self.play()
        # Both 7/4 Tyrannogills die and leave their three Murloc tokens each.
        tokens=[m for m in self.recruits() if m.card_id.startswith('TLC_240t')]
        self.assertEqual(len(tokens),6)
        self.assertTrue(all((m.attack,m.max_health)==(3,2) for m in tokens))
