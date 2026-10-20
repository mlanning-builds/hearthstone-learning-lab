"""Ordinary Genn identity, held parity, and paid upgraded-power behavior."""
import gzip,json,unittest
from copy import deepcopy
import test_expanded_generation as fixtures
from expanded import Action,cards,genn

class GennTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={d['id']:d for d in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.p.minions_set_cost=None
 def upgrade(self,k='MAGE'):
  self.p.hero_class=self.p.starting_hero_class=k
  self.fx.run_ops(self.g,[('genn_upgrade',)])
 def use(self,target=0):
  self.p.mana=10
  action=next(a for a in self.g.legal_actions() if a.kind=='power' and a.target==target)
  self.g.step(action)
  self.assertEqual(self.p.mana,9)
 def test_custom_power_is_preserved_with_usage_and_cost(self):
  for cid in ('EDR_847p','EX1_tk33','TLC_513hp','JAIL_EVENT_101hp'):
   with self.subTest(cid=cid):
    self.p.primary_power=dict(card_id=cid,cost=2,uid=77,damage=4);self.p.power_used=True
    before=deepcopy(self.p.primary_power);self.upgrade()
    self.assertEqual(self.p.primary_power,before);self.assertTrue(self.p.power_used)
 def test_repeat_upgrade_preserves_existing_power_identity_and_usage(self):
  self.upgrade();before=deepcopy(self.p.primary_power);self.p.power_used=True;self.upgrade()
  self.assertEqual(self.p.primary_power,before);self.assertTrue(self.p.power_used)
 def test_secondary_power_is_preserved(self):
  self.p.secondary_power=dict(card_id='JAIL_446hp',used=True)
  self.upgrade();self.assertEqual(self.p.secondary_power,dict(card_id='JAIL_446hp',used=True))
 def test_basic_upgrade_refreshes_used_power(self):
  self.p.power_used=True;self.upgrade();self.assertFalse(self.p.power_used)
 def test_all_eleven_frozen_power_identities(self):
  for k,cid in genn.POWERS.items():
   with self.subTest(k=k):
    self.p.primary_power=None;self.upgrade(k)
    self.assertEqual(self.p.primary_power['card_id'],cid);self.assertEqual(self.p.primary_power['cost'],1)
    self.assertEqual(self.records[cid]['cardClass'],k)
 def test_mage_paid_power_deals_two(self):
  self.upgrade();self.use(-2);self.assertEqual(self.q.health,28)
 def test_priest_paid_power_heals_four(self):
  self.p.health=20;self.upgrade('PRIEST');self.use(-1);self.assertEqual(self.p.health,24)
 def test_warrior_paid_power_gains_four_armor(self):
  self.upgrade('WARRIOR');self.use();self.assertEqual(self.p.armor,4)
 def test_hunter_paid_power_deals_three(self):
  self.upgrade('HUNTER');self.use();self.assertEqual(self.q.health,27)
 def test_druid_paid_power_attack_and_armor(self):
  self.upgrade('DRUID');self.use();self.assertEqual(self.p.armor,2);self.assertEqual(self.g._hero_attack(0),2)
 def test_demon_hunter_paid_power_attack(self):
  self.upgrade('DEMONHUNTER');self.use();self.assertEqual(self.g._hero_attack(0),2)
 def test_warlock_paid_power_draws_without_self_damage(self):
  before=len(self.p.deck);self.upgrade('WARLOCK');self.use()
  self.assertEqual(len(self.p.deck),before-1);self.assertEqual(len(self.p.hand),1);self.assertEqual(self.p.health,30)
 def test_rogue_paid_power_equips_frozen_two_two_weapon(self):
  self.upgrade('ROGUE');self.use();self.assertEqual(self.p.weapon['card_id'],'AT_132_ROGUEt')
  self.assertEqual((self.p.weapon['attack'],self.p.weapon['durability']),(2,2))
 def test_paladin_paid_power_summons_two_recruits(self):
  self.upgrade('PALADIN');self.use();self.assertEqual([m.card_id for m in self.p.minions],['CS2_101t']*2)
 def test_death_knight_paid_power_summons_expiring_two_attack_ghoul(self):
  self.upgrade('DEATHKNIGHT');self.use();m=self.p.minions[0]
  self.assertEqual(m.card_id,'HERO_11bp2t');self.assertEqual((m.attack,m.health),(2,1));self.assertIn('CHARGE',m.keywords)
  self.g.step(Action('end'));self.assertFalse(self.p.minions)
 def test_shaman_paid_power_uses_private_four_totem_choice(self):
  self.upgrade('SHAMAN');self.use();self.assertEqual(self.g.pending_choice['kind'],'genn_totem')
  self.assertEqual(len(self.g.pending_choice['options']),4)
  cid=self.g.pending_choice['options'][0]['card_id']
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='choose' and a.choices==(0,)))
  self.assertEqual(self.p.minions[0].card_id,cid)
 def test_mixed_parity_waits_then_transforms_same_physical_card(self):
  even=self.g._add(0,'CORE_CS2_029');odd=self.g._add(0,'CORE_CS2_023');c=self.g._add(0,'CATA_615');uid=c.uid
  self.g._settle();self.assertEqual(c.card_id,'CATA_615')
  self.p.hand.remove(odd);self.g._settle();self.assertEqual((c.uid,c.card_id),(uid,'CATA_615t'))
 def test_current_discount_changes_parity(self):
  even=self.g._add(0,'CORE_CS2_029');odd=self.g._add(0,'CORE_CS2_023');c=self.g._add(0,'CATA_615')
  self.g._settle();self.assertEqual(c.card_id,'CATA_615')
  odd.cost_delta=-1;self.g._settle();self.assertEqual(c.card_id,'CATA_615t')
 def test_empty_other_hand_transforms_and_never_reverts(self):
  c=self.g._add(0,'CATA_615');self.g._settle();self.assertEqual(c.card_id,'CATA_615t')
  self.g._add(0,'CORE_CS2_029');self.g._add(0,'CORE_CS2_023');self.g._settle();self.assertEqual(c.card_id,'CATA_615t')
 def test_ordinary_registry_contains_every_fixed_dependency(self):
  for cid in ('CATA_615','CATA_615t','AT_132_ROGUEt','HERO_11bp2t',*genn.POWERS.values()):
   self.assertEqual(self.g.cards[cid],self.records[cid])
  self.assertIn('CATA_615',cards.COLLECTIBLE_IDS)
  self.assertNotIn('CATA_615t',cards.COLLECTIBLE_IDS)
 def test_paid_transformed_body_upgrades_without_fixture_registration(self):
  self.g._add(0,'CORE_CS2_029');c=self.g._add(0,'CATA_615');self.g._settle()
  self.assertEqual(c.card_id,'CATA_615t')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.p.mana,6);self.assertEqual(self.p.primary_power['card_id'],'HERO_08bp2')
  self.assertEqual((self.p.minions[0].attack,self.p.minions[0].health),(6,5))
 def test_all_classes_accept_root_in_ordinary_constructed_deck(self):
  import test_expanded_passive_admission as admission
  from expanded import Game
  helper=admission.PassiveAdmissionTests()
  for k in genn.CLASSES:
   with self.subTest(k=k):
    if k=='DEATHKNIGHT':
     from expanded.decks import Deck,eligible,validate
     from expanded.fabled_decks import BUNDLES
     records=cards.registry();runes=(3,0,0)
     ids=[cid for cid in sorted(cards.COLLECTIBLE_IDS) if cid not in BUNDLES and cid not in ('JAIL_397','JAIL_430','CATA_615') and eligible(records[cid],k,runes)]
     deck=Deck(k,('CATA_615',)+tuple(ids[:29]),runes);self.assertEqual(validate(deck),[])
    else:deck=helper.deck(k,'CATA_615')
    g=Game([deck,helper.deck('WARRIOR','CORE_CS2_122')],seed=98)
    self.assertEqual(g.players[0].starting_hero_class,k)
    self.assertIn('CATA_615',g.players[0].starting_deck)
 def test_full_board_disables_summoning_powers_without_payment(self):
  for k in ('SHAMAN','PALADIN','DEATHKNIGHT'):
   with self.subTest(k=k):
    self.p.primary_power=None;self.p.board=[];self.upgrade(k)
    for _ in range(7):self.g._summon(0,'CORE_EX1_162')
    self.assertFalse(any(a.kind=='power' for a in self.g.legal_actions()))
 def test_paladin_one_space_summons_one_without_overflow(self):
  for _ in range(6):self.g._summon(0,'CORE_EX1_162')
  self.upgrade('PALADIN');self.use();self.assertEqual(len(self.p.minions),7)
  self.assertEqual(sum(m.card_id=='CS2_101t' for m in self.p.minions),1)
 def test_silence_preserves_frenzied_ghoul_printed_stats_and_cancels_expiry(self):
  self.upgrade('DEATHKNIGHT');self.use();m=self.p.minions[0]
  self.g._silence(m);self.assertEqual((m.attack,m.health),(2,1))
  self.g.step(Action('end'));self.assertIn(m,self.p.minions)
 def test_frenzied_ghoul_bounce_replay_preserves_identity_and_expiration(self):
  self.upgrade('DEATHKNIGHT');self.use();m=self.p.minions[0];self.g._bounce(m)
  c=self.p.hand[-1];self.assertEqual(c.card_id,'HERO_11bp2t');self.p.mana=10
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  m=self.p.minions[0];self.assertEqual((m.attack,m.health),(2,1))
  self.g.step(Action('end'));self.assertFalse(self.p.minions)
