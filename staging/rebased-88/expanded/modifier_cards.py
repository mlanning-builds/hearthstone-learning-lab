"""Live hand costs, damage replacement and repeated end triggers."""
RULES = {
    'CATA_186': ('none', [('add_opponent','CATA_186t',1)]),
    'CATA_186t': ('none', []),
    'TIME_214': ('none', []),
    'CATA_480': ('none', [('repeat_end_effects',3)]),
}
TOKEN_IDS = {'CATA_186t'}
