# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.database import database
from src.defer    import defer
from src.enums    import TO, FLAG
from src.log      import log


#= FUNZIONI ====================================================================

# Sostituito dalla struttura apposita
def moved_on_init(mob):
    defer(300, remove_mob, mob)
#- Fine Funzione -


def remove_mob(mob):
    # Possibilissimo visto che questa funzione è deferrata
    if not mob:
        return

    mob.act("...flebilmente sparisco e vado altrove.", TO.ENTITY, mob)
    mob.act("...flebilmente $N diviene sempre più diafano fino a sparire nel nulla. ", TO.OTHERS, mob)
    mob.extract(1)
#- Fine Funzione -
