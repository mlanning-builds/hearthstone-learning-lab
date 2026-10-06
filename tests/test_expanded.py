"""Prepared rule fixtures. Not executed by the assistant at the user's request."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, Deck, random_deck, validate
from expanded.cards import registry, COLLECTIBLE_IDS, RULES
from expanded.game import Card, TOTEMS
from engine.cards import UnsupportedCard
from standard.catalog import CLASSES

class ExpandedRulesTests(unittest.TestCase):
    def game(self,hero='MAGE',enemy='WARRIOR'):
        self.g=Game([random_deck(hero,31),random_deck(enemy,53)],seed=71)
        self.g.step(Action('mulligan')); self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.q.hand=[];self.p.mana=self.p.max_mana=10
        return self.g

    def give(self,cid):
        c=Card(self.g._new_id(),cid);self.p.hand.append(c);return c

    def play(self,cid,target=0):
        c=self.give(cid); pos=len(self.p.board) if self.g.cards[cid]['type']=='MINION' else -1
        self.g.step(Action('play',c.uid,target,pos));return c

    def test_all_class_decks_and_hidden_information(self):
        for hero in CLASSES:
            with self.subTest(hero=hero):
                deck=random_deck(hero,13); self.assertEqual(validate(deck),[])
                g=Game([deck,random_deck('WARRIOR',19)])
                obs=g.observe(0)
                self.assertEqual(obs['players'][0]['hero_class'],hero)
                self.assertNotIn('hand',obs['players'][1])
                self.assertNotIn('starting_deck',obs['players'][1])
                self.assertNotIn('deck',obs['players'][0])

    def test_power_warrior(self):
        self.game('WARRIOR');self.g.step(Action('power'))
        self.assertEqual((self.p.armor,self.p.mana),(2,8))
        self.assertNotIn(Action('power'),self.g.legal_actions())

    def test_power_hunter(self):
        self.game('HUNTER');self.g.step(Action('power'));self.assertEqual(self.q.health,28)

    def test_power_priest(self):
        self.game('PRIEST');self.p.health=25;self.g.step(Action('power',target=-1));self.assertEqual(self.p.health,27)

    def test_power_mage(self):
        self.game('MAGE');self.g.step(Action('power',target=-2));self.assertEqual(self.q.health,29)

    def test_power_warlock(self):
        self.game('WARLOCK');self.g.step(Action('power'));self.assertEqual((self.p.health,len(self.p.hand)),(28,1))

    def test_power_rogue_weapon_has_no_lifesteal(self):
        self.game('ROGUE');self.p.health=20;self.g.step(Action('power'))
        self.assertEqual((self.p.weapon['attack'],self.p.weapon['durability']),(1,2))
        self.g.step(Action('attack',-1,-2));self.assertEqual((self.p.health,self.q.health),(20,29))
        self.assertEqual(self.p.weapon['durability'],1)

    def test_power_druid_attack_expires_armor_persists(self):
        self.game('DRUID');self.g.step(Action('power'));self.g.step(Action('attack',-1,-2));self.g.step(Action('end'))
        self.assertEqual((self.p.temporary_attack,self.p.armor,self.q.health),(0,1,29))

    def test_power_demon_hunter_cost(self):
        self.game('DEMONHUNTER');self.g.step(Action('power'));self.assertEqual(self.p.mana,9)
        self.g.step(Action('attack',-1,-2));self.assertEqual(self.q.health,29)

    def test_power_paladin_and_full_board(self):
        self.game('PALADIN');self.g.step(Action('power'));self.assertEqual(self.p.board[0].card_id,'CS2_101t')
        self.p.power_used=False
        for _ in range(6):self.g._summon(0,'CS2_101t')
        self.assertNotIn(Action('power'),self.g.legal_actions())

    def test_power_death_knight(self):
        self.game('DEATHKNIGHT');self.g.step(Action('power'));m=self.p.board[0]
        self.assertIn(Action('attack',m.uid,-2),self.g.legal_actions())
        self.g.step(Action('end'));self.assertEqual((len(self.p.board),self.p.corpses),(0,1))

    def test_power_shaman_no_duplicate_basic_totems(self):
        self.game('SHAMAN')
        for _ in range(4):
            self.p.mana=10;self.p.power_used=False;self.g.step(Action('power'))
        self.assertEqual({m.card_id for m in self.p.board},set(TOTEMS))
        self.p.power_used=False;self.assertNotIn(Action('power'),self.g.legal_actions())

    def test_healing_and_strength_totem_triggers(self):
        self.game('SHAMAN');m=self.g._summon(0,'Core_CS2_200');m.health=5
        self.g._summon(0,'NEW1_009');self.g.step(Action('end'));self.assertEqual(m.health,6)
        self.game('SHAMAN');m=self.g._summon(0,'Core_CS2_200');self.g._summon(0,'CS2_058')
        self.g.step(Action('end'));self.assertEqual(m.attack,7)

    def test_spell_damage_does_not_increase_mage_power(self):
        self.game();self.g._summon(0,'CORE_EX1_012')
        self.g.step(Action('power',target=-2));self.assertEqual(self.q.health,29)
        self.play('CORE_CS2_029',-2);self.assertEqual(self.q.health,22)

    def test_overload_locks_next_turn_only(self):
        self.game('SHAMAN');self.p.mana=self.p.max_mana=3
        self.play('CORE_EX1_238',-2);self.assertEqual(self.p.overload_next,1)
        self.g.step(Action('end'));self.g.step(Action('end'))
        self.assertEqual((self.p.mana,self.p.locked_mana),(3,1))
        self.g.step(Action('end'));self.g.step(Action('end'));self.assertEqual((self.p.mana,self.p.locked_mana),(5,0))

    def test_stealth_untargetable_but_aoe_hits(self):
        self.game();m=self.g._summon(1,'CORE_EX1_028');self.g._summon(0,'Core_CS2_200').summoned_turn=0
        self.give('CORE_CS2_029')
        self.assertFalse(any(a.target==m.uid for a in self.g.legal_actions()))
        self.play('CORE_CS2_032');self.assertNotIn(m,self.q.board)

    def test_stealth_removed_by_attack(self):
        self.game();m=self.g._summon(0,'CORE_EX1_010');m.summoned_turn=0
        self.g.step(Action('attack',m.uid,-2));self.assertNotIn('STEALTH',m.keywords)

    def test_elusive_blocks_spells_and_power_but_not_battlecry(self):
        self.game();m=self.g._summon(1,'CORE_NEW1_023');self.give('CORE_CS2_029');archer=self.give('CORE_CS2_189')
        targeted=[a for a in self.g.legal_actions() if a.target==m.uid]
        self.assertTrue(targeted);self.assertTrue(all(a.kind=='play' and a.source==archer.uid for a in targeted))

    def test_frostbolt_dead_target_does_not_fail(self):
        self.game();m=self.g._summon(1,'CS2_101t');self.play('CORE_CS2_024',m.uid);self.assertNotIn(m,self.q.board)

    def test_freeze_enemy_skips_next_attack_turn(self):
        self.game();m=self.g._summon(1,'Core_CS2_200');self.play('CORE_CS2_024',m.uid)
        self.g.step(Action('end'));self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in self.g.legal_actions()))
        self.g.step(Action('end'));self.assertEqual(m.frozen_until,-1)

    def test_freeze_after_attack_lasts_through_next_own_turn(self):
        self.game();m=self.g._summon(0,'Core_CS2_200');m.summoned_turn=0
        self.g.step(Action('attack',m.uid,-2));self.g._freeze(m.uid)
        self.g.step(Action('end'));self.g.step(Action('end'));self.assertGreaterEqual(m.frozen_until,0)
        self.g.step(Action('end'));self.assertEqual(m.frozen_until,-1)

    def test_outcast_and_combo(self):
        self.game('DEMONHUNTER');self.play('CORE_BT_491');self.assertEqual(len(self.p.hand),2)
        self.game('ROGUE');self.play('CORE_EX1_131');self.assertEqual(len(self.p.board),1)
        self.play('CORE_EX1_131');self.assertEqual(len(self.p.board),3)

    def test_outcast_eye_beam_cost_and_lifesteal(self):
        self.game('DEMONHUNTER');self.p.health=20;m=self.g._summon(1,'Core_CS2_200');self.p.mana=1
        self.play('CORE_BT_801',m.uid);self.assertEqual((self.p.mana,self.p.health,m.health),(0,23,4))

    def test_draw_on_kill_shield_and_survival(self):
        self.game('WARLOCK');m=self.g._summon(1,'CS2_101t');self.play('CORE_EX1_302',m.uid);self.assertEqual(len(self.p.hand),1)
        self.game('WARLOCK');m=self.g._summon(1,'CORE_GVG_085');self.play('CORE_EX1_302',m.uid);self.assertEqual(len(self.p.hand),0)
        self.game('WARRIOR');m=self.g._summon(1,'Core_CS2_200');self.play('CORE_EX1_391',m.uid);self.assertEqual(len(self.p.hand),1)

    def test_generated_flame_elemental_can_be_played(self):
        self.game();self.play('CORE_UNG_809');token=self.p.hand[0]
        self.assertEqual(token.card_id,'UNG_809t1');self.g.step(Action('play',token.uid,0,len(self.p.board)))
        self.assertEqual(len(self.p.board),2)

    def test_wrong_class_and_unknown_effect_rejected(self):
        d=random_deck('WARRIOR',22);wrong=Deck('WARRIOR',('CORE_CS2_029',)+d.cards[1:])
        self.assertTrue(validate(wrong))
        bad=Deck('WARRIOR',('BE_036',)+d.cards[1:])
        with self.assertRaises(UnsupportedCard):Game([bad,d])

    def test_failure_rolls_back_rng_and_state(self):
        self.game();c=self.give('CORE_CS2_029');before=copy.deepcopy(self.g.__dict__)
        with patch.object(Game,'_effect',side_effect=RuntimeError('injected')):
            with self.assertRaises(RuntimeError):self.g.step(Action('play',c.uid,-2))
        self.assertEqual(self.g.players,before['players']);self.assertEqual(self.g.history,before['history'])
        self.assertEqual(self.g.rng.getstate(),before['rng'].getstate())

    def test_new_deathrattles(self):
        self.game();m=self.g._summon(0,'CORE_EX1_012');m.health=0;self.g._settle();self.assertEqual(len(self.p.hand),1)
        self.game();m=self.g._summon(0,'CORE_RLK_657');m.health=0;self.g._settle();self.assertEqual(self.p.armor,6)
        self.game();m=self.g._summon(0,'CORE_ICC_214');enemy=self.g._summon(1,'Core_CS2_200');m.health=0;self.g._settle();self.assertNotIn(enemy,self.q.board)

    def test_implemented_registry_has_all_declared_cards(self):
        cards=registry();self.assertTrue(COLLECTIBLE_IDS.issubset(cards));self.assertTrue(set(RULES).issubset(cards))


    def test_army_raises_only_available_corpses_and_tokens_do_not_refund(self):
        self.game('DEATHKNIGHT');self.p.corpses=3
        self.play('RLK_060')
        self.assertEqual(self.p.corpses,0)
        self.assertEqual([m.card_id for m in self.p.board],['RLK_008t']*3)
        enemy=self.g._summon(1,'Core_CS2_200')
        for m in self.p.board:
            self.assertIn(Action('attack',m.uid,enemy.uid),self.g.legal_actions())
            self.assertNotIn(Action('attack',m.uid,-2),self.g.legal_actions())
            m.health=0
        self.g._settle();self.assertEqual(self.p.corpses,0)

    def test_army_full_board_does_not_waste_corpses(self):
        for occupied in (5,7):
            with self.subTest(occupied=occupied):
                self.game('DEATHKNIGHT');self.p.corpses=8
                for _ in range(occupied):self.g._summon(0,'Core_CS2_200')
                self.play('RLK_060')
                self.assertEqual(len(self.p.board),7)
                self.assertEqual(self.p.corpses,8-(7-occupied))

    def test_boneguard_reserves_its_own_board_slot(self):
        self.game('DEATHKNIGHT');self.p.corpses=8
        self.g._summon(0,'Core_CS2_200');self.play('CORE_RLK_506')
        self.assertEqual(self.p.corpses,3)
        self.assertEqual([m.card_id for m in self.p.board[2:]],['RLK_061t']*5)
        for m in self.p.board[2:]:m.health=0
        self.g._settle();self.assertEqual(self.p.corpses,3)

    def test_tomb_guardians_threshold_and_reborn(self):
        for corpses in (3,4):
            with self.subTest(corpses=corpses):
                self.game('DEATHKNIGHT');self.p.corpses=corpses
                self.play('CORE_RLK_118')
                self.assertEqual(self.p.corpses,0 if corpses==4 else 3)
                self.assertEqual(len(self.p.board),2)
                self.assertTrue(all(('REBORN' in m.keywords)==(corpses==4) for m in self.p.board))
                self.p.board[0].health=0;self.g._settle()
                self.assertEqual(self.p.corpses,1 if corpses==4 else 4)
                self.assertEqual(len(self.p.board),2 if corpses==4 else 1)
                if corpses==4:
                    self.assertEqual(self.p.board[0].health,1)
                    self.assertNotIn('REBORN',self.p.board[0].keywords)

    def test_tomb_guardians_full_board_and_one_slot(self):
        for occupied in (6,7):
            with self.subTest(occupied=occupied):
                self.game('DEATHKNIGHT');self.p.corpses=4
                for _ in range(occupied):self.g._summon(0,'Core_CS2_200')
                self.play('CORE_RLK_118')
                self.assertEqual(len(self.p.board),7)
                self.assertEqual(self.p.corpses,0 if occupied==6 else 4)
                if occupied==6:self.assertIn('REBORN',self.p.board[-1].keywords)

    def test_necromancer_end_turn_spends_one_and_stops_when_full(self):
        self.game('DEATHKNIGHT');self.p.corpses=2
        self.g._summon(0,'RLK_061');self.g.step(Action('end'))
        self.assertEqual(self.p.corpses,1)
        self.assertEqual(self.p.board[-1].card_id,'RLK_061t')
        self.g.step(Action('end'))
        while len(self.p.board)<7:self.g._summon(0,'Core_CS2_200')
        self.g.step(Action('end'));self.assertEqual(self.p.corpses,1)

    def test_frostwyrm_fury_damage_freeze_and_summon(self):
        self.game('DEATHKNIGHT');enemy=self.g._summon(1,'Core_CS2_200')
        self.play('CORE_RLK_063',-2)
        self.assertEqual(self.q.health,25)
        self.assertGreaterEqual(enemy.frozen_until,self.g.turn)
        self.assertEqual(self.p.board[-1].card_id,'RLK_063t')
        self.assertEqual((self.p.board[-1].attack,self.p.board[-1].health),(5,5))

    def test_deathrattle_summons_keep_position_and_obey_board_limit(self):
        for cid,token,count in [('CORE_AV_337','AV_337t',2),('CORE_LOOT_368','CS2_065',3)]:
            with self.subTest(card=cid):
                self.game()
                left=self.g._summon(0,'Core_CS2_200')
                dying=self.g._summon(0,cid)
                right=self.g._summon(0,'Core_CS2_200')
                dying.health=0;self.g._settle()
                self.assertEqual([m.card_id for m in self.p.board],[left.card_id]+[token]*count+[right.card_id])
                self.assertTrue(all('TAUNT' in m.keywords for m in self.p.board[1:-1]))
                self.game();dying=self.g._summon(0,cid)
                for _ in range(6):self.g._summon(0,'Core_CS2_200')
                dying.health=0;self.g._settle()
                self.assertEqual(len(self.p.board),7)
                self.assertEqual(self.p.board[0].card_id,token)

    def test_lightshower_heals_only_friendly_characters(self):
        self.game();self.p.health=15;self.q.health=15
        friend=self.g._summon(0,'Core_CS2_200');friend.health=1
        enemy=self.g._summon(1,'Core_CS2_200');enemy.health=1
        dying=self.g._summon(0,'CORE_BAR_310');dying.health=0;self.g._settle()
        self.assertEqual((self.p.health,self.q.health),(23,15))
        self.assertEqual((friend.health,enemy.health),(friend.max_health,1))

    def test_prize_vendor_battlecry_and_deathrattle_draw_for_both(self):
        self.game();self.play('CORE_DMF_067')
        self.assertEqual((len(self.p.hand),len(self.q.hand)),(1,1))
        self.p.board[0].health=0;self.g._settle()
        self.assertEqual((len(self.p.hand),len(self.q.hand)),(2,2))

    def test_curator_draws_distinct_matching_cards_without_empty_match_fatigue(self):
        self.game()
        self.p.deck=['CORE_EX1_506','CORE_AV_337','RLK_063t','CORE_CS2_029']
        self.play('CORE_KAR_061')
        self.assertEqual({c.card_id for c in self.p.hand},{'CORE_EX1_506','CORE_AV_337','RLK_063t'})
        self.assertEqual(self.p.deck,['CORE_CS2_029'])
        self.p.mana=10;self.play('CORE_KAR_061')
        self.assertEqual(self.p.fatigue,0)

    def test_immortalized_in_stone_order_and_limited_space(self):
        self.game('PALADIN');self.play('CORE_TSC_076')
        self.assertEqual([(m.attack,m.health) for m in self.p.board],[(4,8),(2,4),(1,2)])
        self.game('PALADIN')
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        self.play('CORE_TSC_076')
        self.assertEqual(len(self.p.board),7)
        self.assertEqual(self.p.board[-1].card_id,'TSC_076t3')

    def test_end_turn_helpers_buff_other_draw_and_damage(self):
        self.game()
        source=self.g._summon(0,'CORE_ICC_210')
        friend=self.g._summon(0,'Core_CS2_200')
        self.g._summon(0,'CORE_ULD_133');self.g._summon(0,'CORE_YOP_034')
        enemy=self.g._summon(1,'Core_CS2_200')
        before={m.uid:(m.attack,m.health) for m in self.p.board}
        self.g.step(Action('end'))
        self.assertEqual((source.attack,source.health),before[source.uid])
        self.assertEqual(sum(m.attack-before[m.uid][0] for m in self.p.board),1)
        self.assertEqual(len(self.p.hand),1)
        self.assertNotIn(enemy,self.q.board)
        self.game();self.g._summon(0,'CORE_ULD_133');self.p.mana=0
        self.g.step(Action('end'));self.assertEqual(len(self.p.hand),0)

    def test_all_classes_track_corpses_with_explicit_raised_exceptions(self):
        for hero in CLASSES:
            with self.subTest(hero=hero):
                self.game(hero)
                for cid in ('Core_CS2_200','RLK_008t','RLK_061t'):
                    self.g._summon(0,cid).health=0
                self.g._settle();self.assertEqual(self.p.corpses,1)

if __name__=='__main__':unittest.main()

