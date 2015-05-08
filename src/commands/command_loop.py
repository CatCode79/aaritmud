# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command import get_command_syntax
from src.enums   import LOG
from src.grammar import is_vowel
from src.log     import log
from src.utility import one_argument, is_prefix

from src.entitypes.corpse import decomposer_loop
from src.game             import game_loop
from src.fight            import fight_loop
from src.maintenance      import maintenance_loop
from src.behaviour        import room_behaviour_loop

from src.loops.aggressiveness import aggressiveness_loop
from src.loops.blob           import blob_loop
from src.loops.digestion      import digestion_loop


#= COSTANTI ====================================================================

LOOPS = (aggressiveness_loop,
         blob_loop,
         decomposer_loop,
         digestion_loop,
         game_loop,
         fight_loop,
         maintenance_loop,
         room_behaviour_loop)


#= FUNZIONI ====================================================================

def command_loop(entity, argument):
    """
    Permette di freezare il loop del gioco. Comodo per disattivare i behaviour
    in fase di test.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        output = []
        output.append(get_command_syntax(entity, "command_loop"))
        output.append('''<table class="mud">''')
        for loop in LOOPS:
            loop_name = loop.__class__.__name__.replace("Loop", "").lower()
            output.append('''<tr><td>Attualmente %s%s</td>''' % ("l'" if is_vowel(loop_name[0]) else "il ", loop_name))
            output.append('''<td>%sè[close] in pausa</td>''' % ("[red]" if loop.paused else "[white]non "))
            output.append('''<td>e%sè[close] stoppato.</td></tr>''' % (" [white]non " if loop.running else "d [red]"))
        output.append('''</table>''')
        output.append('''Ricordo che i reset non fanno parte dei loop, ma di un sistema di deferred separato.''')
        entity.send_output("".join(output))
        return False

    # -------------------------------------------------------------------------

    arg, argument = one_argument(argument)

    for loop in LOOPS:
        loop_name = loop.__class__.__name__.replace("Loop", "").lower()
        if is_prefix(arg, loop_name):
            break
    else:
        entity.send_output("Non esiste nessun loop chiamato [white]%s[close]" % arg)
        return False

    if not argument:
        entity.send_output("Vuoi eseguire una [green]pausa[close] o un [green]continua[close] %s%s?" % (
            "all'" if is_vowel(loop_name[0]) else "al ", loop_name))
        return False

    article = "L'" if is_vowel(loop_name[0]) else "Il "

    if is_prefix(argument, ("pausa", "pause")):
        if loop.paused:
            entity.send_output("%s%s si trova già in pausa." % (article, loop_name))
        else:
            entity.send_output("%s%s ora è stato messo in pausa" % (article, loop_name))
            loop.paused = True
    elif is_prefix(argument, ("continua", "continue")):
        if loop.paused:
            entity.send_output("%s%s ora ricomincerà a girare." % (article, loop_name))
            loop.paused = False
        else:
            entity.send_output("%s%s sta già girando." % (article, loop_name))
    else:
        entity.send_output("[white]%s[close] non è un argomento valido da passare al comando loop." % argument)
        return False

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "loop\n"
    for loop in LOOPS:
        loop_name = loop.__class__.__name__.replace("Loop", "").lower()
        syntax += "loop %s pausa|continua\n" % loop_name

    return syntax
#- Fine Funzione -
