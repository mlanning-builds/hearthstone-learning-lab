"""Candidate Imbue bodies: scaling, targeting, payment and ownership."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.selectors import has_tribe
from expanded.pools import GenerationPool
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard

class ImbueBodyTests(unittest.TestCase):
    def game(self, hero, level=1):
        g=Game([random_deck(hero,31),random_deck('WARRIOR',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['AT_037t']*10
            p.mana=p.max_mana=10;p.health=30;p.armor=0
        g._imbue(0,level)
        return g
    def test_druid_scaling_and_single_summon(self):
        for level in (1,4,5,9,10,12):
            with self.subTest(level=level):
                g=self.game('DRUID',level);g.step(Action('power'))
                self.assertEqual(len(g.players[0].minions),1)
                m=g.players[0].minions[0]
                self.assertEqual((m.attack,m.health),(level,level))
                self.assertEqual(g.players[0].mana,8)
    def test_druid_full_board_cannot_activate(self):
        g=self.game('DRUID')
        for _ in range(7):g._summon(0,'EDR_851t')
        self.assertNotIn(Action('power'),g.legal_actions())
    def test_mage_scaling_and_enemy_only_damage(self):
        for level in (1,3,8):
            g=self.game('MAGE',level);g.step(Action('power'))
            self.assertEqual(len(g.players[0].minions),min(level,7))
            self.assertEqual(g.players[1].health,30-level)
            self.assertEqual(g.players[0].health,30)
            self.assertTrue(all(m.health==1 for m in g.players[0].minions))
    def test_mage_full_board_still_deals_damage(self):
        g=self.game('MAGE',3)
        for _ in range(7):g._summon(0,'EDR_851t')
        g.step(Action('power'))
        self.assertEqual(len(g.players[0].minions),7)
        self.assertEqual(g.players[1].health,27)
    def test_mage_ignores_spell_damage(self):
        g=self.game('MAGE',3);g._summon(0,'CORE_EX1_012')
        g.step(Action('power'));self.assertEqual(g.players[1].health,27)
    def test_mage_missiles_account_for_dead_targets(self):
        g=self.game('MAGE',12);g._summon(1,'EDR_851t')
        g.step(Action('power'))
        damage=30-g.players[1].health+int(not g.players[1].minions)
        self.assertEqual(damage,12)
    def test_hunter_buffs_one_physical_beast_and_preserves_health(self):
        g=self.game('HUNTER',3)
        cid=next(cid for cid,c in g.cards.items() if c.get('type')=='MINION' and has_tribe(c,'BEAST'))
        beasts=[Card(g._new_id(),cid),Card(g._new_id(),cid)]
        other=Card(g._new_id(),'EDR_851t');g.players[0].hand=beasts+[other]
        g.step(Action('power'))
        self.assertEqual(sorted(c.attack_bonus for c in beasts),[0,3])
        chosen=next(c for c in beasts if c.attack_bonus)
        self.assertEqual(chosen.cost_delta,-3);self.assertEqual(chosen.health_bonus,0)
        self.assertEqual(other.attack_bonus,0);self.assertEqual(getattr(other,'cost_delta',0),0)
        self.assertEqual(g._cost(chosen,0),max(0,g.cards[cid].get('cost',0)-3))
    def test_hunter_empty_hand_resolves_without_a_target(self):
        g=self.game('HUNTER');g.step(Action('power'))
        self.assertEqual(g.players[0].hand,[]);self.assertEqual(g.players[0].mana,8)
    def test_each_active_body_consumes_one_use(self):
        for hero in ('DRUID','HUNTER','MAGE'):
            g=self.game(hero);g.step(Action('power'))
            self.assertEqual(g.players[0].hero_power_uses,1)
            self.assertTrue(g.players[0].power_used)
            self.assertNotIn(Action('power'),g.legal_actions())

    def test_shaman_only_friendly_targetable_minions(self):
        g=self.game('SHAMAN');friendly=g._summon(0,'EDR_851t')
        enemy=g._summon(1,'EDR_851t');elusive=g._summon(0,'EDR_851t');elusive.keywords.add('ELUSIVE')
        powers=[a for a in g.legal_actions() if a.kind=='power']
        self.assertEqual(powers,[Action('power',target=friendly.uid)])
    def test_shaman_no_minions_no_activation(self):
        g=self.game('SHAMAN');self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))
    def test_shaman_missing_pool_rolls_back_everything(self):
        g=self.game('SHAMAN');m=g._summon(0,'EDR_851t');before=g.observe(0);rng=g.rng.getstate()
        with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):
            g.step(Action('power',target=m.uid))
        self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
    def test_shaman_transform_uses_base_cost_and_retains_position(self):
        g=self.game('SHAMAN',6);left=g._summon(0,'EDR_851t');m=g._summon(0,'EDR_851t');right=g._summon(0,'EDR_851t')
        g._buff(m,9,9)
        request=pool(card_type='MINION',minimum=6,maximum=6)
        g._generation_pools={(request,'SHAMAN'):GenerationPool('fixture only',('EX1_tk34',),'Synthetic test membership, not a Standard pool')}
        g.step(Action('power',target=m.uid))
        board=g.players[0].board;self.assertEqual((board[0].uid,board[2].uid),(left.uid,right.uid))
        self.assertEqual((board[1].card_id,board[1].attack,board[1].health),('EX1_tk34',6,6))
        self.assertNotEqual(board[1].uid,m.uid);self.assertEqual(g.players[0].hero_power_uses,1)
        self.assertEqual(g.players[0].mana,8)
    def test_shaman_reviewed_empty_pool_leaves_target_unchanged(self):
        g=self.game('SHAMAN');m=g._summon(0,'EDR_851t');request=pool(card_type='MINION',minimum=1,maximum=1)
        g._generation_pools={(request,'SHAMAN'):GenerationPool('fixture empty',(),'Synthetic empty membership')}
        rng=g.rng.getstate();g.step(Action('power',target=m.uid))
        self.assertEqual(g.players[0].minions[0].uid,m.uid);self.assertEqual(g.rng.getstate(),rng)
