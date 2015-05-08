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
MESSAGES["death_position_entity"]          = "Ora come ora puoi solo sentire l'[blueviolet]odore[close] del tuo [red]sangue[close]!"
MESSAGES["death_position_entity"]          = "no_send"

MESSAGES["sleep_position_entity"]          = "Ora come ora puoi solo utilizzare il tuo [blueviolet]olfatto[close] nei tuoi [cyan]sogni[close]."
MESSAGES["sleep_position_others"]          = "$n si mette ad [blueviolet]annusare[close] nel sonno."

MESSAGES["not_has_sense_entity"]           = "Non riesci ad [blueviolet]annusare[close] [darkgray]nulla[close]!"
MESSAGES["not_has_sense_others"]           = "no_send"

MESSAGES["no_argument_entity"]             = "Fai come per [blueviolet]annusare[close] qualcosa."
MESSAGES["no_argument_others"]             = "$n fa come per [blueviolet]annusare[close] qualcosa."

MESSAGES["no_found_entity"]                = "Non riesci ad [blueviolet]annusare[close] nessun [white]%s[close] qui."
MESSAGES["no_found_others"]                = "$n cerca di [blueviolet]annusare[close] qualcosa senza riuscirvi."

MESSAGES["no_found_extra_entity"]          = "Non riesci ad [blueviolet]annusare[close] nessun [white]%s[close] di $N."
MESSAGES["no_found_extra_others"]          = "$n sembra voler [blueviolet]annusare[close] qualcosa di $N ma senza riuscirvi."
MESSAGES["no_found_extra_target"]          = "$n sembra voler [blueviolet]annusarti[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt"]      = "[blueviolet]Annusi[close] %s di $N ma non senti nulla di speciale."
MESSAGES["no_found_extra_entity_auto"]     = "Non riesci ad [blueviolet]annusarti[close] nessun [white]%s[close]."
MESSAGES["no_found_extra_others_auto"]     = "$n sembra volersi [blueviolet]annusare[close] qualcosa ma senza riuscirvi."
MESSAGES["no_found_extra_entity_alt_auto"] = "Ti [blueviolet]annusi[close] %s ma non senti nulla di speciale."

MESSAGES["no_found_descr_entity"]          = "[blueviolet]Annusi[close] $N ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others"]          = "$n [blueviolet]annusa[close] $N."
MESSAGES["no_found_descr_target"]          = "$n ti [blueviolet]annusa[close]."
MESSAGES["no_found_descr_entity_auto"]     = "Ti [blueviolet]annusi[close] ma non percepisci nulla di speciale."
MESSAGES["no_found_descr_others_auto"]     = "$n si [blueviolet]annusa[close]."

MESSAGES["direction_entity"]               = "Non percepisci nessun [blueviolet]odore[close] %s."  # da direzione
MESSAGES["direction_others"]               = "$n [blueviolet]annusa[close] l'aria %s"  # verso direzione
MESSAGES["direction_wall_others"]          = "$n [blueviolet]annusa[close] il muro %s"  # verso direzione
MESSAGES["direction_exit_others"]          = "$n [blueviolet]annusa[close] l'uscita %s"  # verso direzione
MESSAGES["direction_target_others"]        = "$n [blueviolet]annusa[close] $N %s"  # verso direzione


# Di seguito i messaggi che hanno solo others perchè TO.ENTITY verrà
# riempita con una descrizione sensoriale

MESSAGES["room_descr_others"]        = "$n [blueviolet]odora[close] l'ambiente."

MESSAGES["room_extra_others"]        = "$n [blueviolet]odora[close] %s."

MESSAGES["entity_descr_others"]      = "$n [blueviolet]annusa[close] $N."
MESSAGES["entity_descr_target"]      = "$n ti [blueviolet]annusa[close]."
MESSAGES["entity_descr_auto"]        = "$n si [blueviolet]annusa[close]."

MESSAGES["entity_extra_others"]      = "$n [blueviolet]annusa %s di $N."
MESSAGES["entity_extra_target"]      = "$n ti [blueviolet]annusa[close] %s."
MESSAGES["entity_extra_auto"]        = "$n si [blueviolet]annusa[close] %s."

MESSAGES["entity_equip_others"]      = "$n [blueviolet]annusa[close] $a di $N."
MESSAGES["entity_equip_target"]      = "$n ti [blueviolet]annusa[close] $a."
MESSAGES["entity_equip_auto"]        = "[blueviolet]Annusi[close] $a di $N ma senza sentire nulla di speciale."
MESSAGES["entity_equip_self"]        = "$n si [blueviolet]annusa[close] $a."


#= FUNZIONI ====================================================================

def command_smell(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return five_senses_handler(entity, argument, behavioured, "smell", "smelled", "smell", "has_smell_sense", MESSAGES)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "smell\n"
    syntax += "smell <qualcuno o qualcosa>\n"
    syntax += "smell <in una direzione>\n"
    syntax += "smell <un particolare> <di qualcuno>\n"
    syntax += "smell <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
