# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei combattimenti.
"""


#= IMPORT ======================================================================

import random
import weakref

from src.config     import config
from src.database   import database
from src.enums      import FLAG
from src.fight      import start_fight
from src.gamescript import check_trigger
from src.interpret  import interpret_or_echo
from src.log        import log
from src.loop       import PersistentLoop, PersistentLoopData
from src.utility    import is_number


#= CLASSI ======================================================================

class AggressivenessLoop(PersistentLoop):
    def __init__(self):
        super(AggressivenessLoop, self).__init__()

        self.filename    = "persistence/loops/aggressivenesses.dat"
        self.comment     = "In questo file vengono salvate tutte le informazioni relative all'invio di messaggi d'avvertimento aggressivi indicanti un imminente attacco"
        self.constructor = ExpressAggressiveness
    #- Fine Inizializzazione -


class ExpressAggressiveness(PersistentLoopData):
    def __init__(self, aggressor=None, victim=None):
        if not aggressor and not victim:
            self.aggressor       = None  # Aggressore che invia i messaggi di avvertimento
            self.victim          = None  # Vittima designata ai messaggi di avvertimento
            self.timer           = 0     # Tempo in secondi prima che scatti il prossimo avvertimento o l'attacco
            self.remaining_tries = 0
        elif aggressor and victim:
            self.aggressor       = weakref.ref(aggressor)
            self.victim          = weakref.ref(victim)
            self.timer           = self.get_timer()
            self.remaining_tries = len(aggressor.aggressivenesses)
        else:
            log.bug("Non tutti i parametri passati sono validi: aggressor=%r victim=%r" % (aggressor, victim))
    #- Fine Inizializzazione -

    def fread(self, file, line):
        if not file:
            log.bug("file non è un parametro valido: %r", file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r", line)
            return

        # ---------------------------------------------------------------------

        aggressor_code, victim_code, timer, remaining_tries = line.split(None, 3)

        # Può essere normale che non vi sia l'aggressore o la vittima a volte
        # le persistenze vengono rimosse
        table_name = aggressor_code.split("_", 2)[1] + "s"
        if not table_name in database:
            log.bug("Non esiste nessuna tabella dal nome %s nel database" % table_name)
            return
        if aggressor_code not in database[table_name]:
            return
        aggressor = database[table_name][aggressor_code]

        if "_" in victim_code:
            table_name = victim_code.split("_", 2)[1] + "s"
        else:
            table_name = "players"
        if not table_name in database:
            log.bug("Non esiste nessuna tabella dal nome %s nel database" % table_name)
            return
        if victim_code not in database[table_name]:
            return
        victim = database[table_name][victim_code]

        if not is_number(timer):
            log.bug("timer ricavato per il buyable %s non è un numero: %s" % (line, timer))
            return

        if not is_number(remaining_tries):
            log.bug("remaining_tries ricavato per il buyable %s non è un numero: %s" % (line, remaining_tries))
            return

        self.aggressor       = weakref.ref(aggressor)
        self.victim          = weakref.ref(victim)
        self.timer           = int(timer)
        self.remaining_tries = int(remaining_tries)

        aggressiveness_loop.datas.append(self)
    #- Fine Metodo -

    def fwrite(self, file):
        if not file:
            log.bug("file non è un parametro valido: %r", file)
            return

        # ---------------------------------------------------------------------

        if not self.is_valid():
            return

        file.write("%s %s %d %d\n" % (self.aggressor().code, self.victim().code, self.timer, self.remaining_tries))
    #- Fine Metodo -

    def is_valid(self):
        if self.aggressor and self.aggressor() and self.victim and self.victim():
            return True
        else:
            return False
    #- Fine Metodo -

    def have_same_purpose(self, aggressor, victim):
        if not aggressor:
            log.bug("aggressor non è un parametro valido: %r", aggressor)
            return False

        if not victim:
            log.bug("victim non è un parametro valido: %r", victim)
            return False

        # ---------------------------------------------------------------------

        if not self.is_valid():
            return False

        if self.aggressor() == aggressor and self.victim() == victim:
            return True
        else:
            return False
    #- Fine Metodo -

    def execute(self):
        if not self.is_valid():
            return

        aggressor = self.aggressor()
        victim = self.victim()

        if not aggressor.aggressivenesses:
            log.bug("aggressor %s non possiede messaggi di aggressivenesses da inviare: %r" % (aggressor, aggressor.aggressivenesses))
            return

        if aggressor.location != victim.location:
            return

        if config.reload_commands:
            reload(__import__("src.commands.command_kill", globals(), locals(), [""]))
        from src.commands.command_kill import command_kill

        force_return = check_trigger(aggressor, "before_express_aggressiveness", self)
        if force_return:
            return
        force_return = check_trigger(victim, "before_undergoes_aggressiveness", self)
        if force_return:
            return

        # Attacca solamente se il numero di tentativi di avvertimento sono
        # terminati oppure per caso ma viene sempre inviato almeno un avvertimento
        if (aggressor.IS_MOB and self.remaining_tries < len(aggressor.aggressivenesses)
        and (self.remaining_tries == 0 or random.randint(0, self.remaining_tries) == 0)):
            command_kill(aggressor, victim.get_numbered_keyword(looker=aggressor))
        else:
            # Se non vi fosse questo check gli oggetti continuerebbero ad inviare
            # il messaggio di minaccia per sempre, questo perché non possono
            # uccidere ed entrare nella condizione superiore
            if self.remaining_tries > 0:
                argument = random.choice(aggressor.aggressivenesses)
                if not argument:
                    log.bug("aggressivenesses di %s possiede del testo non valido: %r" % (aggressor, argument))
                    return
                interpret_or_echo(aggressor, argument, looker=victim)
                self.timer = self.get_timer()
                self.remaining_tries -= 1

        force_return = check_trigger(aggressor, "after_express_aggressiveness", self)
        if force_return:
            return
        force_return = check_trigger(victim, "after_undergoes_aggressiveness", self)
        if force_return:
            return
    #- Fine Metodo -

    def get_timer(self):
        return random.randint(3, 6)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def check_aggressiveness(aggressor, victim=None):
    """
    Controlla se un'entità possa attaccarne un'altra se questa ultima viene
    passata come parametro, altrimenti viene cercata una possibile vittima.
    """
    if not aggressor:
        log.bug("aggressor non è un parametro valido: %r" % aggressor)
        return

    # -------------------------------------------------------------------------

    if FLAG.AGGRESSIVE not in aggressor.flags:
        log.bug("Inattesa chiamata senza che l'entità sia aggressiva: %s (victim: %s)" % (aggressor.code, victim.code if victim else "None"))
        return

    # Se non è stata passata una vittima ne cerca una
    if victim:
        if not aggressor.can_aggress(victim):
            return
    else:
        victims = []
        for en in aggressor.location.iter_contains():
            if aggressor.can_aggress(en):
                victims.append(en)
        if not victims:
            return
        victim = random.choice(victims)

    if aggressor.aggressivenesses:
        aggressiveness_loop.add(aggressor, victim)
    else:
        start_fight(aggressor, victim)
#- Fine Funzione -


# (TD) forse anche per l'attacco dei carnivori ci vorrebbe un check sul livello?
def can_aggress(aggressor, victim):
    """
    Funzione con le regole di aggressivibilità di un'entità rispetto ad un'altra.
    I giocatori sono sempre aggredibili, mentre per le altre entità vengono
    utilizzate regole di legge della natura semplificate.
    """
    if not aggressor:
        log.bug("aggressor non è un parametro valido: %r" % aggressor)
        return

    if not victim:
        log.bug("victim non è un parametro valido: %r" % victim)
        return

    # -------------------------------------------------------------------------

    # I giocatori vengono attaccati solo se di livello relativamente uguale o
    # basso rispetto all'aggressore
    if victim.IS_PLAYER and victim.level <= aggressor.level+1:
        return True

    # Attacca per cibo
    if FLAG.CARNIVOROUS in aggressor.flags and FLAG.HERBIVORE in victim.flags:
        return True

    # Attacca per territorio
    if FLAG.CARNIVOROUS in aggressor.flags and FLAG.CARNIVOROUS in victim.flags:
        return True

    return False
#- Fine Funzione -


#= SINGLETON ===================================================================

aggressiveness_loop = AggressivenessLoop()
