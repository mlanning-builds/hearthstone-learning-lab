"""Explicitly bounded experimental self-play; no automatic experiment launch."""
import math
from .environment import PolicyEnvironment
from .features import encode_decision


def train_episode(policy,decks,*,seed,max_actions,learning_rate,first_player=0,
                  experimental=False):
    """One shared-policy self-play episode, then one atomic gradient update.

    Both seats sample with unchanged weights. Each decision receives its own
    player's terminal reward; no reward is invented for action-capped games.
    No replay, discounting, baseline, entropy bonus or opponent archive yet.
    Exceptions restore policy parameters and sampling state for safe retry.
    """
    if not math.isfinite(learning_rate) or learning_rate<=0:
        raise ValueError('Positive finite learning rate required')
    old_weights=dict(policy.weights);old_rng=policy.rng.getstate()
    try:
        env=PolicyEnvironment(experimental=experimental)
        decision=env.reset(decks,seed=seed,max_actions=max_actions,first_player=first_player)
        samples=[];actor_counts=[0,0]
        while not decision['terminated'] and not decision['truncated']:
            features=encode_decision(decision);chosen=policy.choose(features)
            actor=decision['actor'];actor_counts[actor]+=1
            samples.append((features,chosen,actor))
            decision=env.step(chosen,revision=decision['revision'])
        result=dict(steps=decision['steps'],terminated=decision['terminated'],
                    truncated=decision['truncated'],end_reason=decision['end_reason'],
                    actor_decisions=actor_counts,terminal_rewards=None,updated=False)
        if decision['terminated']:
            rewards=decision['rewards']
            if rewards not in ([1,-1],[-1,1],[0,0]):raise ValueError('Invalid terminal rewards')
            result['terminal_rewards']=list(rewards)
            result['gradient']=policy.reinforce_batch(
                ((features,chosen,rewards[actor]) for features,chosen,actor in samples),
                learning_rate=learning_rate)
            result['updated']=bool(samples) and any(rewards)
        return result
    except BaseException:
        policy.weights.clear();policy.weights.update(old_weights)
        policy.rng.setstate(old_rng)
        raise
