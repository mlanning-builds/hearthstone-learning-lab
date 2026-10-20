"""Available temporary mana ledger for permanent-crystal transformations.

Native total mana remains the payment interface; temporary crystals are spent
first and disappear when spent. New integration remains unvalidated.
"""
def temporary_available(player):
 return min(max(0,getattr(player,'temporary_mana_available',0)),max(0,player.mana))

def grant_temporary(player,amount):
 old=player.mana;remaining=temporary_available(player)
 player.mana=min(player.mana_capacity,player.mana+amount)
 player.temporary_mana_available=remaining+max(0,player.mana-old)

def spent(player,amount):
 player.temporary_mana_available=max(0,getattr(player,'temporary_mana_available',0)-max(0,amount))

def destroy_permanent(player,amount):
 count=min(max(0,amount),player.max_mana)
 temporary=temporary_available(player)
 full=max(0,player.mana-temporary)
 empty=max(0,player.max_mana-full-player.locked_mana)
 # Destroy empty crystals before full ones. Locked crystals occupy permanent
 # crystal slots too; destroying one does not erase next-turn Overload debt.
 locked_removed=min(player.locked_mana,max(0,count-empty))
 player.locked_mana-=locked_removed
 player.max_mana-=count
 player.mana=min(full,max(0,player.max_mana-player.locked_mana))+temporary
 player.temporary_mana_available=temporary
 return count


def refresh_permanent(player,amount):
 temporary=temporary_available(player)
 full=max(0,player.mana-temporary)
 empty=max(0,player.max_mana-player.locked_mana-getattr(player,'historical_mana_burn_active',0)-full)
 gain=min(max(0,amount),empty,max(0,player.mana_capacity-player.mana))
 player.mana+=gain
 player.temporary_mana_available=temporary
 return gain
