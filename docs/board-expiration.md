# Soulrest Ceremony and board expiration

DINO_417 combines shared board Attack buff, Rush grant and a new board_expire operation over the currently friendly minions. It reuses the existing removable expiration flag. Later summons are not affected; Silence clears the effect. End-turn destruction bypasses damage prevention and resolves Deathrattles and Corpse accounting.

Six regression scenarios cover immediate Rush restrictions, end-turn death, later summons, Silence, immunity/shields, Deathrattles and Counterspell. Source: pinned DINO_417 record. Existing expiration timing under control changes, copies and concurrent end-turn triggers remains unverified (board_expiry_controller).
