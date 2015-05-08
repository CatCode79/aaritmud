# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Bruco che mangia la polverina del cadavere decomposto delle Krisantha
# primo scalino della quest


#= TO DO LIST ==================================================================

# tutto


#= IMPORT ======================================================================

from src.defer import defer
from src.log   import log

from src.commands.command_eat   import command_eat
from src.commands.command_emote import command_emote


#= COSTANTI ====================================================================

PROTO_DUST_CODE         = "cimitero_item_polvere-chrysantha"
PROTO_CATERPILLAR2_CODE = "mh?"
PROTO_CRISALIDE_CODE    = "mh? 2.0"


#= CODICE ======================================================================

def on_reset(caterpillar):
    look_for_dust(caterpillar)
#- Fine Funzione -


def on_booting(caterpillar):
    look_for_dust(caterpillar)
#- Fine Funzione -


def look_for_dust(caterpillar):
    for polverina in caterpillar.location.iter_contains():
        if polverina.prototype.code == PROTO_DUST_CODE:
            command_emote(caterpillar, "Si dirige verso %s." % en.get_name(looker=caterpillar))
            polverina.split_entity(1)
            break
    else:
        return

   # Prima di mangiare viene trasformato in un altro bruco in modo che
   # non venga killato dallo script delle farfalle oppure che non si
   # trasformi in una crisalide canonica
   location = caterpillar.location
   caterpillar.extract(1)
   caterpillar2 = Mob(PROTO_CATERPILLAR2_CODE)
   caterpillar2.inject(location)

   # Ora il bruco mangia la polverina, dopo che l'ha mangiata facciamo
   # passare un po di tempo e gli facciamo cambiare colore
   command_eat(caterpillar2, polverina.get_numbered_keyword(looker=caterpillar2))
   defer(10, change_color, caterpillar2)
#- Fine Funzione -


def change_color(caterpillar2):
   # C'è da verificare che abbia mangiato davvero la polvere giusta
   # ora diviene crisalide
   # GATTO: ma se c'è il check PROTO_DUST_CODE precedente a questa chiamata
   # ha per forza mangiato la polverina giusta, o ci sono più tipi di polverina?
   location = caterpillar2.location
   caterpillar2.extract(1)
   crisalide_crisanta = Item(PROTO_CRISALIDE_CODE)
   crisalide_crisanta.inject(location)
#- Fine Funzione -


def before_giving(player, item, caterpillar, direction, behavioured):
    if not player.IS_PLAYER:
        command_emote(caterpillar, "non pare intenzionato ad accettare nulla.")
        return True
#- Fine Funzione -
