# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando che serve a uccidere un'entità sconfitta.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.database   import database
from src.enums      import FLAG, TRUST, TO, OPTION
from src.fight      import start_fight
from src.gamescript import check_trigger
from src.grammar    import grammar_gender
from src.interpret  import translate_input
from src.log        import log
from src.utility    import is_same

if config.reload_commands:
    reload(__import__("src.commands.command_attack", globals(), locals(), [""]))
    reload(__import__("src.commands.command_destroy", globals(), locals(), [""]))
from src.commands.command_attack import VERBS as ATTACK_VERBS
from src.commands.command_destroy import VERBS as DESTROY_VERBS


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[red]uccidere[close]",
         "you2"       : "[red]ucciderti[close]",
         "you"        : "[red]uccidi[close]",
         "gerund"     : "[red]uccidendo[close]",
         "noun"       : "[red]ucciderl%s[close]",
         "it"         : "[red]uccidi[close]"}


#= FUNZIONI ====================================================================

def command_kill(entity, argument="", verbs=VERBS, behavioured=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Chi o che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_kill")
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) Controllo sul mental state

    # Cerca la vittima da attaccare
    entity_tables = ["mobs", "players"]
    target = entity.find_entity(argument, location=entity.location, entity_tables=entity_tables, avoid_equipment=True)
    if not target:
        target = entity.find_entity(argument, location=entity.location, entity_tables=["items"], avoid_equipment=True, compare_functions=[is_same])
        if target:
            destroy_translation = translate_input(entity, "destroy", "en")
            javascript_code = '''javascript:parent.sendInput('%s %s');''' % (destroy_translation, target.get_numbered_keyword(looker=entity))
            destroy_verb = DESTROY_VERBS["noun"] % grammar_gender(target)
            html_code = '''<a href="%s">%s</a>''' % (javascript_code, destroy_verb)
            entity.act("Non puoi %s $N ma puoi sempre %s!" % (verbs["infinitive"], html_code), TO.ENTITY, target)
            entity.act("$n si guarda attorno con [red]brama di sangue[close]...", TO.OTHERS, target)
            entity.act("$N ti guarda con [red]brama di sangue[close]...", TO.TARGET, target)
        else:
            entity.act("Non trovi nessun [white]%s[close] da %s" % (argument, verbs["infinitive"]), TO.ENTITY)
            entity.act("$n si guarda attorno con [red]brama di sangue[close]...", TO.OTHERS)
        return False

    if FLAG.BEATEN in target.flags:
        force_return = check_trigger(entity, "before_kill", entity, target, behavioured)
        if force_return:
            return True
        force_return = check_trigger(target, "before_killed", entity, target, behavioured)
        if force_return:
            return True

        entity.act("Dai il [red]colpo di grazia[close] a $N!", TO.ENTITY, target)
        entity.act("$n dà il [red]colpo di grazia[close] a $N!", TO.OTHERS, target)
        entity.act("$n ti dà il [red]colpo di grazia[close]!", TO.TARGET, target)
        target.dies(opponent=entity)
        entity.player_killed_counter += 1
        target.death_from_player_counter += 1

        force_return = check_trigger(entity, "after_kill", entity, target, behavioured)
        if force_return:
            return True
        force_return = check_trigger(target, "after_killed", entity, target, behavioured)
        if force_return:
            return True
        return True

    # Se non sta combattendo procede all'attacco o alla distruzione della vittima
    if entity.is_fighting(with_him=target):
        entity.act("Non è ancora giusto il momento di dare il colpo di grazia a $N.", TO.ENTITY, target)
        entity.act("$n vorrebbe dare il colpo di grazia a $N, ma non è ancora giunto il suo momento...", TO.OTHERS, target)
        entity.act("$n vorrebbe darti il colpo di grazia, ma non è ancora giunto il tuo momento...", TO.TARGET, target)
        return False

    if target.IS_ITEM:
        execution_result = kill_handler(entity, argument, "command_kill", entity_tables, verbs=DESTROY_VERBS, behavioured=behavioured)
    else:
        execution_result = kill_handler(entity, argument, "command_kill", entity_tables, verbs=ATTACK_VERBS, behavioured=behavioured)
    return execution_result
#- Fine Funzione -


def kill_handler(entity, argument, command_name, entity_tables, attack=False, destroy=False, verbs=VERBS, behavioured=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    if not entity_tables:
        log.bug("entity_tables non è un parametro valido: %r" % entity_tables)
        return False

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Chi o che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, command_name)
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) Controllo sul mental state

    # Cerca la vittima da attaccare
    target = entity.find_entity(argument, location=entity.location, entity_tables=entity_tables, avoid_equipment=True)
    if not target:
        entity.act("Non trovi nessun [white]%s[close] da %s" % (argument, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n non trova nessuno su cui poter sfogare la propria [red]brama di sangue[close].", TO.OTHERS)
        return False

    if entity.IS_ITEM:
        entity.act("Non ti è possibile %s perché sei un oggetto inanimato." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("Non è possibile per $n poter %s $N %s perché è un oggetto inanimato." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("Non è possibile per $n poterti %s perché è un oggetto inanimato." % verbs["infinitive"], TO.TARGET, target)
        return False

    if target == entity:
        entity.act("Non ti puoi %s da sol$o!" % verbs["infinitive"], TO.ENTITY)
        entity.act("$n sembra volersi %s da sol$o..." % verbs["infinitive"], TO.OTHERS)
        return False

    if entity.trust > TRUST.PLAYER and target.trust > TRUST.PLAYER:
        entity.act("Cerca di risolvere la cosa in maniera pacifica...", TO.ENTITY)
        return False

    if entity.is_fighting(with_him=target):
        entity.act("Stai già %s $N!" % verbs["gerund"], TO.ENTITY, target)
        entity.act("$n non riesce a %s $N più di così!" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n non riesce a %s più di così!" % verbs["infinitive"], TO.TARGET, target)
        return False

    if target.IS_ITEM and target.life <= 0:
        from src.commands import command_destroy
        entity.act("Non puoi %s $N più di così." % command_destroy.VERBS["infinitive"], TO.ENTITY, target)
        entity.act("$n non riesce a %s $N più di così." % command_destroy.VERBS["infinitive"], TO.OTHERS, target)
        entity.act("$n non riesce a %s più di così." % command_destroy.VERBS["you2"], TO.TARGET, target)
        return False

    force_return = check_trigger(entity, "before_kill", entity, target, attack, destroy, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_killed", entity, target, attack, destroy, behavioured)
    if force_return:
        return True

    # Avvia il combattimento!
    entity.act("%s $N." % color_first_upper(ATTACK_VERBS["you"]), TO.ENTITY, target)
    entity.act("$n %s $N." % ATTACK_VERBS["it"], TO.OTHERS, target)
    entity.act("$n ti %s." % ATTACK_VERBS["it"], TO.TARGET, target)
    start_fight(entity, target)

    force_return = check_trigger(entity, "after_kill", entity, target, attack, destroy, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_killed", entity, target, attack, destroy, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax  = ""
    syntax += "kill\n"
    syntax += "kill <nome della vittima>\n"

    return syntax
#- Fine Funzione -
