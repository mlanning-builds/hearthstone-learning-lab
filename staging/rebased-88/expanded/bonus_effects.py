"""Constructed Bonus Effects, using the post-30.2 keyword pool."""
from itertools import combinations

MONSTROSITY_DEFAULT=('ELUSIVE','TAUNT')
BONUS_EFFECTS = frozenset({
    'TAUNT', 'WINDFURY', 'DIVINE_SHIELD', 'POISONOUS',
    'ELUSIVE', 'RUSH', 'LIFESTEAL', 'REBORN',
})


class BonusEffects:
    def _held_bonus_pair(self,card):
        pair=tuple(sorted(getattr(card,'rule_state',{}).get('bonus_pair',MONSTROSITY_DEFAULT)))
        if len(pair)!=2 or len(set(pair))!=2 or not set(pair)<=BONUS_EFFECTS:
            raise ValueError('Invalid held Bonus Effect pair')
        return pair

    def _reroll_held_bonus(self,card):
        previous=self._held_bonus_pair(card)
        # Developer clarification: one keyword may repeat, but not both.
        pairs=[pair for pair in combinations(sorted(BONUS_EFFECTS),2) if pair!=previous]
        self._b60_state(card)['bonus_pair']=list(self.rng.choice(pairs))

    def _card_mechanics(self,card):
        data=self._card_data(card);keywords=set(data.get('mechanics',[]))
        keywords.update(self._dark_keywords(card))
        if hasattr(card,'_bound_card') or hasattr(card,'_bound_minion'):keywords.add('DEATHRATTLE')
        if data['id']=='CATA_206':
            keywords.difference_update(MONSTROSITY_DEFAULT)
            keywords.update(self._held_bonus_pair(card))
        return keywords

    def _held_bonus_entry(self,minion,card):
        if minion.card_id=='CATA_206':
            minion.keywords.difference_update(MONSTROSITY_DEFAULT)
            minion.keywords.update(self._held_bonus_pair(card))

    def _bonus_pool(self, minion):
        keywords = self._effective_keywords(minion)
        pool = BONUS_EFFECTS - keywords
        # Rush is offered only when it can remove summoning sickness this turn.
        ready = (minion.frozen_until < 0 and minion.attack > 0
                 and 'CANT_ATTACK' not in keywords
                 and (minion.summoned_turn != self.turn or 'CHARGE' in keywords))
        if minion.owner != self.current or minion.attacks or ready:
            pool = pool - {'RUSH'}
        return sorted(pool)

    def _grant_bonus_effects(self, minion, count=1):
        if minion is None or minion.dormant or minion.health <= 0:
            return
        for _ in range(count):
            pool = self._bonus_pool(minion)
            if not pool:
                break
            minion.keywords.add(self.rng.choice(pool))

    def _bonus_effect(self, op, ctx):
        name = op[0]
        if not name.startswith('bonus_'):
            return False
        owner = ctx['owner']
        if name == 'bonus_target':
            target = next((m for p in self.players for m in p.minions
                           if m.uid == ctx.get('target')), None)
            self._grant_bonus_effects(target, op[1])
        elif name == 'bonus_played':
            target = next((m for m in self.players[owner].minions
                           if m.uid == ctx['event']['source']), None)
            self._grant_bonus_effects(target)
        elif name == 'bonus_summon':
            target = self._summon(owner, op[1], entry_origin='deathrattle',
                                  entry_site='bonus_effects._bonus_effect')
            self._grant_bonus_effects(target)
        elif name == 'bonus_pass_deathrattle':
            candidates = [m for m in self.players[owner].minions if m.health > 0]
            if candidates:
                target = self.rng.choice(candidates)
                self._grant_bonus_effects(target)
                target.attached_death_effects.append(('bonus_pass_deathrattle',))
        elif name == 'bonus_steal':
            target = next((m for m in self.players[1-owner].minions
                           if m.uid == ctx.get('target')), None)
            source = ctx.get('source')
            if target is not None and source is not None:
                stolen = BONUS_EFFECTS & self._effective_keywords(target)
                target.keywords.difference_update(stolen)
                target.temporary_keywords[:] = [e for e in target.temporary_keywords
                                                if e['keyword'] not in stolen]
                # Continuous external grants are recomputed; removing a stored
                # keyword does not silence their source.
                source.keywords.update(stolen)
                self._buff(source, len(stolen), len(stolen))
        else:
            return False
        return True
