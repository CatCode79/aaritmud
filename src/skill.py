# -*- coding: utf-8 -*-

"""
Gestisce le operazioni generiche sulle skill.
"""


#= IMPORT ======================================================================

import random

from src.database import database
from src.element  import Element, Flags
from src.enums    import STYLE, SKILL, STAT, POSITION
from src.log      import log


#= FUNZIONI ====================================================================

def check_skill(entity, target, skill_code, position_check=False):
    """
    Ritorna il valore di conoscenza passata modificata da valori casuali e
    dalla conoscenza che ne ha la vittima (autodifesa).
    Valori ritornati tra un range di -150 e 250, la media è di 50
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return 0

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return 0

    if not skill_code:
        log.bug("skill_code non è un parametro valido: %r" % skill_code)
        return 0

    # -------------------------------------------------------------------------

    percent = random.randint(0, 200)

    # Possibilità di tiro maldestro:
    if percent == 0:
        percent -= random.randint(1, 50)
    # Possibilità di tiro magistrale:
    elif percent == 200:
        percent += random.randint(1, 50)

    # Modifica sulla base della conoscenza dell'entità e della vittima
    # (sarebbe un'autodifesa dalla conoscenza nemica)
    if skill_code in entity.skills:
        percent += entity.skills[skill_code]
    if skill_code in target.skills:
        percent -= target.skills[skill_code]

    # (TD) devo aggiungervi o togliervi i vari affect
    # (o forse il sistema sarà con il valore già inserito nell'attributo skills?)
    pass

    # La percentuale di successo di alcune skill dipende anche dalla posizione
    # con cui viene eseguita
    if position_check:
        if entity.position == POSITION.KNEE:
            percent -= random.randint(0, 10)
        if entity.position == POSITION.REST:
            percent -= random.randint(0, 25)

    return percent
#- Fine Funzione -
