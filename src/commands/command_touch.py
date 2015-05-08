# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.config import config
from src.enums  import TO
from src.log    import log

if config.reload_commands:
    reload(__import__("src.commands.__senses__", globals(), locals(), [""]))
from src.commands.__senses__ import five_senses_handler


#= COSTANTI ====================================================================

MESSAGES = {}

# La posizione mortale non ha altri messaggi di act
MESSAGES["death_position_entity"]           = "Ora come ora puoi solo [lightwood]toccare[close] il feretro che ti sta porgendo la [darkgray]morte[close]!"
MESSAGES["death_position_entity"]           = "no_send"

MESSAGES["sleep_position_entity"]           = "Ora come ora puoi solo [lightwood]toccare[close] oggetti nei tuoi [cyan]sogni[close]."
MESSAGES["sleep_position_others"]           = "$n comincia a muovere le $hands attorno a sé mentre dorme."

MESSAGES["not_has_sense_entity"]            = "Non ti è possibile fare uso del tuo [lightwood]tatto[close]."
MESSAGES["not_has_sense_others"]            = ""

MESSAGES["no_argument_entity"]              = "Fai gesto come per [lightwood]toccare[close] qualcosa."
MESSAGES["no_argument_others"]              = "$n fa gesto come per [lightwood]toccare[close] qualcosa."

MESSAGES["no_found_entity"]                 = "Non riesci a [lightwood]toccare[close] nessun [white]%s[close] qui."
MESSAGES["no_found_others"]                 = "$n cerca di [lightwood]toccare[close] qualcosa senza riuscirvi."

MESSAGES["no_found_extra_entity"]           = "Non riesci a [lightwood]toccare[close] nessun [white]%s[close] di $N."
MESSAGES["no_found_extra_others"]           = "$n sembra voler [lightwood]toccare[close] qualcosa di $N ma senza riuscirvi."
MESSAGES["no_found_extra_target"]           = "$n sembra voler [lightwood]toccarti[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt"]       = "[lightwood]Tocchi[close] %s di $N ma non senti nulla di speciale."
MESSAGES["no_found_extra_entity_auto"]      = "Non riesci a [lightwood]toccarti[close] nessun [white]%s[close]."
MESSAGES["no_found_extra_others_auto"]      = "$n sembra volersi [lightwood]toccare[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt_auto"]  = "Ti [lightwood]tocchi[close] %s ma non senti nulla di speciale."

MESSAGES["no_found_descr_entity"]           = "[lightwood]Tocch[close]i $N ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others"]           = "$n [lightwood]tocca[close] $N."
MESSAGES["no_found_descr_target"]           = "$n ti [lightwood]tocca[close]."
MESSAGES["no_found_descr_entity_auto"]      = "Ti [lightwood]tocchi[close] ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others_auto"]      = "$n si [lightwood]tocca[close]."

MESSAGES["direction_entity"]                = "Non riesci a percepire nulla al [lightwood]tocco[close] %s."  # da direzione
MESSAGES["direction_others"]                = "$n gesticola come per [lightwood]toccare[close] %s"  # verso direzione
MESSAGES["direction_wall_others"]           = "$n [lightwood]tocca[close] il muro %s"  # verso direzione
MESSAGES["direction_exit_others"]           = "$n [lightwood]tocca[close] l'uscita %s"  # verso direzione
MESSAGES["direction_target_others"]         = "$n [lightwood]tocca[close] $N %s"  # verso direzione


# Di seguito i messaggi che hanno solo others perchè TO.ENTITY verrà
# riempita con una descrizione sensoriale

MESSAGES["room_descr_others"]        = "$n cerca di [lightwood]toccare[close] l'ambiente circostante."

MESSAGES["room_extra_others"]        = "$n cerca di [lightwood]toccare[close] %s."

MESSAGES["entity_descr_others"]      = "$n [lightwood]tocca[close] $N."
MESSAGES["entity_descr_target"]      = "$n ti [lightwood]tocca[close]."
MESSAGES["entity_descr_auto"]        = "$n si [lightwood]tocca[close]."

MESSAGES["entity_extra_others"]      = "$n [lightwood]tocca[close] %s di $N."
MESSAGES["entity_extra_target"]      = "$n ti [lightwood]tocca[close] %s."
MESSAGES["entity_extra_auto"]        = "$n si [lightwood]tocca[close] %s."

MESSAGES["entity_equip_others"]      = "$n [lightwood]tocca[close] $a di $N."
MESSAGES["entity_equip_target"]      = "$n ti [lightwood]tocca[close] $a."
MESSAGES["entity_equip_auto"]        = "[lightwood]Tocchi[close] $a di $N ma senza sentire nulla di speciale."
MESSAGES["entity_equip_self"]        = "$n si [lightwood]tocca[close] $a."


#= FUNZIONI ====================================================================

def command_touch(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return five_senses_handler(entity, argument, behavioured, "touch", "touched", "touch", "has_touch_sense", MESSAGES)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "touch\n"
    syntax += "touch <qualcuno o qualcosa>\n"
    syntax += "touch <in una direzione>\n"
    syntax += "touch <un particolare> <di qualcuno>\n"
    syntax += "touch <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
