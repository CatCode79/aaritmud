# -*- coding: utf-8 -*-

"""
Permette di aggiornare le descrizioni delle istanze con quelle di prototipo.
"""

#= IMPORT ======================================================================

from src.database import database, create_all_couples_of_keywords
from src.log      import log
from src.utility  import copy_existing_attributes


#= COSTANTI ====================================================================

# Extras viene copiato a parte poiché è una classe
REFRESHABLE_ATTR_NAMES = ("keywords_name", "keywords_short", "keywords_short_night",
                          "name", "short", "short_night", "long", "long_night",
                          "descr", "descr_night", "descr_hearing", "descr_hearing_night",
                          "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night",
                          "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night")


#= FUNZIONI ====================================================================

def command_refresh(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    for table_name, data_code, data in database.walk_datas(table_names=("rooms", "items", "mobs")):
        if not data.prototype:
            log.bug("data %s senza il proprio prototype valido: %r" % (data.code, data.prototype))
            continue
        # (TD) Evita le entità con owner che è un player, però è un placebo,
        # in realtà bisognerebbe proprio diversificare i restring fatti dagli
        # admin dalle descrizioni vere e proprie con un sistema identificativo
        # fatto ad uopo
        if data.owner and data.owner().code in database["players"]:
            continue
        for attr_name in REFRESHABLE_ATTR_NAMES:
            if hasattr(data.prototype, attr_name):
                setattr(data, attr_name, getattr(data.prototype, attr_name))
        data.extras = data.prototype.extras.copy()
        if table_name != "rooms":
            create_all_couples_of_keywords(data)

    entity.send_output("Hai aggiornato le descrizioni delle istanze con quelle di prototipo.")
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "refresh\n"
#- Fine Funzione -
