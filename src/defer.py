# -*- coding: utf-8 -*-

"""
Modulo che serve a rimpiazzare il funzionamento delle deferred della libreria
twisted.
"""

#= IMPORT ======================================================================

import random
import weakref

from twisted.internet import reactor, task

from src.config import config
#from src.enums import FLAG
from src.log    import log


#= VARIABILI ===================================================================

# Dizionario di liste contenenti tutti i parametri passati alle deferred e che
# di volta in volta vendono aggiornati con altre entità perché i valori vecchi
# vengono estratti dal sistema di raggruppamento fisico
all_deferred_function_params = {}

# Id incrementale per identificare ogni deferred nel momento in cui non servono
# più e bisogna distruggerle
incremental_key = 0


#= FUNZIONI ====================================================================

def get_key():
    global incremental_key
    incremental_key += 1
    return incremental_key
#- Fine Funzione -


def defer(time, function, *args):
    """
    Funzione che viene utilizzata quando si vogliono eseguire dei comandi dopo
    un certo tot di tempo.
    """
    if time < 0:
        log.bug("time non è un parametro valido perchè minore di 0: %d" % time)
        return

    # -------------------------------------------------------------------------

    if config.time_warp:
        time = 1

    key = get_key()
    _before_defer(key, function, *args)

    return task.deferLater(reactor, time, _after_defer, key, function, *args)
#- Fine Funzione -


def defer_random_time(min_time, max_time, function, *args):
    """
    Funzione che viene utilizzata quando si vogliono eseguire dei comandi dopo
    un certo tot di tempo.
    """
    if min_time < 0:
        log.bug("min_time non è un parametro valido perchè minore di 0: %d" % min_time)
        return

    if max_time < min_time:
        log.bug("max_time non è un parametro valido perchè minore di min_time %d: %d" % (min_time, max_time))
        return

    # -------------------------------------------------------------------------

    if config.time_warp:
        time = 1
    else:
        if min_time == max_time:
            time = min_time
        else:
            time = random.randint(min_time, max_time)

    key = get_key()
    _before_defer(key, function, *args)
    return task.deferLater(reactor, time, _after_defer, key, function, *args)
#- Fine Funzione -


def defer_if_possible(min_time, max_time, entity, target, function, *args):
    """
    Versione della defer che prima di tale esecuzione ci si vuole assicurare
    che le due entità non siano state estratte e che si trovino nella stessa
    locazione e che entity veda target.
    Di solito la funzione passata è una funzione di comando.
    """
    if min_time < 0:
        log.bug("min_time non è un parametro valido perchè minore di 0: %d" % min_time)
        return

    if max_time < min_time:
        log.bug("max_time non è un parametro valido perchè minore di min_time %d: %d" % (min_time, max_time))
        return

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not function:
        log.bug("function non è un parametro valido: %r" % function)
        return

    # --------------------------------------------------------------------------

    if config.time_warp:
        time = 1
    else:
        if min_time == max_time:
            time = min_time
        else:
            time = random.randint(min_time, max_time)

    key = get_key()
    _before_defer(key, function, *args)
    return task.deferLater(reactor, time, _execute_if_possible, entity, target, key, function, *args)
#- Fine Funzione -


