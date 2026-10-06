"""Staged generation requiring repeated choices or skipped turns."""
from .generation_cards import pool
DRAGON=pool(card_type='MINION',tribe='DRAGON')
SPELL=pool(card_type='SPELL',classes='own_or_neutral')
RULES={
 'END_037':('none',[('generation_fill_board',DRAGON),('generation_full_heal',),('generation_skip_turn',)]),
 'JAIL_319':('none',[('generation_refresh_offer',SPELL)]),
}
def requests_for(cid):return {'END_037':{DRAGON},'JAIL_319':{SPELL}}.get(cid,set())
