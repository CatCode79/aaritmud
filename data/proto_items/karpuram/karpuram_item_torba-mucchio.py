# -*- coding: utf-8 -*-

#= IDEA INIZIALE =================================================================

# Qui il player arriva e fa un get sull'oggetto manciata di torba.
# e si troverà in mano un pezzo di torba

# on get
# if (peso-max-trasportabile - peso-trasportato) < (peso.po-di terra)
#    act "non puoi trasportare oltre"
#    return
# weight.torba -= 1kg
# if (weight.torba < MIN)
#     remove (torba)
#     load (troppa poca terra)
#     act "hai raccolto quasi tutta la torba che c'era"
# load on inv (po' di terra)
# act "hai un po' di torba in mano"


#= DESCRIZIONE =================================================================

# In pratica cosa succede?
# - Il giocatore cerca di prendere il manciata di torba,
# - viene bloccato nel momento in cui trova la torba eseguendo questo mudscript
# - viene caricato un pezzo di torba
# - al giocatore viene forzato un get sul pezzo di torba
# - se questo get va a buon fine il comando di get precedente viene cancellato


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO
from src.item     import Item
from src.log      import log

from src.commands.command_get import command_get


#= FUNZIONI ====================================================================

def before_try_to_get(entity, target, location, behavioured):
    manciata_torba = Item("karpuram_item_torba-manciata")
    laminetta_oro = Item("karpuram_item_laminetta-oro")

    if random.randint(1, 10) == 1:
        laminetta_oro.inject(location)
        entity.act("Metti la $hand in $N ed un luccicore ti distrae dal tuo proponimento!", TO.ENTITY, target)
        entity.act("tu che sei $N ti senti un po' deprezzato ogni volta $n ti indaga!", TO.TARGET, target)
        entity.act("$n affonda una mano in $N e si ferma sorpres$o.", TO.OTHERS, target)
        execution_result = command_get(entity, laminetta_oro.get_numbered_keyword(looker=entity))
    else:
        manciata_torba.inject(location)
        execution_result = command_get(entity, manciata_torba.get_numbered_keyword(looker=entity))

    # Se execution_result a True significa che è stato raccolta con successo
    # una manciata di torba e quindi ferma l'esecuzione del resto del comando get;
    # altrimenti è False e tornando False viene continuato il get del mucchio
    # di torba, che in futuro fallirà per motivi di peso
    return execution_result
#- Fine Funzione -