def _execute_if_possible(entity, target, key, function, *args):
    """
    Funzione che fa coppia con la defer_if_possible, negli script bisogna
    utilizzare quest'ultima.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if 0 > key >= 1:
        log.bug("key non è un parametro valido: %s" % key)
        return

    if not function:
        log.bug("function non è un parametro valido: %r" % function)
        return

    # --------------------------------------------------------------------------

    if entity.is_extracted():
        return

    if target.is_extracted():
        return

    if entity.location != target.location:
        return

    if not entity.can_see(target):
        return

    _after_defer(key, function, *args)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def _before_defer(key, function, *args):
    """
    Inserendo delle liste di entità in all_deferred_function_params queste
    verranno inserite in coda durante la group_entity del modulo entity
    (quando vengono estratte le entità originali del gruppo), in maniera tale
    che quando la defer scatta i riferimenti andranno a cercare e a puntare
    alla nuova entità raggruppata e non più a quella precedente, ormai inutile.
    """
    if 0 > key >= 1:
        log.bug("key non è un parametro valido: %s" % key)
        return

    if not function:
        log.bug("function non è un parametro valido: %r" % function)
        return

    #--------------------------------------------------------------------------

    global all_deferred_function_params

    # Se c'è almeno un parametro-entità allora inizializza la all_deferred_function_params
    # con la key passata
    for arg in args:
        if arg.__class__.__name__ in ("Mob", "Item"):
            if key in all_deferred_function_params:
                log.bug("key %r già esistente in all_deferred_function_params" % key)
            all_deferred_function_params[key] = []
            break

    for arg in args:
        if arg.__class__.__name__ in ("Mob", "Item"):
            discovered = False
            for deferred_id, deferred_params in all_deferred_function_params.iteritems():
                if deferred_id != key:
                    continue
                discovered = _search_already_deferred_arg(deferred_params, arg)
                if discovered:
                    break
            if not discovered:
                #if arg.prototype.code == "ikea_item_uovo-gallina":
                #    f = open("gallina.txt", "a")
                #    buf = "aggiunta alla _before_defer: %r, %r, %d, %r, %r\n" % (
                #        arg.code, arg.location, arg.quantity, FLAG.EXTRACTED in arg.flags, FLAG.WEAKLY_EXTRACTED in arg.flags)
                #    f.write(buf)
                #    print buf
                #    import traceback
                #    traceback.print_stack(file=f)
                #    f.close()
                all_deferred_function_params[key].append([weakref.ref(arg)])
#- Fine Funzione -


def _search_already_deferred_arg(deferred_params, arg):
    if deferred_params is None:
        log.bug("deferred_params non è un parametro valido: %r" % deferred_params)
        return False

    if not arg:
        log.bug("arg non è un parametro valido: %r" % arg)
        return False

    # -------------------------------------------------------------------------

    for deferred_entities in deferred_params:
        for deferred_entity in deferred_entities:
            if deferred_entity() == arg:
                # Se l'entità è estratta e non è stato trovato nessuna entità
                # adatta a sostituirla allora non serve neppure far partire la
                # deferred: c'è un baco che dev'essere corretto a priori
                if arg.is_extracted():
                    log.bug("arg trovato già estratto in partenza: %r" % arg)
                    return False
                #if arg.prototype.code == "ikea_item_uovo-gallina":
                #    f = open("gallina.txt", "a")
                #    buf = "già inserita alla _before_defer: %r, %r, %d, %r, %r\n" % (
                #        arg.code, arg.location, arg.quantity, FLAG.EXTRACTED in arg.flags, FLAG.WEAKLY_EXTRACTED in arg.flags)
                #    f.write(buf)
                #    print buf
                #    import traceback
                #    traceback.print_stack(file=f)
                #    f.close()
                return True

    return False
#- Fine Funzione -


def _after_defer(key, function, *args):
    """
    La funzione si accerta che i parametri precedentemente passati alle funzioni
    di deferred siano ancora valido una volta che quest'ultima debba scattare.
    Se non lo sono allora pesca dalla lista delle deferred salvata a parte, ed
    impostata durante il raggruppamento fisico (group_entity), l'ultima
    della lista che è l'ultimo residuo dei vari raggruppamenti fisici.
    Se l'ultimo della lista è stato estratto non c'è problema, potrebbe aver
    terminato il suo ciclo vitale (mob è stato ucciso ed estratto) e quindi
    viene passato così com'è, sarà poi la funzione a cui vengono passati i
    parametri a doversi gestire questo caso particolare.
    Oltre a tutto ciò ogni volta che troverà un'entità estratta provvederà a
    sostituirla con un None, ciò per semplificare la stesura dei gamescripts.
    """
    if 0 > key >= 1:
        log.bug("key non è un parametro valido: %s" % key)
        return

    if not function:
        log.bug("function non è un parametro valido: %r" % function)
        return

    #--------------------------------------------------------------------------

    global all_deferred_function_params

    new_args = []
    for arg in args:
        if arg.__class__.__name__ in ("Mob", "Item"):
            discovered = False
            for deferred_id, deferred_params in all_deferred_function_params.iteritems():
                if deferred_id != key:
                    continue
                discovered, arg = _get_already_deferred_arg(deferred_params, arg)
                if discovered:
                    break
            if arg and arg.is_extracted():
                new_args.append(None)
            else:
                new_args.append(arg)
        else:
            new_args.append(arg)

    # E' normale che non tutte le key vengano trovate, questo perché nella
    # _befor_defer non tutti i parametri sono delle entità, e quindi non tutte
    # le key vengono inizializzate
    if key in all_deferred_function_params:
        del(all_deferred_function_params[key])

    function(*new_args)
#- Fine Funzione -


def _get_already_deferred_arg(deferred_params, arg):
    if not deferred_params:
        log.bug("deferred_params non è un parametro valido: %r" % deferred_params)
        return False, None

    if not arg:
        log.bug("arg non è un parametro valido: %r" % arg)
        return False, None

    # -------------------------------------------------------------------------

    for deferred_entities in deferred_params:
        for deferred_entity in deferred_entities:
            if not deferred_entity():
                return False, None
            if deferred_entity() == arg:
                #if arg.prototype.code == "ikea_item_uovo-gallina":
                #    f = open("gallina.txt", "a")
                #    buf = "impostata la deferred_entity alla _after_defer: %r / %r, %r / %r, %d / %d, %r / %r, %r / %r\n" % (
                #        arg.code, deferred_entities[-1].code, arg.location, deferred_entities[-1].location, arg.quantity, deferred_entities[-1].quantity,
                #        FLAG.EXTRACTED in arg.flags, FLAG.EXTRACTED in deferred_entities[-1].flags, FLAG.WEAKLY_EXTRACTED in arg.flags, FLAG.WEAKLY_EXTRACTED in deferred_entities[-1].flags)
                #    f.write(buf)
                #    print buf
                #    import traceback
                #    traceback.print_stack(file=f)
                #    f.close()
                return True, arg

    return False, None
#- Fine Funzione -


def set_deferred_args(from_entity, to_entity):
    """
    Imposta, durante l'ammucchiamento fisico, la nuova entità in coda a quella
    precedente in maniera tale che quest'ultima, venendo estratta, non venga
    presa dalla _after_defer come parametro valido ma utilizzi invece l'ultimo
    della lista.
    """
    if not from_entity:
        log.bug("from_entity non è un parametro valido: %r" % from_entity)
        return

    if not to_entity:
        log.bug("to_entity non è un parametro valido: %r" % to_entity)
        return

    #--------------------------------------------------------------------------

    global all_deferred_function_params

    discovered = False
    for deferred_params in all_deferred_function_params.itervalues():
        for deferred_entities in deferred_params:
            for deferred_entity in deferred_entities:
                if deferred_entity() == from_entity:
                    #if from_entity.prototype.code == "ikea_item_uovo-gallina":
                    #    f = open("gallina.txt", "a")
                    #    buf = "trovata alla group_entity: %r / %r, %r / %r, %d / %d, %r, %r / %r, %r\n" % (
                    #        from_entity.code, to_entity.code, from_entity.location, to_entity.location, from_entity.quantity, to_entity.quantity,
                    #        FLAG.EXTRACTED in from_entity.flags, FLAG.WEAKLY_EXTRACTED in from_entity.flags, FLAG.EXTRACTED in to_entity.flags, FLAG.WEAKLY_EXTRACTED in to_entity.flags)
                    #    f.write(buf)
                    #    print buf
                    #    import traceback
                    #    traceback.print_stack(file=f)
                    #    f.close()
                    if deferred_entity != deferred_entities[-1]:
                        log.bug("deferred_entity %s non è l'ultimo della lista: %s" % (deferred_entity, deferred_entities))
                    deferred_entities.append(weakref.ref(to_entity))
                    discovered = True
                    break
            if discovered:
                break
        if discovered:
            break

    # È normale che from_entity non venga trovata, ciò significa che è stata
    # raggruppata prima di essere utilizzata come parametro in una deferred
#- Fine Funzione -
