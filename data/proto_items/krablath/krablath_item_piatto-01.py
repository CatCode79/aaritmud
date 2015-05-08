# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# Il consueto script di generazione oggetti quando si getta l'entità
# il get sui panzerotti-frutta produce entità panzerottinabili e non
# l'oggetto panzerotti frutta diminuisce di peso man mano che se ne preleva


#= IMPORT ======================================================================

import random

from src.database import database
from src.enums    import TO, FLAG
from src.item     import Item
from src.log      import log

from src.commands.command_get import command_get


#= FUNZIONI ====================================================================

def before_try_to_get(entity, target, location, behavioured):
    panzerotti_db = ["krablath_item_food-panzerotto-01",
                     "krablath_item_food-panzerotto-02",
                     "krablath_item_food-panzerotto-03"]

    num_rand = random.randint(1, 100)
    if num_rand < 33:
        panzerotto_code = panzerotti_db[0]
    elif num_rand < 66:
        panzerotto_code = panzerotti_db[1]
    else:
        panzerotto_code = panzerotti_db[2]

    # Alternativamente una soluzione che potrebbe essere considerata più
    # elegante del codice sopra potrebbe essere questa sotto.
    # Non hai la granularità del 100 ma chi se ne fre'.. e poi è più facilmente
    # percepibile anche solo ad occhio quali panzerotti verranno caricati di più
    # e quali meno
    #Se vuoi tenerla deve decommentare anche l'import del random in alto ed
    #eventualmente commentare quello del random.randint
    #panzerotti_db = ["karpuram_item_mirtillo-rosso-01-frutto",
    #                  "karpuram_item_mirtillo-rosso-01-frutto",
    #                  "karpuram_item_leccio-01-ghianda-viva",
    #                  "karpuram_item_leccio-01-ghianda-viva",
    #                  "karpuram_item_leccio-01-ghianda-viva",
    #                  "karpuram_item_leccio-02-ghianda-morta",
    #                  "karpuram_item_mirtillo-nero-01-frutto",
    #                  "karpuram_item_mirtillo-nero-01-frutto",
    #                  "karpuram_item_mirtillo-nero-01-frutto",
    #                  "karpuram_item_mirtillo-rosso-00-frutto-marcio",
    #                  "karpuram_item_mirtillo-rosso-00-frutto-marcio",
    #                  "karpuram_item_mirtillo-rosso-00-frutto-sterile",
    #                  "karpuram_item_mirtillo-rosso-00-frutto-sterile",
    #                  "karpuram_item_farnia-01-ghianda-viva",
    #                  "karpuram_item_farnia-01-ghianda-viva",
    #                  "karpuram_item_farnia-01-ghianda-viva",
    #                  "karpuram_item_farnia-01-ghianda-viva",
    #                  "karpuram_item_farnia-01-ghianda-viva",
    #                  "karpuram_item_farnia-02-ghianda-morta",
    #                  "karpuram_item_farnia-02-ghianda-morta",
    #                  "karpuram_item_farnia-02-ghianda-morta",
    #                  "karpuram_item_farnia-02-ghianda-morta"]
    #panzerotto_code = random.choice(panzerotti_db)

    # Crea e inserisce il panzerotto scelto nella locazione da cui prenderlo poi
    panzerotto_founded = Item(panzerotto_code)
    panzerotto_founded.inject(location)
    if random.randint(0, 1) == 1:
        panzerotto_founded.flags += FLAG.NO_LOOK_LIST

    # Attenzione che il get invierà i propri messaggi oltre a questi qua.
    entity.act("Infili la $hand verso $N.", TO.ENTITY, target)
    entity.act("$n allunga una mano verso $N.", TO.OTHERS, target)
    entity.act("Ti senti un po' deprezzato ogni volta che $n ti indaga!", TO.TARGET, target)

    # Bisogna utilizzare la get_numbered_keyword perché non si sa se entity
    # in quel momento stia guardando la short diurna, notturna o il nome
    numbered_keyword = panzerotto_founded.get_numbered_keyword(looker=entity)
    if location.IS_ROOM:
        argument = numbered_keyword
    else:
        argument = "%s %s " % (numbered_keyword, location.get_numbered_keyword(looker=entity))
    execution_result = command_get(entity, argument)

    # Questo è meglio farlo solo se il get è andato a buon fine, cioè quando
    # execution_result ha valore di verità positiva
    if execution_result:
        if target.weight < panzerotto_founded.weight:
            target.act("Dei $n che c'erano ora non resta nulla.", TO.OTHERS)
            target.act("Non resta più molto di te.", TO.ENTITY)
            target.extract(1)
        else:
            target.weight = target.weight - panzerotto_founded.weight

    return execution_result
#- Fine Funzione
