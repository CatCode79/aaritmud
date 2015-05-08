# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica delle parti del corpo.
"""


#= IMPORT ======================================================================

from src.element import Element, Flags
from src.enums   import FLAG, GRAMMAR, PART, PARTFLAG, TO, WEAPONFLAG
from src.grammar import add_article
from src.log     import log


#= CLASSI ======================================================================

class Part(object):
    def __init__(self, part, part_of=None, prototype=None, flags=None, together=""):
        self.part    = part
        self.part_of = part_of
        self.prototype   = prototype
        if flags:
            self.flags = Flags(*flags)
        else:
            self.flags = Flags(PARTFLAG.NONE)
        self.together = together
    #- Fine Inizializzazione -


#= FUNZIONI ====================================================================

def get_part_descriptions(weared_entity, command_name, wearer, looker):
    """
    Crea i 3 messaggi di act per tutte le parti di corpo coperte dall'entità
    scelta.
    """
    if not weared_entity:
        log.bug("weared_entity non è un parametro valido: %r" % weared_entity)
        return ""

    if command_name not in ("equip", "wear", "remove"):
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return ""

    if not wearer:
        log.bug("wearer non è un parametro valido: %r" % wearer)
        return ""

    if not looker:
        log.bug("looker non è un parametro valido: %r" % looker)
        return ""

    # -------------------------------------------------------------------------

    part_descriptions = {TO.ENTITY : "",
                         TO.OTHERS : "",
                         TO.TARGET : ""}

    if command_name == "remove" and (PART.HOLD in weared_entity.wear_mode and PART.WIELD in weared_entity.wear_mode) and use_two_handed(wearer):
        part_descriptions = {TO.ENTITY : "con tutte e due le $hands",
                             TO.OTHERS : "con tutte e due le $hands",
                             TO.TARGET : "con tutte e due le $hands"}
        return part_descriptions

    sorted_elements = weared_entity.wear_mode.sort_elements()
    if len(sorted_elements) == 0:
        return part_descriptions

    for to in (TO.ENTITY, TO.OTHERS, TO.TARGET):
        attr_name = "%s_%s" % (command_name, to.get_mini_code())
        for enum_element in sorted_elements[0 : -1]:
            attr_value = getattr(enum_element, attr_name)
            if attr_value:
                part_descriptions[to] += " %s," % attr_value
            else:
                part_descriptions[to] += " %s," % enum_element.description
        if part_descriptions[to]:
            part_descriptions[to] = part_descriptions[to].lstrip().rstrip(",") + " e "
        attr_value = getattr(sorted_elements[-1], attr_name)
        if attr_value:
            part_descriptions[to] = part_descriptions[to] + attr_value
        else:
            part_descriptions[to] = part_descriptions[to] + sorted_elements[-1].description

        if weared_entity.under_weared and weared_entity.under_weared():
            # (bb) commentato, ma scommetto per qualche entità ci vorrà, quindi
            # bisognerà fare un check sulle little words
            #name = add_article(weared_entity.under_weared().get_name(looker=looker), GRAMMAR.INDETERMINATE)
            name = weared_entity.under_weared().get_name(looker=looker)
            part_descriptions[to] = ("sopra %s " % name) + part_descriptions[to]

    return part_descriptions
#- Fine Funzione -


def use_two_handed(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    already_use_wield = entity.get_wielded_entity()

    if not already_use_wield:
        return False

    if not already_use_wield.weapon_type:
        return False

    if WEAPONFLAG.TWO_HANDS not in already_use_wield.weapon_type.flags:
        return False

    return True
#- Fine Funzione -


def check_if_part_is_already_weared(entity, part):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None, None

    if not part:
        log.bug("part non è un parametro valido: %r" % part)
        return None, None

    # -------------------------------------------------------------------------

    # Dà prima la precedenza alle entità layerate così da ritornare l'entità
    # più esterna nella stratificazione dei vestiti
    for possession in entity.iter_contains():
        if not possession.under_weared or not possession.under_weared():
            continue
        if FLAG.INGESTED in possession.flags:
            continue
        for location in possession.wear_mode:
            if location == part:
                return part, possession

    for possession in entity.iter_contains():
        if FLAG.INGESTED in possession.flags:
            continue
        for location in possession.wear_mode:
            if location == part:
                return part, possession

    return None, None
#- Fine Funzione -
