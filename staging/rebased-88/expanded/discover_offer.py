"""Private snapshots of choice offers before their resolver mutates state.

Presence of a snapshot does not make a choice Discover. The resolver's explicit
Discover classification controls publication of the completed event.
"""
from copy import deepcopy
from dataclasses import dataclass
@dataclass(frozen=True)
class DiscoverOffer:
 owner:int
 kind:str
 selected_index:int
 options:tuple
 weapon_uid:int = None
 @property
 def selected(self):return deepcopy(self.options[self.selected_index])
 @property
 def unchosen(self):return tuple(deepcopy(v) for i,v in enumerate(self.options) if i!=self.selected_index)
def capture_offer(choice,index,weapon_uid=None):
 options=choice['options']
 if type(index) is not int or not 0<=index<len(options):raise ValueError('Invalid offer selection')
 if type(choice['owner']) is not int or choice['owner'] not in (0,1):raise ValueError('Invalid offer owner')
 return DiscoverOffer(choice['owner'],choice['kind'],index,tuple(deepcopy(options)),weapon_uid)
