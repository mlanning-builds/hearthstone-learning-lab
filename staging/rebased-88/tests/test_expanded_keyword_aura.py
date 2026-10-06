import unittest
from expanded import Game,Action,random_deck

class KeywordAuraTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:p.hand=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10
        return g
    def test_aura_includes_source_and_friends_not_enemies(self):
        g=self.game();a=g._summon(0,'JAIL_459');friend=g._summon(0,'CORE_WON_351');enemy=g._summon(1,'CORE_WON_351')
        for m in (a,friend):self.assertIn('POISONOUS',g._effective_keywords(m));self.assertNotIn('POISONOUS',m.keywords)
        self.assertNotIn('POISONOUS',g._effective_keywords(enemy))
    def test_rush_poison_combat_kills_large_minion(self):
        g=self.game();a=g._summon(0,'JAIL_459');enemy=g._summon(1,'DINO_132')
        g.step(Action('attack',a.uid,enemy.uid));self.assertNotIn(enemy,g.players[1].minions);self.assertEqual(a.health,1)
    def test_recipient_silence_does_not_remove_external_aura(self):
        g=self.game();a=g._summon(0,'JAIL_459');m=g._summon(0,'CORE_WON_351');g._silence(m)
        self.assertIn('POISONOUS',g._effective_keywords(m));g._silence(a);self.assertNotIn('POISONOUS',g._effective_keywords(m))
    def test_aura_removal_does_not_leave_poison_on_copies(self):
        g=self.game();a=g._summon(0,'JAIL_459');m=g._summon(0,'CORE_WON_351');copy=g._summon(0,m.card_id,copy_from=m)
        self.assertIn('POISONOUS',g._effective_keywords(copy));a.health=0;g._settle()
        self.assertNotIn('POISONOUS',g._effective_keywords(copy));self.assertNotIn('POISONOUS',copy.keywords)
    def test_multiple_sources_and_public_keywords(self):
        g=self.game();a=g._summon(0,'JAIL_459');b=g._summon(0,'JAIL_459');g._silence(a)
        for viewer in (0,1):
            entity=next(x for x in g.observe(viewer)['players'][0]['board'] if x['uid']==a.uid)
            self.assertIn('POISONOUS',entity['keywords'])
        g._silence(b);self.assertNotIn('POISONOUS',g._effective_keywords(a))
    def test_divine_shield_prevents_aura_poison_kill(self):
        g=self.game();a=g._summon(0,'JAIL_459');enemy=g._summon(1,'DINO_132');enemy.keywords.add('DIVINE_SHIELD')
        g.step(Action('attack',a.uid,enemy.uid));self.assertIn(enemy,g.players[1].minions);self.assertEqual(enemy.health,12)
