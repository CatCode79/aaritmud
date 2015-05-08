# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando follow.
"""


#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.enums      import OPTION, SEX, TO, TRUST
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument, get_emote_argument


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[cadetblue]seguire[close]"
VERBS["you2"]       = "[cadetblue]seguirti[close]"
VERBS["gerund"]     = "[cadetblue]seguendo[close]"


#= FUNZIONI ====================================================================

# (TD) se si è seduti non si segue
# (TD) se si ci si muove volontariamente si perde il riferimento al guide
def command_follow(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Chi vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_follow")
            entity.send_output(syntax, break_line=False)
        return False

    ag1, argument = one_argument(argument)
    target = entity.find_entity(ag1, location=entity.location)
    if not target:
        entity.act("Non trovi nessun %s da %s qui attorno." % (ag1, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sembra stia cercando qualcuno qui attorno che non c'è.", TO.OTHERS)
        return False

    # (TD) anche qui forse ci vuole lo split
    pass

    # Se entity è sotto charm preferisce rimanere accanto al proprio master
    if entity.master:
        if entity.master == SEX.FEMALE:
            suffix = "alla tua maestra"
        else:
            suffix = "al tuo maestro"
        entity.act("Preferisci rimanere accanto %s $a." % suffix, TO.ENTITY, target, entity.master)
        entity.act("$n tenta di %s $N ma poi cambia idea, come ipnotizzat$o." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n tenta di %s ma poi cambia idea, come ipnotizzat$o." % verbs["you2"], TO.TARGET, target)
        entity.act("$n tenta di ribellarsi %s $a, ma poi cambia idea, è ancora in mano tua." % (
            verbs["gerund"], TO.TARGET, entity.master, target))  # (bb) possibile errore di doppio messaggio
        return False

    # Per smettere di seguire o essere seguiti basta scegliere come obiettivo
    # sé stessi
    if entity == target:
        if entity.guide:
            show_stop_following_messages(entity, target, verbs)
            entity.guide = None
            return True
        else:
            entity.act("Già non stai %s nessuno" % verbs["gerund"], TO.ENTITY)
            entity.act("$n si accorge solo ora che non sta %s nessuno." % verbs["gerund"], TO.OTHERS)
            return False

    # Evita di farsi seguire a vicenda, sarebbe dannoso in aree maze-like
    if entity.have_circle_follow(target):
        entity.act("Cominci a %s $N, che però segue te! Quindi decidi di smettere di farlo." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n e $N cominciano a seguirsi a vicenda, ma smettono quando capiscono che non è una gran idea.", TO.OTHERS, target)
        entity.act("$n comincia a seguirti, tuttavia tu insegui già lui! Dopo un po' decide di smettere di farlo.", TO.TARGET, target)
        return False

    force_return = check_trigger(entity, "before_follow", entity, target, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_followed", entity, target, behavioured)
    if force_return:
        return True

    if entity.guide:
        show_stop_following_messages(entity, target, verbs)
        entity.guide = None

    emote_argument = get_emote_argument(argument)
    entity.act("Cominci a %s $N%s." % (verbs["infinitive"], emote_argument), TO.ENTITY, target)
    if target.can_see(entity):
        # (TD) è che qui più che qualcuno segue $N è proprio o vedi o non vedi,
        # e non un: riconosci o non riconosci, da pensare se inserire un
        # parametro in più per la act per variare un po'
        entity.act("$n comincia a %s $N%s." % (verbs["infinitive"], emote_argument), TO.OTHERS, target)
        entity.act("$n ti comincia a %s%s." % (verbs["infinitive"], emote_argument), TO.TARGET, target)
    else:
        if target.trust > TRUST.PLAYER:
            target.send_to_admin("Anche se non lo puoi vedere sai che %s ha cominciato a %s." % (entity.name, verbs["you2"]))
    entity.guide = target

    force_return = check_trigger(entity, "after_follow", entity, target, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_followed", entity, target, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def show_stop_following_messages(entity, target, verbs):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # -------------------------------------------------------------------------

    entity.act("Smetti di %s $N." % verbs["infinitive"], TO.ENTITY, entity.guide)
    if target.location == entity.location and target.can_see(entity):
        entity.act("$n smette di %s $N." % verbs["infinitive"], TO.OTHERS, entity.guide)
        if entity != target:
            entity.act("$n smette di %s." % verbs["you2"], TO.TARGET, entity.guide)
    else:
        if target.trust > TRUST.PLAYER:
            target.send_to_admin("Anche se è lontano da te capisci che %s smette di %s." % (entity.name, verbs["you2"]))
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "follow %s\n" % entity.name
    syntax += "follow <nome personaggio o creatura>\n"
    return syntax
#- Fine Funzione -
