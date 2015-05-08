# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.config     import config
from src.connection import connections
from src.database   import database
from src.engine     import engine
from src.enums      import FLAG, OPTION, TRUST
from src.log        import log


#= FUNZIONI ====================================================================

def command_who(entity, argument=""):
    """
    Permette di visualizzare la lista dei giocatori in gioco.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    conn = None
    if entity.IS_PLAYER:
        conn = entity.get_conn()
        if not conn:
            if not engine.test_inputs_mode:
                log.bug("conn non è valido per il giocatore %s: %r" % (conn, entity.code))
            return False

    who_interface = create_who_interface(conn)
    if not who_interface:
        log.bug("who_interface non è valido: %r" % who_interface)
        return False

    entity.send_output(who_interface, break_line=False)
    return True
#- Fine Funzione -


# (TD) per i navigatori offline vedono solo la short del pg, altrimenti
# per coloro che sono loggati e che conoscono il relativo pg online
# visualizzano la stringa memorizzata o conosciuta
def create_who_interface(conn=None):
    """
    Crea il codice html relativo alle informazioni del who.
    """
    from src.web_resource import create_icon

    who_players = get_who_players()
    if not who_players:
        return "In questo momento non v'è nessun giocatore in %s.<br>" % config.game_name

    if conn and conn.player:
        looker = conn.player
        trust = conn.player.trust
    elif conn and conn.account:
        looker = None
        trust = conn.account.trust
    else:
        looker = None
        trust = TRUST.PLAYER

    lines = []
    lines.append(''' [orange]==[yellow]={[cyan]===============-&nbsp; [white]Giocatori[close] su %s &nbsp;[cyan]-===============[yellow]}=[orange]==[close]<br>''' % config.game_name)
    lines.append('''<table class="mud">''')
    if trust > TRUST.PLAYER:
        lines.append('''<tr><th></th><th>Nome</th><th>Titolo</th><th>Stato</th><th>Account</th><th>Browser</th></tr>''')

    for player in who_players:
        if player.trust > TRUST.PLAYER:
            image = "graphics/triskele.gif"
        else:
            image = player.get_icon()
        image = create_icon(image)

        status = ""
        if FLAG.AFK in player.flags:
            if player.account and OPTION.ITALIAN in player.account.options:
                status += "(LDT)"
            else:
                status += "(AFK)"

        linkdead = ""
        if not player.game_request:
            linkdead += "[cyan](scollegato)[close]"

        lines.append('''<tr>''')
        lines.append('''<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>''' % (
            image, player.get_name(looker), player.title, status, linkdead))
        if trust > TRUST.PLAYER:
            lines.append('''<td>%s</td>''' % player.account.name)
            conn = player.get_conn()
            if conn:
                lines.append('''<td>%s</td>''' % conn.get_browser())
            else:
                lines.append('''<td></td>''')
        lines.append('''</tr>''')

    lines.append('''</table>''')
    return "".join(lines)
#- Fine Funzione -


def get_who_players():
    """
    Il comando non fa visualizzare volutamente i giocatori in idle, cioè coloro
    che hanno una game_request ma non una connessione.
    """
    players = []

    for conn in connections.itervalues():
        if conn.player:
            players.append(conn.player)

    return players
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "who\n"
    #syntax += "who gruppi"

    return syntax
#- Fine Funzione -
