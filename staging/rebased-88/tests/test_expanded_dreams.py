"""Closed rewards, held upgrades, enchantment expiry and hero target auras."""
import copy
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.dreams import DREAMS,CORRUPTED
from engine.cards import UnsupportedCard

class DreamTests(unittest.TestCase):
    def game(self,seed=71):
        g=Game([random_deck('MAGE',31),random_deck('HUNTER',53)],seed=seed)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=[];p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def hold(self,g,cid):return g._enter_hand(0,Card(g._new_id(),cid))
    def play(self,g,cid=None,target=0,card=None):
        c=card or self.hold(g,cid);g.players[0].mana=10
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def effect(self,g,op,target=0,owner=0):g._effect(op,dict(owner=owner,target=target,source=None,bonus=0,lifesteal=False))
    def ysera(self,g,owner):
        # Exercise reviewed target identity without claiming its own Start of Game is supported.
        from standard.catalog import load_catalog
        g.cards['EDR_000']=next(c for c in load_catalog() if c['id']=='EDR_000')
        return g._summon(owner,'EDR_000')
    def test_dryad_can_generate_every_dream(self):
        seen=set()
        for seed in range(30):
            g=self.game(seed);self.play(g,'EDR_001');seen.add(g.players[0].hand[-1].card_id)
        self.assertEqual(seen,set(DREAMS))
    def test_missing_dependency_rejects_before_rng(self):
        g=self.game();del g.cards['DREAM_01'];before=g.rng.getstate()
        with self.assertRaises(UnsupportedCard):self.effect(g,('dream_random',))
        self.assertEqual(before,g.rng.getstate());self.assertFalse(g.players[0].hand)
    def test_plain_shaladrassil_gives_one_of_each(self):
        g=self.game();self.play(g,'EDR_846');self.assertEqual(set(c.card_id for c in g.players[0].hand),set(DREAMS))
    def test_all_reward_order_varies_by_seed(self):
        orders=set()
        for seed in range(5):
            g=self.game(seed);self.play(g,'EDR_846');orders.add(tuple(c.card_id for c in g.players[0].hand))
        self.assertGreater(len(orders),1)
    def test_higher_cost_upgrades_held_physical_card(self):
        g=self.game();tree=self.hold(g,'EDR_846');c=self.hold(g,'CORE_CS2_029');c.set_cost=9
        self.play(g,card=c,target=-2);self.assertTrue(tree.rule_state['dream_corrupted'])
        self.play(g,card=tree);self.assertEqual(set(c.card_id for c in g.players[0].hand),set(CORRUPTED))
    def test_equal_cost_not_higher(self):
        g=self.game();tree=self.hold(g,'EDR_846');c=self.hold(g,'CORE_CS2_029');c.set_cost=8
        self.play(g,card=c,target=-2);self.assertFalse(getattr(tree,'rule_state',{}).get('dream_corrupted'))
    def test_discounted_tree_compares_current_cost(self):
        g=self.game();tree=self.hold(g,'EDR_846');tree.cost_delta=-5
        self.play(g,'CORE_CS2_029',-2);self.assertTrue(tree.rule_state['dream_corrupted'])
    def test_discounted_play_does_not_use_printed_cost(self):
        g=self.game();tree=self.hold(g,'EDR_846');tree.cost_delta=-5;c=self.hold(g,'CORE_CS2_029');c.set_cost=2
        self.play(g,card=c,target=-2);self.assertFalse(getattr(tree,'rule_state',{}).get('dream_corrupted'))
    def test_consumed_shared_discount_does_not_count_as_tree_discount(self):
        g=self.game();tree=self.hold(g,'EDR_846');g.players[0].cost_effects=[dict(selector='SPELL',amount=5)]
        self.play(g,'CORE_CS2_029',-2);self.assertFalse(getattr(tree,'rule_state',{}).get('dream_corrupted'))
    def test_enemy_play_does_not_corrupt(self):
        g=self.game();tree=self.hold(g,'EDR_846');g._dream_higher_play(1,None,10)
        self.assertFalse(getattr(tree,'rule_state',{}).get('dream_corrupted'))
    def test_later_entering_tree_not_retroactively_corrupted(self):
        g=self.game();g._dream_higher_play(0,None,10);tree=self.hold(g,'EDR_846')
        self.assertFalse(getattr(tree,'rule_state',{}).get('dream_corrupted'))
    def test_reward_overflow_respects_hand_cap(self):
        g=self.game()
        for _ in range(9):self.hold(g,'CORE_CS2_029')
        self.play(g,'EDR_846');self.assertEqual(len(g.players[0].hand),10)
        self.assertEqual(sum(c.card_id in DREAMS for c in g.players[0].hand),1)
    def test_dream_bounces_both_sides_cleanly(self):
        for owner in (0,1):
            g=self.game();m=g._summon(owner,'EX1_tk34');g._buff(m,3,3);self.play(g,'DREAM_04',m.uid)
            self.assertFalse(g.players[owner].board);c=g.players[owner].hand[-1]
            self.assertEqual((c.card_id,c.attack_bonus,c.health_bonus),('EX1_tk34',0,0))
    def test_nightmare_destroys_on_casters_next_turn(self):
        g=self.game();m=g._summon(1,'EX1_tk34');self.play(g,'DREAM_05',m.uid)
        self.assertEqual((m.attack,m.health),(11,11));g.step(Action('end'));self.assertIn(m,g.players[1].board)
        g.step(Action('end'));self.assertNotIn(m,g.players[1].board)
    def test_nightmare_silence_removes_expiry(self):
        g=self.game();m=g._summon(1,'EX1_tk34');self.play(g,'DREAM_05',m.uid);g._silence(m)
        g.step(Action('end'));g.step(Action('end'));self.assertIn(m,g.players[1].board)
    def test_nightmare_applied_after_silence_still_expires(self):
        g=self.game();m=g._summon(1,'EX1_tk34');g._silence(m);self.play(g,'DREAM_05',m.uid)
        g.step(Action('end'));g.step(Action('end'));self.assertNotIn(m,g.players[1].board)
    def test_nightmare_copy_retains_caster_deadline(self):
        g=self.game();m=g._summon(1,'EX1_tk34');self.play(g,'DREAM_05',m.uid)
        clone=g._summon(0,m.card_id,copy_from=m);g.step(Action('end'));g.step(Action('end'))
        self.assertNotIn(m,g.players[1].board);self.assertNotIn(clone,g.players[0].board)
    def test_bounce_clears_nightmare_enchantment(self):
        g=self.game();m=g._summon(0,'EX1_tk34');self.play(g,'DREAM_05',m.uid);g._bounce(m)
        c=g.players[0].hand[-1];self.assertFalse(getattr(c,'rule_state',{}))
    def test_nightmare_can_be_copied_without_sharing_state(self):
        g=self.game();m=g._summon(0,'EX1_tk34');self.play(g,'DREAM_05',m.uid)
        clone=g._summon(0,m.card_id,copy_from=m);g._silence(m)
        self.assertIn('dream_nightmares',clone.rule_state)
    def test_corrupted_nightmare_immunity_expires_but_stats_stay(self):
        g=self.game();m=g._summon(0,'EX1_tk34');self.play(g,'EDR_846t1',m.uid)
        self.assertIn('IMMUNE',g._effective_keywords(m));self.assertEqual(g._damage(m.uid,5),0)
        g.step(Action('end'));self.assertNotIn('IMMUNE',g._effective_keywords(m));self.assertEqual((m.attack,m.health),(11,11))
    def test_corrupted_dream_shuffles_clean_card_without_death(self):
        g=self.game();m=g._summon(1,'TLC_433t');g._buff(m,2,2);before=g.players[1].corpses
        self.play(g,'EDR_846t2',m.uid);p=g.players[1]
        self.assertFalse(p.board);self.assertEqual(p.corpses,before);self.assertEqual(p.deck[0].card_id,'TLC_433t')
        self.assertEqual((p.deck[0].attack_bonus,p.deck[0].health_bonus),(0,0))
        self.assertEqual(p.shuffle_history[-1]['actor'],0)
    def test_hero_elusive_blocks_own_and_enemy_magic(self):
        g=self.game();g._summon(0,'EDR_846t3')
        for owner in (0,1):self.assertNotIn(-1,g._visible_targets(owner,magic=True))
        self.assertIn(-1,g._visible_targets(1,magic=False))
    def test_hero_elusive_blocks_mage_power(self):
        g=self.game();g._summon(0,'EDR_846t3');self.assertNotIn(Action('power',target=-1),g.legal_actions())
    def test_hero_elusive_does_not_block_attacks_or_area_damage(self):
        g=self.game();g._summon(1,'EDR_846t3');self.assertIn(-2,g._attack_targets())
        self.play(g,'EDR_846t4');self.assertEqual(g.players[1].health,25)
    def test_hero_aura_tracks_silence_death_and_multiple_sources(self):
        g=self.game();a=g._summon(0,'EDR_846t3');b=g._summon(0,'EDR_846t3');g._silence(a)
        self.assertTrue(g._hero_elusive(0));b.health=0;self.assertFalse(g._hero_elusive(0));g._settle()
    def test_dream_minion_stats_and_elusive(self):
        g=self.game();a=g._summon(0,'DREAM_01');b=g._summon(0,'EDR_846t5')
        self.assertEqual((a.attack,a.health),(3,5));self.assertIn('ELUSIVE',g._effective_keywords(a));self.assertEqual((b.attack,b.health),(14,12))
    def test_ordinary_awaken_hits_heroes_and_spares_ysera(self):
        g=self.game();a=self.ysera(g,0);b=self.ysera(g,1);self.play(g,'DREAM_02')
        self.assertEqual([p.health for p in g.players],[25,25]);self.assertEqual(a.health,g.cards['EDR_000']['health']);self.assertEqual(b.health,a.health)
    def test_ordinary_awaken_scales_with_spell_damage(self):
        g=self.game();g.players[0].deck=['DREAM_03'];g._summon(0,'CORE_EX1_012');self.play(g,'DREAM_02');self.assertEqual([p.health for p in g.players],[24,24])
    def test_corrupted_awaken_destroys_even_friendly_ysera(self):
        g=self.game();self.ysera(g,0);self.ysera(g,1);self.play(g,'EDR_846t4')
        self.assertFalse(any(m.card_id=='EDR_000' for p in g.players for m in p.minions))
        self.assertEqual([p.health for p in g.players],[30,25])
    def test_upgrade_state_visible_only_to_owner(self):
        g=self.game();tree=self.hold(g,'EDR_846');g._dream_higher_play(0,None,10)
        self.assertTrue(g.observe(0)['players'][0]['hand'][0]['rule_state']['dream_corrupted'])
        self.assertNotIn('hand',g.observe(1)['players'][0])
    def test_copied_held_upgrade_is_independent(self):
        g=self.game();tree=self.hold(g,'EDR_846');g._dream_higher_play(0,None,10);clone=g._copy_card(tree)
        tree.rule_state.clear();self.assertTrue(clone.rule_state['dream_corrupted'])
    def test_nightmare_follows_control_change_but_not_new_controller_turn(self):
        g=self.game();m=g._summon(1,'EX1_tk34');self.play(g,'DREAM_05',m.uid)
        c=self.hold(g,'TIME_435');c.health_bonus=20;self.play(g,card=c,target=m.uid)
        self.assertEqual(m.owner,0);g.step(Action('end'));self.assertIn(m,g.players[0].board)
        g.step(Action('end'));self.assertNotIn(m,g.players[0].board)
    def test_hero_elusive_follows_control_change(self):
        g=self.game();m=g._summon(1,'EDR_846t3');c=self.hold(g,'TIME_435');c.health_bonus=20;self.play(g,card=c,target=m.uid)
        self.assertTrue(g._hero_elusive(0));self.assertFalse(g._hero_elusive(1))
    def test_countered_spell_still_counts_as_higher_play(self):
        g=self.game();tree=self.hold(g,'EDR_846');c=self.hold(g,'CORE_CS2_029');c.set_cost=9
        g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')];self.play(g,card=c,target=-2)
        self.assertTrue(tree.rule_state['dream_corrupted']);self.assertEqual(g.players[1].health,30)
    def test_failed_generation_rolls_back_whole_play(self):
        g=self.game();c=self.hold(g,'EDR_001');del g.cards['DREAM_01']
        before=copy.deepcopy(g.__dict__);a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        with self.assertRaises(UnsupportedCard):g.step(a)
        self.assertEqual(g.rng.getstate(),before['rng'].getstate())
        self.assertEqual(g.players,before['players']);self.assertEqual(g.uid,before['uid'])
