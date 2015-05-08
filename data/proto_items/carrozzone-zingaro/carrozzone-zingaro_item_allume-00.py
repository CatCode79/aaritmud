# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# il consueto script di generazione oggetti quando si raccoglie l'entità


#= IMPORT ======================================================================

import random

from src.enums     import TO
from src.interpret import send_input
from src.item      import Item

from src.commands.command_get import command_get


#= FUNZIONI =====================================================================

def before_try_to_get(entity, target, location, behavioured):
    # Crea e inserisce il pezzetto di polverina nella locazione da cui prenderlo
    pezzetto = Item("carrozzone-zingaro_item_allume-pezzi-01")
    pezzetto.inject(location)

    entity.act("Rovesci parte del contenuto di $N sulla $hand2.", TO.ENTITY, target)
    entity.act("$n rovescia parte del contenuto di $N sulla sua $hand2.", TO.OTHERS, target)
    entity.act("Ti senti un po' deprezzata ogni volta che $n ti indaga!", TO.TARGET, target)

    # Bisogna utilizzare la get_keywords_attr perché non si sa se entity in quel
    # momento stia guardando la short diurna, notturna o il nome
    first_keyword = pezzetto.get_numbered_keyword(looker=entity)
    if location.IS_ROOM:
        argument = first_keyword
    else:
        argument = "%s %s " % (first_keyword, location.get_numbered_keyword(looker=entity))
    execution_result = command_get(entity, argument)

    # Questo è meglio farlo solo se il get è andato a buon fine, cioè quando
    # execution_result ha valore di verità positiva
    if execution_result:
        # faccio fluttuare il valore di peso del pezzo di allume di +o- 10
        pezzetto.weight = pezzetto.weight + random.randint(-10, 10)
        if target.weight < pezzetto.weight:
            target.act("È stato estratto da te l'ultimo pezzo.", TO.ENTITY)
            target.act("Una volta c'era $n ma ora è vuot$o.", TO.OTHERS)
            target.extract(1)
        else:
            target.weight = target.weight - pezzetto.weight

    return execution_result
#- Fine Funzione
