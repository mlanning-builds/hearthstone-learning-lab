"""Shared field embeddings, entity Transformer, legal-action and value heads."""

from dataclasses import asdict, dataclass
import torch
from torch import nn


@dataclass(frozen=True)
class ModelConfig:
    buckets: int = 32768
    width: int = 128
    heads: int = 4
    layers: int = 3
    feedforward: int = 384

    def __post_init__(self):
        if (
            min(self.buckets, self.width, self.heads, self.layers, self.feedforward) < 1
            or self.width % self.heads
        ):
            raise ValueError("Invalid Transformer dimensions")


class TransformerPolicyValue(nn.Module):
    def __init__(self, config=ModelConfig()):
        super().__init__()
        self.config = config
        self.fields = nn.EmbeddingBag(config.buckets, config.width, mode="sum")
        self.token_norm = nn.LayerNorm(config.width)
        self.cls = nn.Parameter(torch.zeros(1, 1, config.width))
        layer = nn.TransformerEncoderLayer(
            config.width,
            config.heads,
            dim_feedforward=config.feedforward,
            dropout=0.0,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, config.layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(config.width)
        self.policy = nn.Sequential(
            nn.Linear(3 * config.width, config.width), nn.GELU(), nn.Linear(config.width, 1)
        )
        self.value = nn.Sequential(
            nn.Linear(config.width, config.width), nn.GELU(), nn.Linear(config.width, 1), nn.Tanh()
        )

    def _embed(self, rows):
        ids, weights, offsets = [], [], []
        for row in rows:
            offsets.append(len(ids))
            scale = max(1, len(row)) ** -0.5
            for token, value in row:
                ids.append(token)
                weights.append(value * scale)
        device = self.cls.device
        return self.token_norm(
            self.fields(
                torch.tensor(ids, dtype=torch.long, device=device),
                torch.tensor(offsets, dtype=torch.long, device=device),
                per_sample_weights=torch.tensor(weights, dtype=torch.float32, device=device),
            )
        )

    def forward(self, encoded_batch):
        if not encoded_batch:
            raise ValueError("Empty batch")
        states = [self._embed(item["state"]) for item in encoded_batch]
        length = max(s.shape[0] for s in states) + 1
        padded = self.cls.new_zeros((len(states), length, self.config.width))
        mask = torch.ones((len(states), length), dtype=torch.bool, device=self.cls.device)
        for i, state in enumerate(states):
            padded[i, 0] = self.cls[0, 0]
            padded[i, 1 : len(state) + 1] = state
            mask[i, : len(state) + 1] = False
        context = self.norm(self.encoder(padded, src_key_padding_mask=mask)[:, 0])
        logits = []
        for i, item in enumerate(encoded_batch):
            action = self._embed(item["actions"])
            ctx = context[i].expand(len(action), -1)
            logits.append(self.policy(torch.cat((action, ctx, action * ctx), dim=-1)).squeeze(-1))
        # Only legal candidates exist: variable candidate sets need no fixed action vocabulary.
        return logits, self.value(context).squeeze(-1)

    def metadata(self):
        return asdict(self.config)
