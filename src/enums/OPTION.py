# -*- coding: utf-8 -*-

"""
Enumerazione delle flag di opzione dell'account.
"""

from src.element import EnumElement, finalize_enumeration


#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#-------------------------------------------------------------------------------

class OptionElement(EnumElement):
    def __init__(self, name, description=""):
        super(OptionElement, self).__init__(name, description)
        self.icon = ""  # Icona rappresentante l'opzione
    #- Fine Inizializzazione -


#-------------------------------------------------------------------------------

NONE         = OptionElement("Nessuna")
NEWBIE       = OptionElement("newbie",          "Se impostato qui e là si verrà guidati con dei messaggi di aiuto")
ITALIAN      = OptionElement("italiano",        "Se impostato preferisci i comandi in italiano a quelli in inglese")
DOUBLE_LANG  = OptionElement("doppia lingua",   "Se impostato cerca il comando inviato sia tra quelli in italiano sia tra quelli in inglese, dando la precedenza alla lingua scelta con l'opzione sopra")
AUTO_GOLD    = OptionElement("auto monete",     "Se impostato le monete vengono raccolte automaticamente dai corpi dei mob uccisi")
AUTO_SPLIT   = OptionElement("auto dividi",     "Se impostato le monete raccolte nelle uccisioni vengono divise equamente col gruppo")
AUTO_LOOT    = OptionElement("auto saccheggia", "Se impostato gli oggetti vengono automaticamente tolti dai corpi dei mob uccisi")
AUTO_OPEN    = OptionElement("auto apri",       "Se impostato, sia le uscite chiuse ma apribili nella direzione in cui stai andando verranno automaticamente aperte, sia i contenitori chiusi ma apribili dai quali si sa già cosa prelevare verranno automaticamente aperti")
AUTO_FLEE    = OptionElement("auto fuggi",      "Se impostato quando sarai in combattimento potrai utilizzare i comandi direzione per tentare di fuggire")
COMET        = OptionElement("comet",           "Se impostato utilizzerete il vecchio metodo di connessione al gioco, più performante ma meno compatibile, disattivate quest'opzione se avete problemi di connessione!")
MAP          = OptionElement("mappa",           "Se impostato visualizzerete, accanto alla descrizione di ogni stanza, una mappa della zona in cui ti trovi")
LESS_COLORS  = OptionElement("meno colori",     "Se impostato vi verrà inviato testo con meno colore")
COMPACT      = OptionElement("compatto",        "Se impostato il teso inviato sarà più compatto evitando di inviare una riga vuota prima del prompt")
COURIER_FONT = OptionElement("courier font",    "Se impostato i caratteri della finestra di gioco del gioco saranno in Courier, solo per gli inguaribili nostalgici. (per rendere effettiva quest'opzione avrai bisogno di ricaricare la pagina di gioco nel qual caso fosse già aperta)")
SOUND        = OptionElement("sound",           "Se impostato potrai sentire il sonoro inviato dal gioco (in alcuni browser bisognerà installare un plugin apposito)")
MUSIC        = OptionElement("musica",          "Se impostato potrai sentire la musica inviata dal gioco (in alcuni browser bisognerà installare un plugin apposito)")
LOOP         = OptionElement("loop",            "Se impostato le sole musiche d'ambiente verranno ripetute in continuazione anziché una volta sola")

NEWBIE.icon       = "options/newbie.png"
ITALIAN.icon      = "options/italian.png"
DOUBLE_LANG.icon  = "options/double_lang.png"
AUTO_GOLD.icon    = "options/auto_gold.png"
AUTO_SPLIT.icon   = "options/auto_split.png"
AUTO_LOOT.icon    = "options/auto_loot.png"
AUTO_OPEN.icon    = "options/auto_open.png"
AUTO_FLEE.icon    = "options/auto_flee.png"
COMET.icon        = "options/comet.png"
MAP.icon          = "options/map.png"
LESS_COLORS.icon  = "options/less_colors.png"
COMPACT.icon      = "options/compact.png"
COURIER_FONT.icon = "options/courier_font.png"
SOUND.icon        = "options/sound.png"
MUSIC.icon        = "options/music.png"
LOOP.icon         = "options/loop.png"


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
