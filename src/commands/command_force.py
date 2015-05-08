# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command   import get_command_syntax
from src.enums     import LOG
from src.grammar   import grammar_gender
from src.interpret import interpret, multiple_search_on_inputs, translate_input
from src.log       import log
from src.utility   import one_argument, format_for_admin


#= FUNZIONI ====================================================================

def command_force(entity, argument=""):
    """
    Forza l'esecuzione di un comando da parte di un'altra entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_force")
        entity.send_output(syntax, break_line=False)
        return False

    arg1, argument = one_argument(argument)
    target = entity.find_entity_extensively(arg1, inventory_pos="first")
    if not target:
        target = entity.find_entity_extensively(arg1)
        if not target:
            entity.send_output("Nessuna entità trovata con argomento [white]%s[close]" % arg1)
            return False

    arg2, argument = one_argument(argument)
    if not arg2:
        entity.send_output("Che comando vorresti [red]forzare[close] a %s?" % target.get_name(entity))
        return False

    input, huh_input, input_lang = multiple_search_on_inputs(entity, arg2)
    if not input:
        entity.send_output("L'argomento %s non è relativo ad un comando valido." % arg2)
        return False

    if input.command and input.command.fun_name == "command_force":
        entity.send_output("Non puoi forzare un force.")
        return False

    translated_input = translate_input(target, arg2, input_lang)
    if not translated_input:
        entity.send_output("Non è stato possibile tradurre l'input %s per %s (lingua originale: %s)" % (
            arg2, target.get_name(entity), input_lang))
        return False

    target.send_output("\n")
    execution_result = interpret(target, "%s %s" % (translated_input, argument), force_position=True, show_input=False)
    if not execution_result:
        if target == entity:
            entity.send_output("\nL'esecuzione dell'input [limegreen]%s[close] forzato su di [white]te stess%c[close] non è andata a buon fine." % (
                arg2, grammar_gender(entity)))
        else:
            entity.send_output("\nL'esecuzione dell'input %s forzato su di %s non è andata a buon fine." % (
                arg2, target.get_name(entity)))
            if not entity.incognito:
                target.send_output("\n%s ti ha forzato a fare qualcosa." % entity.get_name(target))
            log.admin("%s ha cercato di forzare %s a fare: %s %s" % (entity.name, target.name, arg2, argument))
        return False

    if target == entity:
        message = "\n" + format_for_admin("Il force dell'input [green]%s[close] su [white]te stess%c[close] sembra essere andato a buon fine." % (
            arg2, grammar_gender(entity)))
        entity.send_output(message)
    else:
        message = "\n" + format_for_admin("Il force dell'input [green]%s[close] su di %s sembra andato a buon fine." % (
            arg2, target.get_name(entity)))
        entity.send_output(message)
        if not entity.incognito:
            target.send_output("\n%s ti ha forzato a fare qualcosa." % entity.get_name(target))
        log.admin("%s ha forzato %s a fare: %s %s" % (entity.name, target.name, arg2, argument))

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "force\n"
    syntax += "force <qualcuno o qualcosa> <comando da forzare>\n"

    return syntax
#- Fine Funzione -
