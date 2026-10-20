"""Paid finite quest, persistent entry grants and temporary-control boundaries."""
import unittest
from expanded import Action,cards
from expanded.selectors import effective_tribes
from expanded.decks import eligible
import test_expanded_imbue_azure_admission as fixtures

class MountainControlAdmissionTests(unittest.TestCase):
 def test_real_typed_minion_plays_complete_and_reward_has_two_adaptations(self):
  helper=fixtures.ImbueAzureAdmissionTests();g=helper.game('SHAMAN','TLC_229');helper.play(g,'TLC_229')
  records=cards.registry();used=set()
  for tribe in ('BEAST','DRAGON','ELEMENTAL','MURLOC','PIRATE','UNDEAD'):
   cid=next(cid for cid in sorted(cards.COLLECTIBLE_IDS) if cid not in used and cid!='TLC_229' and eligible(records[cid],'SHAMAN',(0,0,0)) and tribe in effective_tribes(records[cid]) and not set(records[cid].get('mechanics',()))&{'BATTLECRY','COLOSSAL'} and records[cid]['cost']<=10)
   used.add(cid);helper.play(g,cid)
  self.assertIsNone(g.players[0].quest);self.assertEqual(g.players[0].hand[-1].card_id,'TLC_229t14')
  helper.play(g,'TLC_229t14')
  for _ in range(2):g.step(Action('choose',choices=(0,)))
  self.assertEqual(len(g.players[0].ashalon_adaptations),2)
  g._bounce(g.players[0].minions[0]);g.assert_invariants()
 def test_paid_cursed_chains_returns_after_enemy_turn(self):
  helper=fixtures.ImbueAzureAdmissionTests();g=helper.game('WARLOCK','CATA_496');m=g._summon(1,'CORE_CS2_188')
  helper.play(g,'CATA_496',m.uid);self.assertEqual(m.owner,0);self.assertIn('CANT_ATTACK',g._effective_keywords(m))
  g.step(Action('end'));self.assertEqual(m.owner,0)
  g.step(Action('end'));self.assertEqual(m.owner,1);g.assert_invariants()
 def test_full_caster_board_does_not_offer_cursed_chains(self):
  helper=fixtures.ImbueAzureAdmissionTests();g=helper.game('WARLOCK','CATA_496')
  for _ in range(7):g._summon(0,'CORE_CS2_188')
  g._summon(1,'CORE_CS2_188');c=g._add(0,'CATA_496')
  self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
