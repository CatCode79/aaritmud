# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.channel   import talk_channel
from src.color     import get_first_color, remove_colors
from src.command   import get_command_syntax
from src.database  import database
from src.enums     import FLAG, CHANNEL, OPTION
from src.grammar   import is_vowel
from src.interpret import translate_input
from src.log       import log
from src.utility   import (clean_string, is_same, is_prefix, one_argument,
                           number_argument, multiple_arguments)


#= FUNZIONI ====================================================================

def command_tell(entity, argument=""):
    """
    Permette di parlare con tutti nel Mud, in maniera off-gdr.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        entity.send_output("Vuoi %s a qualcuno che cosa?" % CHANNEL.TELL)
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_tell")
            entity.send_output(syntax, break_line=False)
        return False

    # Qui per la ricerca di target non viene utilizzata la find_entity perché
    # deve cercare solo i giocatori online
    # (TD) oltre alla ricerca di admin che possiedono mob o oggetti
    arg, argument = one_argument(argument)
    target = search_for_player(entity, arg)
    if not target:
        # (TD) se non è stato tovato allora cerca tra gli identificativi
        # personali relativi ai personaggi invisibili (implementazione
        # alternativa del reply)
        entity.send_output("Non è stato trovato nessun giocatore con argomento [white]%s[close]" % arg)
        return False

    # (TD) possibile implementazione di NOTELL, anche se è preferibile punizione
    # classica di NO_ENTER_IN_GAME per tot giorni

    if entity == target:
        entity.send_output("Non puoi comunicare con [white]te stess$o[close]!")
        return False

    if not target.game_request:
        entity.send_output("Il giocatore [white]%s[close] è attualmente [darkslategray]offline[close]." % target.name)
        return False

    if not argument:
        entity.send_output("Che messaggio privato vorresti inviare a [white]%s[close]?" % target.name)
        return False

    channel_color = get_first_color(str(CHANNEL.TELL))

    afk_status = ""
    if FLAG.AFK in target.flags:
        if entity.account and OPTION.ITALIAN in entity.account.options:
            afk_status = " (LDT)"
        else:
            afk_status = " (AFK)"

    if is_vowel(remove_colors(target.name)[0]):
        preposition = "ad"
    else:
        preposition = "a"

    entity.send_output("%s %s%s[close] %s: %s'%s'" % (
        CHANNEL.TELL.verb_you, channel_color, preposition, target.name, afk_status, argument), avoid_snoop=True)
    # (TD) inviare anche il soft beep per avvertire che ha ricevuto un messaggio
    # ed aggiungere l'opzione apposita
    if target.get_conn().get_browser():
        numbered_keyword = entity.get_numbered_keyword(looker=target)
        javascript = '''javascript:putInput('%s %s ');''' % (translate_input(target, "tell", "en"), numbered_keyword)
        target.send_output("""\n<a href="%s">%s%s ti[close]%s</a>: '%s'""" % (javascript, entity.name, channel_color, CHANNEL.TELL.verb_it, argument), avoid_snoop=True)
    else:
        target.send_output("""\n%s %sti[close]%s: '%s'""" % (entity.name, channel_color, CHANNEL.TELL.verb_it, argument), avoid_snoop=True)
    target.send_prompt()

    return True
#- Fine Funzione -


def search_for_player(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    number, argument = number_argument(argument)

    counter = 1
    for player in database["players"].itervalues():
        if not player.game_request:
            continue
        if player.incognito and player.trust > entity.trust:
            continue
        if is_same(argument, player.name):
            if counter == number:
                return player
            counter += 1

    counter = 1
    for player in database["players"].itervalues():
        if not player.game_request:
            continue
        if player.incognito and player.trust > entity.trust:
            continue
        if is_prefix(argument, player.name):
            if counter == number:
                return player
            counter += 1

    # Cerca ora tra i giocatori offline, giusto per ritornare un qualcosa
    counter = 1
    for player in database["players"].itervalues():
        if player.game_request:
            continue
        if player.incognito and player.trust > entity.trust:
            continue
        if is_same(argument, player.name):
            if counter == number:
                return player
            counter += 1

    counter = 1
    for player in database["players"].itervalues():
        if player.game_request:
            continue
        if player.incognito and player.trust > entity.trust:
            continue
        if is_prefix(argument, player.name):
            if counter == number:
                return player
            counter += 1

    return None
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "tell <giocatore> <messaggio privato>\n"
#- Fine Funzione -
