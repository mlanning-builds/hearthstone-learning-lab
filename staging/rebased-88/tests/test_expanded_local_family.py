"""Bounded-zone and Cannoneer integration scenarios."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card

class LocalFamilyTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*25;p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def put(self,g,cid,owner=0):
        c=Card(g._new_id(),cid);g.players[owner].hand.append(c);return c
    def play_card(self,g,c,target=None,choice=None):
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target) and (choice is None or a.choices==(choice,))]
        self.assertTrue(actions,(c.card_id,target,choice));first=actions[0];g.step(max((a for a in actions if a.target==first.target and a.choices==first.choices),key=lambda a:a.position));return c
    def play(self,g,cid,target=None,choice=None):return self.play_card(g,self.put(g,cid,g.current),target,choice)
    def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
    def cycle(self,g):g.step(Action('end'));g.step(Action('end'))
    def kill(self,g,m):m.health=0;g._settle(allow_event_choices=True)
    def attack(self,g,m,target):
        m.summoned_turn=g.turn-1
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==target))
    def test_land_ho_draws_and_summons(self):
        g=self.game();self.play(g,'CAP_102')
        self.assertEqual(len(g.players[0].hand),2)
        self.assertEqual([m.card_id for m in g.players[0].minions],['CAP_107t']*2)
    def test_land_ho_board_limit(self):
        g=self.game()
        for _ in range(6):g._summon(0,'EDR_851t')
        self.play(g,'CAP_102');self.assertEqual(len(g.players[0].minions),7);self.assertEqual(len(g.players[0].hand),2)
    def test_cannonmaster_gets_playable_token(self):
        g=self.game();self.play(g,'CAP_107');c=g.players[0].hand[0]
        self.assertEqual(c.card_id,'CAP_107t');self.play_card(g,c);g.step(Action('end'));self.assertEqual(g.players[1].health,29)
    def test_cannon_end_owner_only(self):
        g=self.game();g._summon(1,'CAP_107t');g.step(Action('end'));self.assertEqual(g.players[0].health,30)
        g.step(Action('end'));self.assertEqual(g.players[0].health,29)
    def test_crowley_two_cannons_extra_shots(self):
        g=self.game();self.play(g,'CAP_106');g.step(Action('end'));self.assertEqual(g.players[1].health,26)
    def test_crowley_stacks(self):
        g=self.game();g._summon(0,'CAP_106');g._summon(0,'CAP_106');g._summon(0,'CAP_107t')
        g.step(Action('end'));self.assertEqual(g.players[1].health,27)
    def test_silenced_crowley_no_bonus(self):
        g=self.game();m=g._summon(0,'CAP_106');g._silence(m);g._summon(0,'CAP_107t')
        g.step(Action('end'));self.assertEqual(g.players[1].health,29)
    def test_silenced_cannon_no_fire(self):
        g=self.game();g._silence(g._summon(0,'CAP_107t'));g.step(Action('end'));self.assertEqual(g.players[1].health,30)
    def test_hand_cannon_last_durability(self):
        g=self.game();g._summon(0,'CAP_107t');self.play(g,'CAP_103');g.players[0].weapon['durability']=1
        g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.target==g.hero_id(1)))
        self.assertIsNone(g.players[0].weapon);self.assertEqual(g.players[1].health,26)
    def test_hand_cannon_fires_only_friendly(self):
        g=self.game();g._summon(0,'CAP_107t');g._summon(1,'CAP_107t');self.play(g,'CAP_103')
        with patch.object(g.rng,'choice',side_effect=lambda xs:xs[0]):
            g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.target==g.hero_id(1)))
        self.assertEqual(g.players[0].health,30);self.assertEqual(g.players[1].health,26)
    def test_cannon_lifesteal(self):
        g=self.game();g.players[0].health=20;g._summon(0,'CAP_107t').keywords.add('LIFESTEAL')
        g.step(Action('end'));self.assertEqual(g.players[0].health,21)
    def test_frame_job_kills_before_private_choice(self):
        g=self.game();g._summon(1,'EDR_851t');g._summon(1,'EDR_851t')
        g.players[1].deck=['CATA_551t','CORE_CS2_029','EDR_851t'];self.play(g,'CAP_403')
        self.assertFalse(g.players[1].minions)
        self.assertEqual({o['card_id'] for o in g.pending_choice['options']},{'CATA_551t','EDR_851t'})
        self.assertNotIn('CATA_551t',str(g.observe(1,False)))
        selected=g.pending_choice['options'][0]['card_id'];self.choose(g);self.assertEqual(g._card_data(g.players[1].deck[-1])['id'],selected)
    def test_frame_job_keeps_physical_deck_modifiers(self):
        g=self.game();c=Card(g._new_id(),'EDR_851t',attack_bonus=4);g.players[1].deck=[c,'CORE_CS2_029']
        self.play(g,'CAP_403');self.choose(g);self.assertIs(g.players[1].deck[-1],c);self.assertEqual(c.attack_bonus,4)
    def test_frame_job_no_minions_no_choice(self):
        g=self.game();self.play(g,'CAP_403');self.assertIsNone(g.pending_choice)
    def test_blaze_survives_spawns_base_copy(self):
        g=self.game();m=g._summon(0,'CATA_586');g._damage(m.uid,1);g._settle()
        self.assertEqual([(v.attack,v.health) for v in g.players[0].minions],[(3,2),(3,3)])
    def test_blaze_fatal_does_not_spawn(self):
        g=self.game();m=g._summon(0,'CATA_586');self.kill(g,m)
        self.assertFalse(g.players[0].minions);self.assertEqual(g.players[1].health,28)
    def test_blaze_shield_does_not_spawn(self):
        g=self.game();m=g._summon(0,'CATA_586');m.keywords.add('DIVINE_SHIELD');g._damage(m.uid,1);g._settle()
        self.assertEqual(len(g.players[0].minions),1)
    def test_blaze_silenced_no_effects(self):
        g=self.game();m=g._summon(0,'CATA_586');g._silence(m);g._damage(m.uid,1);g._settle();self.kill(g,m)
        self.assertFalse(g.players[0].minions);self.assertEqual(g.players[1].health,30)
    def test_grove_spell_payload(self):
        g=self.game();g._summon(0,'EDR_271');self.play(g,'TIME_702',g.hero_id(1))
        treant=g.players[0].minions[-1];self.assertEqual(treant.card_id,'EDR_271t');self.kill(g,treant)
        self.assertEqual([c.card_id for c in g.players[0].hand],['TIME_702'])
    def test_grove_non_nature_no_treant(self):
        g=self.game();g._summon(0,'EDR_271');self.play(g,'TOKEN_COIN');self.assertEqual(len(g.players[0].minions),1)
    def test_grove_copied_payload_and_silence(self):
        g=self.game();g._summon(0,'EDR_271');self.play(g,'TIME_702',g.hero_id(1));m=g.players[0].minions[-1]
        copied=g._summon(0,m.card_id,copy_from=m);g._silence(m);self.kill(g,m);self.assertFalse(g.players[0].hand)
        self.kill(g,copied);self.assertEqual(g.players[0].hand[-1].card_id,'TIME_702')
    def test_grove_full_board_no_phantom_reward(self):
        g=self.game();g._summon(0,'EDR_271')
        for _ in range(6):g._summon(0,'EDR_851t')
        self.play(g,'TIME_702',g.hero_id(1));self.assertEqual(len(g.players[0].minions),7);self.assertFalse(g.players[0].hand)
    def test_resurrect_only_own_dead_dragons(self):
        g=self.game();g.players[0].death_history=['EDR_851t','CATA_551t','CATA_551t'];g.players[1].death_history=['CATA_553t']
        self.play(g,'EDR_455');self.assertEqual([o['card_id'] for o in g.pending_choice['options']],['CATA_551t'])
        self.choose(g);self.assertEqual(g.players[0].minions[0].health,6)
    def test_resurrect_empty_no_choice(self):
        g=self.game();self.play(g,'EDR_455');self.assertIsNone(g.pending_choice)
    def test_resurrect_full_board_consumes_spell(self):
        g=self.game();g.players[0].death_history=['CATA_551t']
        for _ in range(7):g._summon(0,'EDR_851t')
        self.play(g,'EDR_455');self.choose(g);self.assertEqual(len(g.players[0].minions),7);self.assertFalse(g.players[0].hand)
    def test_ancient_eats_stats_and_returns_fresh_card(self):
        g=self.game();c=Card(g._new_id(),'EDR_851t',attack_bonus=2,health_bonus=3);g.players[0].deck=[c]
        m=g._summon(0,'EDR_494');g.step(Action('end'));self.assertFalse(g.players[0].deck);self.assertEqual((m.attack,m.health),(9,11))
        self.kill(g,m);self.assertEqual(g.players[0].hand[0].card_id,'EDR_851t');self.assertEqual(g.players[0].hand[0].attack_bonus,0)
    def test_ancient_no_minion_does_not_fatigue(self):
        g=self.game();m=g._summon(0,'EDR_494');g.players[0].deck=[];g.step(Action('end'))
        self.assertEqual(g.players[0].health,30);self.assertEqual((m.attack,m.health),(6,7))
    def test_ancient_silence_removes_remembered_rewards(self):
        g=self.game();m=g._summon(0,'EDR_494');g.players[0].deck=['EDR_851t'];g.step(Action('end'));g._silence(m);self.kill(g,m)
        self.assertFalse(g.players[0].hand)
    def test_hellraiser_empty_buff(self):
        g=self.game();g.players[0].deck=[];self.play(g,'JAIL_734');m=g.players[0].minions[0]
        self.assertEqual((m.attack,m.health),(6,6));self.assertIn('TAUNT',m.keywords)
    def test_hellraiser_choice_moves_physical_card(self):
        g=self.game();c=Card(g._new_id(),'EDR_851t',health_bonus=3);g.players[0].deck=[c];self.play(g,'JAIL_734');self.choose(g)
        self.assertIs(g.players[0].hand[0],c);self.assertFalse(g.players[0].deck);self.assertEqual(g.players[0].minions[0].health,2)
    def test_hooktail_chest_rewards_opponent_of_chest(self):
        g=self.game();self.play(g,'TIME_713');chest=g.players[1].minions[0]
        self.assertEqual((chest.attack,chest.health),(0,8));self.kill(g,chest)
        self.assertEqual([c.card_id for c in g.players[0].hand],['GAME_005']*10);self.assertFalse(g.players[1].hand)
    def test_chest_full_hand_keeps_existing_cards(self):
        g=self.game();held=[self.put(g,'EDR_851t') for _ in range(10)];chest=g._summon(1,'TIME_713t');self.kill(g,chest)
        self.assertEqual(g.players[0].hand,held)
    def test_chest_silence_no_coins(self):
        g=self.game();chest=g._summon(1,'TIME_713t');g._silence(chest);self.kill(g,chest);self.assertFalse(g.players[0].hand)
    def test_gladiatorial_recruits_without_battlecry(self):
        g=self.game();g.players[0].deck=['CAP_107'];self.play(g,'TIME_870')
        self.assertEqual(g.players[0].minions[0].card_id,'CAP_107');self.assertFalse(g.players[0].hand)
        tiger=g.players[1].minions[0];self.assertEqual((tiger.attack,tiger.health),(5,5));self.assertIn('STEALTH',tiger.keywords)
    def test_gladiatorial_full_friendly_board_still_enemy_tiger(self):
        g=self.game();g.players[0].deck=['CAP_107']
        for _ in range(7):g._summon(0,'EDR_851t')
        self.play(g,'TIME_870');self.assertEqual(g.players[0].deck,['CAP_107']);self.assertEqual(g.players[1].minions[0].card_id,'TIME_870t')
    def test_frame_job_invalid_choice_rolls_no_state(self):
        g=self.game();g.players[1].deck=['EDR_851t'];self.play(g,'CAP_403');before=g.observe(0,False);rng=g.rng.getstate()
        with self.assertRaises(ValueError):self.choose(g,5)
        self.assertEqual(g.observe(0,False),before);self.assertEqual(g.rng.getstate(),rng)
    def test_cannon_does_not_retarget_dying_minion(self):
        g=self.game();g._summon(0,'CAP_106');g._summon(0,'CAP_107t');g._summon(1,'EDR_851t');self.play(g,'CAP_103')
        with patch.object(g.rng,'choice',side_effect=lambda xs:xs[-1]):
            g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.target==g.hero_id(1)))
        self.assertFalse(g.players[1].minions);self.assertEqual(g.players[1].health,26)
    def test_dead_crowley_does_not_add_shot(self):
        g=self.game();crowley=g._summon(0,'CAP_106');g._summon(0,'CAP_107t');self.kill(g,crowley)
        g.step(Action('end'));self.assertEqual(g.players[1].health,29)
    def test_blaze_full_board_does_not_overfill(self):
        g=self.game();m=g._summon(0,'CATA_586')
        for _ in range(6):g._summon(0,'EDR_851t')
        g._damage(m.uid,1);g._settle();self.assertEqual(len(g.players[0].minions),7)
    def test_blaze_aoe_snapshots_original_listeners(self):
        g=self.game();g._summon(0,'CATA_586');g._summon(0,'CATA_586')
        with g._damage_batch():
            for m in list(g.players[0].minions):g._damage(m.uid,1)
        g._settle();self.assertEqual(sorted(m.health for m in g.players[0].minions),[2,2,3,3])
    def test_ancient_repeated_meals_and_copy(self):
        g=self.game();m=g._summon(0,'EDR_494');g.players[0].deck=['EDR_851t','EDR_851t']
        g.step(Action('end'));g.step(Action('end'));g.players[0].deck=['EDR_851t'];g.step(Action('end'))
        copied=g._summon(0,m.card_id,copy_from=m);g.players[0].hand=[];self.kill(g,copied)
        self.assertEqual([c.card_id for c in g.players[0].hand],['EDR_851t']*2)
    def test_grove_rewards_distinct_spells(self):
        g=self.game();g._summon(0,'EDR_271');self.play(g,'TIME_702',g.hero_id(1));self.play(g,'CORE_EX1_169')
        trees=[m for m in g.players[0].minions if m.card_id=='EDR_271t']
        self.assertEqual(len(trees),2)
        for m in trees:self.kill(g,m)
        self.assertEqual([c.card_id for c in g.players[0].hand][-2:],['TIME_702','CORE_EX1_169'])
    def test_gladiatorial_empty_deck_still_tiger(self):
        g=self.game();g.players[0].deck=[];self.play(g,'TIME_870')
        self.assertFalse(g.players[0].minions);self.assertEqual(g.players[1].minions[0].card_id,'TIME_870t')
    def test_gladiatorial_enemy_full_board(self):
        g=self.game();g.players[0].deck=['EDR_851t']
        for _ in range(7):g._summon(1,'EDR_851t')
        self.play(g,'TIME_870');self.assertEqual(len(g.players[1].minions),7);self.assertEqual(g.players[0].minions[0].card_id,'EDR_851t')
    def test_choice_suspension_copies_and_replays(self):
        g=self.game();g.players[1].deck=['CATA_551t','EDR_851t'];self.play(g,'CAP_403');copied=deepcopy(g)
        self.choose(g);self.choose(copied);self.assertEqual(g.observe(0),copied.observe(0));self.assertEqual(g.rng.getstate(),copied.rng.getstate())
    def test_chest_coins_are_playable(self):
        g=self.game();self.kill(g,g._summon(1,'TIME_713t'));c=g.players[0].hand[0];g.players[0].mana=0
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(g.players[0].mana,1)
