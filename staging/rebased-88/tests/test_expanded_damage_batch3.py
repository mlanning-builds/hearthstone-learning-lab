import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DamageBatchCardsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def crowd(self,g):
        c=Card(g._new_id(),'JAIL_307');g.players[0].hand.append(c);g.step(Action('play',c.uid))
    def test_asphyxiodon_hits_one_enemy_only(self):
        g=self.game();g._summon(0,'DINO_132');a=g._summon(1,'CS3_025');b=g._summon(1,'CS3_025')
        g.step(Action('end'));self.assertEqual(sorted([a.health,b.health]),[1,6])
        self.assertEqual([p.health for p in g.players],[30,30])
    def test_asphyxiodon_empty_board_silence_and_enemy_turn(self):
        g=self.game();m=g._summon(0,'DINO_132');g.step(Action('end'))
        a=g._summon(1,'CS3_025');g.step(Action('end'));self.assertEqual(a.health,6)
        g._silence(m);g.step(Action('end'));self.assertEqual(a.health,6)
    def test_sporegnasher_poison_kills_high_health(self):
        g=self.game();s=g._summon(0,'EDR_110');m=g._summon(1,'DINO_132')
        s.health=0;g._settle();self.assertNotIn(m,g.players[1].minions)
        self.assertEqual(g.players[1].health,30)
    def test_sporegnasher_shield_and_immunity_prevent_poison(self):
        for keyword in ('DIVINE_SHIELD','IMMUNE'):
            g=self.game();s=g._summon(0,'EDR_110');m=g._summon(1,'CS3_025');m.keywords.add(keyword)
            s.health=0;g._settle();self.assertIn(m,g.players[1].minions);self.assertEqual(m.health,6)
    def test_sporegnasher_silenced_death_does_not_trigger(self):
        g=self.game();s=g._summon(0,'EDR_110');m=g._summon(1,'CS3_025');g._silence(s)
        s.health=0;g._settle();self.assertEqual(m.health,6)
    def test_crowd_hits_both_boards_twice_and_not_heroes(self):
        g=self.game();a=g._summon(0,'CS3_025');b=g._summon(1,'CS3_025');self.crowd(g)
        self.assertEqual((a.health,b.health),(2,2));self.assertEqual([p.health for p in g.players],[30,30])
    def test_crowd_shield_absorbs_only_first_hit(self):
        g=self.game();m=g._summon(1,'CS3_025');m.keywords.add('DIVINE_SHIELD');self.crowd(g)
        self.assertEqual(m.health,4);self.assertNotIn('DIVINE_SHIELD',m.keywords)
    def test_crowd_reborn_between_hits(self):
        g=self.game();m=g._summon(1,'CORE_WON_351');m.keywords.add('REBORN');self.crowd(g)
        self.assertEqual(g.players[1].minions,[])
    def test_crowd_discount_threshold_and_actual_payment(self):
        g=self.game();c=Card(g._new_id(),'JAIL_307')
        for size,expected in ((24,5),(25,3),(26,3),(24,5)):
            g.players[0].deck=['CORE_CS2_029']*size;self.assertEqual(g._cost(c,0),expected)
        g.players[0].deck=['CORE_CS2_029']*25;g.players[0].mana=3
        g.players[0].hand.append(c);g.step(Action('play',c.uid));self.assertEqual(g.players[0].mana,0)
    def test_crowd_countered_has_no_pulses(self):
        g=self.game();m=g._summon(1,'CS3_025');g.players[1].secrets.append(Card(g._new_id(),'CORE_EX1_287'))
        self.crowd(g);self.assertEqual(m.health,6)
