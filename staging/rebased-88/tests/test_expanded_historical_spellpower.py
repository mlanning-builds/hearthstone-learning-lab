import sys, unittest
sys.path.insert(0, '.');sys.path.insert(0, 'tests')
from expanded import cards, Action
from expanded import historical_spellpower as rules
import test_expanded_generation as fixtures

class HistoricalSpellpowerTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  card=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  return next(m for m in g.players[0].minions if m.card_id==cid)
 def test_all_printed_spellpower_amounts_stack_then_silence(self):
  for cid,amount in rules.SPELL_DAMAGE_VALUES.items():
   with self.subTest(cid=cid):
    g=self.game();m=g._summon(0,cid)
    self.assertEqual(g._spell_damage(0),amount)
    other=g._summon(0,'SCH_310');self.assertEqual(g._spell_damage(0),amount+1)
    g._silence(m);self.assertEqual(g._spell_damage(0),1)
    g._silence(other);self.assertEqual(g._spell_damage(0),0)
 def test_printed_two_overrides_boolean_archive_tag_in_damage(self):
  for cid in ('BOT_604','CFM_039','GIL_121','ICC_856','OG_082','SW_061','WON_365'):
   with self.subTest(cid=cid):
    g=self.game();self.play(g,cid);before=g.players[1].health
    spell=g._add(0,'CORE_CS2_029');g.players[0].mana=10
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==spell.uid and a.target==g.hero_id(1)))
    self.assertEqual(g.players[1].health,before-8)
 def test_restriction_removed_by_silence(self):
  for cid in rules.ATTACK_RESTRICTED:
   with self.subTest(cid=cid):
    g=self.game();m=self.play(g,cid);m.summoned_turn=-1
    self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
    g._silence(m)
    self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
 def test_spellzerker_changes_with_damage_healing_and_silence(self):
  g=self.game();m=self.play(g,'TRL_312');self.assertEqual(g._spell_damage(0),0)
  m.health-=1;self.assertEqual(g._spell_damage(0),2)
  m.health=m.max_health;self.assertEqual(g._spell_damage(0),0)
  m.health-=1;g._silence(m);self.assertEqual(g._spell_damage(0),0)
 def test_azure_drake_draw_and_squallhunter_overload(self):
  g=self.game();g.players[0].deck.append('CS2_182')
  before=len(g.players[0].hand);self.play(g,'EX1_284')
  self.assertEqual(len(g.players[0].hand),before+1)
  self.play(g,'DRG_211');self.assertEqual(g.players[0].overload_next,2)
 def test_generated_only_and_hash_reviewed(self):
  registry=cards.registry()
  self.assertEqual(len(rules.GENERATED_IDS),25)
  self.assertFalse(rules.GENERATED_IDS & cards.COLLECTIBLE_IDS)
  self.assertTrue(rules.GENERATED_IDS <= set(registry))

if __name__=='__main__':unittest.main()
