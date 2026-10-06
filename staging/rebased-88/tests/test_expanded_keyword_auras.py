import unittest
from expanded import Game,Action,random_deck

class KeywordAuraTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.mana=p.max_mana=10
    def keywords(self,m):return self.g._effective_keywords(m)
    def test_survivalist_toggles_with_other_minions(self):
        m=self.g._summon(0,'CATA_613');health=m.health
        self.assertIn('IMMUNE',self.keywords(m));self.g._damage(m.uid,1);self.assertEqual(m.health,health)
        other=self.g._summon(0,'CORE_EX1_506');self.assertNotIn('IMMUNE',self.keywords(m))
        self.g._damage(m.uid,1);self.assertEqual(m.health,health-1)
        other.health=0;self.g._settle();self.assertIn('IMMUNE',self.keywords(m))
    def test_locations_do_not_disable_immunity(self):
        m=self.g._summon(0,'CATA_613');self.g._place_location(0,'CORE_REV_990')
        self.assertIn('IMMUNE',self.keywords(m))
    def test_silenced_survivalist_is_targetable(self):
        m=self.g._summon(1,'CATA_613');self.assertNotIn(m.uid,self.g._visible_targets(0))
        self.g._silence(m);self.assertIn(m.uid,self.g._visible_targets(0))
    def test_survivalist_copy_does_not_store_immunity(self):
        m=self.g._summon(0,'CATA_613');copy=self.g._summon(0,'CATA_613',copy_from=m)
        self.assertNotIn('IMMUNE',self.keywords(m));self.assertNotIn('IMMUNE',self.keywords(copy))
        self.assertNotIn('IMMUNE',copy.keywords)
    def test_lancer_grants_enemy_taunt_and_updates_targeting(self):
        lancer=self.g._summon(0,'CATA_898');enemy=self.g._summon(1,'CORE_EX1_506')
        self.assertIn('TAUNT',self.keywords(enemy));self.assertNotIn('TAUNT',self.keywords(lancer))
        self.assertEqual(self.g._attack_targets(),[enemy.uid])
    def test_silencing_recipient_keeps_aura_but_provider_removes_it(self):
        lancer=self.g._summon(0,'CATA_898');enemy=self.g._summon(1,'CORE_EX1_506')
        self.g._silence(enemy);self.assertIn('TAUNT',self.keywords(enemy))
        self.g._silence(lancer);self.assertNotIn('TAUNT',self.keywords(enemy))
    def test_multiple_sources_and_inherent_taunt_preserved(self):
        a=self.g._summon(0,'CATA_898');b=self.g._summon(0,'CATA_898')
        enemy=self.g._summon(1,'CORE_EX1_506');enemy.keywords.add('TAUNT')
        self.g._silence(a);self.assertIn('TAUNT',self.keywords(enemy))
        self.g._silence(b);self.assertIn('TAUNT',self.keywords(enemy))
    def test_aura_not_copied_as_permanent_enchantment(self):
        self.g._summon(0,'CATA_898');enemy=self.g._summon(1,'CORE_EX1_506')
        copy=self.g._summon(0,'CORE_EX1_506',copy_from=enemy)
        self.assertNotIn('TAUNT',self.keywords(copy))
    def test_immune_taunt_is_bypassed_and_observation_shows_both(self):
        self.g._summon(0,'CATA_898');enemy=self.g._summon(1,'CATA_613')
        self.assertEqual(self.g._attack_targets(),[-2])
        keywords=self.g.observe(0)['players'][1]['board'][0]['keywords']
        self.assertTrue({'IMMUNE','TAUNT'}<=set(keywords))
