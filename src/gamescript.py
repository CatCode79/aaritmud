# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica dei gamescript.
"""


#= IMPORT ======================================================================

import datetime
import os
import sys

from src.database import database
from src.engine   import engine
from src.enums    import LOG
from src.log      import log
from src.utility  import get_module_functions, import_from_anywhere, html_escape

from src.games.wumpus import get_wumpus_gamescripts_module


#= COSTANTI ====================================================================

PERSONAL_TRIGGERS = ("on_booting", "on_shutdown", "on_reset", "on_repop", "on_init",
                     "before_inject", "after_inject", "before_extract", "after_extract",
                     "before_to_location", "after_to_location", "before_from_location", "after_from_location",
                     "on_dawn", "on_sunrise", "on_noon", "on_sunset", "on_dusk", "on_midnight")


#= VARIABILI ===================================================================

# Tiene traccia delle chiamate di ogni trigger, ogni valore del dizionario e
# composta da una lista di due numeri, il primo numero indica quante chiamate
# andranno a interrompere il normale flusso del codice, mentre il secondo numero
# indica la quantità totale di chiamate per quel trigger
trigger_tracker = {}


#= FUNZIONI ====================================================================

def create_init_files(root_name, dir_names):
    if not root_name:
        log.bug("root_name non è un parametro valido: %r" % root_name)
        return

    if not dir_names:
        log.bug("dir_names non è un parametro valido: %r" % dir_names)
        return

    # -------------------------------------------------------------------------

    folder_names = []
    for dir_name in dir_names:
        folder_names.append("%s/%s" % (root_name, dir_name))

    for folder_name in ["data"] + folder_names:
        if not os.path.exists("%s/__init__.py" % folder_name):
            open("%s/__init__.py" % folder_name, "w")

    for folder_name in folder_names:
        for root, dirs, files in os.walk(folder_name):
            for directory in dirs:
                if not os.path.exists("%s/%s/__init__.py" % (root, directory)):
                    open("%s/%s/__init__.py" % (root, directory), "w")
#- Fine Funzione -


def _import_all_gamescripts(root_name, dir_names, import_gamescripts_function):
    """
    Cerca i moduli python tra i dati e prova a caricarli come gamescripts.
    """
    if not root_name:
        log.bug("root_name non è un parametro valido: %r" % root_name)
        return

    if not dir_names:
        log.bug("dir_names non è un parametro valido: %r" % dir_names)
        return

    if not import_gamescripts_function:
        log.bug("import_gamescripts_function non è un parametro valido: %r" % import_gamescripts_function)
        return

    # -------------------------------------------------------------------------

    for dir_name in dir_names:
        log.booting("-> %s" % dir_name)
        folder_name = "%s/%s" % (root_name, dir_name)
        for root, dirs, files in os.walk(folder_name):
            for filename in files:
                if filename[0] == "_" or not filename.endswith(".py"):
                    continue

                code = os.path.splitext(filename)[0]
                if not code:
                    log.bug("Il nome del file %s/%s del dato non è valido: %r" % (root, filename, code))
                    continue

                if code not in database[dir_name]:
                    log.bug("Il dato con il codice %s non è stato caricato nel database." % code)
                    # Nonostante sia intercorso un errore non interrompe il
                    # ciclo provando comunque a caricare i gamescript

                data = database[dir_name][code]
                data.gamescripts = import_gamescripts_function(data)
#- Fine Funzione -


def import_all_proto_gamescripts(root_name, dir_names):
    _import_all_gamescripts(root_name, dir_names, import_proto_gamescripts)
#- Fine Funzione -


def import_all_instance_gamescripts(root_name, dir_names):
    _import_all_gamescripts(root_name, dir_names, import_instance_gamescripts)
#- Fine Funzione -


def import_all_area_gamescripts():
    """
    Importa tutti i gamescript da file python realtivi alle aree.
    """
    for root, dirs, files in os.walk("data/areas"):
        for filename in files:
            if filename[0] == "_" or not filename.endswith(".py"):
                continue

            area_code = os.path.splitext(filename)[0]
            if not area_code:
                log.bug("Il nome del file %s/%s dell'area non è valido: %r" % (root, filename, area_code))
                continue

            if area_code not in database["areas"]:
                log.bug("Il dato con il codice %s non è stato caricato nel database." % area_code)
                # Nonostante sia intercorso un errore non interrompe il
                # ciclo provando comunque a caricare i gamescript

            area = database["areas"][area_code]
            area.gamescripts = import_area_gamescript(area)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def check_trigger(obj, trigger, *args, **kw):
    """
    Controlla se vi sia un gamescript da chiamare relativi all'oggetto e al
    trigger passati, se lo trova lo esegue.
    """
    if not obj:
        log.bug("obj non è un parametro valido: %s" % obj)
        return

    if not trigger:
        log.bug("trigger non è un parametro valido: %s" % trigger)
        return

    # -------------------------------------------------------------------------

    from src.config import config

    if not config.use_gamescripts:
        return

    # Prima controlla i gamescript particolari
    if obj.gamescripts:
        if config.reload_gamescripts:
            obj.gamescripts = import_instance_gamescripts(obj)
        if obj.gamescripts and trigger in obj.gamescripts:
            log.gamescript("Attivazione del trigger %s per l'entità %s" % (trigger, obj.code))
            stop_execution = obj.gamescripts[trigger](*args, **kw)
            update_trigger_tracker(trigger, stop_execution)
            return stop_execution
    # E poi controlla quelli generici, del prototipo, il check è dentro un elif
    # per evitare di eseguire "un'eredità" di trigger tra il prototype e l'istanza,
    # è stato preferito così per evitare confusione per gli scripters
    elif hasattr(obj, "prototype") and obj.prototype and obj.prototype.gamescripts:
        if config.reload_gamescripts:
            obj.prototype.gamescripts = import_proto_gamescripts(obj.prototype)
        if obj.prototype.gamescripts and trigger in obj.prototype.gamescripts:
            log.gamescript("Attivazione del trigger %s per il prototipo %s" % (trigger, obj.prototype.code))
            stop_execution = obj.prototype.gamescripts[trigger](*args, **kw)
            update_trigger_tracker(trigger, stop_execution)
            return stop_execution

    # Se il trigger era uno di quelli attivabili solo se trovato "addosso" e non
    # anche nella stanza o nell'area che lo contiene, allora esce
    if trigger in PERSONAL_TRIGGERS:
        return False

    # Prova a controllare i trigger nella stanza che lo contiene
    # È voluto che il check lo faccia solo sulle stanze, altrimenti
    # accadrebbero solo pasticci
    if not obj.IS_ROOM and obj.location and obj.location.IS_ROOM:
        if obj.location.gamescripts:
            if config.reload_gamescripts:
                obj.location.gamescripts = import_instance_gamescripts(obj.location)
            if obj.location.gamescripts and trigger in obj.location.gamescripts:
                log.gamescript("Attivazione del trigger %s per location %s tramite %s" % (
                    trigger, obj.location.code, obj.code))
                stop_execution = obj.location.gamescripts[trigger](*args, **kw)
                update_trigger_tracker(trigger, stop_execution)
                return stop_execution
        elif hasattr(obj.location, "prototype") and obj.location.prototype and obj.location.prototype.gamescripts:
            if config.reload_gamescripts:
                obj.location.prototype.gamescripts = import_proto_gamescripts(obj.location.prototype)
            if obj.location.prototype.gamescripts and trigger in obj.location.prototype.gamescripts:
                log.gamescript("Attivazione del trigger %s per location prototipo %s tramite %s" % (
                    trigger, obj.location.prototype.code, obj.code))
                stop_execution = obj.location.prototype.gamescripts[trigger](*args, **kw)
                update_trigger_tracker(trigger, stop_execution)
                return stop_execution

    # Prova a controllare i trigger nell'area che lo contiene
    if obj.area and obj.area.gamescripts:
        if config.reload_gamescripts:
            obj.area.gamescripts = import_area_gamescript(obj.area)
        if obj.area.gamescripts and trigger in obj.area.gamescripts:
            log.gamescript("Attivazione del trigger %s per l'area %s tramite %s" % (
               trigger, obj.area.code, obj.code))
            stop_execution = obj.area.gamescripts[trigger](*args, **kw)
            update_trigger_tracker(trigger, stop_execution)
            return stop_execution

    return False
#- Fine Funzione -


def import_proto_gamescripts(obj):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return {}

    # -------------------------------------------------------------------------

    area_code = obj.code.split("_", 1)[0]
    try:
        area = database["areas"][area_code]
    except KeyError:
        log.bug("Non esiste nessuna area con codice %s" % area_code)
        return {}

    import_path = "data.%s.%s.%s" % (obj.ACCESS_ATTR, area_code, obj.code)

    if import_path in sys.modules:
        module = reload(sys.modules[import_path])
    else:
        filepath = import_path.replace(".", "/") + ".py"
        if os.path.exists(filepath):
            module = import_from_anywhere(filepath)
        else:
            module = get_wumpus_gamescripts_module(obj)
            if not module:
                return {}

    return get_module_functions(module)
#- Fine Funzione -


def import_instance_gamescripts(obj):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return {}

    # -------------------------------------------------------------------------

    if obj.IS_PLAYER:
        import_path = "data.players.%s.%s" % (obj.account.name, obj.code)
    else:
        area_code = obj.code.split("_")[0]
        import_path = "persistence.%s.%s.%s" % (obj.ACCESS_ATTR, area_code, obj.code)

    if import_path in sys.modules:
        module = reload(sys.modules[import_path])
    else:
        filepath = import_path.replace(".", "/") + ".py"
        if os.path.exists(filepath):
            module = import_from_anywhere(filepath)
        else:
            return {}

    return get_module_functions(module)
#- Fine Funzione -


def import_area_gamescript(area):
    if not area:
        log.bug("area non è un parametro valido: %r" % area)
        return {}

    # -------------------------------------------------------------------------

    import_path = "data.areas.%s" % area.code
    if import_path in sys.modules:
        module = reload(sys.modules[import_path])
    else:
        filepath = import_path.replace(".", "/") + ".py"
        module = import_from_anywhere(filepath)

    return get_module_functions(module)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def triggering_on_booting():
    """
    Viene utilizzato il values e reversed per evitare errori tipo:
    RuntimeError: dictionary changed size during iteration
    """
    for table_name, data_code, data in database.walk_datas(table_names=("rooms", "mobs", "items", "players"), use_reversed=True):
        check_trigger(data, "on_booting", data)
#- Fine Funzione -


def triggering_on_shutdown():
    """
    Relativamente all'uso di values e reversed al posto di itervalues leggere
    il commento della funzione triggering_on_booting.
    """
    for table_name, data_code, data in database.walk_datas(table_names=("rooms", "mobs", "items", "players"), use_reversed=True):
        check_trigger(data, "on_shutdown", data)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def update_trigger_tracker(trigger, stop_execution):
    if not trigger:
        log.bug("trigger non è un parametro valido: %r" % trigger)
        return

    # stop_execution ha valore di verità

    # -------------------------------------------------------------------------

    global trigger_tracker

    if trigger not in trigger_tracker:
        trigger_tracker[trigger] = [0, 0]

    if stop_execution:
        trigger_tracker[trigger][0] += 1
    trigger_tracker[trigger][1] += 1
#- Fine Funzione -


def write_trigger_tracker():
    global trigger_tracker

    file_path = "log/triggers.txt"
    try:
        trigger_file = open(file_path, "w")
    except IOError:
        log.bug("Impossibile aprire il file %s in scrittura" % file_path)
        return

    now = datetime.datetime.now()
    trigger_file.write("TRIGGERS %dy_%dm_%dd_%dh_%dm_%ds\n" % (
        now.year, now.month, now.day, now.hour, now.minute, now.second))
    for key in sorted(trigger_tracker):
        value = trigger_tracker[key]
        trigger_file.write("%s: %d/%d\n" % (key, value[0], value[1]))
    trigger_file.write("\n")
    trigger_file.close()
#- Fine Funzione -


#-------------------------------------------------------------------------------

def create_tooltip_gamescripts(conn, obj):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Gamescripts[close]"]

    if hasattr(obj, "prototype"):
        if not obj.prototype:
            log.bug("%s non ha un prototype valido: %r" % (obj.code, obj.prototype))
            return
        for function_name in obj.prototype.gamescripts:
            tooltip.append("[cyan][prototype][close] " + function_name)

    for function_name in obj.gamescripts:
        tooltip.append(function_name)

    if len(tooltip) == 1:
        return ""
    else:
        from web_resource import create_tooltip
        return create_tooltip(conn, "\n".join(tooltip), "{G}")
#- Fine Funzione -


def create_tooltip_specials(conn, obj):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return ""

    # -------------------------------------------------------------------------

    tooltip = ["[royalblue]Specials[close]"]

    for key, value in obj.specials.iteritems():
        if value:
            tooltip.append("%s = %s" % (key, html_escape(str(value))))
        else:
            tooltip.append("%s = %r" % (key, value))

    if len(tooltip) == 1:
        return ""
    else:
        from web_resource import create_tooltip
        return create_tooltip(conn, "\n".join(tooltip), "{S}")
#- Fine Funzione -
