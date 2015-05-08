# -*- coding: utf-8 -*-

"""
Modulo di gestione del loop principale del gioco.
"""

# (OO) in questo modulo per motivi di prestazione si accede all'attributo data
# delle flags, invece di utilizzare flags stessa come da norma.


#= IMPORT ======================================================================

import random
import sys

from twisted.internet import reactor

from src.calendar   import calendar
from src.connection import connections
from src.config     import config
from src.database   import database
from src.defer      import defer
from src.engine     import engine
from src.enums      import FLAG
from src.log        import log
from src.reset      import check_room_reset_events
from src.loop       import UnstoppableLoop

from src.games.maze import remake_mazes


#= COSTANTI ====================================================================

SHUTDOWN_INTERVALS = (900, 600, 300, 60, 30, 1)


#= CLASSI ======================================================================

class GameLoop(UnstoppableLoop):
    def __init__(self):
        super(GameLoop, self).__init__()

        self.paused          = False
        self.elapsed_seconds = 0  # Numero dei secondi trascorsi dal boot, cioè prima di attivare il loop
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        if seconds == 0:
            seconds = config.game_loop_seconds
        super(GameLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(GameLoop, self).stop()
        else:
            log.bug("Il GameLoop non è stato trovato attivo.")
    #- Fine Metodo -

    def cycle(self):
        """
        Sostanzialmente la classica funzione di game_loop presente in tutti i
        Diku-Like.
        """
        if self.paused:
            return
        self.elapsed_seconds += 1

        #- Parte relativa lo shutdown ---------------------------------------

        if engine.seconds_to_shutdown >= 0:
            if engine.seconds_to_shutdown in SHUTDOWN_INTERVALS:
                for conn in reversed(connections.values()):
                    if not conn.player or not conn.player.game_request:
                        continue
                    if engine.seconds_to_shutdown > 60:
                        time_descr = "%d minuti" % engine.seconds_to_shutdown / 60
                    elif engine.seconds_to_shutdown == 60:
                        time_descr = "1 minuto"
                    elif engine.seconds_to_shutdown == 1:
                        time_descr = "ORA!!"
                    else:
                        time_descr = "%d secondi" % engine.seconds_to_shutdown
                    # (bb) Ok, lo si risolve così questo problema dei colori,
                    # ma bisognerebbe supportare le colorazioni annidate,
                    # visto che il nome del mud potrebbe essere colorato, e
                    # sarebbe meglio la riga commentata sotto
                    #conn.player.send_output("\n[red]Attenzione! Lo Shutdown di %s avverrà tra %s![close]" % (
                    conn.player.send_output("\n[red]Attenzione! Lo Shutdown di[close] %s [red]avverrà tra %s![close]" % (
                        config.game_name, time_descr))
                    conn.player.send_prompt()
            engine.seconds_to_shutdown -= 1
            if engine.seconds_to_shutdown < 0:
                # Bisogna uscire dallo scope del loop tramite una deferred
                # per eseguire uno shutdown senza fastidiose eccezioni
                defer(0, shutdown_mud)

        #- Cose aggiornate ad ogni minuto RPG: ---------------------------------

        if self.elapsed_seconds % config.seconds_in_minute == 0:
            # Aggiorna il calendario rpg
            calendar.update()

            # Aggiorna i punti di vita, mana e movimento dei mob e dei pg
            # (TD) yield iter dei valori del database
            for entity in database["mobs"].values() + database["players"].values():
                if not entity.location:
                    continue
                if entity.location.IS_ROOM:
                    if FLAG.INGESTED not in entity.flags.data:
                        entity.update_points()
                else:
                    player_carrier = entity.get_player_carrier()
                    if not player_carrier or player_carrier.game_request:
                        if FLAG.INGESTED not in entity.flags.data:
                            entity.update_points()

            # Aggiorna l'exp e invia le informazioni per il client
            for player in database["players"].itervalues():
                if player.game_request:
                    player.update()

            # Controlla che gli eventi di reset siano attivi correttamente;
            # una volta trovato un possibile room reset senza evento lo
            # ricontrolla dopo più di due secondi per essere sicuri che non
            # sia una transizione tra l'estinzione di un evento di reset e
            # la creazione di quello successivo
            if config.check_references:
                pass
                # (TT) Per ora disattivato che magari fa casino con i reset
                #check_room_reset_events()

            # Questo si attiva ogni ora rpg
            if calendar.minute == 0:
                remake_mazes()

        # Per bilanciare il carico della cpu visto che su Aarit un minuto è
        # formato da due secondi l'altro secondo è utilizzato per eseguire
        # i comportamenti
        if (self.elapsed_seconds % config.seconds_in_minute == 1
        or config.seconds_in_minute == 1):
            areas = database["areas"].values()
            # Può capitare che il gioco sia stato avviato vergine di aree
            if areas:
                self.update_behaviours(areas, "mobs")
                self.update_behaviours(areas, "items")

        #- Cose aggiornate ogni mezz'ora RPG: ---------------------------------

        if self.elapsed_seconds % ((config.seconds_in_minute * config.minutes_in_hour) / 2) == 0:
            # Aggiornamento delle condizioni: fame, sete, sonno... etc etc
            # (TD) fare quel sistema di iter database
            for entity in database["mobs"].values() + database["players"].values():
                if not entity.location:
                    continue
                if entity.location.IS_ROOM:
                    if FLAG.INGESTED not in entity.flags.data:
                        entity.update_conditions()
                else:
                    player_carrier = entity.get_player_carrier()
                    if not player_carrier or player_carrier.game_request:
                        if FLAG.INGESTED not in entity.flags.data:
                            entity.update_conditions()
    #- Fine Metodo -

    # (TD) fare una superclass e spostare questo in behaviour, magari
    # creare un loop apposito
    def update_behaviours(self, areas, list_to_use):
        """
        Esegue un update dei comportamenti per una metà casuale di aree.

        In questo metodo per ragioni prestazionali viene effettuato il controllo
        dell'esistenza di una flag direttamente sul dizionario invece che
        sulle flags.
        """
        if not areas:
            log.bug("areas non è un parametro valido: %r" % areas)
            return

        if list_to_use not in ("mobs", "items"):
            log.bug("list_to_use non è un parametro valido: %s" % list_to_use)
            return

        # ---------------------------------------------------------------------

        if not config.use_behaviours:
            return

        for area in random.sample(areas, len(areas) / 2 + 1):
            for entity in getattr(area, list_to_use):
                if not entity.location:
                    continue
                # Se l'entità possiede delle interazioni attive su di sé allora
                # non esegue nessun behaviour
                if entity.interactions:
                    continue
                if entity.location.IS_ROOM:
                    if not entity.behaviour and (not getattr(entity.location, entity.ACCESS_ATTR[:-1] + "_behaviour") or FLAG.NO_ROOM_BEHAVIOUR in entity.flags):
                        continue
                    if FLAG.INGESTED not in entity.flags.data and FLAG.BURIED not in entity.flags.data:
                        entity.update_behaviour()
                else:
                    if not entity.behaviour:
                        continue
                    player_carrier = entity.get_player_carrier()
                    if not player_carrier or player_carrier.game_request:
                        if FLAG.INGESTED not in entity.flags.data and FLAG.BURIED not in entity.flags.data:
                            entity.update_behaviour()
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def shutdown_mud():
    reactor.stop()
    sys.exit(0)
#- Fine Funzione -


#= SINGLETON ===================================================================

game_loop = GameLoop()
