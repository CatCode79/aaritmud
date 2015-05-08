# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Il cerchio di funghi ad ogni get produce un fungo su base random
# la maggior parte delle volte non dà neppure la soddisfazione e
# non succede nulla


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO
from src.item     import Item
from src.log      import log

from src.commands.command_get import command_get


#= FUNZIONI ====================================================================

def before_try_to_get(entity, target, location, behavioured):

    funghi_db = {1: "villaggio-zingaro_item_fungo-01",
                 2: "villaggio-zingaro_item_fungo-02",
                 3: "villaggio-zingaro_item_fungo-03"}

    num_rand = random.randint(1, 100)
    if num_rand < 14: 
        fungo_label = funghi_db[3]
    elif num_rand < 32:
        fungo_label = funghi_db[2]
    elif num_rand < 49:
        fungo_label = funghi_db[1]
    # in tutti gli altri casi esce dallo script con il return True
    # che esce dal flusso del get senza raccattare nulla
    else :
        entity.act("Fai come per afferrarne uno ma questo ti sguscia tra le mani e si ritrae sotto terra.", TO.ENTITY, target)    
        entity.act("$n fa come per afferrare un fungo ma questo $gli sguscia tra le mani e si ritrae sotto terra.", TO.OTHERS, target)    
        return True

    fungo = Item(fungo_label)
    fungo.inject(location)

    entity.act("Allunghi la $hand verso $N per raccoglierne uno.", TO.ENTITY, target)
    entity.act("$n allunga una $hand verso $N per raccoglierne uno.", TO.OTHERS, target)
    entity.act("Ti senti un po' deprezzat$O ogni volta $n ti indaga!", TO.TARGET, target)

    numbered_keyword = fungo.get_numbered_keyword(looker=entity)
    execution_result = command_get(entity, numbered_keyword)

    # Il peso del cerchio viene diminuito man mano che se ne preleva 
    # prima di farlo verifica che sia uscita una keyword quando ne
    # resta troppo poco viene eliminato
    if execution_result:
        if target.weight < fungo.weight:
           target.act("Ed ora non ne trovi neanche uno, o così sembra.", TO.ENTITY, target)
           target.act("Ed ora non ne è rimasto neanche uno, o così sembra.", TO.OTHERS, target)
           target.extract(1)
        else:
           target.weight = target.weight - fungo.weight

    return execution_result
#- Fine Funzione
