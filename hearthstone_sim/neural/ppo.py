"""Clipped PPO with frozen rollout probabilities and per-learner-seat GAE."""

from dataclasses import dataclass
import math
import torch
from torch.distributions import Categorical


@dataclass(frozen=True)
class PPOConfig:
    learning_rate: float = 0.0003
    gamma: float = 1.0
    gae_lambda: float = 0.95
    clip: float = 0.2
    value_weight: float = 0.5
    entropy_weight: float = 0.01
    max_grad_norm: float = 0.5
    epochs: int = 4
    minibatch: int = 16
    target_kl: float = 0.02

    def __post_init__(self):
        for value in self.__dict__.values():
            if not math.isfinite(value):
                raise ValueError("PPO settings must be finite")
        if not (
            0 < self.learning_rate <= 1
            and 0 < self.gamma <= 1
            and 0 <= self.gae_lambda <= 1
            and 0 < self.clip < 1
            and self.value_weight >= 0
            and self.entropy_weight >= 0
            and self.max_grad_norm > 0
            and self.target_kl > 0
            and type(self.epochs) is int
            and self.epochs > 0
            and type(self.minibatch) is int
            and self.minibatch > 0
        ):
            raise ValueError("Invalid PPO settings")


def terminal_gae(values, reward, gamma=1.0, lam=0.95):
    """Values are consecutive decisions of ONE learner seat in a finished game.

    Gamma advances per learner decision, not opponent action. Capped episodes
    are excluded by the collector: no fabricated terminal labels/bootstrap.
    """
    if reward not in (-1, 0, 1):
        raise ValueError("Invalid terminal reward")
    advantage = 0.0
    next_value = 0.0
    advantages = []
    for i in reversed(range(len(values))):
        r = float(reward) if i == len(values) - 1 else 0.0
        delta = r + gamma * next_value - values[i]
        advantage = delta + gamma * lam * advantage
        advantages.append(advantage)
        next_value = values[i]
    advantages.reverse()
    return advantages, [a + v for a, v in zip(advantages, values)]


def objective(new_logp, old_logp, advantages, values, old_values, returns, entropy, config):
    logratio = new_logp - old_logp
    ratio = logratio.exp()
    policy = -torch.minimum(
        ratio * advantages, ratio.clamp(1 - config.clip, 1 + config.clip) * advantages
    ).mean()
    clipped_values = old_values + (values - old_values).clamp(-config.clip, config.clip)
    value = (
        0.5 * torch.maximum((values - returns).square(), (clipped_values - returns).square()).mean()
    )
    loss = policy + config.value_weight * value - config.entropy_weight * entropy.mean()
    kl = ((ratio - 1) - logratio).mean()
    return loss, policy, value, kl


def update(model, optimizer, samples, config, generator):
    """Explicit learning entry point. Never invoked by imports or preflight."""
    if not samples:
        raise ValueError("No completed-game learner samples")
    device = next(model.parameters()).device
    advantages = torch.tensor([s["advantage"] for s in samples], device=device)
    if len(samples) > 1:
        advantages = (advantages - advantages.mean()) / advantages.std(unbiased=False).clamp_min(
            1e-8
        )
    totals = []
    stopped = False
    model.eval()  # No dropout discrepancy between collection and PPO recomputation.
    for epoch in range(config.epochs):
        order = torch.randperm(len(samples), generator=generator).tolist()
        for start in range(0, len(order), config.minibatch):
            indices = order[start : start + config.minibatch]
            batch = [samples[i] for i in indices]
            logits, values = model([s["encoded"] for s in batch])
            distributions = [Categorical(logits=action_logits) for action_logits in logits]
            logp = torch.stack(
                [
                    d.log_prob(torch.tensor(s["action"], device=device))
                    for d, s in zip(distributions, batch)
                ]
            )
            entropy = torch.stack([d.entropy() for d in distributions])
            old_logp = torch.tensor([s["logp"] for s in batch], device=device)
            old_values = torch.tensor([s["value"] for s in batch], device=device)
            returns = torch.tensor([s["return"] for s in batch], device=device)
            loss, policy, value, kl = objective(
                logp, old_logp, advantages[indices], values, old_values, returns, entropy, config
            )
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite PPO loss")
            if kl.item() > config.target_kl:
                stopped = True
                break
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), config.max_grad_norm, error_if_nonfinite=True
            )
            optimizer.step()
            totals.append(
                dict(
                    loss=loss.item(),
                    policy=policy.item(),
                    value=value.item(),
                    entropy=entropy.mean().item(),
                    kl=kl.item(),
                    grad_norm=norm.item(),
                )
            )
        if stopped:
            break
    return dict(
        samples=len(samples),
        optimizer_steps=len(totals),
        kl_early_stop=stopped,
        means={k: sum(t[k] for t in totals) / len(totals) for k in totals[0]} if totals else {},
    )
