# -*- coding: utf-8 -*-

"""
Modulo per la gestione del frameset per le due pagine di gioco di input/output.
"""

#= IMPORT ======================================================================

import datetime
import string

from src.color        import colors_to_html
from src.config       import config
from src.enums        import OPTION, TRUST
from src.utility      import commafy, is_number
from src.web_resource import IFRAME_BROWSERS, WebResource, send_audio, create_tooltip


#= CLASSI ======================================================================

class GameInterfacePage(WebResource):
    """
    Pagina web per giocare al Mud.
    """
    TITLE = "Game Interface"

    TALENTS_HEADER_TEMPLATE    = string.Template(open("src/views/game_interface_talents_header.view").read())
    NO_GAMING_ALLOWED_TEMPLATE = string.Template(open("src/views/game_no_gaming_allowed.view").read())
    NO_SUPPORT_TEMPLATE        = string.Template(open("src/views/game_no_support.view").read())
    NO_NAME_FOUND_TEMPLATE     = string.Template(open("src/views/game_no_name_found.view").read())
    SUGGESTED_TEMPLATE         = string.Template(open("src/views/game_suggested.view").read())
    GAME_TEMPLATE              = string.Template(open("src/views/game_interface.view").read())

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True
    PLAYER_MUST_EXIST_IN_GET   = False
    PLAYER_MUST_EXIST_IN_POST  = True

    def create_header(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_menu(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_square(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_footer(self, request, conn):
        return ""
    #- Fine Metodo -

    def render_GET(self, request, conn):
        pg_code = ""
        if "pg_code" in request.args:
            pg_code = request.args["pg_code"][0].capitalize()
        if pg_code not in conn.account.players:
            return self.NO_NAME_FOUND_TEMPLATE.safe_substitute({"player_code" : "???"})

        player = conn.account.players[pg_code]
        player.login_time = datetime.datetime.now()
        conn.player = player
        conn.account.player = player

        mapping = {"max_life"      : conn.player.max_life,
                   "max_mana"      : conn.player.max_mana,
                   "max_vigour"    : conn.player.max_vigour,
                   "talents" : conn.player.talents}
        spinner_header = self.TALENTS_HEADER_TEMPLATE.safe_substitute(mapping)

        courier_font_style = ""
        if OPTION.COURIER_FONT in conn.account.options:
            courier_font_style = '''<link rel="stylesheet" type="text/css" href="style_courier.css">'''

        browser_code = conn.get_browser()
        if browser_code.startswith(("CHROME", "FIREFOX")):
            suggested = ""
        else:
            suggested = self.SUGGESTED_TEMPLATE.safe_substitute({})

        disabled_tabs = ""
        if conn.player.talents == 0:
            disabled_tabs = '''$("#talents_title").parent().hide();'''

        talents_body = self.create_talents_body(conn)

        if conn.player and conn.player.last_input:
            # Forza la formattazione corretta da inviare nell'html
            last_input = colors_to_html(conn.player.last_input).replace("'", "\'").replace('"', '\"')
        else:
            last_input = ""

        save_last_input_script = ""
        if last_input:
            save_last_input_script = '''<script>parent.saveInputOnHistory("%s");</script>''' % last_input

        if OPTION.ITALIAN in conn.account.options:
            language = "it"
        else:
            language = "en"

        show_last_input_span = '''<span id="show_last_input" class="invisible"></span>'''

        # Indica se il giocatore vuole utilizzare la nuova tipologia di connessione
        output_iframe = ""
        if OPTION.COMET in conn.account.options:
            use_comet = '''<span id="use_comet" />'''
        else:
            use_comet = ""
            # Ad alcuni browser forza la connessione tramite un iframe
            if browser_code in IFRAME_BROWSERS:
                output_iframe = '''<iframe id='output_iframe' class="invisible"></iframe>'''

        mapping = {"spinner_header"         : spinner_header,
                   "player_menu"            : "", # (TD)
                   "player_code"            : conn.player.code,
                   "courier_font_style"     : courier_font_style,
                   "use_comet"              : use_comet,
                   "output_iframe"          : output_iframe,
                   "audio"                  : send_audio(conn, "intro.mid", loop=False),
                   "game_name"              : config.game_name,
                   "suggested"              : suggested,
                   "disabled_tabs"          : disabled_tabs,
                   "talents_body"           : talents_body,
                   "last_input"             : last_input,
                   "save_last_input_script" : save_last_input_script,
                   "language"               : language,
                   "show_last_input_span"   : show_last_input_span,
                   "life"                   : conn.player.life,
                   "max_life"               : conn.player.max_life,
                   "mana"                   : conn.player.mana,
                   "max_mana"               : conn.player.max_mana,
                   "vigour"                 : conn.player.vigour,
                   "max_vigour"             : conn.player.max_vigour}

        if not config.allow_player_gaming and conn.player.trust == TRUST.PLAYER and conn.account.trust == TRUST.PLAYER:
            return self.NO_GAMING_ALLOWED_TEMPLATE.safe_substitute(mapping)

        # Ignora il supporto per browser di internet explorer
        if browser_code in ("IE5", "IE6"):
            browser_name = "Internet Explorer " + browser_code[-1]
            mapping.update({"browser_name" : browser_name})
            return self.NO_SUPPORT_TEMPLATE.safe_substitute(mapping)

        return self.GAME_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        """
        Quando la pagina di gioco viene chiusa viene chiusa anche la connessione
        di gioco e, quindi, fatto uscire dal gioco il player.
        C'è da notare che se il browser-client crasha questa chiamata
        probabilmente non viene fatta e quindi l'uscita del player dal gioco
        viene eseguita tramite il contatore di idle.
        """
        # Se è stato passato l'argomento apposito allora esegue la
        # distribuzione dei talenti sui punti e sulle skill
        distribute = "0"
        if "distribute" in request.args:
            distribute = request.args["distribute"][0]
        if distribute == "1":
            if "initial_talents" not in request.args:
                return "Punti di talento iniziali non sono stati passati."
            if "talents" not in request.args:
                return "Punti di talento non sono stati passati."
            if "initial_life" not in request.args:
                return "Punti di vita iniziali non sono stati passati."
            if "initial_mana" not in request.args:
                return "Punti di mana iniziali non sono stati passati."
            if "initial_vigour" not in request.args:
                return "Punti di vigore iniziali non sono stati passati."
            if "life_points" not in request.args:
                return "Punti di vita non sono stati passati."
            if "mana_points" not in request.args:
                return "Punti di mana non sono stati passati."
            if "vigour_points" not in request.args:
                return "Punti di vigore non sono stati passati."

            initial_talents = request.args["initial_talents"][0]
            talents   = request.args["talents"][0]
            initial_life    = request.args["initial_life"][0]
            initial_mana    = request.args["initial_mana"][0]
            initial_vigour  = request.args["initial_vigour"][0]
            life_points     = request.args["life_points"][0]
            mana_points     = request.args["mana_points"][0]
            vigour_points   = request.args["vigour_points"][0]

            if not is_number(initial_talents):
                return "Punti di talento iniziali non sono un numero: %s" % initial_talents
            if not is_number(talents):
                return "Punti di talento non sono un numero: %s" % talents
            if not is_number(initial_life):
                return "Punti di vita iniziali non sono un numero: %s" % initial_life
            if not is_number(initial_mana):
                return "Punti di mana iniziali non sono un numero: %s" % initial_mana
            if not is_number(initial_vigour):
                return "Punti di vigore iniziali non sono un numero: %s" % initial_vigour
            if not is_number(life_points):
                return "Punti di vita non sono un numero: %s" % life_points
            if not is_number(mana_points):
                return "Punti di mana non sono un numero: %s" % mana_points
            if not is_number(vigour_points):
                return "Punti di vigore non sono un numero: %s" % vigour_points

            initial_talents = int(initial_talents)
            talents         = int(talents)
            initial_life    = int(initial_life)
            initial_mana    = int(initial_mana)
            initial_vigour  = int(initial_vigour)
            life_points     = int(life_points)
            mana_points     = int(mana_points)
            vigour_points   = int(vigour_points)

            distributed_talents = initial_talents - talents
            if distributed_talents == 0:
                return "Non è stato distribuito nessun talento"

            total_initial = initial_life + initial_mana + initial_vigour
            total_points  = life_points + mana_points + vigour_points
            if distributed_talents != total_points - total_initial:
                return "C'è stato un errore nella distribuzione dei talenti"

            if not conn.player:
                log.bug("Impossibile distribuire i talenti ad una connessione senza player valido: %r (conn: %s)" % (conn.player, conn.get_id()))
                return

            conn.player.talents = talents
            conn.player.max_life      = life_points
            conn.player.max_mana      = mana_points
            conn.player.max_vigour    = vigour_points

            return ""

        # Se è stato passato l'argomento apposito aggiorna il pannello
        # della tab relativa i talenti
        refresh_talents = "0"
        if "refresh_talents" in request.args:
            refresh_talents = request.args["refresh_talents"][0]
        if refresh_talents == "1":
            return self.create_talents_body(conn)

        # Se è stato passato l'argomento apposito chiude la connessione
        close_connection = "0"
        if "close_connection" in request.args:
            close_connection = request.args["close_connection"][0]
        if close_connection == "1":
            conn.close_game_request()
    #- Fine Metodo -

    def create_talents_body(self, conn):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        # -------------------------------------------------------------------------

        player = conn.player
        if not player:
            log.bug("player non è valido %r per la connessione %s" % (player, conn.get_id()))
            return ""

        output = []

        ie_problem = ""
        # Per IE9 non c'è bisogno del messaggio, (TT) bisognerà testare piuttosto se per IE7 sì
        if conn.get_browser() == "IE_8":
            ie_problem = '''Se per caso visualizzate spostate in maniera errata le freccette per aumentare e diminuire i valori sottostanti allora potete risolvere cliccando sul bottone <img src="graphics/ie_broken_button.png" /> in alto.<br><br>'''
        output.append(ie_problem)

        if conn.player.talents == 0:
            talents_title = '''Non hai nessun talento da poter distribuire.'''
        else:
            talents_title = '''Hai [white]<span id="talents">%d</span>[close] talenti da poter distribuire in:''' % conn.player.talents
        output.append('''<center><span style="font-weight:bold;">%s</span></center><br>''' % talents_title)

        # Se non vi sono talenti da spendere allora ritorna l'html finora creato
        if conn.player.talents == 0:
            return "".join(output)

        output.append('''<script>initial_life = %d; initial_mana = %d; initial_vigour = %d; initial_talents = %d;</script>''' % (
            player.max_life, player.max_mana, player.max_vigour, player.talents))

        output.append('''<div class="ui-widget-content ui-corner-all" style="padding:5px">''')
        output.append('''<table align="center" class="ui-widget-content"><tr>''')
        output.append('''<td><span style="color:red">Vita</span>:</td>''')
        output.append('''<td><input type="text" id="life" class="spinner" value="%d" readonly="readonly" onChange="changeTalentPoints(this)" onBlur="changeTalentPoints(this)" /></td>''' % player.max_life)
        output.append('''<td>%s </td>''' % create_tooltip(conn, "La vita indica la quantità di danni che puoi sostenere prima di morire"))
        output.append('''<td><span style="color:royalblue">Mana</span>:</td>''')
        output.append('''<td><input type="text" id="mana" class="spinner" value="%d" readonly="readonly" onChange="changeTalentPoints(this)" onBlur="changeTalentPoints(this)" /></td>''' % player.max_mana)
        output.append('''<td>%s </td>''' % create_tooltip(conn, "Il mana è quell'energia utile nel pronunciare incantesimi o utilizzare oggetti magici"))
        output.append('''<td><span style="color:green">Vigore</span>:</td>''')
        output.append('''<td><input type="text" id="vigour" class="spinner" value="%d" readonly="readonly" onChange="changeTalentPoints(this)" onBlur="changeTalentPoints(this)" /></td>''' % player.max_vigour)
        output.append('''<td>%s </td>''' % create_tooltip(conn, "Il vigore indica quanto ti puoi muovere e quanto peso puoi trasportare"))
        output.append('''</tr></table>''')
        output.append('''</div><br>''')

        output.append('''<div class="ui-widget-content ui-corner-all" style="padding:5px; text-align:center">''')
        output.append('''<input type="submit" id="send" value="Distribuisci" onclick="distribute();"/> ''')
        output.append('''<input type="submit" id="close" value="Chiudi" onclick="$("#talents_title").parent().hide(); $("#game_tabs").tabs({selected: 0}"/><br>''')
        output.append('''<span id="error_message" style="color:red"></span>''')
        output.append('''</div>''')

        return "".join(output)
    #- Fine Metodo -
