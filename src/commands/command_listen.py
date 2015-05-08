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
MESSAGES["death_position_entity"]          = "Ora come ora puoi solo [thistle]ascoltare[close] le [bluesteel]campane[close]!"
MESSAGES["death_position_entity"]          = "no_send"

MESSAGES["sleep_position_entity"]          = "Ora come ora puoi solo [thistle]ascoltare[close] i tuoi [cyan]sogni[close]."
MESSAGES["sleep_position_others"]          = "$n si agita nel sonno come se fosse disturbato da dei rumori."

MESSAGES["not_has_sense_entity"]           = "Non riesci ad [thistle]ascoltare[close] [darkgray]nulla[close]!"
MESSAGES["not_has_sense_others"]           = "$n si comporta come se non riesca ad udire nulla."

MESSAGES["no_argument_entity"]             = "Fai come per [thistle]ascoltare[close] qualcosa."
MESSAGES["no_argument_others"]             = "$n fa come per [thistle]ascoltare[close] qualcosa."

MESSAGES["no_found_entity"]                = "Non riesci ad [thistle]ascoltare[close] nessun [white]%s[close] qui."
MESSAGES["no_found_others"]                = "$n cerca di [thistle]ascoltare[close] qualcosa senza riuscirvi."

# (TD) nella no_found_extra_entity_alt dovrei, prima del %s, fare una ricerca dell'articolo grammaticalmente corretto
MESSAGES["no_found_extra_entity"]          = "Non riesci ad [thistle]ascoltare[close] nessun [white]%s[close] di $N."
MESSAGES["no_found_extra_others"]          = "$n sembra voler [thistle]ascoltare[close] qualcosa di $N ma senza riuscirvi."
MESSAGES["no_found_extra_target"]          = "$n sembra voler [thistle]ascoltarti[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt"]      = "[thistle]Ascolti[close] %s di $N ma non senti nulla di speciale."
MESSAGES["no_found_extra_entity_auto"]     = "Non riesci ad [thistle]ascoltarti[close] nessun [white]%s[close]."
MESSAGES["no_found_extra_others_auto"]     = "$n sembra volersi [thistle]ascoltare[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt_auto"] = "Ti [thistle]ascolti[close] %s ma non senti nulla di speciale."

MESSAGES["no_found_descr_entity"]          = "[thistle]Ascolti[close] $N ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others"]          = "$n [thistle]ascolta[close] di $N."
MESSAGES["no_found_descr_target"]          = "$n ti [thistle]ascolta[close]."
MESSAGES["no_found_descr_entity_auto"]     = "Ti [thistle]ascolti[close] ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others_auto"]     = "$n si [thistle]ascolta[close]."

MESSAGES["direction_entity"]               = "Non proviene nessun rumore %s."  # da direzione
MESSAGES["direction_others"]               = "$n tende l'orecchia %s"  # verso direzione
MESSAGES["direction_wall_others"]          = "$n tende l'orecchia al muro %s"  # verso direzione
MESSAGES["direction_exit_others"]          = "$n tende l'orecchia all'uscita %s"  # verso direzione
MESSAGES["direction_target_others"]        = "$n tende l'orecchia a $N %s"  # verso direzione


# Di seguito i messaggi che hanno solo others perchè TO.ENTITY verrà
# riempita con una descrizione sensoriale

MESSAGES["room_descr_others"]        = "$n [thistle]ascolta[close] i rumori attorno a sé."

MESSAGES["room_extra_others"]        = "$n[thistle] ascolta[close] i rumori di %s."

MESSAGES["entity_descr_others"]      = "$n [thistle]ascolta[close] $N."
MESSAGES["entity_descr_target"]      = "$n ti [thistle]ascolta[close]."
MESSAGES["entity_descr_auto"]        = "$n si [thistle]ascolta[close]."

MESSAGES["entity_extra_others"]      = "$n [thistle]ascolta[close] %s di $N."
MESSAGES["entity_extra_target"]      = "$n ti [thistle]ascolta[close] %s."
MESSAGES["entity_extra_auto"]        = "$n si [thistle]ascolta[close] %s."

MESSAGES["entity_equip_others"]      = "$n [thistle]ascolta[close] $a di $N."
MESSAGES["entity_equip_target"]      = "$n ti [thistle]ascolta[close] $a."
MESSAGES["entity_equip_auto"]        = "[thistle]Ascolti[close] $a di $N ma senza sentire nulla di speciale."
MESSAGES["entity_equip_self"]        = "$n si [thistle]ascolta[close] $a."


#= FUNZIONI ====================================================================

def command_listen(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return five_senses_handler(entity, argument, behavioured, "listen", "listened", "hearing", "has_hearing_sense", MESSAGES)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "listen\n"
    syntax += "listen <qualcuno o qualcosa>\n"
    syntax += "listen <in una direzione>\n"
    syntax += "listen <un particolare> <di qualcuno>\n"
    syntax += "listen <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
