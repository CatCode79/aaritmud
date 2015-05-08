# -*- coding: utf-8 -*-

"""
Comando che permette di creare una copia di un personaggio in un mob.
"""

#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.config  import config
from src.enums   import TO, TRUST
from src.item    import Item
from src.log     import log
from src.mob     import Mob
from src.player  import search_online_player
from src.utility import copy_existing_attributes, quantity_argument


#= FUNZIONI ====================================================================

def command_create(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    entity.send_output("Il comando che crea un mob partendo da un personaggio è disabilitato per problematiche tecniche.")
    return True

    #return create_handler(entity, argument, "command_create", "players", can_create_multiple=True)
#- Fine Funzione -


def create_handler(entity, argument, command_name, table_name, can_create_multiple=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not command_name:
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    if not table_name:
        log.bug("table_name non è un parametro valido: %r" % table_name)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, command_name)
        entity.send_output(syntax, break_line=False)
        return False

    if can_create_multiple:
        quantity, argument = quantity_argument(argument)
    else:
        quantity = 1
    
    target = None
    if table_name == "players":
        target = search_online_player(argument, only_exact=True)

    if not target:
        target = entity.find_proto(argument, entity_tables=[table_name])
        if not target:
            entity.send_output("Non è stato trovato nessun %s con argomento [green]%s[close]." % (table_name, argument))
            return False

    if quantity == 0:
        quantity = target.quantity

    if not target.IS_PLAYER and target.max_global_quantity > 0 and target.current_global_quantity + quantity > target.max_global_quantity:
        if entity.trust == TRUST.IMPLEMENTOR:
            entity.send_to_admin("Ti è possibile iniettare in gioco %s nonostante questo raggiungerà il suo MaxGlobalQuantity di %d" % (
                target.get_name(looker=entity), target.max_global_quantity))
        else:
            entity.send_output("Non ti è possibile iniettare in gioco questa entità perché ha già raggiunto il suo MaxGlobalQuantity di %d" % target.max_global_quantity)
            return False

    if target.IS_PLAYER:
        result = Mob("limbo_mob_clone-pg")
        copy_existing_attributes(target, result, except_these_attrs=["code", "prototype"])
        result.short = result.name  # (TD) creazione dinamica della short, un po' come la long
        result.incognito = False
    elif target.IS_MOB:
        result = Mob(target.code)
    elif target.IS_ITEM:
        result = Item(target.code)
    else:
        log.bug("Entità base non valida: %s" % target.code)
        entity.send_output("C'è stato un'errore nell'esecuzione del comando.")
        return False

    # Se l'oggetto è uno dell'area rip avrà il tag %material da dover sostituire
    if "%material" in result.short:
        result.short.replace("%material", "qualcosa")
    if "%material" in result.short_night:
        result.short_night.replace("%material", "qualcosa")
    if "%material" in result.name:
        result.name.replace("%material", "qualcosa")

    result.quantity = quantity
    result.inject(entity)

    if entity == target:
        entity.act("Crei dal nulla una copia di te stess$O.", TO.ENTITY, target)
        entity.act("$n crea dal nulla una copia di se stess$O.", TO.OTHERS, target)
    elif entity.location == target.location:
        entity.act("Crei dal nulla una copia di $N.", TO.ENTITY, target)
        entity.act("$n crea dal nulla una copia di $N, ma ora qual'è quello vero?", TO.OTHERS, target)
        entity.act("$n crea dal nulla una copia di te stess$O!", TO.TARGET, target)
    else:
        entity.act("Crei dal nulla una copia di $N.", TO.ENTITY, target)
        entity.act("$n crea dal nulla una copia di $N.", TO.OTHERS, target)

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "create\n"
    syntax += "create <codice personaggio o suo prefisso>\n"
    syntax += "create <nome personaggio o suo prefisso>\n"
    syntax += "create <quantità> <codice personaggio o suo prefisso>\n"
    syntax += "create <quantità> <nome personaggio o suo prefisso>\n"

    return syntax
#- Fine Funzione -
