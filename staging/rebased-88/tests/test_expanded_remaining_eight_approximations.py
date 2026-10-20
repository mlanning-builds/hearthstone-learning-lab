"""Owner-authorized approximation invariants, not Blizzard fidelity tests."""
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import test_expanded_generation as fixtures
import test_expanded_imbue_generation_powers as powers
from expanded import death_inheritance,exceptional_finish
from expanded.game import Card
from expanded.pools import GenerationPool
from expanded.historical_utility_spells import CHAMELEONS
from expanded.selectors import effective_tribes

class RemainingEightApproximationTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def test_copied_hammer_memory_uses_fresh_ids_without_moving_donor(self):
  g=self.game();donor=g._summon(0,'CORE_CS2_188');original=Card(g._new_id(),'TIME_209t')
  donor._muradin_hammer=dict(card=original,attack=3,durability=4)
  bound=death_inheritance.capture(g,donor,(('muradin_return',),))[0]
  for _ in range(2):death_inheritance.execute(g,('inherited_death_atomic',*bound[1:]),dict(owner=1,source=None))
  self.assertEqual(len(g.players[1].hand),2)
  self.assertEqual(len({original.uid,*[c.uid for c in g.players[1].hand]}),3)
  self.assertIs(donor._muradin_hammer['card'],original)
 def test_inherited_shuffle_uses_bearer_attack_and_unique_weapon(self):
  g=self.game();donor=SimpleNamespace(card_id='TIME_209t',rule_state={})
  bound=death_inheritance.capture(g,donor,(('hammer_shuffle',),))[0]
  death_inheritance.execute(g,('inherited_death_atomic',*bound[1:]),dict(owner=0,source=SimpleNamespace(attack=9)))
  card=next(c for c in g.players[0].deck if isinstance(c,Card) and c.card_id=='TIME_209t')
  self.assertEqual(card.card_id,'TIME_209t');self.assertEqual(g.cards[card.card_id]['attack']+card.attack_bonus,11)
 def test_bashana_uniform_tuple_sampler_preserves_budget_and_clone(self):
  g=self.game();values=('A','B','C')
  g.cards.update({cid:dict(cost=cost) for cid,cost in zip(values,(0,4,10))})
  clone=deepcopy(g)
  for game in (g,clone):
   result=game._learned_carve_allocation(values,3)
   self.assertEqual(sum(game.cards[c]['cost'] for c in result),12)
   self.assertEqual(len(result),3)
  self.assertEqual(g.rng.getstate(),clone.rng.getstate())
 def test_watfin_all_five_mutations_execute_with_physical_overlay(self):
  for field in ('attack','health','cost','name','tribe'):
   with self.subTest(field=field):
    g=self.game();cid='CORE_CS2_188'
    request=exceptional_finish.MINIONS
    g._generation_pools={(request,g.players[0].hero_class):GenerationPool('test',(cid,),'controlled')}
    mutation=dict(field=field)
    if field in ('attack','health','cost'):mutation['delta']=-1 if field=='cost' else 1
    g.suspicious_mutation_contract=dict(source='Explicit fixture',mutations=[mutation])
    g._finish_effect(('suspicious_discover',),dict(owner=0,source=None))
    choice=g.pending_choice;card=choice['cards'][0];data=g._card_data(card)
    if field=='name':self.assertNotEqual(data['name'],g.cards[cid]['name'])
    if field=='tribe':self.assertGreater(len(effective_tribes(data)),len(effective_tribes(g.cards[cid])))
    if hasattr(card,'_suspicious_overlay'):
     copy=g._copy_card(card);self.assertEqual(g._card_data(copy),data)
 def test_watfin_numeric_and_tribe_overlays_survive_play_and_bounce(self):
  for field in ('attack','health','cost','tribe','name'):
   with self.subTest(field=field):
    g=self.game();cid='CORE_CS2_188'
    g._generation_pools={(exceptional_finish.MINIONS,g.players[0].hero_class):GenerationPool('test',(cid,),'controlled')}
    mutation=dict(field=field)
    if field in ('attack','health','cost'):mutation['delta']=-1 if field=='cost' else 1
    g.suspicious_mutation_contract=dict(source='fixture',mutations=[mutation])
    g._finish_effect(('suspicious_discover',),dict(owner=0,source=None))
    card=g.pending_choice['cards'][0];before=g._card_data(card);cost=g._cost(card,0)
    m=g._summon(0,cid,entry_origin='play',entry_site='fixture',entry_zone='hand',entry_source=card)
    returned=g._bounce(m)
    self.assertEqual(g._card_data(returned),before);self.assertEqual(g._cost(returned,0),cost)
 def test_default_watfin_is_labeled_and_executable(self):
  g=self.game();g._generation_pools={(exceptional_finish.MINIONS,g.players[0].hero_class):GenerationPool('test',('CORE_CS2_188',),'controlled')}
  g._finish_effect(('suspicious_discover',),dict(owner=0,source=None))
  self.assertEqual(g.pending_choice['kind'],'suspicious_discover')
  self.assertIn('watfin',g.observe(0)['additional_approximations']['rules'])
 def test_garona_multiple_kings_destroys_one_and_halves_once(self):
  g=self.game();p=g.players[1];p.hand=[]
  for _ in range(3):g._add(1,'TIME_875t')
  g._garona_effect(('garona_assassinate',),dict(owner=0))
  self.assertEqual(len(p.hand),2);self.assertEqual(p.health,15)
 def test_free_rogue_generation_does_not_spend_mana_or_power_use(self):
  g=powers.ImbueGenerationPowerTests().rogue();p=g.players[0];mana=p.mana;used=p.power_used
  g._start_play_effects((('imbue_trigger_power',),),dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
  g._settle(allow_event_choices=True)
  self.assertEqual(len(p.hand),1);self.assertEqual((p.mana,p.power_used),(mana,used));self.assertIsNone(g.pending_choice)
 def test_exhausted_mount_still_attaches_valid_chameleon(self):
  g=self.game();m=g._summon(0,'CORE_CS2_188');m.keywords.update(CHAMELEONS)
  g._effect(('historical_utility_mount',),dict(owner=0,source=None,target=m.uid,bonus=0,lifesteal=False))
  summons=[op for op in m.attached_death_effects if op[0]=='summon']
  self.assertEqual(len(summons),1);self.assertIn(summons[0][1],CHAMELEONS.values())
