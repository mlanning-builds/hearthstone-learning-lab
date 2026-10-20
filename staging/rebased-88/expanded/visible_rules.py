"""Plain-data copies of explicit public rule definitions."""
from copy import deepcopy
from dataclasses import asdict
from .generation_cards import PoolRequest
from .dark_gift_generators import GiftRequest


def plain_rules(value):
    if isinstance(value,(PoolRequest,GiftRequest)):return asdict(value)
    if isinstance(value,dict):return {key:plain_rules(item) for key,item in value.items()}
    if isinstance(value,tuple):return tuple(plain_rules(item) for item in value)
    if isinstance(value,list):return [plain_rules(item) for item in value]
    return deepcopy(value)
