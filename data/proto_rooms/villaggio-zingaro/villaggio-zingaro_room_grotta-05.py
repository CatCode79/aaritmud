# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.enums import TO
from src.log   import log


#= FUNZIONI ====================================================================

def after_touch(player, room, descr, detail, behavioured):
    # Solo per i giocatori
    if not player.IS_PLAYER:
        return False

    # Se quello che si tocca non è una extra
    if not detail.IS_EXTRA:
        return False

    # Se l'extra non è quella delle canne allora esce
    if "canne" not in detail.keywords:
        return False

    if random.randint(1, 100) < 50:
        player.act("Ti giunge un doloroso morso!", TO.ENTITY, room)
        player.act("Qualcosa di molto repentino ha appena morso $n!", TO.OTHERS, room)
        player.life -= give_damage(player)
    else:
        player.act("Riesci quasi ad azzannare $n ad un polpaccio", TO.TARGET, room)    
        player.act("Qualcosa ha cercato di morderti!", TO.ENTITY, room)    
        player.act("Qualcosa di molto repentino ha appena cercato di mordere $n!", TO.OTHERS, room)

def give_damage(player):
    damage = random.randint(1, 10)
    if player.life <= damage:
        damage = 0
    return damage
