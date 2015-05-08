# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# - Il medaglione contiene un unguento
# - Raccogliendo l'unguento questo si "indossa sulle mani"
# - Se la mani sono occupate (una solo o entrambe) non si raccatta
# - L'ungunto è anche una KEY per aprire la porta spinosa poco più avanti
# - Dopo un po' di tempo l'unguento si asciuga e se ne va
# - Il medaglione contenitore una volta che è stato svuotato si rompe
#   poi sparisce polverizzandosi


#= PROBLEMI ====================================================================

# i messaggi non si vedono se l'item medaglione è in inventario (quasi sempre)
# quando rompo il medaglione deve rimanere nella locazione esatta di prima


#= IMPORT ======================================================================

from src.database import database
from src.defer    import defer
from src.enums    import OPTION, PART, TO
from src.log      import log
from src.item     import Item
from src.part     import check_if_part_is_already_weared, get_part_descriptions

from src.entitypes.wear import send_wear_messages


#= FUNZIONI ====================================================================

def before_get(player, unguento, medaglione, behavioured):
    # Pensato per essere usato con item generico
    # va a vedere che le parti dove si attacca indossa siano libere
    for mode in unguento.wear_type.modes:
        for part in mode:
            already_weared_part, already_weared_possession = check_if_part_is_already_weared(player, part)
            if already_weared_part:
                player.act("$N, come dotata di vita propria, ti si avvolge attorno a $a ma poi scivola via.", TO.ENTITY, unguento, already_weared_possession)
                player.act("$n cerca di prendere qualcosa che però scivola via.", TO.OTHERS)
                return True


def after_get(player, unguento, medaglione, behavioured):
    for mode in unguento.wear_type.modes:
        for part in mode:
            unguento.wear_mode += part
            part_descriptions = get_part_descriptions(mode, "wear")
        send_wear_messages(player, unguento, "Indossi", "indossa", part_descriptions)
        break
    defer(3600, unguento_cleaning, unguento, player)

    if medaglione.IS_ITEM:
        print medaglione.code
        defer(120, medaglione_corruption, medaglione, player)
        return False


def medaglione_corruption(medaglione, player):
    # Normale perché la funzione è deferrata
    if not medaglione or not player:
        return

    old_medallion = Item("villaggio-zingaro_item_medaglione-rotto")
    old_medallion.inject(medaglione.location)

    medaglione.act("$n si consuma lentamente...", TO.ENTITY, send_to_location=player.location)
    medaglione.act("$n si consuma lentamente...", TO.OTHERS, send_to_location=player.location)
    medaglione.extract(1)

    defer(120, medaglione_remove, old_medallion, player)
    return False


def medaglione_remove(medaglione, player):
    # Normale perché la funzione è deferrata
    if not medaglione or not player:
        return

    medaglione.act("$n si disfa e diviene polvere.", TO.ENTITY, send_to_location=player.location)
    medaglione.act("$n si disfa e diviene polvere.", TO.OTHERS, send_to_location=player.location)
    medaglione.extract(1)
    return False


def unguento_cleaning(unguento, player):
    # Normale perché la funzione è deferrata
    if not unguento or not player:
        return

    if player:
        player.act("$N si è asciugat$O e le sue $hands non sono più unte.", TO.OTHERS, unguento)
        player.act("$N si è asciugat$O e le tue $hands non sono più unte.", TO.ENTITY, unguento)
    unguento.extract(1)
    return False
