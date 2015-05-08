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

MESSAGES["death_position_entity"]          = "Ora come ora non hai bisogno del tuo [darkturquoise]sesto senso[close] per capire che sei ad un passo dalla [darkgray]morte[close]!"
MESSAGES["death_position_entity"]          = "no_send"

MESSAGES["sleep_position_entity"]          = "Ora come ora puoi solo [darkturquoise]intuire[close] cosa significhino i tuoi [cyan]sogni[close]."
MESSAGES["sleep_position_others"]          = "no_send"

MESSAGES["not_has_sense_entity"]           = "Non ti è possibile fare uso del tuo [darkturquoise]sesto senso[close]."
MESSAGES["not_has_sense_others"]           = "no_send"

MESSAGES["no_argument_entity"]             = "Ti gratti la fronte cercando di [darkturquoise]capire[close]..."
MESSAGES["no_argument_others"]             = "$n si gratta la fronte come se stesse [darkturquoise]pensando[close]..."

MESSAGES["no_found_entity"]                = "Non riesci ad [darkturquoise]intuire[close] nessun [white]%s[close] qui."
MESSAGES["no_found_others"]                = "no_send"

MESSAGES["no_found_extra_entity"]          = "Non riesci ad [darkturquoise]intuire[close] nessun [white]%s[close] di $N."
MESSAGES["no_found_extra_others"]          = "no_send"
MESSAGES["no_found_extra_target"]          = "no_send"
MESSAGES["no_found_extra_entity_alt"]      = "Non riesci ad [darkturquoise]intuirvi[close] nulla di speciale in %s di $N."  # (GR) provare a vedere in futuro se sia possibile aggiungervi l'argoment con le funzioni grammaticali
MESSAGES["no_found_extra_entity_auto"]     = "Non riesci ad [darkturquoise]intuire[close] nessun [white]%s[close]."
MESSAGES["no_found_extra_others_auto"]     = "no_send"
MESSAGES["no_found_extra_entity_alt_auto"] = "Non riesci ad [darkturquoise]intuire[close] nulla di speciale in %s."  # (GR) provare a vedere in futuro se sia possibile aggiungervi l'argoment con le funzioni grammaticali

MESSAGES["no_found_descr_entity"]          = "Non riesci ad [darkturquoise]intuire[close] nulla di speciale di $N."
MESSAGES["no_found_descr_others"]          = "no_send"
MESSAGES["no_found_descr_target"]          = "no_send"
MESSAGES["no_found_descr_entity_auto"]     = "Non riesci ad [darkturquoise]intuire[close] a nulla di speciale riguardo a te stesso."
MESSAGES["no_found_descr_others_auto"]     = "no_send"

MESSAGES["direction_entity"]               = "Non riesci ad [darkturquoise]intuire[close] nulla concentrandoti %s."  # da direzione
MESSAGES["direction_others"]               = "no_send"
MESSAGES["direction_wall_others"]          = "no_send"
MESSAGES["direction_exit_others"]          = "no_send"
MESSAGES["direction_target_others"]        = "no_send"


# Di seguito i messaggi che hanno solo others perchè TO.ENTITY verrà
# riempita con una descrizione sensoriale

MESSAGES["room_descr_others"]        = "no_send"

MESSAGES["room_extra_others"]        = "no_send"

MESSAGES["entity_descr_others"]      = "no_send"
MESSAGES["entity_descr_target"]      = "no_send"
MESSAGES["entity_descr_auto"]        = "no_send"

MESSAGES["entity_extra_others"]      = "no_send"
MESSAGES["entity_extra_target"]      = "no_send"
MESSAGES["entity_extra_auto"]        = "no_send"

MESSAGES["entity_equip_others"]      = "no_send"
MESSAGES["entity_equip_target"]      = "no_send"
MESSAGES["entity_equip_auto"]        = "[darkturquoise]Intuisci[close] $a di $N ma senza percepire nulla di speciale."
MESSAGES["entity_equip_self"]        = "no_send"


#= FUNZIONI ====================================================================

# (TD) provare a fare la
# get_extra_descr(descriptive, argument, exact, type)
def command_intuition(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    return five_senses_handler(entity, argument, behavioured, "intuition", "intuited", "sixth", "has_sixth_sense", MESSAGES)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "intuition\n"
    syntax += "intuition <qualcuno o qualcosa>\n"
    syntax += "intuition <in una direzione>\n"
    syntax += "intuition <un particolare> <di qualcuno>\n"
    syntax += "intuition <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
