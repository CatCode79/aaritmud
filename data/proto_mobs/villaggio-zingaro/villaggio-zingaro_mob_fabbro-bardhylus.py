# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.color import color_first_upper
from src.enums import TO

from src.commands.command_say import command_say


#= FUNZIONI ====================================================================

def before_giving(player, arma, fabbro, direction, behavioured):
    # Solo per i giocatori
    if not player.IS_PLAYER:
        player.act("$N non accetta che tu gli dia alcunché.", TO.ENTITY, fabbro)
        player.act("$n cerca inutilmente di dare qualcosa a $n.", TO.OTHERS, fabbro)
        player.act("$n cerca di darti robaccia ma tu non accetti.", TO.TARGET, fabbro)
        return True

    arma_name = arma.get_name(looker=fabbro)

    # Solo se l'oggetto è un'arma
    if not arma.weapon_type:
        to_say = "a %s Non mi pare proprio che %s sia un'arma." % (player.code, arma_name)
        command_say(fabbro, to_say)
        return True

    if arma.life >= arma.max_life:
        to_say = "a %s Si vede ad occhio che %s non ha bisogno di riparazioni!" % (player.code, arma_name)
        command_say(fabbro, to_say)
        return True

    to_say = "a %s %s ha proprio bisogno di una sistemata." % (player.code, color_first_upper(arma_name))
    command_say(fabbro, to_say)

    # (TD) farei una defer con messaggio di act con il lavorio sull'arma
    arma.life = arma.max_life
    to_say = "a %s Ecco fatto, ora %s è a posto!" % (player.code, arma_name)
    command_say(fabbro, to_say)
    return True

    #entity.act("\n$n ha scavato per un certo tratto.\n", TO.OTHERS)
    #entity.act("\nSei riuscito a procedere per un certo tratto.\n", TO.ENTITY)
        #$N arma
        #player.act("cerca di darti robaccia ma tu non accetti.", TO.ENTITY, arma)
        #player.act("$n non accetta che tu gli dia alcunché.", TO.TARGET, arma)
        #player.act("$N cerca inutilmente di dare qualcosa a $n.", TO.OTHERS, arma)
#- Fine Funzione -
