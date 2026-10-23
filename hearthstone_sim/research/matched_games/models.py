"""Common visible-feature/action interface; no main-player source modifications."""

from dataclasses import asdict
import torch
from torch import nn
from hearthstone_sim.neural.model import ModelConfig, TransformerPolicyValue

ARMS = ("mlp", "gru", "large_transformer")
CONTENDERS = ("mlp", "gru", "transformer", "large_transformer", "transformer_search")


def model_config(architecture, small=None):
    if architecture not in CONTENDERS:
        raise ValueError("Unknown architecture: " + architecture)
    if small is not None:
        return small
    return (
        ModelConfig(width=192, heads=6, layers=6, feedforward=768)
        if architecture == "large_transformer"
        else ModelConfig()
    )


class PooledPolicy(nn.Module):
    _prepare_rows = TransformerPolicyValue._prepare_rows
    _embed = TransformerPolicyValue._embed

    def __init__(self, config, recurrent=False):
        super().__init__()
        self.config = config
        self.recurrent = recurrent
        self.fields = nn.EmbeddingBag(config.buckets, config.width, mode="sum")
        self.token_norm = nn.LayerNorm(config.width)
        self.context = (
            nn.GRU(config.width, config.width, batch_first=True)
            if recurrent
            else nn.Sequential(
                nn.Linear(config.width, config.width),
                nn.GELU(),
                nn.Linear(config.width, config.width),
                nn.GELU(),
            )
        )
        self.norm = nn.LayerNorm(config.width)
        self.policy = nn.Sequential(
            nn.Linear(3 * config.width, config.width), nn.GELU(), nn.Linear(config.width, 1)
        )
        self.value = nn.Sequential(
            nn.Linear(config.width, config.width), nn.GELU(), nn.Linear(config.width, 1), nn.Tanh()
        )

    @property
    def cls(self):
        return self.fields.weight

    def forward(self, items):
        if not items:
            raise ValueError("Empty batch")
        contexts = []
        for item in items:
            if self.recurrent:
                # Recompute the bounded sequence with CURRENT weights for PPO.
                # No stale hidden states, shuffled time steps, or cross-game memory.
                history = item.get("memory", []) + [item["state"]]
                states = torch.stack([self._embed(rows).mean(0) for rows in history])
                _, hidden = self.context(states.unsqueeze(0))
                ctx = hidden[0, 0]
            else:
                ctx = self.context(self._embed(item["state"]).mean(0))
            contexts.append(self.norm(ctx))
        context = torch.stack(contexts)
        logits = []
        for item, ctx in zip(items, contexts):
            actions = self._embed(item["actions"])
            expanded = ctx.expand(len(actions), -1)
            logits.append(
                self.policy(torch.cat((actions, expanded, actions * expanded), -1)).squeeze(-1)
            )
        return logits, self.value(context).squeeze(-1)

    def metadata(self):
        return dict(
            architecture="gru-window-16" if self.recurrent else "mean-pool-mlp",
            **asdict(self.config),
        )


def make_model(architecture, config=None):
    cfg = model_config(architecture, config)
    if architecture == "mlp":
        return PooledPolicy(cfg)
    if architecture == "gru":
        return PooledPolicy(cfg, True)
    return TransformerPolicyValue(cfg)


def with_memory(encoded, history, architecture, window=16):
    if architecture == "gru":
        encoded = dict(encoded, memory=list(history[-(window - 1) :]))
    return encoded
