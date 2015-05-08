# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei rifornimenti ai negozianti.
"""

#= IMPORT ======================================================================

import math
import random
import weakref

from src.config     import config
from src.database   import database
from src.enums      import FLAG, TO
from src.gamescript import check_trigger
from src.log        import log
from src.loop       import PersistentLoop, PersistentLoopData
from src.utility    import is_number


#= CLASSI ======================================================================

class DigestionLoop(PersistentLoop):
    def __init__(self):
        super(DigestionLoop, self).__init__()

        self.filename    = "persistence/loops/digestions.dat"
        self.comment     = "In questo file vengono salvate tutte le informazioni relative alle digestioni in corso"
        self.constructor = Digestion
    #- Fine Inizializzazione -


class Digestion(PersistentLoopData):
    def __init__(self, entity=None, ingested=None):
        if not entity:
            self.entity   = None # Entità che sta digerendo qualche cosa
            self.ingested = None # Entità da digerire
            self.timer    = 0    # Minuti reali prima che la digestione termini
        else:
            four_rpg_hour_in_minutes = (config.seconds_in_minute * config.minutes_in_hour * 4) / 60
            ingested.flags += FLAG.INGESTED
            self.entity   = weakref.ref(entity)
            self.ingested = weakref.ref(ingested)
            self.timer    = four_rpg_hour_in_minutes + (0 if ingested.get_total_weight() <= 0 else int(math.log(ingested.get_total_weight())))
    #- Fine Inizializzazione -

    def fread(self, file, line):
        if not file:
            log.bug("file non è un parametro valido: %r", file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r", line)
            return

        # ---------------------------------------------------------------------

        entity_code, ingested_code, timer = line.split(None, 2)

        # Può essere normale che non vi sia l'entità, a volte le persistenze vengono rimosse
        if "_" in entity_code:
            table_name = entity_code.split("_", 2)[1] + "s"
        else:
            table_name = "players"
        if not table_name in database:
            log.bug("Non esiste nessuna tabella dal nome %s nel database" % table_name)
            return
        if entity_code not in database[table_name]:
            return
        entity = database[table_name][entity_code]

        table_name = ingested_code.split("_", 2)[1] + "s"
        if not table_name in database:
            log.bug("Non esiste nessuna tabella dal nome %s nel database" % table_name)
            return
        if ingested_code not in database[table_name]:
            return
        ingested = database[table_name][ingested_code]

        if not is_number(timer):
            log.bug("timer ricavato per il supply %s non è un numero: %s" % (line, timer))
            return

        self.entity   = weakref.ref(entity)
        self.ingested = weakref.ref(ingested)
        self.timer    = int(timer)

        digestion_loop.datas.append(self)
    #- Fine Metodo -

    def fwrite(self, file):
        if not file:
            log.bug("file non è un parametro valido: %r", file)
            return

        # ---------------------------------------------------------------------

        if not self.is_valid():
            return

        file.write("%s %s %d\n" % (self.entity().code, self.ingested().code, self.timer))
    #- Fine Metodo -

    def is_valid(self):
        if self.entity and self.entity() and self.ingested and self.ingested():
            return True
        else:
            return False
    #- Fine Metodo -

    def have_same_purpose(self, entity, ingested):
        if not entity:
            log.bug("entity non è un parametro valido: %r", entity)
            return False

        # ---------------------------------------------------------------------

        if not self.is_valid():
            return False

        if self.entity() == entity and self.ingested() == ingested:
            return True
        else:
            return False
    #- Fine Metodo -

    def execute(self):
        """
        Anche ai giocatori offline esegue la digestione.
        """
        if not self.is_valid():
            return

        entity = self.entity()
        ingested = self.ingested()

        force_return = check_trigger(entity, "before_digestion", self)
        if force_return:
            return
        force_return = check_trigger(ingested, "before_digested", self)
        if force_return:
            return

        entity.act("Dall'aria che sale dal tuo stomaco sembra che tu abbia appena digerito $N.", TO.ENTITY, ingested)
        # Per galanteria viene inviato solo una volta ogni tanto
        if random.randint(0, 100) == 0:
            entity.act("A $n scappa un rutto! Sembra che abbia appena digerito qualcosa.", TO.OTHERS, ingested)
        entity.act("Sembra che $n ti abbia appena digerito, è giunto il momento di andare sempre più giù...", TO.TARGET, ingested)
        ingested.extract(ingested.quantity, use_repop=True)

        force_return = check_trigger(entity, "after_digestion", self)
        if force_return:
            return
        force_return = check_trigger(ingested, "after_digested", self)
        if force_return:
            return
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def stop_digestion(ingested, remove_flag=True):
    if not ingested:
        log.bug("ingested non è un parametro valido: %r" % ingested)
        return

    # -------------------------------------------------------------------------

    if remove_flag:
        ingested.flags -= FLAG.INGESTED
#- Fine Metodo -


#= SINGLETON ===================================================================

digestion_loop = DigestionLoop()
