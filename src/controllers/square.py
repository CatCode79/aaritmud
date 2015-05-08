# -*- coding: utf-8 -*-

"""
Modulo per la lettura e l'invio dei messaggi sulla Piazzetta.
"""


#= IMPORT ======================================================================

import datetime
import string
import urllib

from src.color        import close_color, get_first_color, convert_colors
from src.config       import config
from src.database     import database
from src.enums        import TRUST
from src.log          import log
from src.utility      import convert_urls, pretty_date
from src.web_resource import WebResource


#= COSTANTI ====================================================================

ADDITIONAL_HEADER = """<meta name="robots" content="noindex" />"""


#= CLASSI ======================================================================

class SquarePage(WebResource):
    """
    Pagina utilizzata per gestire la Piazzetta.
    """
    TITLE = "Square"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = True

    PAGE_TEMPLATE        = string.Template(open("src/views/square.view").read())
    SQUARE_MESSAGES_LIST = map(string.strip, open("persistence/square_messages.list").readlines())

    NEW_PAGE = True

    def create_additional_header(self, request, conn):
        return ADDITIONAL_HEADER
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
        """
        Ritorna la pagina con gli ultimi messaggi della piazzetta.
        """
        hide_watermark = ""
        if conn and conn.account:
            hide_watermark = '''document.getElementById("square_login").className += ' invisible';'''
        else:
            hide_watermark = '''document.getElementById("square_input").className += ' invisible'; document.getElementById("square_submit").className += ' invisible';'''

        output_lines = []
        # Inizializza il counter per alternare correttamente il background di grigio
        counter = len(self.SQUARE_MESSAGES_LIST)
        if counter > config.max_square_messages:
            messages = self.SQUARE_MESSAGES_LIST[counter - config.max_square_messages : ]
        else:
            messages = self.SQUARE_MESSAGES_LIST
        for line in reversed(messages):
            if not line:
                continue
            square_message = create_square_message(line, conn, counter)
            if square_message:
                output_lines.append(square_message)
            counter -= 1
        square_output = "".join(output_lines)
        if not square_output:
            square_output = "<div id='chat0' class='square_message'> <i>Non vi sono messaggi nella Piazzetta</i></div>"

        mapping = {"max_square_msg_len" : config.max_square_msg_len,
                   "hide_watermark"     : hide_watermark,
                   "square_output"      : square_output,
                   "last_refresh_id"    : len(self.SQUARE_MESSAGES_LIST)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if not conn:
            return "La connessione non è valida"

        if not conn.account:
            return "Per poter inviare messaggi devi eseguire il login al sito"

        message = ""
        if "msg" in request.args:
            message = request.args["msg"][0]
        if not message:
            log.bug("messagge non valido: %r" % message)
            return "Il messaggio è vuoto"

        message = urllib.unquote(message)
        if len(message) > config.max_square_msg_len:
            return "Il messaggio è troppo lungo, massimo %d" % config.max_square_msg_len

        message = convert_urls(message)
        if "[" in message:
            message = close_color(message)

        square_path = "persistence/square_messages.list"
        try:
            square_file = open(square_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in append: %r" % square_path)
            return "Errore nell'apertura del database dei messaggi"

        line = "%s;%s;%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), conn.account.name, message)
        self.SQUARE_MESSAGES_LIST.append(line)
        square_file.write(line)
        square_file.close()

        return ""
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def create_square_message(line, conn, counter, use_quote=False):
    if not line:
        log.bug("line non è un parametro valido: %r" % line)
        return ""

    if not conn:
        log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if counter < 0:
        log.bug("counter non è un parametro valido: %d" % counter)
        return ""

    # use_quote_plus ha valore di verità

    # ---------------------------------------------------------------------

    line_pieces = line.split(";", 2)
    if len(line_pieces) < 3:
        return ""

    if conn.account and conn.account.name == line_pieces[1]:
        name = "[royalblue]Tu[close]"
    elif get_first_color(line_pieces[1]):
        name = line_pieces[1]
    else:
        name = "[white]%s[close]" % line_pieces[1]

    dt = ""
    if conn.account and conn.account.trust >= TRUST.MASTER:
        dt = "title='%s'" % pretty_date(past=datetime.datetime.strptime(line_pieces[0], "%Y-%m-%d %H:%M:%S"))

    bg_color = ""
    if counter % 2:
        bg_color = "style='background-color:#222;'"

    if use_quote:
        square_message = urllib.quote(line_pieces[2])
    else:
        square_message = line_pieces[2]

    square_message = "<div id='chat%d' class='square_message' %s%s>%s: %s</div>\n" % (
        counter, bg_color, dt, name, square_message)
    return convert_colors(square_message)
#- Fine Funzioni -
