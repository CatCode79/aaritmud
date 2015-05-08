# -*- coding: utf-8 -*-

"""
Modulo di gestione generica dei loop, in particolar modo serve a evitare che
i loop crashino bloccando funzionalità del gioco.
"""


#= IMPORT ======================================================================

import os
import sys
import traceback

from twisted.internet import task

from src.config   import config
from src.database import database
from src.log      import log
from src.utility  import create_folders, create_file, from_capitalized_words


#= CLASSI ======================================================================

class UnstoppableLoop(task.LoopingCall):
    """
    Questa è la classe madre per tutti i loop del gioco.
    Viene chiamata unstoppable perché un'eccezione alzata dal codice eseguito
    tramite cycle non ferma il relativo loop, cosa che accade nei normali
    LoopingCall di twisted, questo permette di mantenere funzionante il gioco
    al 100%.
    L'eccezione viene stampata sulla stdout, attenzione quindi nel qual caso
    stiate redirezionando l'output relativo su file, utilizzate un logrotate
    così da evitare intasamenti dello spazio fisico nel qual caso il loop
    invii eccezioni ad ogni ciclo (che nel caso di alcuni loop potrebbero essere
    più di uno al secondo)
    """
    def __init__(self):
        super(UnstoppableLoop, self).__init__(self.unstoppable_cycle)
        self.paused = False  # Indica se il loop è stato messo in pausa o meno
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        log.booting("-> %s" % self.__class__.__name__)
        if seconds == 0:
            attr_name = from_capitalized_words(self.__class__.__name__) + "_seconds"
            seconds = getattr(config, attr_name)
        super(UnstoppableLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        log.shutdown("-> %s" % self.__class__.__name__)
        if self.running:
            super(UnstoppableLoop, self).stop()
        else:
            log.bug("Il loop %s non è stato trovato attivo." % self.__class__.__name__)
    #- Fine Metodo -

    def unstoppable_cycle(self):
        try:
            self.cycle()
        except:
            traceback.print_exc(file=sys.stdout)
    #- Fine Metodo -

    def cycle(self):
        raise NotImplementedError
    #- Fine Metodo -


class PersistentLoop(UnstoppableLoop):
    def __init__(self):
        super(PersistentLoop, self).__init__()

        self.filename    = ""     # File in cui salvare i dati del loop
        self.comment     = ""     # Commento descrittivo inserito nel file ogni volta che viene salvato
        self.constructor = None   # Classe utilizzata per creare i dati del loop
        self.datas       = []     # Dati del loop su cui eseguire il cycle
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        self.read()
        super(PersistentLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(PersistentLoop, self).stop()
            self.save()
        else:
            log.bug("Il loop %s non è stato trovato attivo." % self.__class__.__name__)
    #- Fine Metodo -

    def read(self):
        folder = os.path.split(self.filename)[0]
        create_folders(folder)
        create_file(self.filename)
        try:
            loop_file = open(self.filename, "r")
        except IOError:
            log.bug("Impossibile aprire il file %s in lettura" % self.filename)
            return

        for line in loop_file:
            line = line.strip()
            if not line:
                continue
            if line[0] == "#":
                continue
            data = self.constructor()
            data.fread(loop_file, line)
            self.datas.append(data)
    #- Fine Metodo -

    def save(self):
        # Il file viene comunque creato all'avvio con il solo commento.
        if not config.save_persistence:
            return

        if database.avoid_save_on_shutdown:
            return

        folder = os.path.split(self.filename)[0]
        create_folders(folder)
        create_file(self.filename)
        try:
            loop_file = open(self.filename, "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % self.filename)
            return

        if self.comment:
            loop_file.write("# %s\n" % self.comment)

        for data in self.datas:
            data.fwrite(loop_file)
    #- Fine Metodo -

    def add(self, *args):
        """
        Crea ed inserisce nel ciclo un nuovo supply.
        """
        # Evita di inserire un nuovo supply nel loop se ne trova un'altro
        # con la stessa funzione già in atto
        for data in self.datas:
            if data.have_same_purpose(*args):
                return

        data = self.constructor(*args)
        # Se il timer è stato impostato a 0 significa che si vuole l'esecuzione
        # subito quindi non vi è neppure la necessità di inserirlo nel loop
        if data.timer == 0:
            data.execute()
        else:
            self.datas.append(data)
    #- Fine Metodo -

    def cycle(self):
        if self.paused:
            return

        for data in self.datas:
            # Coglie l'occasione per rimuovere eventuali supply non più validi
            if not data.is_valid():
                self.datas.remove(data)
                continue
            data.timer -= 1
            if data.timer <= 0 or config.time_warp:
                data.execute()
                # Il timer potrebbe essere stato modificato durante un trigger
                # nell'execute quindi ricontrolla se veramente rimuoverlo o meno
                if data.timer <= 0:
                    self.datas.remove(data)
    #- Fine Metodo -


class PersistentLoopData(object):
    """
    È sempre meglio che dati dei loop persistenti posseggano, laddove possibile,
    degli attributi inizializzati tramite il modulo weakref in maniera tale che
    la natura asincrona dei loop non obblighi determinati oggetti a rimanere in
    memoria inficiando sulla quantità della stessa.
    """
    def __init__(self):
        self.timer = 0  # Serve a tenere conto del tempo trascorso tramite il loop
    #- Fine dell'Inizializzazione -

    def fread(self):
        raise NotImplementedError
    #- Fine dell'Inizializzazione -

    def fwrite(self):
        raise NotImplementedError
    #- Fine dell'Inizializzazione -

    def is_valid(self):
        raise NotImplementedError
    #- Fine dell'Inizializzazione -

    def have_same_purpose(self):
        raise NotImplementedError
    #- Fine dell'Inizializzazione -

    def execute(self):
        raise NotImplementedError
    #- Fine dell'Inizializzazione -
