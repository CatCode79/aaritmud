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
MESSAGES["death_position_entity"]          = "Ora come ora puoi solo [brown]assaggiare[close] l'odore del tuo [red]sangue[close]!"
MESSAGES["death_position_entity"]          = "no_send"

MESSAGES["sleep_position_entity"]          = "Ora come ora puoi solo [brown]assaggiare cibarie nei tuoi [cyan]sogni[close]."
MESSAGES["sleep_position_others"]          = "$n nel sonno fa più volte schioccare piano la $tongue contro il palato."

MESSAGES["not_has_sense_entity"]           = "Non riesci a sentire il [brown]sapore[close] di [darkgray]nulla[close]!"
MESSAGES["not_has_sense_others"]           = ""

MESSAGES["no_argument_entity"]             = "Fai come per [brown]gustare[close] qualcosa."
MESSAGES["no_argument_others"]             = "$n fa come per [brown]gustare[close] qualcosa."

MESSAGES["no_found_entity"]                = "Non riesci ad [brown]assaggiare[close] nessun [white]%s[close] qui."
MESSAGES["no_found_others"]                = "$n cerca di [brown]assaggiare[close] qualcosa senza riuscirvi."

MESSAGES["no_found_extra_entity"]          = "Non riesci a [brown]assaggiare[close] nessun [white]%s[close] di $N."
MESSAGES["no_found_extra_others"]          = "$n sembra voler [brown]assaggiare[close] qualcosa di $N ma senza riuscirvi."
MESSAGES["no_found_extra_target"]          = "$n sembra voler [brown]assaggiarti[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt"]      = "[brown]Assaggi[close] %s di $N ma non senti nulla di speciale."
MESSAGES["no_found_extra_entity_auto"]     = "Non riesci a [brown]assaggiarti[close] nessun [white]%s[close]."
MESSAGES["no_found_extra_others_auto"]     = "$n sembra volersi [brown]assaggiare[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt_auto"] = "Ti [brown]assaggi[close] %s ma non senti nulla di speciale."

MESSAGES["no_found_descr_entity"]          = "[brown]Assaggi[close] $N ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others"]          = "$n [brown]assaggia[close] $N."
MESSAGES["no_found_descr_target"]          = "$n ti [brown]assaggia[close]."
MESSAGES["no_found_descr_entity_auto"]     = "Ti [brown]assaggi[close] ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others_auto"]     = "$n si [brown]assaggia[close]."

MESSAGES["direction_entity"]               = "Non riesci a [brown]gustare[close] nulla %s."  # da direzione
MESSAGES["direction_others"]               = "$n [brown]gusta[close] l'aria %s"  # verso direzione
MESSAGES["direction_wall_others"]          = "$n [brown]gusta[close] il muro %s"  # verso direzione
MESSAGES["direction_exit_others"]          = "$n [brown]gusta[close] l'uscita %s"  # verso direzione
MESSAGES["direction_target_others"]        = "$n [brown]gusta[close] $N %s"  # verso direzione


# Di seguito i messaggi che hanno solo others perchè TO.ENTITY verrà
# riempita con una descrizione sensoriale

MESSAGES["room_descr_others"]        = "$n cerca di [brown]gustare[close] l'ambiente attorno a sé."

MESSAGES["room_extra_others"]        = "$n cerca di [brown]gustare[close] %s."

MESSAGES["entity_descr_others"]      = "$n [brown]assaggia[close] $N."
MESSAGES["entity_descr_target"]      = "$n ti [brown]assaggia[close]."
MESSAGES["entity_descr_auto"]        = "$n si [brown]assaggia[close]."

MESSAGES["entity_extra_others"]      = "$n [brown]assaggia[close] %s di $N."
MESSAGES["entity_extra_target"]      = "$n ti [brown]assaggia[close] %s."
MESSAGES["entity_extra_auto"]        = "$n si [brown]assaggia[close] %s."

MESSAGES["entity_equip_others"]      = "$n [brown]assaggia[close] $a di $N."
MESSAGES["entity_equip_target"]      = "$n ti [brown]assaggia[close] $a."
MESSAGES["entity_equip_auto"]        = "[brown]Assaggi[close] $a di $N ma senza sentire nulla di speciale."
MESSAGES["entity_equip_self"]        = "$n si [brown]assaggia[close] $a."


#= FUNZIONI ====================================================================

def command_taste(entity, argument="", behavioured=False):
    """
    Comando che serve a sentire il gusto di un'entità e quello relativo alla
    stanza.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return five_senses_handler(entity, argument, behavioured, "taste", "tasted", "taste", "has_taste_sense", MESSAGES)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "taste\n"
    syntax += "taste <qualcuno o qualcosa>\n"
    syntax += "taste <in una direzione>\n"
    syntax += "taste <un particolare> <di qualcuno>\n"
    syntax += "taste <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
