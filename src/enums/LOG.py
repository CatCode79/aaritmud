# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di log.
"""

from src.element import EnumElement, finalize_enumeration
from src.enums import TRUST


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#-------------------------------------------------------------------------------

class LogElement(EnumElement):
    def __init__(self, name, description=""):
        super(LogElement, self).__init__(name, description)
        self.trust              = TRUST.MASTER
        self.is_checkable       = True
        self.show_on_mud        = True
        self.write_on_file      = True
        self.print_on_console   = True
        self.show_last_function = True
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE        = LogElement("Nessuno")
ALWAYS      = LogElement("Always",     "Messaggi importanti che vengono visualizzati agli admin nonostante non abbiano l'opzione attiva")
BOOTING     = LogElement("Booting",    "Messaggi relativi al caricamento del database all'avvio del Mud")
BACKUP      = LogElement("Backup",     "Messaggi relativo al backup di tutto il database del Mud")
SAVE        = LogElement("Save",       "Messaggi relativo al salvataggio dei dati per la persistenza del mondo del Mud")
SHUTDOWN    = LogElement("Shutdown",   "Messaggi relativo allo shutdown del Mud")
FREAD       = LogElement("Fread",      "Messaggio relativo alla lettura dei dati su file testuali")
FWRITE      = LogElement("Fwrite",     "Messaggio relativo alla scrittura dei dati su file testuali")
CONN        = LogElement("Conn",       "Messaggio relativi alle connessioni")
WARNING     = LogElement("Warning",    "Informazioni di warning, tipo presunti bachi.")
ERROR       = LogElement("Error",      "Messaggi della get_error_message() e altri che non vogliono far scattare il tracking della send_log")
BUG         = LogElement("Bug",        "Messaggi riguardanti i bachi, di solito questa è la tipologia più diffusa di log")
INPUT       = LogElement("Input",      "Messaggi riguardanti gli input digitati dai giocatori")
DELETE      = LogElement("Delete",     "Messaggi riguardanti la cancellazione di dati")
BADWORD     = LogElement("BadWord",    "Messaggi che indicano che in un canale rpg sono state dette parolacce")
OFFRPG      = LogElement("OffRpg",     "Messaggi che indicano che in un canale rpg sono state dette parole off-rpg o altre azioni non rpg")
HUH         = LogElement("Huh",        "Messaggi relativi a input digitato scorrettamente")
TIME        = LogElement("Time",       "Messaggi relativi agli input che ci mettono troppo tempo nell'esecuzione")
CONVERT     = LogElement("Convert",    "Messaggi relativi alla conversione delle aree")
COMMAND     = LogElement("Command",    "Messaggi relativi a comandi da loggare")
CHECK_RESET = LogElement("CheckReset", "Messaggi relativi al controllo degli eventi di reset")
RESET       = LogElement("Reset",      "Messaggi relativi al resetting delle stanze e delle entità")
REPOP       = LogElement("Repop",      "Messaggi relativi al repopping delle entità")
GAMESCRIPT  = LogElement("Gamescript", "Messaggi relativi all'attivazione dei gamescript")
PLANT       = LogElement("Plant",      "Messaggi relativi ai differenti stadi di crescita")
HTTP        = LogElement("Http",       "Messaggi relativi alle richieste di risorse http")  # (TD)
ADMIN       = LogElement("Admin",      "Messaggi relativi alle azioni degli admin che è meglio monitorare")
MONITOR     = LogElement("Monitor",    "Messaggi di vario genere che servono a monitorare la situazione")
AUTORELOAD  = LogElement("Autoreload", "Messaggi relativi al ricaricamento automatico di dati, moduli e pagine web")


# Indica che queste tipologie di log non sono visualizzate nella lista
# cliccabile nella pagina apposita degli amministratori
ALWAYS.is_checkable = False


# Impostazione delle trust di log differenti dalle normali TRUST.MASTER
# Da ricordare che la trust dei log viene confrontata con la trust degli
# account e non con quella dei player
BACKUP.trust     = TRUST.BUILDER
SAVE.trust       = TRUST.BUILDER
SHUTDOWN.trust   = TRUST.BUILDER
FREAD.trust      = TRUST.BUILDER
FWRITE.trust     = TRUST.BUILDER
RESET.trust      = TRUST.BUILDER
GAMESCRIPT.trust = TRUST.BUILDER


INPUT.show_on_mud   = False
INPUT.write_on_file = True

CHECK_RESET.write_on_file = False

RESET.show_on_mud   = False
RESET.write_on_file = False
RESET.print_on_console = False
RESET.show_last_function = False

REPOP.show_on_mud   = False
REPOP.write_on_file = False
REPOP.print_on_console = False
REPOP.show_last_function = False

GAMESCRIPT.show_on_mud   = False
GAMESCRIPT.write_on_file = False
GAMESCRIPT.print_on_console = False
GAMESCRIPT.show_last_function = False

HTTP.write_on_file = False

PLANT.write_on_file = False

BOOTING.show_last_function  = False
SHUTDOWN.show_last_function = False
BACKUP.show_last_function   = False
SAVE.show_last_function     = False
INPUT.show_last_function    = False


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
