import unittest
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards
from expanded.historical_numeric import FIXED_BATTLECRIES
from engine.cards import UnsupportedCard

class HistoricalBattlecrySummonTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid,position=1):
  p=g.players[0];p.mana=10;c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.position==position))
  self.assertEqual(p.mana,10-cost);self.assertNotIn(c,p.hand);g.assert_invariants()
  return next(m for m in p.minions if m.card_id==cid)
 def test_all_paid_battlecries_summon_printed_children_to_right(self):
  for cid,(child,count) in FIXED_BATTLECRIES.items():
   with self.subTest(cid=cid):
    g=self.game();left=g._summon(0,'CS2_182');right=g._summon(0,'CS2_182');root=self.play(g,cid)
    self.assertEqual([m.card_id for m in g.players[0].board[2:-1]],[child]*count)
    self.assertEqual([g.players[0].board[0],g.players[0].board[1],g.players[0].board[-1]],[left,root,right])
    self.assertEqual(len({m.uid for m in g.players[0].board}),3+count)
    for m in g.players[0].board[2:-1]:
     self.assertEqual((m.attack,m.health),(g.cards[child]['attack'],g.cards[child]['health']))
 def test_last_board_slot_goes_to_paid_parent(self):
  for cid in FIXED_BATTLECRIES:
   with self.subTest(cid=cid):
    g=self.game()
    for _ in range(6):g._summon(0,'CS2_182')
    root=self.play(g,cid);self.assertEqual(len(g.players[0].board),7)
    self.assertEqual(g.players[0].board[1],root)
    self.assertFalse(any(m.card_id==FIXED_BATTLECRIES[cid][0] for m in g.players[0].board))
 def test_only_one_child_fits_after_parent(self):
  for cid,(child,count) in FIXED_BATTLECRIES.items():
   with self.subTest(cid=cid):
    g=self.game()
    for _ in range(5):g._summon(0,'CS2_182')
    self.play(g,cid);self.assertEqual(len(g.players[0].board),7)
    self.assertEqual(g.players[0].board[2].card_id,child)
    self.assertEqual(sum(m.card_id==child for m in g.players[0].board),1)
 def test_parent_hand_buffs_do_not_change_fixed_children(self):
  for cid,(child,count) in FIXED_BATTLECRIES.items():
   with self.subTest(cid=cid):
    g=self.game();c=g._add(0,cid);c.attack_bonus=3;c.health_bonus=4;g.players[0].mana=10
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    children=[m for m in g.players[0].minions if m.card_id==child]
    self.assertEqual([(m.attack,m.health) for m in children],[(g.cards[child]['attack'],g.cards[child]['health'])]*count)
 def test_recruiting_parent_does_not_execute_battlecry(self):
  for cid in FIXED_BATTLECRIES:
   with self.subTest(cid=cid):
    g=self.game();g._summon(0,cid);self.assertEqual([m.card_id for m in g.players[0].board],[cid])
 def test_child_paid_replay_has_no_parent_battlecry(self):
  for child,count in FIXED_BATTLECRIES.values():
   with self.subTest(child=child):
    g=self.game();self.play(g,child,0);self.assertEqual([m.card_id for m in g.players[0].board],[child])
 def test_printed_rush_and_taunt_are_kept(self):
  for cid,keyword in (('BAR_060','RUSH'),('KAR_710','TAUNT'),('OG_156','TAUNT'),('REV_936','TAUNT'),('SW_076','TAUNT')):
   with self.subTest(cid=cid):
    g=self.game();self.play(g,cid,0);child=FIXED_BATTLECRIES[cid][0]
    self.assertTrue(all(keyword in m.keywords for m in g.players[0].minions if m.card_id==child))
 def test_missing_right_summon_source_fails_explicitly(self):
  g=self.game();source=g._summon(0,'CFM_315');g.players[0].board.remove(source)
  with self.assertRaisesRegex(UnsupportedCard,'source'):
   g._effect(('summon_right','CFM_315t',1),dict(owner=0,source=source,target=0))
 def test_each_right_child_has_a_reaction_checkpoint(self):
  g=self.game();summon=g._summon;seen=[]
  def reacting(owner,cid,*args,**kwargs):
   if cid=='SW_076t':
    seen.append(g.players[0].armor)
   m=summon(owner,cid,*args,**kwargs)
   if cid=='SW_076t' and len(seen)==1:
    g._rule_events.append(('captured_effects',dict(operations=(('armor',1),),context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)),[]))
   return m
  with patch.object(g,'_summon',side_effect=reacting):self.play(g,'SW_076',0)
  self.assertEqual(seen,[0,1]);self.assertEqual(g.players[0].armor,1)
 def test_source_death_between_children_rejects_and_rolls_back_paid_play(self):
  g=self.game();summon=g._summon;c=g._add(0,'SW_076');g.players[0].mana=10
  def reacting(owner,cid,*args,**kwargs):
   m=summon(owner,cid,*args,**kwargs)
   if cid=='SW_076t':
    next(x for x in g.players[0].minions if x.card_id=='SW_076').health=0
   return m
  action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with patch.object(g,'_summon',side_effect=reacting):
   with self.assertRaisesRegex(UnsupportedCard,'source'):g.step(action)
  self.assertEqual(g.players[0].mana,10);self.assertFalse(g.players[0].board)
  self.assertTrue(any(x.uid==c.uid for x in g.players[0].hand))
