"""Rule fixtures have explicit outcomes, separate from random-game smoke checks."""
import copy
import json
import random
import unittest
from collections import Counter
from unittest.mock import patch

from lab import random_deck, RUNE_PROFILES
from engine import Game, Action, UnsupportedCard, supported_pool
from engine.cards import SUPPORTED, registry
from engine.game import Card


class GameTests(unittest.TestCase):
    def setUp(self):
        self.pool = supported_pool()
        self.deck = random_deck(self.pool, (1, 1, 1), random.Random(8))
        self.g = Game([self.deck, self.deck], [(1,1,1), (1,1,1)], seed=7)

    def start(self):
        self.g.step(Action('mulligan'))
        self.g.step(Action('mulligan'))
        self.g.players[0].hand = []
        self.g.players[1].hand = []
        self.g.players[0].mana = 10
        self.g.players[0].max_mana = 10
        return self.g.players[0], self.g.players[1]

    def give(self, cid, owner=0):
        c = Card(self.g._new_id(), cid)
        self.g.players[owner].hand.append(c)
        return c

    def play(self, cid, target=0, position=None):
        c = self.give(cid)
        pos = len(self.g.players[0].board) if self.g.cards[cid]['type']=='MINION' else -1
        if position is not None:
            pos = position
        self.g.step(Action('play', c.uid, target, pos))
        return c

    def summon(self, cid, owner=0, ready=False):
        m = self.g._summon(owner, cid)
        if ready:
            m.summoned_turn = 0
        return m

    def test_opening_hands_and_coin(self):
        self.assertEqual([len(p.hand) for p in self.g.players], [3, 4])
        self.g.step(Action('mulligan'))
        self.g.step(Action('mulligan'))
        self.assertEqual([len(p.hand) for p in self.g.players], [4, 5])
        self.assertEqual(self.g.players[1].hand[-1].card_id, 'TOKEN_COIN')
        self.assertEqual(self.g.players[0].mana, 1)
        self.assertEqual(self.g.players[1].mana, 0)

    def test_mulligan_card_conservation_and_rejected_physical_cards(self):
        p = self.g.players[0]
        replaced = [c.card_id for c in p.hand]
        originals = [c.uid for c in p.hand]
        self.g.step(Action('mulligan', choices=tuple(originals)))
        self.assertFalse(set(originals) & {c.uid for c in p.hand})
        self.assertEqual(Counter(p.deck + [c.card_id for c in p.hand]), Counter(self.deck))
        self.assertEqual(len(p.deck), 27)

    def test_second_player_can_start(self):
        g = Game([self.deck]*2, [(1,1,1)]*2, first_player=1)
        self.assertEqual([len(p.hand) for p in g.players], [4,3])
        g.step(Action('mulligan')); g.step(Action('mulligan'))
        self.assertEqual(g.current, 1)
        self.assertEqual(g.players[0].hand[-1].card_id, 'TOKEN_COIN')

    def test_unsupported_cards_fail_before_game(self):
        bad = self.deck.copy(); bad[0] = 'CORE_RLK_066'
        with self.assertRaises(UnsupportedCard):
            Game([bad, self.deck], [(1,1,1)]*2)

    def test_wrong_runes_and_duplicate_legendary_rejected(self):
        bad = self.deck.copy(); bad[0] = 'RLK_707'
        with self.assertRaises(ValueError):
            Game([bad, self.deck], [(1,1,1)]*2)
        bad[:2] = ['CORE_EX1_110']*2
        with self.assertRaises(ValueError):
            Game([bad, self.deck], [(0,0,3), (1,1,1)])

    def test_manifest_rejects_modified_card_data(self):
        from lab import load_cards
        cards = load_cards()
        next(c for c in cards if c['id']=='RLK_503')['attack'] += 1
        with patch('engine.cards.load_cards', return_value=cards):
            with self.assertRaises(RuntimeError):
                registry()

    def test_illegal_action_does_not_change_state(self):
        self.start()
        before = copy.deepcopy(self.g.__dict__)
        with self.assertRaises(ValueError):
            self.g.step(Action('attack', 999, -2))
        self.assertEqual(self.g.players, before['players'])
        self.assertEqual(self.g.history, before['history'])
        self.assertEqual(self.g.rng.getstate(), before['rng'].getstate())

    def test_mana_cost_and_coin_expiry(self):
        p, _ = self.start(); p.mana = p.max_mana = 1
        c = self.give('Core_CS2_200')
        self.assertFalse(any(a.source==c.uid for a in self.g.legal_actions()))
        self.play('TOKEN_COIN')
        self.assertEqual((p.mana,p.max_mana),(2,1))
        self.g.step(Action('end')); self.g.step(Action('end'))
        self.assertEqual((p.mana,p.max_mana),(2,2))

    def test_ghoul_charge_expiry_and_corpse(self):
        p,q = self.start()
        self.g.step(Action('power'))
        ghoul=p.board[0]
        self.assertIn(Action('attack',ghoul.uid,-2),self.g.legal_actions())
        self.g.step(Action('attack',ghoul.uid,-2))
        self.assertEqual(q.health,29)
        self.assertFalse(any(a.kind=='power' for a in self.g.legal_actions()))
        self.g.step(Action('end'))
        self.assertEqual((len(p.board),p.corpses),(0,1))

    def test_summoning_sickness_and_rush(self):
        self.start()
        m=self.summon('Core_CS2_200')
        rush=self.summon('CS3_038')
        enemy=self.summon('Core_CS2_200',1)
        acts=self.g.legal_actions()
        self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in acts))
        self.assertIn(Action('attack',rush.uid,enemy.uid),acts)
        self.assertNotIn(Action('attack',rush.uid,-2),acts)
        self.g.step(Action('end')); self.g.step(Action('end'))
        self.assertIn(Action('attack',m.uid,-2),self.g.legal_actions())

    def test_taunt_and_one_attack(self):
        self.start()
        attacker=self.summon('Core_CS2_200',ready=True)
        guard=self.summon('CORE_CS2_179',1)
        self.assertNotIn(Action('attack',attacker.uid,-2),self.g.legal_actions())
        self.g.step(Action('attack',attacker.uid,guard.uid))
        self.assertEqual(attacker.health,4)
        self.assertFalse(any(a.kind=='attack' and a.source==attacker.uid for a in self.g.legal_actions()))

    def test_simultaneous_combat_and_corpses(self):
        p,q=self.start()
        a=self.summon('CORE_CS2_189',ready=True)
        b=self.summon('CORE_CS2_189',1)
        self.g.step(Action('attack',a.uid,b.uid))
        self.assertEqual((len(p.board),len(q.board),p.corpses,q.corpses),(0,0,1,1))

    def test_shield_prevents_damage_poison_and_lifesteal(self):
        p,q=self.start(); p.health=20
        a=self.summon('CORE_GIL_558',ready=True); a.keywords.add('POISONOUS')
        b=self.summon('CORE_GVG_085',1)
        self.g.step(Action('attack',a.uid,b.uid))
        self.assertEqual(b.health,2)
        self.assertNotIn('DIVINE_SHIELD',b.keywords)
        self.assertEqual(p.health,20)

    def test_poisonous_kills_large_minion(self):
        self.start()
        a=self.summon('RLK_503',ready=True)
        b=self.summon('Core_CS2_200',1)
        self.play('CORE_EDR_002',a.uid)
        self.g.step(Action('attack',a.uid,b.uid))
        self.assertEqual(len(self.g.players[1].board),0)

    def test_elusive_only_blocks_spells_not_battlecries(self):
        self.start(); m=self.summon('CORE_NEW1_023',1)
        spell=self.give('RLK_024'); archer=self.give('CORE_CS2_189')
        acts=self.g.legal_actions()
        self.assertNotIn(Action('play',spell.uid,m.uid),acts)
        self.assertIn(Action('play',archer.uid,m.uid,0),acts)

    def test_target_requirements_and_no_self_battlecry(self):
        self.start()
        poison=self.give('CORE_EDR_002'); sidekick=self.give('RLK_958')
        self.assertFalse(any(a.source==poison.uid for a in self.g.legal_actions()))
        self.g.step(Action('play',sidekick.uid,0,0))
        self.assertEqual(self.g.players[0].board[0].attack,1)

    def test_board_limit_and_spell_availability(self):
        p,q=self.start()
        for _ in range(7): self.summon('Core_CS2_200')
        self.give('RLK_503'); spell=self.give('RLK_709')
        acts=self.g.legal_actions()
        self.assertFalse(any(a.kind=='power' for a in acts))
        self.assertEqual([a.source for a in acts if a.kind=='play'],[spell.uid])
        self.assertIsNone(self.g._summon(0,'TOKEN_GHOUL'))

    def test_full_hand_burn_and_fatigue(self):
        p,_=self.start()
        for _ in range(10): self.give('RLK_503')
        before=len(p.deck)
        self.g._draw(0)
        self.assertEqual((len(p.hand),len(p.deck)),(10,before-1))
        p.deck=[]; p.armor=1
        self.g._draw(0); self.g._draw(0)
        self.assertEqual((p.health,p.armor,p.fatigue),(28,0,2))

    def test_reborn_resets_buffs_and_only_happens_once(self):
        p,_=self.start()
        m=self.summon('CORE_ULD_723'); self.g._buff(m,5,5)
        m.health=0; self.g._settle()
        reborn=p.board[0]
        self.assertEqual((reborn.attack,reborn.health,reborn.max_health),(1,1,1))
        self.assertNotIn('REBORN',reborn.keywords)
        reborn.health=0; self.g._settle()
        self.assertEqual((len(p.board),p.corpses),(0,2))

    def test_draw_deathrattles_and_harbinger_spell_school(self):
        p,_=self.start()
        self.play('RLK_708')
        self.assertEqual(len(p.hand),1)
        p.board[0].health=0; self.g._settle()
        self.assertEqual(len(p.hand),2)
        m=self.summon('CORE_EX1_096'); m.health=0; self.g._settle()
        self.assertEqual(len(p.hand),3)
        p.deck=['RLK_709','RLK_503']
        m=self.summon('RLK_511'); m.health=0; self.g._settle()
        self.assertEqual(p.hand[-1].card_id,'RLK_709')
        self.assertEqual(p.deck,['RLK_503'])
        p.deck=[]; fatigue=p.fatigue
        m=self.summon('RLK_511'); m.health=0; self.g._settle()
        self.assertEqual(p.fatigue,fatigue)

    def test_deathrattle_armor_and_baine(self):
        p,_=self.start()
        for cid in ['CORE_LOOT_413','CORE_SW_068','CORE_EX1_110']:
            self.summon(cid).health=0
        self.g._settle()
        self.assertEqual(p.armor,11)
        self.assertEqual([(m.card_id,m.attack,m.health) for m in p.board],[('TOKEN_BAINE',5,5)])
        self.assertEqual(p.corpses,3)

    def test_battlecry_damage_healing_and_health_buff(self):
        p,q=self.start(); p.health=20
        self.play('CORE_CS2_189',-2)
        self.play('CORE_UNG_084',-2)
        self.play('CORE_EX1_011',-1)
        self.play('CORE_ULD_191',p.board[0].uid)
        self.assertEqual((q.health,p.health,p.board[0].health),(26,22,3))

    def test_lifedrinker_and_injured_tolvir(self):
        p,q=self.start(); p.health=20
        self.play('CORE_GIL_622'); self.play('CORE_ULD_271')
        self.assertEqual((p.health,q.health),(23,27))
        self.assertEqual((p.board[-1].health,p.board[-1].max_health),(3,6))

    def test_body_bagger_and_skeletal_sidekick(self):
        p,_=self.start()
        self.play('RLK_503')
        self.play('RLK_958',p.board[0].uid)
        self.assertEqual((p.corpses,p.board[0].attack),(1,3))

    def test_summon_tokens_dont_repeat_battlecry(self):
        p,_=self.start()
        self.play('CORE_EX1_506')
        self.assertEqual([m.card_id for m in p.board],['CORE_EX1_506','TOKEN_SCOUT'])
        self.play('CORE_RLK_062')
        self.assertEqual(len(p.board),5)
        self.assertEqual(sum(m.card_id=='CORE_RLK_062' for m in p.board),3)

    def test_swarmguard_copies_hand_buffs_and_respects_board_limit(self):
        p,_=self.start()
        for _ in range(5): self.summon('Core_CS2_200')
        c=self.give('CORE_RLK_062'); c.attack_bonus=c.health_bonus=2
        self.g.step(Action('play',c.uid,0,5))
        self.assertEqual(len(p.board),7)
        self.assertEqual([(m.attack,m.health) for m in p.board[5:]],[(3,5),(3,5)])

    def test_blood_tap_spends_only_when_enough_and_buffs_minions(self):
        p,_=self.start(); p.corpses=2
        m=self.give('RLK_503'); spell=self.give('RLK_709')
        self.play('CORE_RLK_712')
        self.assertEqual((p.corpses,m.attack_bonus,m.health_bonus,spell.attack_bonus),(0,2,2,0))
        self.g.step(Action('play',m.uid,0,0))
        self.assertEqual((p.board[0].attack,p.board[0].health),(3,5))

    def test_grave_strength_with_and_without_corpses(self):
        p,_=self.start(); m=self.summon('RLK_503'); p.corpses=4
        self.play('RLK_707')
        self.assertEqual((m.attack,p.corpses),(2,4))
        p.corpses=5
        self.play('RLK_707')
        self.assertEqual((m.attack,p.corpses),(5,0))

    def test_anti_magic_shell(self):
        p,_=self.start(); m=self.summon('RLK_503')
        self.play('RLK_048')
        self.assertEqual((m.attack,m.health,m.max_health),(2,4,4))
        self.assertIn('ELUSIVE',m.keywords)

    def test_asphyxiate_bypasses_shield_and_selects_highest_attack(self):
        self.start(); a=self.summon('Core_CS2_200',1); a.keywords.add('DIVINE_SHIELD')
        b=self.summon('CORE_GVG_085',1)
        self.play('CORE_RLK_087')
        self.assertEqual(self.g.players[1].board,[b])

    def test_death_strike_overkill_and_shield(self):
        p,_=self.start(); p.health=10
        m=self.summon('RLK_503',1)
        self.play('RLK_024',m.uid)
        self.assertEqual(p.health,16)
        m=self.summon('CORE_GVG_085',1)
        self.play('RLK_024',m.uid)
        self.assertEqual((p.health,m.health),(16,2))

    def test_remorseless_winter_aoe_and_draw(self):
        p,q=self.start()
        self.summon('CORE_CS2_189',1); self.summon('CORE_GVG_085',1)
        self.play('RLK_709')
        self.assertEqual((q.health,len(q.board),q.corpses,len(p.hand)),(28,1,1,1))
        self.assertEqual(q.board[0].health,2)

    def test_marrow_manipulator_spends_up_to_five(self):
        p,q=self.start(); p.corpses=7
        self.play('CORE_RLK_505')
        self.assertEqual((p.corpses,q.health),(2,20))

    def test_weapon_attacks_breaks_and_lifesteal(self):
        p,q=self.start(); p.health=20
        self.play('RLK_067')
        target=self.summon('CORE_CS2_179',1)
        self.g.step(Action('attack',-1,target.uid))
        self.assertEqual((p.health,p.weapon['durability']),(22,1))
        self.assertNotIn(Action('attack',-1,-2),self.g.legal_actions())
        self.g.step(Action('end')); self.g.step(Action('end'))
        self.g.step(Action('attack',-1,-2))
        self.assertIsNone(p.weapon)
        self.assertEqual((p.health,q.health),(27,25))

    def test_defending_hero_weapon_does_not_retaliate(self):
        p,q=self.start()
        q.weapon={'card_id':'RLK_067','attack':5,'durability':2}
        a=self.summon('Core_CS2_200',ready=True)
        self.g.step(Action('attack',a.uid,-2))
        self.assertEqual((a.health,q.health,q.weapon['durability']),(7,24,2))

    def test_heal_caps_at_max_health(self):
        p,_=self.start(); p.health=29
        self.g._heal(-1,10)
        m=self.summon('Core_CS2_200'); m.health=1
        self.g._heal(m.uid,20)
        self.assertEqual((p.health,m.health),(30,7))

    def test_lethal_reward_and_terminal_actions(self):
        _,q=self.start(); q.health=1
        self.play('CORE_CS2_189',-2)
        self.assertEqual((self.g.winner,self.g.rewards(),self.g.legal_actions()),(0,(1,-1),[]))
        with self.assertRaises(ValueError): self.g.step(Action('end'))

    def test_simultaneous_lethal_is_draw(self):
        self.start()
        for p in self.g.players: p.health=0
        self.g._settle()
        self.assertTrue(self.g.terminal)
        self.assertIsNone(self.g.winner)
        self.assertEqual(self.g.rewards(),(0,0))

    def test_turn_limit_recorded_separately(self):
        self.start(); self.g.max_turns=1
        self.g.step(Action('end'))
        self.assertTrue(self.g.terminal)
        self.assertEqual(self.g.end_reason,'turn_limit')

    def test_observation_hides_opponent_cards_and_deck_order(self):
        self.start()
        self.give('RLK_503',1)
        before=self.g.observe(0)
        self.g.players[1].hand[0].card_id='Core_CS2_200'
        self.g.players[1].deck.reverse()
        self.g.players[0].deck.reverse()
        self.g.players[1].starting_deck.reverse()
        self.assertEqual(before,self.g.observe(0))
        self.assertNotIn('runes',before['players'][1])
        before['players'][0]['hand'].append('corrupt')
        self.assertNotEqual(before,self.g.observe(0))

    def test_passive_stats_and_keywords_match_frozen_data(self):
        self.start()
        for cid in ['CORE_CS2_179','Core_CS2_200','CORE_GIL_558','CORE_GVG_085',
                    'CORE_LOOT_137','CORE_NEW1_023','CS3_038']:
            with self.subTest(cid=cid):
                self.g.players[0].board=[]
                m=self.summon(cid); c=self.g.cards[cid]
                self.assertEqual((m.attack,m.health),(c['attack'],c['health']))
                self.assertEqual(m.keywords,set(c.get('mechanics',[])))

if __name__=='__main__': unittest.main()
