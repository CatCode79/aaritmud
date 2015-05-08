# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando use.
"""

#= IMPORT ======================================================================

from src.config     import config
from src.command    import get_command_syntax
from src.enums      import CONTAINER, DOOR, ENTITYPE, OPTION, TO
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument

if config.reload_commands:
    reload(__import__("src.commands.command_close",  globals(), locals(), [""]))
    reload(__import__("src.commands.command_drink",  globals(), locals(), [""]))
    reload(__import__("src.commands.command_eat",    globals(), locals(), [""]))
    reload(__import__("src.commands.command_enter",  globals(), locals(), [""]))
    reload(__import__("src.commands.command_open",   globals(), locals(), [""]))
    reload(__import__("src.commands.command_plant",  globals(), locals(), [""]))
    reload(__import__("src.commands.command_read",   globals(), locals(), [""]))
    reload(__import__("src.commands.command_remove", globals(), locals(), [""]))
    reload(__import__("src.commands.command_seed",   globals(), locals(), [""]))
    reload(__import__("src.commands.command_unlock", globals(), locals(), [""]))
    reload(__import__("src.commands.command_unbolt", globals(), locals(), [""]))
    reload(__import__("src.commands.command_wear",   globals(), locals(), [""]))
from src.commands.command_close  import command_close
from src.commands.command_drink  import command_drink
from src.commands.command_eat    import command_eat
from src.commands.command_enter  import command_enter
from src.commands.command_open   import command_open
from src.commands.command_plant  import command_plant
from src.commands.command_read   import command_read
from src.commands.command_remove import command_remove
from src.commands.command_seed   import command_seed
from src.commands.command_unlock import command_unlock
from src.commands.command_unbolt import command_unbolt
from src.commands.command_wear   import command_wear


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[orange]usare[close]",
         "noun"       : "[orange]usarlo[close]",
         "you"        : "[orange]usi[close]",
         "you2"       : "[orange]usarti[close]",
         "it"         : "[orange]usa[close]"}


#= FUNZIONI ====================================================================

def command_use(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di usare un'entità, tenterà di usare il comando relativo all'entità
    e al suo stato.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_use")
            entity.send_output(syntax, break_line=False)
        return False

    original_argument = argument
    arg, argument = one_argument(argument)

    target_for_eat_drink  = entity.find_entity(arg, location=entity)
    target_for_open_close = entity.find_entity_extensively(arg, inventory_pos="last")
    target_for_enter      = entity.find_entity_extensively(arg)
    target_for_read       = entity.find_entity_extensively(arg, inventory_pos="first")
    target_for_remove     = entity.find_equipped_entity(arg, entity)

    target = target_for_eat_drink or target_for_open_close or target_for_enter or target_for_read or target_for_remove
    if not target:
        entity.act("Non trovi nessun [white]%s[close] da %s." % (arg, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sembra cercare qualcosa che non riesce proprio a trovare.", TO.ENTITY)
        return False

    # È voluto che i trigger di use scattino anche su entità che non hanno una
    # struttura di entitype valida, questo per dare la possibilità di inserire
    # trigger su entità qualsiasi in maniera tale da poterle utilizzare per far
    # scattare una qualsiasi cosa usandoli.
    # Ricordo che se in un trigger viene ritornato un valore True il normale
    # flusso di codice viene fermato, ecco cosa serve il force_return.
    force_return = check_trigger(entity, "before_use", entity, target, argument, behavioured)
    if force_return:
        return True

    force_return = check_trigger(target, "before_used", entity, target, argument, behavioured)
    if force_return:
        return True

    # -------------------------------------------------------------------------

    if target_for_open_close and target_for_open_close.entitype == ENTITYPE.CONTAINER and CONTAINER.CLOSABLE in target_for_open_close.container_type.flags:
        if CONTAINER.BOLTED in target_for_open_close.container_type.flags:
            return command_unbolt(entity, original_argument, behavioured=behavioured)
        elif CONTAINER.LOCKED in target_for_open_close.container_type.flags:
            return command_unlock(entity, original_argument, behavioured=behavioured)
        elif CONTAINER.CLOSED in target_for_open_close.container_type.flags:
            return command_open(entity, original_argument, behavioured=behavioured)
        else:
            return command_close(entity, original_argument, behavioured=behavioured)

    elif target_for_open_close and target_for_open_close.entitype == ENTITYPE.DOOR and DOOR.CLOSABLE in target_for_open_close.door_type.flags:
        if DOOR.BOLTED in target_for_open_close.door_type.flags:
            return command_unbolt(entity, original_argument, behavioured=behavioured)
        elif DOOR.LOCKED in target_for_open_close.door_type.flags:
            return command_unlock(entity, original_argument, behavioured=behavioured)
        elif DOOR.CLOSED in target_for_open_close.door_type.flags:
            return command_open(entity, original_argument, behavioured=behavioured)
        else:
            return command_close(entity, original_argument, behavioured=behavioured)

    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.DRINK:
        return command_drink(entity, original_argument, behavioured=behavioured)

    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.FOOD:
        return command_eat(entity, original_argument, behavioured=behavioured)

    # La ricerca del seme nel comando seme è uguale a quella del cibo e delle
    # bevande, ecco perchè viene utilizzato comunque target_for_eat_drink
    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.SEED:
        return command_seed(entity, original_argument, behavioured=behavioured)

    # La ricerca della pianta è uguale a quella del seme più sotto
    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.PLANT:
        return command_plant(entity, original_argument, behavioured=behavioured)

    elif target_for_enter and target_for_enter.entitype == ENTITYPE.PORTAL:
        return command_enter(entity, original_argument, behavioured=behavioured)

    # C'è da notare relativamente al read che con il comando use non è possibile
    # leggere entità dentro altre entità, poco male direi...
    elif target_for_read and target_for_read.entitype == ENTITYPE.READABLE:
        return command_read(entity, original_argument, behavioured=behavioured)

    # Stesse considerazioni dette per il tipo seed
    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.WEAR:
        return command_wear(entity, original_argument, behavioured=behavioured)

    # Stesse considerazioni dette per il tipo seed
    elif target_for_eat_drink and target_for_eat_drink.entitype == ENTITYPE.WEAPON:
        return command_wield(entity, original_argument, behavioured=behavioured)

    elif target_for_remove and target_for_remove.entitype == ENTITYPE.WEAR:
        return command_remove(entity, original_argument, behavioured=behavioured)

    #elif target.entitype == ENTITYPE.CORPSE:
    #elif target.entitype == ENTITYPE.FISHING:
    #elif target.entitype == ENTITYPE.FLOWER:
    #elif target.entitype == ENTITYPE.FRUIT:
    #elif target.entitype == ENTITYPE.GROUND:
    #elif target.entitype == ENTITYPE.INSTRUMENT:
    #elif target.entitype == ENTITYPE.KEY:
    #elif target.entitype == ENTITYPE.KEYRING:
    #elif target.entitype == ENTITYPE.MENHIR:
    #elif target.entitype == ENTITYPE.MONEY:

    # -------------------------------------------------------------------------

    entity.act("Non sai proprio come poter %s $N." % verbs["infinitive"], TO.ENTITY, target)
    entity.act("$n non sa proprio come poter %s $N." % verbs["infinitive"], TO.OTHERS, target)
    entity.act("$n non sa proprio come poter %s." % verbs["you2"], TO.TARGET, target)

    # Per saperne di più sul perché questi trigger si trovato a questo livello
    # è bene leggersi il commento in alto relativo agli altri trigger che vale
    # anche per questa coppia
    force_return = check_trigger(entity, "after_use", entity, target, argument, behavioured)
    if force_return:
        return True

    force_return = check_trigger(target, "after_used", entity, target, argument, behavioured)
    if force_return:
        return True

    return False
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "use <nome oggetto o creatura> (altro)\n"
#- Fine Funzione -
