# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# bruco che mangia la polverina del cadavere decomposto delle Krisantha
# primo scalino della quest


#= TO DO LIST ==================================================================

# tutto


#= IMPORT ======================================================================

from src.defer import defer
from src.enums import TO
from src.log   import log
from src.mob   import Mob

# Forse non serve, basta solo simularlo
from src.commands.command_eat import command_eat
from src.commands.command_say import command_say


#= COSTANTI ====================================================================

PROTO_CATERPILLAR_CODE = "cimitero_mob_bruco-saturnia-quest"


#= CODE ====================================================================

def on_reset(dust):
    if not dust:
        log.bug("dust non è un parametro valido: %r" % dust)
        return

    look_for_caterpillar(dust)
#- Fine Funzione -


def on_booting(dust):
    if not dust:
        log.bug("dust non è un parametro valido: %r" % dust)
        return

    look_for_caterpillar(dust)
#- Fine Funzione -


def look_for_caterpillar(dust, show_act=True):
    if not dust:
        log.bug("dust non è un parametro valido: %r" % dust)
        return

    caterpillar = dust.find_entity("bruco", dust.location, ["mobs"])
    if not caterpillar:
        if show_act:
            dust.act("My name is $n: niente bruchi" % dust, TO.OTHERS)
            dust.act("My name is $n: niente bruchi" % dust, TO.ENTITY)

        defer(60, look_for_caterpillar, dust)
        return

    if show_act:
        dust.act("My name is $n, ho visto un bruco: %r" % caterpillar, TO.OTHERS)
        dust.act("My name is $n, ho visto un bruco: %r" % caterpillar, TO.ENTITY)
        command_say(caterpillar, "sa la vist cus'è?")

    #defer(60, look_for_caterpillar, dust)
    # il bruco potrebbe essere soggetto a script che lo potrebbero mutare senza
    # avvisaglie quindi tolgo di mezzo il bruco per sostituirlo con un altro
    # che so non essere afflitto da script
    location = caterpillar.location
    caterpillar.extract(1)
    new_caterpillar = Mob(PROTO_CATERPILLAR_CODE)
    new_caterpillar.inject(location)
    new_caterpillar.act("$n cambia aspetto in modo repentino.", TO.OTHERS)

    dust_eating(dust, new_caterpillar)
    # Ora resta solo da far mangiare la polvere che è bene rimuovere e
    # rimpiazzare con con qualcosaltro
#- Fine Funzione -


def dust_eating(dust, caterpillar):
    if not dust:
        log.bug("dust non è un parametro valido: %r" % dust)
        return

    if not caterpillar:
        log.bug("caterpillar non è un parametro valido: %r" % caterpillar)
        return

    if dust.location != caterpillar.location:
       caterpillar.act("$n vaga disorientato alla ricerca diqualcosa", TO.OTHERS)
       defer(60, dust_eating, dust, caterpillar)
       return

    #command_eat(caterpillar, dust)
    caterpillar.act("$n viene avvolto dalla polvere bianca.", TO.OTHERS)
    dust.extract(1)
#- Fine Funzione -
