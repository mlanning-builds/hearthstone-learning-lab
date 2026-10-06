"""Prepared scenarios for v0.8; execution belongs to the notebook user."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.cards import COLLECTIBLE_IDS


class CardBatchTests(unittest.TestCase):
    def setUp(self):
        self.g = Game([random_deck('MAGE',31), random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan')); self.g.step(Action('mulligan'))
        self.p, self.q = self.g.players
        self.p.hand = []; self.q.hand = []
        self.p.mana = self.p.max_mana = 10
        self.p.deck = ['CORE_CS2_029']*10
        self.q.deck = ['CORE_CS2_029']*10

    def give(self,cid):
        c = Card(self.g._new_id(),cid); self.p.hand.append(c); return c

    def play(self,cid,target=0):
        c = self.give(cid)
        pos = len(self.p.board) if self.g.cards[cid]['type'] in ('MINION','LOCATION') else -1
        self.g.step(Action('play',c.uid,target,pos))
        return c

    def kill(self,m):
        m.health = 0; self.g._settle()

    def test_ducklings_have_rush_and_respect_shared_board_capacity(self):
        loc = self.g._place_location(0,'CORE_REV_990')
        for _ in range(4): self.g._summon(0,'Core_CS2_200')
        self.play('EDR_492')
        ducks = [m for m in self.p.minions if m.card_id=='EDR_492t']
        self.assertEqual(len(ducks),1)
        self.assertIn('RUSH',ducks[0].keywords)
        self.assertEqual(len(self.p.board),7); self.assertIn(loc,self.p.board)

    def test_bronze_keeper_summons_shielded_dragon_at_end(self):
        self.play('CATA_476'); self.g.step(Action('end'))
        dragon = self.p.minions[-1]
        self.assertEqual((dragon.card_id,dragon.attack,dragon.health),('CATA_476t',6,6))
        self.assertIn('DIVINE_SHIELD',dragon.keywords)

    def test_end_damage_sources_do_not_use_spell_damage(self):
        self.g._summon(0,'CORE_EX1_012')
        self.g._summon(0,'CATA_999'); self.g._summon(0,'CORE_BT_493')
        self.g.step(Action('end'))
        self.assertEqual(self.q.health,20)

    def test_other_minion_end_buffs_skip_self_and_locations(self):
        mosquito = self.g._summon(0,'EDR_816')
        yesterloc = self.g._summon(0,'TIME_428')
        location = self.g._place_location(0,'CORE_REV_990')
        self.g.step(Action('end'))
        self.assertEqual((mosquito.attack,mosquito.max_health),(1,3))
        self.assertEqual((yesterloc.attack,yesterloc.max_health),(4,1))
        self.assertEqual(location.durability,3)

    def test_end_hand_buff_only_buffs_minions(self):
        self.g._summon(0,'TIME_100')
        minion = self.give('Core_CS2_200'); spell = self.give('CORE_CS2_029')
        self.g.step(Action('end'))
        self.assertEqual((minion.attack_bonus,minion.health_bonus),(1,1))
        self.assertEqual((spell.attack_bonus,spell.health_bonus),(0,0))

    def test_caretaker_heals_both_heroes_up_to_maximum(self):
        self.p.health=20; self.q.health=29
        self.g._summon(0,'EDR_971'); self.g.step(Action('end'))
        self.assertEqual((self.p.health,self.q.health),(23,30))

    def test_moonwell_damage_bonus_does_not_increase_healing(self):
        self.p.health=20
        self.g._summon(0,'CORE_EX1_012')
        friendly=self.g._summon(0,'Core_CS2_200'); friendly.health=2
        enemy=self.g._summon(1,'Core_CS2_200')
        location=self.g._place_location(1,'CORE_REV_990')
        self.play('EDR_476')
        self.assertEqual((self.p.health,self.q.health),(24,25))
        self.assertEqual((friendly.health,enemy.health),(6,2))
        self.assertIn(location,self.q.board)

    def test_avatar_death_hits_minions_while_imp_hits_all_enemies(self):
        self.g._summon(0,'CORE_EX1_012')
        enemy=self.g._summon(1,'Core_CS2_200')
        self.kill(self.g._summon(0,'FIR_778'))
        self.assertNotIn(enemy,self.q.board); self.assertEqual(self.q.health,30)
        enemy=self.g._summon(1,'Core_CS2_200')
        self.kill(self.g._summon(0,'JAIL_007'))
        self.assertEqual((self.q.health,enemy.health),(28,5))

    def test_fire_tutor_and_no_match_do_not_fatigue(self):
        self.p.deck=['Core_CS2_200','CORE_CS2_029']
        self.kill(self.g._summon(0,'FIR_929'))
        self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
        self.kill(self.g._summon(0,'FIR_929'))
        self.assertEqual(len(self.p.hand),1); self.assertEqual(self.p.fatigue,0)

    def test_generated_missiles_play_with_spell_damage_but_are_not_deck_cards(self):
        self.kill(self.g._summon(0,'CORE_DRG_107'))
        self.g._summon(0,'CORE_EX1_012')
        c=self.p.hand[0]
        self.assertEqual(c.card_id,'EX1_277')
        self.g.step(Action('play',c.uid))
        self.assertEqual(self.q.health,26)
        self.assertNotIn('EX1_277',COLLECTIBLE_IDS)
        self.assertNotIn('WW_001t',COLLECTIBLE_IDS)

    def test_contraband_generation_stops_at_hand_limit(self):
        for _ in range(8): self.give('CORE_CS2_029')
        self.play('JAIL_312')
        self.assertEqual(len(self.p.hand),10)
        self.assertEqual(sum(c.card_id=='EX1_277' for c in self.p.hand),2)

    def test_bookie_coin_can_be_played(self):
        self.kill(self.g._summon(0,'JAIL_720')); self.p.mana=2
        coin=self.p.hand[0]
        self.assertEqual(coin.card_id,'TOKEN_COIN')
        self.g.step(Action('play',coin.uid))
        self.assertEqual(self.p.mana,3)

    def test_cranium_counts_hand_after_its_own_removal(self):
        self.give('CORE_CS2_029'); self.give('CORE_CS2_029')
        self.play('JAIL_513')
        self.assertEqual(self.p.minions[0].health,3)
        self.assertIn('TAUNT',self.p.minions[0].keywords)

    def test_epoch_copies_buffs_without_double_counting_aura(self):
        self.g._summon(0,'CORE_EX1_162')
        c=self.give('TIME_605'); c.attack_bonus=2; c.health_bonus=1
        self.g.step(Action('play',c.uid,0,1))
        original,clone=self.p.minions[1:]
        self.assertEqual((original.attack,clone.attack),(6,5))
        self.assertEqual((original.health,clone.health),(5,5))
        self.assertEqual(original.keywords,clone.keywords)

    def test_troubled_double_requires_combo(self):
        self.play('TIME_710'); self.play('TIME_710')
        self.assertEqual(len(self.p.minions),3)
        self.assertTrue(all('STEALTH' in m.keywords for m in self.p.minions))

    def test_paradox_summons_do_not_repeat_battlecry(self):
        self.play('TIME_059')
        self.assertEqual(len(self.p.minions),3)
        self.assertTrue(all(m.card_id=='TIME_059' and 'ELUSIVE' in m.keywords for m in self.p.minions))

    def test_cinderfin_death_chain_produces_two_missiles(self):
        self.kill(self.g._summon(0,'TLC_225'))
        cinder=self.p.minions[0]
        self.assertEqual(cinder.card_id,'TLC_249')
        self.kill(cinder)
        self.assertEqual(self.q.health,28); self.assertEqual(self.p.board,[])

    def test_longneck_summons_before_buffing_board(self):
        other=self.g._summon(0,'Core_CS2_200')
        self.kill(self.g._summon(0,'DINO_130'))
        beast=self.p.minions[-1]
        self.assertEqual((beast.card_id,beast.attack,beast.health),('DINO_130t',4,4))
        self.assertEqual((other.attack,other.health),(7,8))

    def test_eggs_fill_only_available_slots(self):
        self.g._place_location(0,'CORE_REV_990')
        for _ in range(4): self.g._summon(0,'Core_CS2_200')
        self.kill(self.g._summon(0,'TLC_237'))
        self.assertEqual(len(self.p.board),7)
        self.assertEqual(sum(m.card_id=='TLC_237t' for m in self.p.minions),2)

    def test_wrangler_reborn_does_not_repeat_reborn(self):
        self.kill(self.g._summon(0,'TLC_443'))
        reborn=next(m for m in self.p.minions if m.card_id=='TLC_443')
        self.assertNotIn('REBORN',reborn.keywords)
        self.kill(reborn)
        self.assertEqual([m.card_id for m in self.p.minions],['TLC_443t','TLC_443t'])
        self.assertTrue(all('TAUNT' in m.keywords for m in self.p.minions))

    def test_blob_tokens_keep_order_and_distinct_keywords(self):
        self.kill(self.g._summon(0,'TLC_468'))
        poison,taunt=self.p.minions
        self.assertEqual([poison.card_id,taunt.card_id],['TLC_468t1','TLC_468t2'])
        self.assertIn('POISONOUS',poison.keywords); self.assertNotIn('TAUNT',poison.keywords)
        self.assertIn('TAUNT',taunt.keywords); self.assertNotIn('POISONOUS',taunt.keywords)

    def test_rockskipper_generates_playable_damage_spell(self):
        self.play('TLC_427'); rock=self.p.hand[0]
        self.assertEqual(rock.card_id,'WW_001t')
        self.g.step(Action('play',rock.uid,-2))
        self.assertEqual(self.q.health,27)

    def test_beast_discount_consumes_once_and_expires(self):
        target=self.g._summon(1,'Core_CS2_200')
        self.play('TLC_823',target.uid)
        beast=self.give('EDR_492'); other=self.give('Core_CS2_200')
        self.assertEqual(self.g._cost(beast,0),2)
        self.assertEqual(self.g._cost(other,0),6)
        self.g.step(Action('play',beast.uid,0,0))
        self.assertEqual(self.p.cost_effects,[])
        self.play('TLC_823',target.uid)
        self.g.step(Action('end'))
        self.assertEqual(self.p.cost_effects,[])

    def test_drink_blood_heals_and_refreshes_spent_hero_power(self):
        self.p.hero_class='DEATHKNIGHT'; self.p.health=20
        self.g.step(Action('power'))
        target=self.g._summon(1,'Core_CS2_200')
        self.play('JAIL_441',target.uid)
        self.assertEqual(self.p.health,23); self.assertFalse(self.p.power_used)
        self.g.step(Action('power'))
        self.assertEqual(self.p.mana,4); self.assertTrue(self.p.power_used)

    def test_staff_break_destroys_minions_but_leaves_locations(self):
        location=self.g._place_location(0,'CORE_REV_990')
        self.g._summon(0,'Core_CS2_200'); self.g._summon(1,'Core_CS2_200')
        self.play('TLC_EVENT_402')
        self.g._break_weapon(0); self.g._settle()
        self.assertEqual(self.p.board,[location]); self.assertEqual(self.q.board,[])
        self.assertIsNone(self.p.weapon)

    def test_assistant_targets_only_friendly_beasts(self):
        beast=self.g._summon(0,'DINO_130t')
        other=self.g._summon(0,'Core_CS2_200')
        enemy=self.g._summon(1,'DINO_130t')
        c=self.give('DINO_419')
        targets={a.target for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid}
        self.assertEqual(targets,{beast.uid})
        self.g.step(Action('play',c.uid,beast.uid,len(self.p.board)))
        self.assertEqual((beast.attack,beast.health),(5,5))
        self.assertIn('RUSH',beast.keywords)
