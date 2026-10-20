"""Physical paid minion plays validate exact buffs, tribes, expiry and Overload."""
import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards
from expanded.historical_battlecry_buffs import RULES,HistoricalBattlecryBuffs

class HistoricalBuffTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  records={c['id']:c for c in json.load(gzip.open(Path('data/standard/all_cards.json.gz'),'rt'))}
  self.g.cards.update({cid:records[cid] for cid in set(RULES)|{'CS2_106'}})
  manager=patch.dict(cards.RULES,RULES);manager.start();self.addCleanup(manager.stop)
  base=self.g.__class__
  if issubclass(base,HistoricalBattlecryBuffs):return
  class Harness(HistoricalBattlecryBuffs,base):
   def _targets_for(self,cid,owner,mode_override=None):
    mode=mode_override if mode_override is not None else cards.RULES.get(cid,('none',))[0]
    result=self._historical_buff_targets(cid,owner,mode)
    return result if result is not None else super()._targets_for(cid,owner,mode_override)
   def _effect(self,op,ctx):
    if not self._historical_buff_effect(op,ctx):return super()._effect(op,ctx)
  self.g.__class__=Harness
 def target(self,tribe=None,owner=0):
  m=self.g._summon(owner,'CORE_CS2_188')
  if tribe:
   cid='FIX_'+tribe+str(m.uid);self.g.cards[cid]=dict(self.g.cards[m.card_id],id=cid,races=[tribe]);m.card_id=cid
  return m
 def play(self,cid,target=0):
  c=self.g._add(0,cid);self.p.mana=10
  action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
  self.g.step(action);return next(m for m in self.p.minions if m.card_id==cid)
 def test_every_weapon_battlecry_exact_attack_and_durability(self):
  for cid in ('BAR_061','BOT_083','CFM_651','GVG_023','NEW1_024','ETC_102'):
   with self.subTest(cid=cid):
    self.setUp();self.g._equip(0,'CS2_106');before=dict(self.p.weapon);self.play(cid)
    attack,dur=RULES[cid][1][0][1:];self.assertEqual((self.p.weapon['attack'],self.p.weapon['durability']),(before['attack']+attack,before['durability']+dur))
 def test_weapon_missing_still_plays_body(self):
  for cid in ('BAR_061','ETC_102'):
   self.setUp();self.play(cid);self.assertIsNone(self.p.weapon)
 def test_every_targeted_fixed_buff_exact_values_and_keywords(self):
  targeted=[cid for cid,(mode,ops) in RULES.items() if mode!='none']
  tribes={'friendly_beast':'BEAST','friendly_undead':'UNDEAD','historical_friendly_mech':'MECHANICAL','historical_friendly_murloc':'MURLOC','historical_friendly_pirate':'PIRATE'}
  for cid in targeted:
   with self.subTest(cid=cid):
    self.setUp();mode,ops=RULES[cid];m=self.target(tribes.get(mode));a,h=m.attack,m.health;self.play(cid,m.uid)
    for op in ops:
     if op[0]=='buff':a+=op[1];h+=op[2]
     elif op[0]=='keyword':self.assertIn(op[1],m.keywords)
    self.assertEqual((m.attack,m.health),(a,h))
 def test_new_tribe_targets_reject_enemy_wrong_tribe_and_dormant(self):
  for cid,tribe in (('AT_096','MECHANICAL'),('DAL_077','MURLOC'),('VAC_937','PIRATE')):
   self.setUp();good=self.target(tribe);wrong=self.target('BEAST');enemy=self.target(tribe,1)
   self.assertEqual(self.g._targets_for(cid,0),[good.uid]);good.dormant=True
   self.assertEqual(self.g._targets_for(cid,0),[0])
 def test_all_tribe_inherits_target_eligibility(self):
  m=self.target('ALL');self.assertEqual(self.g._targets_for('AT_096',0),[m.uid]);self.assertEqual(self.g._targets_for('DAL_077',0),[m.uid])
 def test_no_eligible_target_allows_body_without_buff(self):
  self.play('DAL_077');self.assertEqual(len(self.p.minions),1);self.assertNotIn('POISONOUS',self.p.minions[0].keywords)
 def test_self_attack_bonus_expires_and_preserves_intrinsic_keywords(self):
  for cid,amount in (('BT_720',4),('GIL_803',3)):
   with self.subTest(cid=cid):
    self.setUp();m=self.play(cid);base=self.g.cards[cid]['attack'];self.assertEqual(m.attack,base+amount);self.assertIn('RUSH',m.keywords)
    if cid=='BT_720':self.assertIn('TAUNT',m.keywords)
    self.g.step(Action('end'));self.assertEqual(m.attack,base);self.assertEqual(m.temporary_attack,0)
 def test_mistrunner_overloads_after_untargeted_or_targeted_play(self):
  for targeting in (False,True):
   self.setUp();m=self.target() if targeting else None;self.play('YOP_022',m.uid if m else 0)
   self.assertEqual(self.p.overload_next,1);self.assertEqual(self.p.overloaded_total,1)
