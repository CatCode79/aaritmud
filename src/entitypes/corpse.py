# -*- coding: utf-8 -*-

"""
Modulo riguardante il cadavere di un mob.
"""

#= IMPORT ======================================================================

from src.config   import config
from src.database import database
from src.log      import log
from src.loop     import UnstoppableLoop
from src.utility  import copy_existing_attributes


#= COSTANTI ====================================================================

CORPSE_DESCRS = ("$N giace qui.",
                 "$N è attaccato da un nugolo di mosche.",
                 "$N appesta l'aria con un terribile olezzo.",
                 "$N pullula di vermi e parassiti.",
                 "$N è ormai all'ultimo stadio di decadimento.")


#= CLASSI ======================================================================

class Corpse(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment                 = ""     # Commento relativo a questa entitype
        self.was_player              = False  # Indica se il cadavere era di un giocatore o di un mob
        self.decomposition_rpg_hours = 0      # Ore di decomposizione
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if self.decomposition_rpg_hours < 0:
            return "decomposition_rpg_hours non è un valore di ore rpg valido: %d" % self.decomposition_rpg_hours

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Corpse()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, corpse2):
        if not corpse2:
            return False

        if self.comment != corpse2.comment:
            return False
        if self.was_player != corpse2.was_player:
            return False
        if self.decomposition_rpg_hours != corpse2.decomposition_rpg_hours:
            return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_long(self):
        days = self.decomposition_rpg_hours / config.hours_in_day
        if days >= len(CORPSE_DESCRS):
            days = len(CORPSE_DESCRS) - 1

        return CORPSE_DESCRS[days]
    #- Fine Metodo -


class DecomposerLoop(UnstoppableLoop):
    def __init__(self):
        super(DecomposerLoop, self).__init__()
        self.paused = False  # Indica se questo ciclo è stato messo in pausa dal comando loop
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        if seconds == 0:
            # Qui i secondi andrebbero impostati come:
            # config.seconds_in_minute * config.minutes_in_hour
            # tuttavia per rendere omogeneo tutto il codice e la configurazione
            # dei cicli il valore è stato calcolato e inserito nel config
            seconds = config.decomposer_loop_seconds
        super(DecomposerLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(DecomposerLoop, self).stop()
        else:
            log.bug("Il DecomposerLoop non è stato trovato attivo.")
    #- Fine Metodo -

    def cycle(self):
        if self.paused:
            return

        to_extracts = []
        for table_name in ("items", "mobs", "players"):
            for data in database[table_name].itervalues():
                if not data.corpse_type:
                    continue
                data.corpse_type.decomposition_rpg_hours += 1
                if data.corpse_type.decomposition_rpg_hours / config.hours_in_day >= len(CORPSE_DESCRS):
                    # Rimuove dopo un po' solo i cadaveri dei mob oppure quelli vuoti
                    if not data.corpse_type.was_player or data.is_empty():
                        to_extracts.append(data)

        # Li estrai in un ciclo a parte perché altrimenti sballerebbe l'iterabilità
        # del ciclo superiore, l'alternativa è quella di utilizzare reversed
        # ma si va a perdere in performance
        for en in to_extracts:
            en.extract(en.quantity, use_repop=False)
    #- Fine Metodo -


#= SINGLETON ===================================================================

decomposer_loop = DecomposerLoop()
