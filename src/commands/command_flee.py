# -*- coding: utf-8 -*-

"""
Comando per fuggire da un combattimento.
"""

#= IMPORT ======================================================================

import random

from src.color      import color_first_upper
from src.config     import config
from src.enums      import DOOR, EXIT, ENTITYPE, FLAG, TO
from src.exit       import get_direction
from src.gamescript import check_trigger
from src.log        import log

if config.reload_commands:
    reload(__import__("src.commands.command_enter", globals(), locals(), [""]))
    reload(__import__("src.commands.command_open", globals(), locals(), [""]))
from src.commands.command_enter import command_enter
from src.commands.command_open  import command_open


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[firebrick]fuggire[close]",
         "you2"       : "[firebrick]sfuggirti[close]",
         "participle" : "[firebrick]fuggit$o[close]",
         "noun"       : "[firebrick]fuga[close]"}

FLEE_WAIT = 1.5


#= FUNZIONI ====================================================================

# (TD) convertirla in skill
def command_flee(entity, argument="", verbs=VERBS, behavioured=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) Se non si ha la skill non prova neppure a fuggire
    pass

    followers = []
    if not entity.is_fighting():
        followers = entity.get_followers_here()
        if not followers:
            entity.send_output("Non stai combattendo contro nessuno e nessuno ti sta seguendo!")
            return False

    # (TD) se l'adrenalina è al massimo o si è in berserker non si può fuggire

    if entity.vigour <= 0:
        entity.act("Sei troppo stanc$o per poter %s!" % verbs["infinitive"], TO.ENTITY)
        entity.act("$n è troppo stanco per poter %s!" % verbs["infinitive"], TO.OTHERS)
        return False

    # (TD) magari in futuro fare la fuga anche tramite comando exit se
    # location è un contenitore aperto
    if not entity.location.IS_ROOM:
        message = {}
        messages["entity"] = "Non trovi nessuna via di %s qui dentro!" % verbs["noun"]
        messages["others"] = "$n non trova nessuna via di %s qui dentro!" % verbs["noun"]
        return flee_with_portal(entity, messages)

    # Se non ci sono uscite praticabili allora prova a cercare dei portali,
    # da cui è facile fuggire, però non si sa mai dove possano portare...
    directions = list(entity.location.iter_viable_directions(closed_doors=True))
    if not directions:
        message = {}
        messages["entity"] = "Non trovi nessuna via di %s qui dentro!" % verbs["noun"]
        messages["others"] = "$n non trova nessuna via di %s qui dentro!" % verbs["noun"]
        return flee_with_portal(entity, "Non trovi nessuna uscita da cui poter %s!" % verbs["infinitive"])

    opponent = entity.get_opponent()
    if not opponent:
        opponent = random.choice(followers)
    if not opponent:
        log.bug("Inaspettato: opponent non è valido: %r (entità in fuga: %s)" % (opponent, entity.code))
        return False

    for direction in reversed(directions):
        door = entity.location.get_door(direction)
        if not door:
            continue
        if opponent == door:
            directions.remove(direction)
            break;

    if not directions:
        message = {}
        messages["entity"] = "$N blocca l'unica via di %s disponibile!" % verbs["noun"]
        messages["others"] = "$N blocca a $n l'unica via di %s disponibile!" % verbs["noun"]
        messages["target"] = "Blocchi a $n l'unica via di %s disponibile!" % verbs["noun"]
        return flee_with_portal(entity, messages, opponent)

    # (TD) fino a che il flee non è una skill la fallacità è casuale e
    # proporzionale al numero di uscite praticabili della stanza
    if random.randint(1, 6) > len(directions):
        entity.act("Nella foga non riesci ad orientarti e trovare una via di %s!" % verbs["noun"], TO.ENTITY)
        entity.act("Nella foga $n non riesce ad orientarti e trovare una via di %s!" % verbs["noun"], TO.OTHERS)
        entity.wait(FLEE_WAIT)
        return False

    # Tramite queste righe è possibile scegliere dove fuggire, oppure se fugge
    # in una direzione a caso
    if argument:
        direction = get_direction(argument)
    else:
        direction = random.choice(directions)

    # (TD) bisognerà ricordarsi di far fuggire tramite porte se si ha il
    # pass door (anche se penso che come effetto costante ai player non lo
    # vorrò) però come incantesimo sì, e quindi anche come flag di
    exit = entity.location.exits[direction]
    if EXIT.NO_FLEE in exit.flags:
        entity.act("Stai per %s verso %s ma ti rendi conto che ti è impossibile!" % (verbs["infinitive"], direction), TO.ENTITY)
        entity.act("$n sta per %s verso %s ma si rendi conto che è impossibile..." % (verbs["infinitive"], direction), TO.OTHERS)
        entity.wait(FLEE_WAIT)
        return False

    if exit.door and exit.door.door_type:
        # Le uscite con le porte chiuse a chiave sono bloccate alla fuga
        if DOOR.LOCKED in exit.door.door_type.flags:
            entity.act("Sbatti contro $N chiusa a chiave, non si può %s da qui!" % (verbs["infinitive"]), TO.ENTITY, exit.door)
            entity.act("$n sbatte contro $N chiusa a chiave, non si può %s da lì!" % (verbs["infinitive"]), TO.OTHERS, exit.door)
            entity.wait(FLEE_WAIT)
            return False

        # Mentre per le porte semplicemente chiuse c'è la possibilità di entrarvi e fuggire
        if DOOR.CLOSED in exit.door.door_type.flags:
            if random.randint(0, 1) == 0:
                # (TD) e magari chiudergliela in faccia
                if not command_open(entity, exit.door.get_numbered_keyword(looker=entity)):
                    entity.wait(FLEE_WAIT)
                    return False
            else:
                entity.act("Sbatti contro $N chiusa, non riesci a %s da qui!" % (verbs["infinitive"]), TO.ENTITY, exit.door)
                entity.act("$n sbatte contro $N chiusa, non riesce a %s da lì!" % (verbs["infinitive"]), TO.OTHERS, exit.door)
                entity.wait(FLEE_WAIT)
                return False

    force_return = check_trigger(entity, "before_flee", entity, opponent, direction, None, behavioured)
    if force_return:
        return True
    force_return = check_trigger(opponent, "before_fleeing", entity, opponent, direction, None, behavioured)
    if force_return:
        return True

    if followers:
        opponent.guide = None

    entity.act("$n riesce a %s da $N!" % (verbs["infinitive"]), TO.OTHERS, opponent)
    entity.act("$n riesce a %s!" % (verbs["you2"]), TO.TARGET, opponent)
    execution_result = entity.move(direction, behavioured=behavioured, fleeing=True)
    entity.act("Riesci a %s da $N!" % (verbs["infinitive"]), TO.ENTITY, opponent)

    if not followers:
        xp_loss_and_stop_fight(entity, opponent, verbs)

    entity.wait(FLEE_WAIT)

    force_return = check_trigger(entity, "after_flee", entity, opponent, direction, None, behavioured)
    if force_return:
        return True
    force_return = check_trigger(opponent, "after_fleeing", entity, opponent, direction, None, behavioured)
    if force_return:
        return True

    return execution_result
