"""Architecture baseline with the same visible features and legal-action heads."""

from dataclasses import asdict
import torch
from torch import nn
from hearthstone_sim.neural.model import TransformerPolicyValue, ModelConfig


class MeanPoolMLP(nn.Module):
    """Field embeddings -> mean entity pool -> two-layer MLP; no attention."""

    _prepare_rows = TransformerPolicyValue._prepare_rows
    _embed = TransformerPolicyValue._embed

    def __init__(self, config=ModelConfig()):
        super().__init__()
        self.config = config
        self.fields = nn.EmbeddingBag(config.buckets, config.width, mode="sum")
        self.token_norm = nn.LayerNorm(config.width)
        self.context = nn.Sequential(
            nn.Linear(config.width, config.width),
            nn.GELU(),
            nn.Linear(config.width, config.width),
            nn.GELU(),
            nn.LayerNorm(config.width),
        )
        self.policy = nn.Sequential(
            nn.Linear(3 * config.width, config.width), nn.GELU(), nn.Linear(config.width, 1)
        )
        self.value = nn.Sequential(
            nn.Linear(config.width, config.width), nn.GELU(), nn.Linear(config.width, 1), nn.Tanh()
        )

    @property
    def cls(self):
        # _embed uses cls.device; this exposes an existing tensor without extra parameters.
        return self.fields.weight

    def forward(self, encoded_batch):
        if not encoded_batch:
            raise ValueError("Empty batch")
        context = torch.stack(
            [self.context(self._embed(item["state"]).mean(0)) for item in encoded_batch]
        )
        logits = []
        for i, item in enumerate(encoded_batch):
            action = self._embed(item["actions"])
            ctx = context[i].expand(len(action), -1)
            logits.append(self.policy(torch.cat((action, ctx, action * ctx), dim=-1)).squeeze(-1))
        return logits, self.value(context).squeeze(-1)

    def metadata(self):
        return dict(architecture="mean-pool-mlp", **asdict(self.config))


def make_model(architecture, config=ModelConfig()):
    if architecture == "mlp":
        return MeanPoolMLP(config)
    if architecture == "transformer":
        return TransformerPolicyValue(config)
    raise ValueError("Unknown research architecture")
