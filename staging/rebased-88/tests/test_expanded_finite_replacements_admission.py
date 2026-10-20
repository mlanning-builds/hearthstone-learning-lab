"""Normal paid registry paths for finite replacements and Prison release."""
import unittest
import test_expanded_imbue_azure_admission as fixtures
from expanded import Action

class FiniteReplacementAdmissionTests(unittest.TestCase):
 def game(self,hero,cid):return fixtures.ImbueAzureAdmissionTests().game(hero,cid)
 def play(self,g,cid,target=0):return fixtures.ImbueAzureAdmissionTests().play(g,cid,target)
 def test_deios_paid_weapon_deathrattle_and_power_repeat(self):
  g=self.game('ROGUE','TIME_064');p=g.players[0];p.deck=['CORE_EX1_162']*4
  self.play(g,'TIME_064');self.play(g,'JAIL_503');g._break_weapon(0);g._settle()
  self.assertEqual(len(p.hand),2)
  p.mana=10;g.step(Action('power'));self.assertEqual(p.weapon['card_id'],'CS2_082');self.assertEqual(p.hero_power_uses,1);self.assertEqual(p.mana,8)
 def test_plague_paid_charge_inserts_eight_blights_instead_of_hero_damage(self):
  g=self.game('DEATHKNIGHT','JAIL_443');p,q=g.players
  self.play(g,'JAIL_443');m=p.minions[0]
  g.step(Action('attack',m.uid,g.hero_id(1)))
  self.assertEqual(q.health,30);self.assertEqual([c.card_id for c in q.deck],['JAIL_443t']*8)
  self.assertEqual(len({c.uid for c in q.deck}),8);q.deck.insert(0,'CORE_EX1_162')
  g._draw(1);g._settle();self.assertEqual(q.health,14)
 def test_noggenfogger_paid_spell_reroutes_to_valid_friendly_target(self):
  g=self.game('MAGE','CORE_CFM_670');self.play(g,'CORE_CFM_670');g.rng.seed(3)
  self.play(g,'CORE_CS2_029',g.hero_id(1))
  self.assertEqual(g.players[0].health,24);self.assertEqual(g.players[1].health,30)
 def test_prison_paid_three_charges_release_pool_and_replay_one_card(self):
  g=self.game('MAGE','JAIL_887');p=g.players[0];self.play(g,'JAIL_887');loc=p.locations[0]
  for remaining in (2,1,0):
   c=g._add(0,'CORE_EX1_162');loc.ready_turn=g.turn;g.step(Action('activate',loc.uid,c.uid))
   self.assertEqual(loc.durability,remaining);self.assertNotIn(c,p.hand)
  self.assertFalse(p.locations)
  freed=next(m for m in p.minions if m.card_id=='JAIL_887t2')
  self.assertEqual(len(freed.rule_state['prison_cards']),3)
  g.step(Action('end'));self.assertEqual(len(freed.rule_state['prison_cards']),2)
  self.assertEqual(sum(m.card_id=='CORE_EX1_162' for m in p.minions),1)
  g.assert_invariants()

if __name__=='__main__':unittest.main()
