"""Conditional attack immunity spans declarations, but not after-attack effects."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.cards import TRIGGERS
from engine.cards import UnsupportedCard

class AttackImmunityTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('DEMONHUNTER',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
    def cast(self,middle=False):
        if middle:self.g._add(0,'TOKEN_COIN')
        c=self.g._add(0,'DINO_136')
        if middle:self.g._add(0,'TOKEN_COIN')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return list(self.p.minions)
    def attack(self,m,target):self.g.step(Action('attack',m.uid,target))

    def test_outcast_summons_three_rush_raptors_with_conditional_effect(self):
        ms=self.cast();self.assertEqual(len(ms),3)
        for m in ms:
            self.assertEqual((m.attack,m.health),(2,1));self.assertIn('RUSH',m.keywords)
            self.assertIn('IMMUNE_WHILE_ATTACKING',self.g._effective_keywords(m))
            self.assertNotIn('IMMUNE',self.g._effective_keywords(m))

    def test_non_outcast_raptors_take_retaliation(self):
        m=self.cast(middle=True)[0];enemy=self.g._summon(1,'CORE_EX1_110')
        self.attack(m,enemy.uid);self.assertNotIn(m,self.p.board)
        self.assertEqual(enemy.health,3)

    def test_outcast_raptor_ignores_retaliation_but_not_later_damage(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        self.attack(m,enemy.uid);self.assertEqual(m.health,1);self.assertEqual(enemy.health,3)
        self.assertEqual(self.g._attack_windows,[])
        self.g._damage(m.uid,1);self.g._settle();self.assertNotIn(m,self.p.board)

    def test_only_attacking_raptor_survives_explosive_trap(self):
        ms=self.cast();attacker=ms[0];attacker.keywords.add('CHARGE')
        secret=self.g._add(1,'CORE_EX1_610');self.q.hand.remove(secret);self.q.secrets=[secret]
        self.attack(attacker,self.g.hero_id(1))
        self.assertEqual(self.p.minions,[attacker]);self.assertEqual(attacker.health,1)
        self.assertEqual(self.p.health,28);self.assertEqual(self.q.health,28)
        self.assertEqual(self.g._attack_windows,[])

    def test_freezing_trap_cancels_and_clears_attack_window(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        secret=self.g._add(1,'CORE_EX1_611');self.q.hand.remove(secret);self.q.secrets=[secret]
        self.attack(m,enemy.uid)
        self.assertNotIn(m,self.p.board);self.assertEqual(enemy.health,5)
        self.assertEqual(self.g._attack_windows,[])

    def test_defending_raptor_is_not_immune(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        self.g._force_attack(enemy.uid,m.uid)
        self.assertNotIn(m,self.p.board);self.assertEqual(enemy.health,3)
        self.assertEqual(self.g._attack_windows,[])

    def test_forced_attack_has_same_immunity_without_spending_attack(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        self.g._force_attack(m.uid,enemy.uid)
        self.assertEqual(m.health,1);self.assertEqual(m.attacks,0)
        self.assertEqual(enemy.health,3);self.assertEqual(self.g._attack_windows,[])

    def test_forced_pre_attack_choice_keeps_window_until_resume(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        rule=('attacking_self',[('discover_deck',)])
        with patch.dict(TRIGGERS,{'DINO_136t':rule}):
            self.g._force_attack(m.uid,enemy.uid)
            self.assertEqual(self.g.phase,'choice');self.assertIn('IMMUNE',self.g._effective_keywords(m))
            cloned=copy.deepcopy(self.g)
            self.g.step(Action('choose',choices=(0,)));cloned.step(Action('choose',choices=(0,)))
        self.assertEqual(self.g.observe(0),cloned.observe(0));self.assertEqual(m.health,1)
        self.assertEqual(self.g._attack_windows,[])

    def test_pre_attack_damage_is_prevented(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        with patch.dict(TRIGGERS,{'DINO_136t':('attacking_self',[('damage_self',5)])}):self.attack(m,enemy.uid)
        self.assertEqual(m.health,1);self.assertEqual(enemy.health,3)

    def test_after_attack_damage_is_not_prevented(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        with patch.dict(TRIGGERS,{'DINO_136t':('attacked_self',[('damage_self',1)])}):self.attack(m,enemy.uid)
        self.assertNotIn(m,self.p.board);self.assertEqual(self.g._attack_windows,[])

    def test_silence_removes_conditional_immunity(self):
        m=self.cast()[0];self.g._silence(m);m.keywords.add('RUSH')
        enemy=self.g._summon(1,'CORE_EX1_110');self.attack(m,enemy.uid)
        self.assertNotIn(m,self.p.board)

    def test_copy_inherits_remaining_turn_effect(self):
        m=self.cast()[0];other=self.g._summon(0,m.card_id,copy_from=m)
        enemy=self.g._summon(1,'CORE_EX1_110');self.attack(other,enemy.uid)
        self.assertEqual(other.health,1)

    def test_effect_expires_at_turn_end(self):
        ms=self.cast();self.g.step(Action('end'))
        self.assertTrue(all(not m.temporary_keywords for m in ms))
        self.assertTrue(all('IMMUNE_WHILE_ATTACKING' not in self.g._effective_keywords(m) for m in ms))

    def test_full_board_and_counterspell_do_not_create_effects(self):
        for _ in range(7):self.g._summon(0,'EDR_851t')
        self.cast();self.assertTrue(all(not m.temporary_keywords for m in self.p.minions))
        self.p.board=[];self.p.mana=10
        secret=self.g._add(1,'CORE_EX1_287');self.q.hand.remove(secret);self.q.secrets=[secret]
        self.cast();self.assertEqual(self.p.board,[])

    def test_failure_rolls_back_attack_window_and_combat(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110');before=copy.deepcopy(self.g.__dict__)
        with patch.object(Game,'_resolve_combat',side_effect=UnsupportedCard('injected')):
            with self.assertRaises(UnsupportedCard):self.attack(m,enemy.uid)
        self.assertEqual(self.g.players,before['players'])
        self.assertEqual(getattr(self.g,'_attack_windows',[]),before.get('_attack_windows',[]))

    def test_nested_windows_for_same_attacker_close_independently(self):
        m=self.cast()[0];a=self.g._open_attack_window(m.uid);b=self.g._open_attack_window(m.uid)
        self.g._close_attack_window(b);self.assertIn('IMMUNE',self.g._effective_keywords(m))
        self.g._close_attack_window(b);self.assertEqual(len(self.g._attack_windows),1)
        self.g._close_attack_window(a);self.assertNotIn('IMMUNE',self.g._effective_keywords(m))

    def test_terminal_cleanup_clears_windows(self):
        m=self.cast()[0];m.keywords.add('CHARGE');self.q.health=2
        self.attack(m,self.g.hero_id(1));self.assertTrue(self.g.terminal)
        self.assertEqual(self.g._attack_windows,[])

    def test_target_lost_during_pre_attack_trigger_clears_forced_window(self):
        m=self.cast()[0];enemy=self.g._summon(1,'CORE_EX1_110')
        with patch.dict(TRIGGERS,{'DINO_136t':('attacking_self',[('force_pre_damage',20)])}):
            self.g._force_attack(m.uid,enemy.uid)
        self.assertEqual(self.g._attack_windows,[])
        self.assertNotIn('IMMUNE',self.g._effective_keywords(m));self.assertEqual(m.health,1)
        self.assertEqual(self.p.friendly_attacks,0)

    def test_partial_board_grants_only_successfully_summoned_raptors(self):
        for _ in range(5):self.g._summon(0,'EDR_851t')
        self.cast();raptors=[m for m in self.p.minions if m.card_id=='DINO_136t']
        self.assertEqual(len(raptors),2)
        self.assertTrue(all(m.temporary_keywords for m in raptors))
        self.assertTrue(all(not m.temporary_keywords for m in self.p.minions if m.card_id!='DINO_136t'))