#- Fine Funzione -


def flee_with_portal(entity, messages, opponent=None):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not messages:
        log.bug("messages non è un parametro valido: %r" % messages)
        return False

    # -------------------------------------------------------------------------

    portals = []
    for en in entity.location.iter_contains():
        if FLAG.NO_LOOK_LIST in en.flags and en.entitype == ENTITYPE.PORTAL and en.portal_type:
            portals.append(en)

    if not portals:
        entity.act(messages["entity"], TO.ENTITY, opponent)
        entity.act(messages["others"], TO.OTHERS, opponent)
        if "target" in messages:
            entity.act(messages["target"], TO.TARGET, opponent)
        return False

    if random.randint(0, 1) == 0:
        entity.act("Non riesci a cogliere l'attimo giusto per la %s!" % verbs["noun"], TO.ENTITY, opponent)
        entity.act("$n non riesce a cogliere l'attimo giusto per la sua %s!" % verbs["noun"], TO.OTHERS, opponent)
        entity.act("$n non riesce a cogliere l'attimo giusto per la sua %s!" % verbs["noun"], TO.TARGET, opponent)
        entity.wait(FLEE_WAIT)
        return False

    opponent = entity.get_opponent()
    portal = random.choice(portals)

    force_return = check_trigger(entity, "before_flee", entity, opponent, None, portal, behavioured)
    if force_return:
        return True

    execution_result = command_enter(entity, portal.get_numbered_keyword(looker="entity"), fleeing=True)
    xp_loss_and_stop_fight(entity, opponent, verbs)
    entity.wait(FLEE_WAIT)

    force_return = check_trigger(entity, "after_flee", entity, opponent, None, portal, behavioured)
    if force_return:
        return True

    return execution_result
#- Fine Funzione -


def xp_loss_and_stop_fight(entity, opponent, verbs):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not opponent:
        log.bug("opponent non è un parametro valido: %r" % opponent)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    fight = entity.get_fight(with_him=opponent)
    if not fight:
        log.bug("Inatteso che l'entità %s stia eseguendo un flee senza che stia combattendo" % entity.code)
        entity.act("Ti rendi improvvisamente conto che non hai bisogno di %s." % verbs["infinitive"], TO.ENTITY)
        entity.act("$n si rende improvvisamente conto che non ha bisogno di %s." % verbs["infinitive"], TO.ENTITY)
        return

    # (TD) in arena non vi deve essere la perdita di xp
    xp_loss = opponent.level * 2
    entity.send_output("Perdi %d punti di esperienza per essere %s" % (xp_loss, verbs["participle"]))
    entity.experience -= xp_loss

    fight.stop()
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax  = "flee\n"
    syntax += "flee <direzione>\n"

    return syntax
#- Fine Funzione -

# (TD) servirà volendo anche ad evitare di essere seguiti
#        elif self.followers:
#            followers = [follower.get_name(entity) for follower in self.followers]
#            followers = pretty_list(followers)
#            forevers = [follower.get_name(entity) for follower in self.followers]
#            forevers = pretty_list(forevers)
#            if followers and forevers:
#                entity.act("Smetti di farti %s da%s ma non riesci con%s." % (VERB, followers, forevers), TO.ENTITY, target)
#            elif forevers:
#                entity.act("Cerchi di non farti %s da%s ma non ci riesci." % (VERB, forevers), TO.ENTITY, target)
#            else:
#                entity.act("Smetti di farti %s da%s." % (VERB, followers), TO.ENTITY, target)
#                entity.act("$n smette di farsi %s $N." % VERB, TO.OTHERS, target)
#                entity.act("$n smette di farsi %s." % VERB_YOU2, TO.TARGET, target)
#        return False
