"""Physical keyword pairs, with the developer's no-identical-reroll contract."""
import copy
import json
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.bonus_effects import BONUS_EFFECTS,MONSTROSITY_DEFAULT
from expanded.features import SCHEMA,encode_decision

class HeldBonusTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
    def hold(self,owner=0):return self.g._add(owner,'CATA_206')
    def play(self,c):
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        return next(m for m in self.p.minions if m.card_id=='CATA_206')
    def pair(self,c,pair):self.g._b60_state(c)['bonus_pair']=list(pair)

    def test_default_pair_when_created_or_summoned(self):
        c=self.hold();self.assertEqual(self.g._held_bonus_pair(c),MONSTROSITY_DEFAULT)
        m=self.g._summon(0,'CATA_206');self.assertEqual(m.keywords,set(MONSTROSITY_DEFAULT))

    def test_same_turn_play_uses_default(self):
        m=self.play(self.hold());self.assertEqual(m.keywords,set(MONSTROSITY_DEFAULT))

    def test_owner_end_rerolls_but_opponent_end_does_not(self):
        c=self.hold();self.g.step(Action('end'));pair=self.g._held_bonus_pair(c)
        self.assertNotEqual(pair,MONSTROSITY_DEFAULT)
        self.g.step(Action('end'));self.assertEqual(self.g._held_bonus_pair(c),pair)

    def test_other_player_card_does_not_reroll_on_our_end(self):
        c=self.hold(1);self.g.step(Action('end'))
        self.assertEqual(self.g._held_bonus_pair(c),MONSTROSITY_DEFAULT)
        self.g.step(Action('end'));self.assertNotEqual(self.g._held_bonus_pair(c),MONSTROSITY_DEFAULT)

    def test_pool_has_every_distinct_pair_except_previous(self):
        c=self.hold()
        with patch.object(self.g.rng,'choice',return_value=('LIFESTEAL','TAUNT')) as choose:
            self.g._reroll_held_bonus(c)
            pool=choose.call_args[0][0]
        self.assertEqual(len(pool),27);self.assertEqual(len(set(pool)),27)
        self.assertNotIn(MONSTROSITY_DEFAULT,pool)
        self.assertTrue(all(len(set(pair))==2 and set(pair)<=BONUS_EFFECTS for pair in pool))
        self.assertEqual(self.g._held_bonus_pair(c),('LIFESTEAL','TAUNT'))

    def test_successive_rerolls_never_repeat_exact_pair(self):
        c=self.hold()
        for _ in range(100):
            before=self.g._held_bonus_pair(c);self.g._reroll_held_bonus(c)
            self.assertNotEqual(self.g._held_bonus_pair(c),before)

    def test_observation_does_not_change_pair_or_rng(self):
        c=self.hold();state=self.g.rng.getstate()
        for _ in range(3):self.g.observe(0);self.g.observe(1);self.g.legal_actions()
        self.assertEqual(self.g.rng.getstate(),state);self.assertEqual(self.g._held_bonus_pair(c),MONSTROSITY_DEFAULT)

    def test_tick_guard_prevents_double_reroll(self):
        c=self.hold();op=('held_tick',c.uid,c.card_id);ctx=dict(owner=0)
        self.g._held_effect(op,ctx);before=self.g.rng.getstate();pair=self.g._held_bonus_pair(c)
        self.g._held_effect(op,ctx)
        self.assertEqual(self.g.rng.getstate(),before);self.assertEqual(self.g._held_bonus_pair(c),pair)

    def test_departed_or_transformed_card_does_not_tick(self):
        c=self.hold();op=('held_tick',c.uid,c.card_id);self.p.hand.remove(c)
        before=self.g.rng.getstate();self.g._held_effect(op,dict(owner=0))
        self.p.hand.append(c);c.card_id='CORE_EX1_506';self.g._held_effect(op,dict(owner=0))
        self.assertEqual(self.g.rng.getstate(),before)

    def test_play_replaces_printed_pair_before_actions(self):
        c=self.hold();self.pair(c,('RUSH','WINDFURY'));m=self.play(c)
        self.assertEqual(m.keywords,{'RUSH','WINDFURY'})
        enemy=self.g._summon(1,'CORE_EX1_110')
        self.assertTrue(any(a.kind=='attack' and a.source==m.uid and a.target==enemy.uid for a in self.g.legal_actions()))

    def test_hand_recruitment_keeps_pair_and_stat_buffs(self):
        c=self.hold();self.pair(c,('DIVINE_SHIELD','LIFESTEAL'));c.attack_bonus=2
        m=self.g._recruit_from_zone(0,'hand',())
        self.assertEqual(m.keywords,{'DIVINE_SHIELD','LIFESTEAL'});self.assertEqual(m.attack,8)

    def test_physical_deck_recruit_keeps_stored_pair(self):
        c=self.hold();self.pair(c,('POISONOUS','WINDFURY'));self.p.hand.remove(c);self.p.deck=[c]
        m=self.g._recruit_from_zone(0,'deck',())
        self.assertEqual(m.keywords,{'POISONOUS','WINDFURY'})

    def test_board_copy_keeps_current_keywords_without_default_pair(self):
        c=self.hold();self.pair(c,('POISONOUS','WINDFURY'));m=self.play(c)
        other=self.g._summon(0,'CATA_206',copy_from=m)
        self.assertEqual(other.keywords,{'POISONOUS','WINDFURY'})

    def test_silence_removes_current_pair(self):
        c=self.hold();self.pair(c,('POISONOUS','WINDFURY'));m=self.play(c);self.g._silence(m)
        self.assertEqual(m.keywords,set());self.g._refresh_auras();self.assertEqual(m.keywords,set())

    def test_bounce_resets_pair_to_default(self):
        c=self.hold();self.pair(c,('POISONOUS','WINDFURY'));m=self.play(c);self.g._bounce(m)
        self.assertEqual(self.g._held_bonus_pair(self.p.hand[0]),MONSTROSITY_DEFAULT)

    def test_reborn_returns_printed_pair(self):
        c=self.hold();self.pair(c,('REBORN','LIFESTEAL'));m=self.play(c);m.health=0;self.g._settle()
        m=self.p.minions[0];self.assertEqual(m.health,1);self.assertEqual(m.keywords,set(MONSTROSITY_DEFAULT))

    def test_hand_copy_is_independent_and_keeps_pair(self):
        c=self.hold();self.pair(c,('LIFESTEAL','TAUNT'));other=self.g._copy_card(c)
        self.assertEqual(self.g._held_bonus_pair(other),('LIFESTEAL','TAUNT'))
        self.g._reroll_held_bonus(other);self.assertEqual(self.g._held_bonus_pair(c),('LIFESTEAL','TAUNT'))

    def test_filters_use_current_pair(self):
        c=self.hold();self.pair(c,('RUSH','WINDFURY'))
        self.assertTrue(self.g._matches_filter(c,(('mechanic','eq','RUSH'),)))
        self.assertFalse(self.g._matches_filter(c,(('mechanic','eq','TAUNT'),)))
        self.assertTrue(self.g._matches_filter('CATA_206',(('mechanic','eq','TAUNT'),)))

    def test_pair_visible_only_to_owner_and_encoded(self):
        c=self.hold();self.pair(c,('POISONOUS','WINDFURY'));view=self.g.observe(0)
        self.assertEqual(view['players'][0]['hand'][0]['bonus_effects'],['POISONOUS','WINDFURY'])
        self.assertNotIn('bonus_pair',json.dumps(self.g.observe(1)))
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertTrue(any('bonus_effects' in str(row) for row in rows));self.assertEqual(SCHEMA,'visible-action-features-v58')

    def test_bad_pair_fails_atomically_when_played(self):
        c=self.hold();self.pair(c,('RUSH','RUSH'))
        action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
        before=copy.deepcopy(self.g.__dict__)
        with self.assertRaises(ValueError):self.g.step(action)
        self.assertEqual(self.g.players,before['players']);self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())

    def test_taunt_hand_buff_uses_rolled_pair_not_printed_default(self):
        taunt=self.hold();other=self.hold();self.pair(other,('RUSH','WINDFURY'))
        c=self.g._add(0,'CORE_WW_329')
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual((taunt.attack_bonus,taunt.health_bonus),(2,2))
        self.assertEqual((other.attack_bonus,other.health_bonus),(0,0))

    def test_clean_shuffle_resets_pair_but_hand_copy_preserves_it(self):
        c=self.hold();self.pair(c,('RUSH','WINDFURY'))
        cloned=self.g._clone_hand_card(0,c)
        clean=self.g._shuffle_hand_card(0,c)
        self.assertEqual(self.g._held_bonus_pair(cloned),('RUSH','WINDFURY'))
        self.assertEqual(self.g._held_bonus_pair(clean),MONSTROSITY_DEFAULT)
