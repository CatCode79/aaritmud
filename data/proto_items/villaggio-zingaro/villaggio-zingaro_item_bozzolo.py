# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.enums import CONTAINER, TO
from src.mob   import Mob
from src.fight import Fight

from src.commands.command_follow import command_follow


#= VARIABILI ===================================================================

PROTO_RAGNETTI_CODE = "villaggio-zingaro_mob_nugolo-ragnetti"


#= FUNZIONI ====================================================================

def on_reset(bozzolo):
    command_follow(bozzolo, "ragno")


def after_inject(bozzolo, location):
    command_follow(bozzolo, "ragno")


def after_open(player, bozzolo, reverse_target, container_only, behavioured):
    ragnetti = Mob(PROTO_RAGNETTI_CODE)
    ragnetti.inject(player.location)

    player.act("Un brivido ti percorre lungo tutta la schiena mentre senti un urlo lontano.", TO.ENTITY)
    player.act("Un urlo lontano accompagna l'apertura del $N.", TO.OTHERS, bozzolo)

    fight = Fight(ragnetti, player)
    fight.start()
