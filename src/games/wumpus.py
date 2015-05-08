# -*- coding: utf-8 -*-

import sys

from src.database import database
from src.utility  import import_from_anywhere


class Wumpus(object):
    def get_error_message(self):
        return ""
    #- Fine Metodo -

    def get_related_attr_name(self, obj):
        if not obj:
            log.bug("obj non è un parametro valido: %r" % obj)
            return ""

        # ---------------------------------------------------------------------

        for attr_name in dir(self):
            if attr_name[-1] != "s":
                continue
            for proto_entity in getattr(self, attr_name):
                if obj.code == proto_entity.code:
                    return attr_name

        return ""
    #- Fine Metodo -


def import_all_wumpus_gamescripts():
    """
    Cerca nelle aree wumpus i dati che abbisognano dei gamescript appositi
    """
    for area in database["areas"].itervalues():
        if not area.wumpus:
            continue
        # Per tutto il contenuto dell'area wumpus controlla se una delle entità
        # è uguale come codice ad una indicata nella istanza della classe Wumpus,
        # se è così allora importa nel dato relativo al codice tutte le funzioni
        # wumpus generiche adatte
        for obj in area.iter_protos():
            attr_name = area.wumpus.get_related_attr_name(obj)
            if attr_name:
                import_wumpus_gamescripts(obj, attr_name)
#- Fine Funzione -


def get_wumpus_gamescripts_module(obj, attr_name=""):
    """
    Importa tutti i necessari gamescript relativi ad un'entità di un'area wumpus.
    """
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return None

    # ---------------------------------------------------------------------

    # Se non è stato passato il nome dell'attributo della classe Wumpus a cui
    # appartiene l'obj passato allora è normale che obj non sia uno di quelli
    if not attr_name:
        area_code = obj.code.split("_")[0]
        try:
            area = database["areas"][area_code]
        except KeyError:
            log.bug("Non esiste nessuna area con codice %s" % area_code)
            return None
        if not area.wumpus:
            return None
        attr_name = area.wumpus.get_related_attr_name(obj)
        if not attr_name:
            return None

    import_path = "src.games.wumpus_%s_scripts" % attr_name
    if import_path in sys.modules:
        return reload(sys.modules[import_path])

    filepath = import_path.replace(".", "/") + ".py"
    if not os.path.exists(filepath):
        log.bug("Non è stato trovato nessun file %s richiesto per i gamescripts di %s" % (filepath, obj.code))
        return None

    return import_from_anywhere(filepath)
#- Fine Metodo -
