# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica dei comandi.
Il codice sorgente relativo ai comandi lo trovate alla cartella src/commands.
"""


#= IMPORT ======================================================================

import sys

from src.data      import Data
from src.database  import database
from src.element   import Element, Flags
from src.enums     import CMDTYPE, TRUST, POSITION, CMDFLAG, RACE
from src.interpret import yield_inputs_items, translate_input
from src.log       import log
from src.utility   import html_escape


#= CLASSI ======================================================================

class Command(Data):
    """
    Gestisce tutte le caratteristiche di un comando.
    Se tra gli attributi cercate quelli che servono per chiamare il comando
    tramite il testo inviato dai giocatori qui non li troverete, per quel
    compito ci pensa la classe Input().
    """
    PRIMARY_KEY = "fun_name"
    VOLATILES   = ["timer",    "module", "function",]
    MULTILINES  = ["mini_help"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, fun_name=""):
        self.comment   = ""
        self.fun_name  = fun_name or ""  # Nome della funzione
        self.type      = Element(CMDTYPE.INFORMATION) # Tipologia del comando
        self.trust     = Element(TRUST.PLAYER)  # Fiducia minima per digitarlo
        self.position  = Element(POSITION.REST)  # Posizione minima per utilizzarlo
        self.flags     = Flags(CMDFLAG.NONE)  # Flag dei comandi
        self.no_races  = Flags(RACE.NONE)  # Razze che NON possono usarlo (RACE.NONE significa che tutti lo possono utilizzare)
        self.mini_help = ""   # Piccola descrizione dell'utilizzo del comando
        self.timer     = 0.0  # Tempo totale di esecuzione del comando (anche se nelle pagine d'amministrazione visualizza il tempo medio)

        # Variabili volatili
        self.module    = None  # Riferimento al modulo che contiene la funzione
        self.function  = None  # Riferimento alla funzione
        if self.fun_name:
            self.import_module_and_function()
    #- Fine Inizializzazione -

    def get_error_message(self):
        """
        Ritorna un messaggio di errore se qualcosa nel comando è sbagliata,
        altrimenti se tutto è a posto ritorna una stringa vuota.
        """
        if not self.fun_name:
            msg = "il nome della funzione non è valido"
        elif (not self.fun_name.startswith("command_")
        and   not self.fun_name.startswith("skill_")
        and   not self.fun_name.startswith("social_")):
            msg = "il nome della funzione non inizia per command_, skill_ o social_"
        elif self.type.get_error_message(CMDTYPE, "type") != "":
            msg = self.type.get_error_message(CMDTYPE, "type")
        elif self.trust.get_error_message(TRUST, "trust") != "":
            msg = self.trust.get_error_message(TRUST, "trust")
        elif self.position.get_error_message(POSITION, "position") != "":
            msg = self.position.get_error_message(POSITION, "position")
        elif self.flags.get_error_message(CMDFLAG, "flags") != "":
            msg = self.flags.get_error_message(CMDFLAG, "flags")
        elif self.no_races.get_error_message(RACE, "no_races") != "":
            msg = self.no_races.get_error_message(RACE, "no_races")
        # Ignora i minihelp vuoti relativi ai comandi-social
        elif not self.mini_help and not self.fun_name.startswith("social_"):
            msg = "la stringa di mini help è vuota"
        elif self.timer < 0.0:
            msg = "il timer non può essere negativo: %f" % self.timer
        elif not self.module:
            msg = "modulo non importato"
        elif not self.function:
            msg = "funzione non importata"
        else:
            return ""
        # Se arriva qui significa che ha un messaggio da inviare
        log.bug("(Command: fun_name %s) %s" % (self.fun_name, msg))
        return msg
    #- Fine Metodo -

    def get_total_use_count(self):
        """
        Ritorna l'utilizzo totale della funzione di comando tra tutti gli input.
        """
        total_use_count = 0

        for inputs_name, inputs in yield_inputs_items():
            for input in inputs:
                if input.command == self:
                    total_use_count += input.counter_use

        return total_use_count
    #- Fine Metodo -

    def import_module_and_function(self):
        """
        Importa il modulo che contiene la funzione del comando.
        """
        if   self.fun_name.startswith("command_"):  package = "src.commands."
        elif self.fun_name.startswith("skill_"):    package = "src.skills."
        elif self.fun_name.startswith("social_"):   package = "src.socials."
        else:
            log.bug("la fun_name del comando è errata: %s" % self.fun_name)
            return None

        import_path = package + self.fun_name
        self.module = __import__(import_path, globals(), locals(), [""])
        self.function = getattr(self.module, self.fun_name)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def import_modules_and_functions():
    for command in database["commands"].itervalues():
        command.import_module_and_function()
#- Fine Funzione -


def check_commands_fun_name():
    """
    Controlla che esista almeno e solo una funzione di comando non alternativa
    per ogni lista di inputs.
    """
    for command in database["commands"].itervalues():
        command_type = command.fun_name[ : command.fun_name.find("_")]

        # Controlla prima che una funzione di comando non si trovi in una
        # lista di inputs non congrua alla sua tipologia
        for inputs_name, inputs in yield_inputs_items():
            input_type = inputs_name[len("inputs_") : inputs_name.rfind("_")]
            for input in inputs:
                if input.command == command and command_type != input_type:
                    log.bug("input con tipologia di comando %s utilizzato in una lista di input errata: %s" % (
                        command.fun_name, inputs_name))

        # Controlla che esista una e una sola funzione di comando non
        # alternativa laddove serve
        for inputs_name, inputs in yield_inputs_items():
            input_type = inputs_name[len("inputs_") : inputs_name.rfind("_")]
            count = 0
            for input in inputs:
                if input.command != command or command_type != input_type:
                    continue
                if not input.alternative:
                    count += 1

            if command_type == input_type:
                if count == 0:
                    log.bug("fun_name %s inesistente per gli input %s" % (command.fun_name, inputs_name))
                if count > 1:
                    log.bug("Più di una fun_name %s 'ufficiale', deve esservene solo una le altre sono le alternative, negli input %s" % (command.fun_name, inputs_name))
#- Fine Funzione -


def get_command_syntax(entity, fun_name):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not fun_name:
        log.bug("fun_name non è un parametro valido: %r" % fun_name)
        return ""

    # -------------------------------------------------------------------------

    module = database["commands"][fun_name].module
    if not module:
        log.bug("module non è valido: %r" % module)
        return ""

    syntax_string = getattr(module, "get_syntax_template")(entity)
    if not syntax_string:
        log.bug("syntax_string non è valida: %r" % syntax_string)
        return ""

    # Ricava il nome dell'input dalla funzione del comando
    input_word = fun_name[fun_name.find("_")+1 : ]
    # Ricava la traduzione dell'input a seconda della lingua dei
    # comandi utilizzata dall'entità
    translation = translate_input(entity, input_word, "en")

    # Preparare ed invia la tabella con la sintassi colorata del comando
    output = '''<table class="mud">'''
    for x, line in enumerate(syntax_string.split("\n")):
        if not line.strip():
            continue

        # Esegue un replace di tutti i simboli di minore e maggiore che devono
        # essere passati nella pagina come entità html
        line = html_escape(line)

        # Se trova uno spazio significa che ci sono argomenti aggiuntivi
        # al comando normale che colora di verde più scuro
        if " " in line:
            line = line.replace(input_word, "[limegreen]%s[close][green]" % translation, 1)
        else:
            line = line.replace(input_word, "[limegreen]%s" % translation, 1)
        line = '''<td>%s[close]</td></tr>''' % line

        # Alla prima linea inserisce la dicitura di Sintassi, alle altre dello
        # spazio per incolonnare correttamente
        if x == 0:
            line = '''<tr><td>[yellow]Sintassi[close]:</td>%s''' % line
        else:
            line = '''<tr><td></td>%s''' % line
        output += line
    output += '''</table>'''

    return output
#- Fine Funzione -
