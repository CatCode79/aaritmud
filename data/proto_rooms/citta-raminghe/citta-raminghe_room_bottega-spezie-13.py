# -*- coding: utf_8 -*-

#= IMPORT ======================================================================

import random

from src.defer import defer_if_possible
from src.enums import TO

from src.commands.command_say import command_say


#= COSTANTI ====================================================================

SPICES = ("citta-raminghe_item_spezia-zenzero",
          "citta-raminghe_item_spezia-peperoncino",
          "citta-raminghe_item_spezia-curcuma",
          "citta-raminghe_item_spezia-pepenero",
          "citta-raminghe_item_spezia-vaniglia")

SELLER_PROTO_CODE = "citta-raminghe_mob_venditrice-spezie"
SHELF_PROTO_CODE  = "citta-raminghe_item_scaffale-spezie"


#= FUNZIONI ====================================================================

def before_get(entity, target, location, behavioured):
    # Se l'oggetto raccolto non è una spezia allora esce
    if target.prototype.code not in SPICES:
        return False

    # Se l'oggetto non è stato preso da terra allora esce
    if location != entity.location:
        return False

    # Recupera la venditrice che gestisce il baratto, se non c'è esce
    seller = get_seller(entity)
    if not seller:
        return False

    # Se ha effettuato almeno il drop di un oggetto per il baratto allora esce.
    # Questo check si trova dopo aver cercato la seller cosicché la presenza di
    # lei fa come da garante al resetting del drop_for_spice.
    if "drop_for_spice" in entity.specials and entity.specials["drop_for_spice"]:
        entity.specials["drop_for_spice"] = False
        entity.act("$a ti sorride.", TO.ENTITY, target, seller)
        entity.act("$a sorride a $n", TO.OTHERS, target, seller)
        return False

    seller.act("$n ferma $N mentre sta raccogliendo $a.", TO.ENTITY, entity, target)
    seller.act("$n ferma $N mentre sta raccogliendo $a.", TO.OTHERS, entity, target)
    seller.act("$n ti ferma mentre stai raccogliendo $a.", TO.TARGET, entity, target)

    entity_keyword = entity.get_numbered_keyword(looker=seller)
    to_say = "a %s Ti esorto a lasciare qualcosa in cambio per poter prendere %s." % (entity_keyword, target.get_name(looker=seller))
    defer_if_possible(1, 2, seller, entity, command_say, seller, to_say)

    return True
#- Fine Funzione -


def after_drop(entity, target, location, behavioured):
    # Se l'oggetto lasciato non lo è stato per terra allora esce
    if location != entity.location:
        return

    # Recupera la venditrice che gestisce il baratto, se non c'è esce
    seller = get_seller(entity)
    if not seller:
        return

    # Imposta la special che indica che è stato lasciato un oggetto per il baratto.
    # Ignora volutamente la quantity, è l'azione del drop che conta.
    # Anche qui questo check bisogna farlo dopo che è stata trovata seller che
    # fa da garante per l'azione di drop
    entity.specials["drop_for_spice"] = True

    entity.act("$N annuisce sorridendoti.", TO.ENTITY, seller)
    entity.act("$N annuisce sorridendo a $n", TO.OTHERS, seller)
#- Fine Funzione -


def after_giving(entity, target, receiver, direction, behavioured):
    # Recupera la venditrice che gestisce il baratto, se non c'è esce
    seller = get_seller(entity)
    if not seller:
        return

    # Se la persona a cui si lascia l'oggetto non è la venditrice allora esce
    if receiver != seller:
        return

    # Imposta la special che indica che è stato lasciato un oggetto per il baratto.
    entity.specials["drop_for_spice"] = True

    entity.act("$N annuisce sorridendoti.", TO.ENTITY, seller)
    entity.act("$N annuisce sorridendo a $n", TO.OTHERS, seller)
#- Fine Funzione -


def after_putting(entity, target, receiver, direction, behavioured):
    # Recupera lo scaffale in cui è possibile inserire le cose da barattare, se non c'è esce
    shelf = get_shelf(entity)
    if not shelf:
        return False

    # Se la cosa a cui si vuole dare l'oggetto non è lo scaffale allora esce
    if receiver != shelf:
        return False

    # Recupera anche la venditrice che è lei annuisce e sorride
    seller = get_seller(entity)
    if not seller:
        return False

    # Imposta la special che indica che è stato lasciato un oggetto per il baratto.
    entity.specials["drop_for_spice"] = True

    entity.act("$N annuisce sorridendoti.", TO.ENTITY, seller)
    entity.act("$N annuisce sorridendo a $n", TO.OTHERS, seller)
    return False
#- Fine Funzione -


#-------------------------------------------------------------------------------

def get_seller(entity):
    return _get_target(entity, SELLER_PROTO_CODE)
#- Fine Funzione -

def get_shelf(entity):
    return _get_target(entity, SHELF_PROTO_CODE)
#- Fine Funzione -

def _get_target(entity, proto_code):
    for en in entity.location.iter_contains():
        if en.IS_PLAYER:
            continue
        if en.prototype.code == proto_code:
            return en.split_entity(1)
            #return en

    return None
#- Fine Funzione -
