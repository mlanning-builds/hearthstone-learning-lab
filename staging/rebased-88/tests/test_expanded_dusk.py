"""Rogue Quest, reward and physical filtered-draw integration."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.cards import TRIGGERS
from expanded.features import SCHEMA,encode_decision

class DuskTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('ROGUE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10

    def play(self,cid):
        c=self.g._add(0,cid)
        # _add has no return contract; locate the physical copy just added.
        c=self.p.hand[-1]
        a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        self.g.step(a)

    def master(self):self.play('TLC_513t')
    def power(self):self.g.step(Action('power'))
    def card(self,cid,started=False):
        c=Card(self.g._new_id(),cid)
        if started:
            c._starting_owner=0;c._starting_identity=self.g.cards[cid].get('dbfId',cid)
        return c

    def test_quest_counts_events_not_number_of_cards(self):
        self.play('TLC_513')
        self.g._record_deck_insertion(0,0,10,'shuffle')
        self.assertEqual(self.p.quest['progress'],1)
        for _ in range(4):self.g._record_deck_insertion(0,0,1,'shuffle')
        self.assertIsNone(self.p.quest);self.assertEqual([c.card_id for c in self.p.hand],['TLC_513t'])

    def test_trade_enemy_actor_and_enemy_destination_do_not_count(self):
        self.play('TLC_513')
        for dest,actor,kind in ((0,0,'trade'),(0,1,'shuffle'),(1,0,'shuffle')):
            self.g._record_deck_insertion(dest,actor,1,kind)
        self.assertEqual(self.p.quest['progress'],0)

    def test_prior_shuffle_not_retroactive(self):
        self.g._record_deck_insertion(0,0,1,'shuffle');self.play('TLC_513')
        self.assertEqual(self.p.quest['progress'],0)

    def test_actual_multi_card_shuffle_gives_one_progress(self):
        self.play('TLC_513');self.play('TLC_518')
        self.assertEqual(self.p.quest['progress'],1)
        self.assertEqual(len(self.p.deck),3)

    def test_reward_waits_for_hand_space(self):
        self.play('TLC_513')
        for _ in range(10):self.g._add(0,'TOKEN_COIN')
        for _ in range(5):self.g._record_deck_insertion(0,0,1,'shuffle')
        self.assertEqual(self.p.quest['progress'],5);self.assertEqual(len(self.p.hand),10)
        self.assertNotIn('TLC_513t',[c.card_id for c in self.p.hand])
        self.p.hand.pop();self.g._settle()
        self.assertIsNone(self.p.quest);self.assertEqual(self.p.hand[-1].card_id,'TLC_513t')

    def test_hero_stats_power_and_two_stealth_ninjas(self):
        self.p.health=17;self.p.armor=2;self.master()
        self.assertEqual((self.p.health,self.p.armor,self.p.mana),(17,10,7))
        self.assertEqual(self.p.primary_power['card_id'],'TLC_513hp')
        self.assertEqual(len(self.p.minions),2)
        self.assertTrue(all(m.card_id=='TLC_513t2' and 'STEALTH' in m.keywords for m in self.p.minions))
        self.assertTrue(self.p.ninja_returns)

    def test_full_board_still_enables_player_effect(self):
        for _ in range(7):self.g._summon(0,'CORE_EX1_506')
        self.master();self.assertEqual(len(self.p.board),7);self.assertTrue(self.p.ninja_returns)

    def test_power_selects_two_generated_physical_cards_only(self):
        self.master();original=self.card('CORE_CS2_029',True)
        generated=[self.card('CORE_CS2_029'),self.card('CORE_EX1_506')]
        self.p.deck=[original]+generated
        self.power();self.assertEqual(self.p.deck,[original])
        self.assertEqual({c.uid for c in self.p.hand},{c.uid for c in generated})
        self.assertEqual(self.p.mana,6)

    def test_missing_matches_do_not_fatigue(self):
        self.master();self.power()
        self.assertEqual(self.p.fatigue,0);self.assertEqual(self.p.hero_power_uses,1)

    def test_one_match_draws_once(self):
        self.master();self.p.deck=[self.card('CORE_CS2_029')]
        self.power();self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.fatigue,0)

    def test_full_hand_burns_selected_matches(self):
        self.master();self.p.hand=[self.card('TOKEN_COIN') for _ in range(10)]
        self.p.deck=[self.card('CORE_CS2_029'),self.card('CORE_EX1_506')]
        self.power();self.assertEqual(self.p.deck,[]);self.assertEqual(len(self.p.hand),10)

    def test_draw_choice_finishes_before_second_filtered_draw(self):
        self.master();self.g._summon(0,'CORE_EX1_007')
        self.p.deck=[self.card('CORE_CS2_029'),self.card('CORE_EX1_506'),self.card('CORE_CS2_023')]
        with patch.dict(TRIGGERS,{'CORE_EX1_007':('friendly_card_drawn',[('discover_deck',)])}):
            self.power();self.assertEqual(len(self.p.hand),1);self.assertEqual(len(self.p.deck),2)
            self.assertEqual(self.p.hero_power_uses,0)
            self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(len(self.p.hand),3);self.assertEqual(self.p.hero_power_uses,1)
        self.assertIsNone(self.g._power_frame)

    def test_drawn_ninja_summons_and_replacement_draw_resolves(self):
        self.master();self.p.deck=[self.card('CORE_CS2_029',True),self.card('TLC_513t2')]
        self.power();self.assertEqual(len(self.p.minions),3)
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
        self.assertEqual(self.p.fatigue,0)

    def test_ninja_death_returns_clean_card_even_if_silenced(self):
        self.master();m=self.p.minions[0];self.g._buff(m,4,4);self.g._silence(m)
        m.health=0;self.g._settle()
        self.assertEqual(len(self.p.deck),1);c=self.p.deck[0]
        self.assertEqual(c.card_id,'TLC_513t2');self.assertEqual((c.attack_bonus,c.health_bonus),(0,0))
        self.assertFalse(self.g._started_in_deck(c,0))

    def test_existing_ninja_uses_player_effect(self):
        m=self.g._summon(0,'TLC_513t2');self.master();m.health=0;self.g._settle()
        self.assertEqual(len(self.p.deck),1)

    def test_ninja_without_effect_and_enemy_ninja_do_not_return(self):
        m=self.g._summon(0,'TLC_513t2');m.health=0;self.g._settle();self.assertEqual(self.p.deck,[])
        self.master();m=self.g._summon(1,'TLC_513t2');m.health=0;self.g._settle();self.assertEqual(self.q.deck,[])

    def test_player_return_is_not_a_replayable_deathrattle(self):
        self.master();self.assertEqual(self.g._death_operations(self.p.minions[0]),())
        self.p.minions[0].health=0;self.g._settle()
        self.assertEqual(self.p.death_records[-1]['operations'],())

    def test_two_dead_ninjas_return_once_each(self):
        self.master()
        for m in self.p.minions:m.health=0
        self.g._settle();self.assertEqual(len(self.p.deck),2)
        self.assertEqual(self.g._own_shuffle_count(0),2)

    def test_hero_replacement_preserves_player_effect(self):
        self.master();self.g._play_hero_card(0,'CORE_EX1_323')
        self.p.minions[0].health=0;self.g._settle();self.assertEqual(len(self.p.deck),1)

    def test_public_player_effect_and_features(self):
        self.master();view=self.g.observe(0)
        self.assertTrue(view['players'][0]['ninja_returns'])
        self.assertTrue(self.g.observe(1)['players'][0]['ninja_returns'])
        rows=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']))
        self.assertTrue(any('ninja_returns' in str(row) for row in rows))
        self.assertEqual(SCHEMA,'visible-action-features-v58')

    def test_summon_deaths_before_final_battlecry_operation_do_not_return(self):
        self.g._summon(1,'EDR_815');self.q.corpses=4
        self.master()
        self.assertTrue(self.p.ninja_returns)
        self.assertEqual(self.p.deck,[]);self.assertEqual(self.p.minions,[])

    def test_ninja_return_advances_active_shuffle_quest(self):
        self.master();self.play('TLC_513')
        self.p.minions[0].health=0;self.g._settle()
        self.assertEqual(self.p.quest['progress'],1)

    def test_returned_ninja_keeps_on_draw_behavior(self):
        self.master();self.p.minions[0].health=0;self.g._settle()
        self.p.deck.insert(0,self.card('CORE_CS2_029',True))
        self.power();self.assertEqual(len(self.p.minions),2)
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])

    def test_countered_quest_never_becomes_active(self):
        self.q.secrets=[self.card('CORE_EX1_287')]
        self.play('TLC_513');self.assertIsNone(self.p.quest)
        self.g._record_deck_insertion(0,0,10,'shuffle')
        self.assertEqual(self.p.hand,[])
