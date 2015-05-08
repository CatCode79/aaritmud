# -*- coding: utf-8 -*-

"""
Pagina web con la lista dei personaggi con cui giocare.
"""

#= IMPORT ======================================================================

import operator

from src.account      import get_error_message_password, get_error_message_email, MAX_LEN_EMAIL
from src.color        import remove_colors
from src.config       import config
from src.element      import Flags
from src.enums        import FLAG, OPTION, SEX
from src.utility      import pretty_date, is_number
from src.web_resource import (WebResource, create_form_row, create_form, create_tooltip,
                              create_checklist_of_flags, set_checked_flags, create_icon)


#= CLASSI ======================================================================

class PlayersPage(WebResource):
    TITLE = "Personaggi"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    def render_GET(self, request, conn):
        page = ""

        page += '''<h3>Elenco dei tuoi Personaggi:</h3>'''
        page += '''<table rules="rows" width="100%">'''
        page += '''  <tr align="center"><th>Gioca con</th><th>Razza</th><th>Livello</th><th>Creato il</th><th>Connesso il</th><th>Disconnesso il</th><th>Giocato</th></tr>'''
        for player in sorted(conn.account.players.values(), key=lambda player: remove_colors(player.name)):
            if player.login_time:
                login_time = pretty_date(past=player.login_time)
            else:
                login_time = "Mai"

            if player.logout_time:
                logout_time = pretty_date(past=player.logout_time)
            else:
                logout_time = "Mai"

            # (TD) pensare se separare il codice e fare una funzione come la pretty_date
            seconds = (player.seconds_played) % 60
            minutes = (player.seconds_played / 60) % 60
            hours   = (player.seconds_played / 3600) % 24
            days    = (player.seconds_played / 86400)
            if days == 0:
                if hours == 0:
                    if minutes == 0:
                        time_played = "%d second%s" % (seconds, "o" if seconds == 1 else "i")
                    else:
                        time_played = "%d minut%s" % (minutes, "o" if minutes == 1 else "i")
                else:
                    time_played = "%d or%s e %d minut%s" % (hours, "a" if hours == 1 else "e", minutes, "o" if minutes == 1 else "i")
            else:
                time_played = "%d giorn%s e %d or%s" % (days, "o" if days == 1 else "i", hours, "a" if hours == 1 else "e",)

            # Sotto alcuni browser non funziona la pagina di gioco se non si
            # inserisce l'url per intero
            browser = conn.get_browser()
            server_address = ""
            if browser.startswith("IE"):
                server_address = "%s:%s/" % (config.site_address, config.http_port)

            href = '''href="game_interface.html?pg_code=%s" target="game_page"''' % player.code
            page += '''  <tr align="center"><td align="left">%s<a %s>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>''' % (
                create_icon(player.get_icon()),
                href,
                player.name,
                player.sex_replacer(player.race.name),
                player.level,
                pretty_date(past=player.created_time),
                login_time,
                logout_time,
                time_played)
        if config.max_account_players == 0:
            page += '''  <tr><td colspan="7">La creazione di nuovi personaggi è disattiva.</td></tr>'''
        elif len(conn.account.players) < config.max_account_players:
            page += '''  <tr><td colspan="7"><a href="create_player1.html">Un Nuovo Personaggio</a></td></tr>'''
        else:
            page += '''  <tr><td colspan="7">Numero massimo di personaggi creabili raggiunto.</td></tr>'''
        page += '''</table>'''
        page += '''%s personaggi creati su %s.<br>''' % (len(conn.account.players), config.max_account_players)
        page += '''<br>'''

        page += '''<br>È inevitabile per i personaggi creati durante questa apertura finiscano lentamente con l'acquisire vantaggi, oggetti ed abilità troppo potenti per poter essere conservati quando si passerà dalla beta alla versione definitiva; è altrettanto inevitabile che sia una sofferenza indicibile rinunciarvi... pertanto concerteremo assieme una via che consenta ai partecipanti di mantenere almeno una parte dello status e dei privilegi acquisiti anche come segno virtuale-tangibile della nostra riconoscenza per aver contribuito alla crescita di Aarit.'''

        page += '''<script>$.post("players.html", {width:screen.width, height:screen.height});</script>'''

        return page
    #- Fine Metodo -

    def render_POST(self, request, conn):
        width = 0
        if "width" in request.args:
            width = request.args["width"][0]
            if is_number(width):
                width = int(width)
            else:
                log.bug("resolution width passato dal client con account %s non è un numero valido: %s" % (conn.account.code, width))
                return "0"

        height = 0
        if "height" in request.args:
            height = request.args["height"][0]
            if is_number(height):
                height = int(height)
            else:
                log.bug("resolution height passato dal client con account %s non è un numero valido: %s" % (conn.account.code, height))
                return "0"

        if width != height and (width == 0 or height == 0):
            log.bug("Non sono stati ricavati tutti e due i valori di risoluzione dello schermo del client: width=%d height=%d" % (width, height))
            return "0"

        conn.account.resolution_width  = width
        conn.account.resolution_height = height
    #- Fine Metodo -
