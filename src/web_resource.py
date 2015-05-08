# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica di tutto ciò che riguarda il web: gestione
richieste http, invio delle pagine.
"""


#= IMPORT ======================================================================

import datetime
import math
#import pprint
import random
import string
import sys
import time
import types
import urllib

from twisted.web import resource, server

from act            import replace_act_tags_translate
from src.color      import remove_colors, convert_colors, get_first_color
from src.connection import connections, Connection
from src.config     import config
from src.database   import database
from src.element    import Element, Flags, get_enum_element
from src.engine     import engine
from src.enums      import COLOR, LOG, OPTION, SEX, TRUST
from src.log        import log
from src.utility    import is_prefix, sort_datas, commafy, html_escape, email_encoder

from src.commands.command_who import get_who_players


#= COSTANTI ====================================================================

# Elenco dei codici dei browser che non supportano l'http streaming continuo
# ma che funzionano tramite la connessione con l'iframe
# (TD) Probabilmente devo inserire anche "SAFARI3"
IFRAME_BROWSERS = ("IE_7", "IE_8", "SAFARI_4", "FIREFOX_2", "OPERA_10", "LINKS_2", "ELINKS_0")

# Separatore dei vari messaggi di output inviati ad alcuni browser per
# permettere di riconoscere l'output ricevuto completamente ed inserirlo
# così nell'interfaccia; è un tag chiaramente inesistente nelle specifiche HTML.
OUTPUT_END_TAG = "<e>"


#= CLASSI ======================================================================

class WebResource(resource.Resource):
    """
    Questa classe sovrascrive il metodo render della classe resource.Resource
    per una gestione trasparente della connessione ad un pagina.
    """
    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = False

    PLAYER_MUST_EXIST_IN_GET   = False
    PLAYER_MUST_EXIST_IN_POST  = False

    MINIMUM_TRUST_ON_GET       = TRUST.NONE
    MINIMUM_TRUST_ON_POST      = TRUST.NONE

    GOOGLE_ANALYTICS_TEMPLATE  = string.Template(open("src/views/__google_analytics__.view").read())
    HEADER_TEMPLATE            = string.Template(open("src/views/__header__.view").read())
    FOOTER_TEMPLATE            = string.Template(open("src/views/__footer__.view").read())
    MENU_TEMPLATE              = string.Template(open("src/views/__menu__.view").read())
    SQUARE_TEMPLATE            = string.Template(open("src/views/__square__.view").read())
    NO_SHOW_SQUARE_TEMPLATE    = string.Template(open("src/views/__no_show_square__.view").read())
    WEB_MENU_LIST              = map(string.strip, open("data/web_menu.list").readlines())

    NEW_PAGE = False

    def render(self, request):
        starting_time = time.time()

        # Ricava, se esiste, la connessione dalla sessione
        session = request.getSession()
        if session in connections:
            conn = connections[session]
            log_descr = "di %s" % conn.get_id()
        else:
            # Se non è stata trovata nessuna connessione ne crea una nuova
            conn = connections[session] = Connection()
            conn.session = session

            # Imposta la funzione da eseguire nel qual caso la sessione web scada
            conn.session.notifyOnExpire(conn.close_game_request)

            conn.ip = "%s:%s" % (request.client.host, request.client.port)
            log_descr = "nuova connessione di %s" % conn.get_id()
        conn.request = request

        # Controlla che la richiesta sia lecita per questo tipo di risorsa
        if ((request.method == "GET"  and self.ACCOUNT_MUST_EXIST_IN_GET  and not conn.account)
        or  (request.method == "POST" and self.ACCOUNT_MUST_EXIST_IN_POST and not conn.account)):
            log.conn("Redirezionamento %s verso la pagina login.html" % log_descr)
            request.redirect("login.html")
            request.finish()
            return server.NOT_DONE_YET
        elif ((request.method == "GET"  and self.PLAYER_MUST_EXIST_IN_GET  and not conn.player)
        or    (request.method == "POST" and self.PLAYER_MUST_EXIST_IN_POST and not conn.player)):
            log.conn("Redirezionamento %s verso la pagina players.html (1)" % log_descr)
            request.redirect("players.html")
            request.finish()
            return server.NOT_DONE_YET
        elif ((request.method == "GET"  and self.MINIMUM_TRUST_ON_GET  != TRUST.NONE and conn.account and not conn.account.trust >= self.MINIMUM_TRUST_ON_GET)
        or    (request.method == "POST" and self.MINIMUM_TRUST_ON_POST != TRUST.NONE and conn.account and not conn.account.trust >= self.MINIMUM_TRUST_ON_POST)):
            if conn.player and str(request.URLPath()).split("/")[-1] not in conn.player.permissions:
                log.conn("Redirezionamento %s verso la pagina players.html (2)" % log_descr)
                request.redirect("players.html")
                request.finish()
                return server.NOT_DONE_YET

        page_url = str(request.URLPath()).rsplit("/", 1)[-1]
        if not page_url:
            page_url = "index.html"
        if request.method != "POST" and page_url not in ("refresh_infos.html", "game_connection_ajax.html", "below_menu.html", "square.html"):
            log.conn("%s: caricamento della pagina %s (%s)" % (log_descr.capitalize(), page_url, conn.get_browser()))

        # Se arriva fino a qui, processa normalmente il metodo di render voluto
        method = getattr(self, 'render_%s' % request.method, None)
        if not method:
            raise server.UnsupportedMethod(getattr(self, 'allowedMethods', ()))

        page = self.get_page(method, request, conn)
        if page == server.NOT_DONE_YET:
            return server.NOT_DONE_YET
        elif page:
            result = ""

            if self.NEW_PAGE and request.method == "POST":
                result = page
            else:
                result  = self.create_header(request, conn)
                result += self.create_menu(request, conn)
                result += page
                result += self.create_square(request, conn)
                result += self.create_footer(request, conn)

            # Sistema di replace degli act di tag anche al di fuori del
            # gioco, questo serve per esempio per i nomi delle razze o
            # per il testo degli help
            if "$o" in result:
                if conn.player and conn.player.sex == SEX.FEMALE:
                    result = result.replace("$o", "a")
                else:
                    result = result.replace("$o", "o")
            if "$t" in result or "$T" in result:
                if "$t" in result:
                    result = replace_act_tags_translate(result, "$t", conn.player)
                if "$T" in result:
                    result = replace_act_tags_translate(result, "$T", conn.player)

            if "[" in result:
                result = convert_colors(result)

            if "${milliseconds}" in result:
                milliseconds = str(int((time.time() - starting_time) * 1000))
                result = result.replace("${milliseconds}", milliseconds)

            if "${bytes}" in result:
                bytes = len(result)
                # Avverte di diminuire la grandezza della pagina
                if (bytes > 100000
                and not self.ACCOUNT_MUST_EXIST_IN_GET
                and not self.ACCOUNT_MUST_EXIST_IN_POST
                and not self.PLAYER_MUST_EXIST_IN_GET
                and not self.PLAYER_MUST_EXIST_IN_POST
                and self.MINIMUM_TRUST_ON_GET == TRUST.NONE
                and self.MINIMUM_TRUST_ON_POST == TRUST.NONE):
                    log.bug("Attenzione! Google indicizzerà solo i primi 100 Kb della pagina pubblica %s" % request.uri)
                result = result.replace("${bytes}", commafy(bytes))

            return result
        else:
            # Normalmente accade solo nei redirect e quindi non è un errore
            return ""
    #- Fine Metodo -

    def render_HEAD(self, request, conn):
        # questa riga:
        #super(WebResource, self).render_HEAD(request)
        # dona:
        #exceptions.TypeError: super() argument 1 must be type, not classobj

        # Una volta cambiata in questa:
        #resource.Resource.render_HEAD(request)
        # dona:
        #exceptions.TypeError: unbound method render_HEAD() must be called with Resource instance as first argument (got Request instance instead)

        #resource.Resource.render_HEAD(self, request)
        self.render_GET(request, conn)
    #- Fine Metodo -

    def get_page(self, method, request, conn):
        """
        Questo metodo esiste per essere sovrascritto da alcune classi che
        eseguono i metodi render_ in maniera differente.
        """
        return method(request, conn)
    #- Fine Metodo -

    def create_header(self, request, conn):
        """
        Ritorna la prima parte uguale per tutte le pagine html del Mud.
        """
        cache = ""
        if engine.options.mode != "official":
            cache += '''<meta http-equiv="PRAGMA" content="NO-CACHE">'''
            cache += '''<meta content="no-cache" http-equiv="Cache-Control">'''

        if config.allow_web_robots:
            allow_web_robots = ""
        else:
            allow_web_robots = '''<meta name="robots" content="noindex, nofollow">'''

        if config.google_analytics_ua:
            if config.reload_web_pages:
                self.GOOGLE_ANALYTICS_TEMPLATE = string.Template(open("src/views/__google_analytics__.view").read())
            mapping = {"google_analytics_ua" : config.google_analytics_ua}
            google_analytics = self.GOOGLE_ANALYTICS_TEMPLATE.safe_substitute(mapping)
        else:
            google_analytics = ""

        mapping = {"cache"             : cache,
                   "title"             : self.TITLE,
                   "game_name_nocolor" : remove_colors(config.game_name).upper(),
                   "additional_header" : self.create_additional_header(request, conn),
                   "allow_web_robots"      : allow_web_robots,
                   "google_analytics"  : google_analytics}
        if config.reload_web_pages:
            self.HEADER_TEMPLATE = string.Template(open("src/views/__header__.view").read())
        return self.HEADER_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_additional_header(self, request, conn):
        """
        Serve per aggiunge altre risorse come file css, javascript e altro.
        """
        return ""
    #- Fine Metodo -

    def create_menu(self, request, conn):
        """
        Crea il menù a sinistra nelle pagine normali del sito.
        """
        if config.reload_web_pages:
            self.MENU_TEMPLATE = string.Template(open("src/views/__menu__.view").read())
            self.WEB_MENU_LIST = map(string.strip, open("data/web_menu.list").readlines())

        page_url = str(request.URLPath()).rsplit("/", 1)[-1]
        if not page_url:
            page_url = "index.html"

        account_block = []
        if conn.account:
            account_block.append('''Benvenuto [white]%s[close]!<br>''' % conn.account.name)
            account_block.append('''<img src="menu/account.png" width="16" heigth="16" class="icon" /><a href="account.html"> Visita il tuo Account</a><br>''')
            account_block.append('''<img src="menu/descriptions.png" width="16" heigth="16" class="icon" /><a href="descriptions.html"> Crea le Descrizioni</a><br>''')
            account_block.append('''<img src="menu/alias.png" width="16" heigth="16" class="icon" /><a href="aliases.html"> Crea gli Alias</a><br><br>''')
            account_block.append('''<img src="menu/logout.png" width="16" heigth="16" class="icon" /><a href="logout.html"> Scollegati</a>''')
        else:
            account_block.append('''<br class="demi"><form id="login" method="POST" onsubmit="return false;" action="">''')
            account_block.append('''<table>''')
            account_block.append('''<tr><td align="left">Nome</td><td><input type="text" id="name" class="account_block_input" onkeypress="checkEnter();" /><td>''')
            account_block.append('''<tr><td align="left">Password</td><td><input type="password" id="password" class="account_block_input" onkeypress="checkEnter();" /><td>''')
            account_block.append('''</table>''')
            account_block.append('''<input type="submit" id="login" value="Collegati" onclick="fastLogin();" />''')
            account_block.append('''</form>''')

        counter = 0
        menu_items = []
        menu_items.append('''<ul class="menu">\n''')
        for line in self.WEB_MENU_LIST:
            if not line:
                continue
            if line[0] == "#":
                continue

            # (TD) spostare i link alla fine della lista del menù, così da
            # separare un numero finito di volte e supportare eventuali link
            # con ; all'interno
            pieces = map(string.strip, line.split("|"))
            if len(pieces) == 1:
                log.bug("C'è una linea errata nel file con le voci del menù web: %s" % line)
                continue

            if len(pieces) > 1 and pieces[1]:
                img = "menu/%s" % pieces[1]
            else:
                img = "blank.gif"
            img = '''<img style="border:0px solid black" class="icon" src="%s" width="16" height="16" /> ''' % img

            if len(pieces) > 3 and pieces[3]:
                if pieces[3] == "account" and (not conn or not conn.account):
                    continue
                elif pieces[3] == "!account" and conn and conn.account:
                    continue

            if len(pieces) > 4 and pieces[4]:
                trust_element = get_enum_element(pieces[4])
                if not trust_element or not conn or not conn.account or conn.account.trust < trust_element:
                    continue

            target_blank = ""
            if len(pieces) > 5 and pieces[5] == "blank":
                target_blank = " target='_blank'"

            if pieces[0] == "SEPARATOR":
                menu_items.append('''</ul><br>\n''')
                menu_items.append('''<ul class="menu">\n''')
                continue

            nowrap = ""
            if " " in pieces[2]:
                 nowrap = ''' style="white-space:nowrap;"'''

            menu_items.append('''<li onmouseover="$('ul.menu li a img:eq(%d)').fadeOut('fast').fadeIn('fast')"><a href="%s"%s%s>%s%s</a>\n''' % (
                counter, pieces[2], nowrap, target_blank, img, pieces[0]))
            counter += 1
        menu_items.append('''</ul>\n''')

        menu = "".join(menu_items)

        # (TD) qui per ${who_counter} viene effettuato un replace al posto di
        # un substitute da template, forse è meglio spostare il menù in un
        # altro view e gestirlo come tale?
        # (TD) in realtà bisognerebbe fare il who counter dinamico tramite ajax
        if "${who_counter}" in menu:
            who_counter = len(get_who_players())
            if who_counter == 0:
                who_span = ''' <span id="who_counter" style="font-size:smaller"></span>'''
            else:
                who_span = ''' <span id="who_counter" style="font-size:smaller">(%d)</span>''' % who_counter
            menu = menu.replace("${who_counter}", who_span)

        # Fa visualizzare l'eventuale conto alla rovescia dello shutdown
        seconds_to_shutdown = ""
        if engine.seconds_to_shutdown >= 0:
            javascript = '''<script>current_interval = setInterval(refreshSecondsToShut, 1000)</script>'''
            seconds_to_shutdown = '''Secondi allo Shutdown: <span name="seconds_to_shutdown">%d</span>%s<br><br>''' % (
                engine.seconds_to_shutdown, javascript)

        mapping = {"account_block"     : "".join(account_block),
                   "game_name_nocolor" : remove_colors(config.game_name).upper(),
                   "event_image"       : self.get_event_image(),
                   "menu"              : menu,
                   "seconds_to_shutdown"   : seconds_to_shutdown}
        return self.MENU_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def get_event_image(self):
        now = datetime.datetime.now()

        if engine.options.mode == "testing":
            return '''<img src="holidays/test.png" width="100" height="50" border="0" style="position:relative; left:-100px" />'''

        if now.month == 10 and now.day == 31:
            return '''<img src="holidays/halloween.png" width="49" height="46" border="0" style="position:relative; left:-338px" />'''
        elif now.month == 12 and now.day in (24, 25, 26):
            return '''<img src="holidays/natale.png" width="54" height="62" border="0" style="position:relative; left:-79px" />'''
        elif (now.month == 12 and now.day == 31) or (now.month == 1 and now.day == 1):
            return '''<img src="holidays/capodanno.png" width="48" height="48" border="0" style="position:relative; left:-75px" />'''
        elif (now.year == 2012 and now.month == 4 and now.day == 8
        or    now.year == 2013 and now.month == 3 and now.day == 31
        or    now.year == 2014 and now.month == 4 and now.day == 20
        or    now.year == 2015 and now.month == 4 and now.day == 5):  # (TD) trovare la formula generica della data pasquale
            return '''<img src="holidays/pasqua.png" width="" height="" border="0" style="position:relative; left:-63px" />'''
        elif now.month == 9 and now.day == 2:
            return '''<img src="holidays/tolkien.png" width="" height="" border="0" style="position:relative; left:-63px" />'''

        # (TD) fino a che siamo in beta si utilizzata l'immagine sotto
        #return ""
        return '''<img src="holidays/beta.png" width="100" height="50" border="0" style="position:relative; left:-100px" />'''
    #- Fine Metodo -

    def create_square(self, request, conn):
        """
        Crea il codice html per chiudere il menù di sinistra nelle pagine
        normali del sito.
        """
        if config.max_square_messages == 0:
            if config.reload_web_pages:
                self.NO_SHOW_SQUARE_TEMPLATE = string.Template(open("src/views/__no_show_square__.view").read())
            return self.NO_SHOW_SQUARE_TEMPLATE.safe_substitute({})

        # ---------------------------------------------------------------------

        if config.reload_web_pages:
            self.SQUARE_TEMPLATE = string.Template(open("src/views/__square__.view").read())

        # (TD) aggiungerne delle altre per migliorare graficamente il sito
        image_paths = ("images/bg.jpg", )
        mapping = {"image_path" : random.choice(image_paths)}
        return self.SQUARE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_footer(self, request, conn):
        """
        Ritorna il footer generico delle pagine html del Mud.
        """
        mapping = {"email"          : email_encoder(config.email),
                   "game_name"      : config.game_name,
                   "year"           : datetime.date.today().year,
                   "staff_name"     : config.staff_name,
                   "engine_name"    : config.engine_name,
                   "engine_version" : config.engine_version,
                   "server_name"    : config.server_name}
        if config.reload_web_pages:
            self.FOOTER_TEMPLATE = string.Template(open("src/views/__footer__.view").read())
        return self.FOOTER_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_bar(self, length=17):
        """
        Ritorna una barra stile celtico formata da varie immaginette in una tabella.
        """
        bar = ""
        bar += """<table border="0" cellpadding="0" cellspacing="0" align="center"><tr><td nowrap>"""
        bar += """<img src="graphics/horiz_left.gif" width="52" height="22">"""
        bar += """<img src="graphics/horiz_center.gif" width="44" height="22">""" * length
        bar += """<img src="graphics/horiz_right.gif" width="52" height="22">"""
        bar += """</td></tr></table>"""
        return bar
    #- Fine Metodo -


class EnumResource(WebResource):
    # Variabili che devono essere sovrascitte dalla classe figlia
    enum_name = ""
    h3_title  = ""
    first_th  = ""

    def render_GET(self, request, conn):
        page = ""
        page += """<h3 align="center">%s:</H3>""" % self.h3_title.upper()
        page += """<p><table>"""
        page += """<tr><th>%s:</th><th>Descrizione:</th></tr>""" % self.first_th.title()
        for element in sys.modules["src.enums.%s" % self.enum_name].elements:
            page += """<tr><td><a href="%s_%s.html">%s</a></td><td>%s</td></tr>""" % (
                self.enum_name.lower(), element.code[len(self.enum_name)+1 : ].lower(), element, element.description)
        page += """</table></p>"""
        return page
    #- Fine Metodo -


class EditResource(WebResource):
    """
    Pagina base per la gestione di tutte le pagine per la creazione o modifica
    dei dati di un database.
    """
    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True
    MINIMUM_TRUST_ON_GET          = TRUST.MASTER
    MINIMUM_TRUST_ON_POST         = TRUST.MASTER

    # (TT) qui forse c'è un problema con gli a capo \n aggiunti con la """\ e la formattazione con la """\
    tooltip_approved = """\
        Indica se il dato è stato approvato dagli Admin del Mud, ogni modifica
        del dato resetta l'approvazione positiva fino a che il dato non viene
        nuovamente controllato.<br>
        Se il dato non dovesse venire controllato potrebbe essere modificato
        (o in casi limite cancellato) dagli Admin contattando l'autore o
        lasciando un commento a riguardo."""
    tooltip_creator = """\
        Indica chi ha creato il dato, se non c'è nulla significa che il dato
        è stato generato automaticamente dal Mud"""
    tooltip_revisor = """\
        Indica chi è stato l'ultimo a modificare il dato, se non c'è nulla
        significa che il dato è stato generato automaticamente dal Mud"""
    tooltip_created_time = """\
        Indica la data di creazione del dato"""
    tooltip_revised_time = """\
        Indica la data di ultima modifica del dato da parte del revisore."""
    tooltip_comment = """\
        Il commento può essere una mini descrizione del dato ad uso e consumo
        degli Admin del Mud, per avvisare che il tal dato non è ancora
        terminato, il perché di alcune scelte nella creazione o qualsiasi
        cosa che possa apparire 'diversa dal solito' bisogna indicarla qui per
        evitare che il dato venga cancellato per incomprensione"""

    tooltip_key_value_alert = """\
        Un codice di dato è unico per ogni tipologia di dato, significa che se
        lo cambiate e salvate il dato non state modificando la chiave del
        vecchio dato, ma ne state creando uno nuovo. Se vi dimenticate di
        questo comportamento il dato con la chiave precedente rimane comunque
        nel database; se questo non è ciò che volete dovete andarlo a cercare
        e cancellarlo a mano.<br>
        D'altra parte cambiando la chiave ad un dato già esistente è il metodo
        più comodo e veloce per copiarlo.<br>
        L'importante è sapere quello che si sta facendo."""

    def get_page(self, method, request, conn):
        """
        Ricava e controlla il nome del database poi passa al metodo corretto
        ritornando la pagina html.
        """
        # Ricava e controlla il nome del database  # (TT) ma se si scrive l'indirizzo in maiuscolo? servirà anche un metodo lower?
        db_name = request.path.replace("/build_", "").replace(".html", "")
        if not db_name in database:
            error_message = "Database %s inesistente, non si può creare o accedere al dato" % db_name
            log.bug(error_message)
            return error_message

        # Ricava il dato, se non esiste ne crea uno nuovo
        data = None
        if "key" in request.args and request.args["key"][0] in database[db_name]:
            data = database[db_name][request.args["key"][0]]
        if not data:
            # data_class non è un metodo, è il riferimento ad un tipo di classe,
            # in pratica se non esiste un dato lo crea inizializzando la classe
            data = self.data_class()

        # Ritorna la pagina con il metodo adatto: GET o POST
        return method(request, conn, db_name, data)
    #- Fine Metodo -

    def create_menu(self, request, conn):
        return ""
    #- Fine Metodo -

    def create_square(self, request, conn):
        return ""
    #- Fine Metodo -

    def render_GET(self, request, conn, db_name, data):
        self.create_page(request, conn, db_name, data)
    #- Fine Metodo -

    def render_POST(self, request, conn, db_name, data):
        # Ricava la chiave del dato
        key = getattr(data, self.data_key)

        # Ad ogni bottone schiacciato nel post c'è un'azione precisa
        if request.method == "POST":
            if "previous" in request.args:
                self.redirect_to_previous(request, db_name, data, key)
                return ""
            elif "approve" in request.args:
                if database[db_name][key].approved:
                    database[db_name][key].approved = False
                else:
                    database[db_name][key].approved = True
                request.redirect("edit_%s.html?key=%s" % (db_name[0 : -1], key))
                request.finish()
                return server.NOT_DONE_YET
            elif "delete" in request.args:
                del database[db_name][key]
                log.delete("Dato %s del database %s cancellato da %s il %s" % (
                    key, db_name, conn.account.name, datetime.now()))
                self.redirect_to_next(request, db_name, data, key)
                return ""
            elif "next" in request.args:
                self.redirect_to_next(request, db_name, data, key)
                return ""
            elif "save" in request.args and data.get_error_message() == "":
                if "comment" in request.args:
                    data.comment = request.args["comment"][0]
                self.autoset_form_args(request, conn, db_name, data, key)
                database[db_name][key] = data

        # Dopo il posting ricrea la pagina
        self.create_page(request, conn, db_name, data, key)
    #- Fine Metodo -

    def autoset_form_args(self, request, conn, db_name, data, key):
        """
        Salva automaticamente tutti i valori del form nel dato.
        """
        dirty = False

        for row in self.form_rows:
            if row.attr in request.args:
                attribute = getattr(data, row.attr)
                value = None

                if row.set_field_fun == set_checked_flags:
                    set_checked_flags(request, row.attr, value)
                elif isinstance(attribute, basestring):
                    value = request.args[row.attr][0]
                    if row.string_action:
                        # (TD) come diamine si chiamava un metodo in maniera pulita? forse con globals o locals
                        pass
                elif type(attribute) in (int, long):
                    value = int(request.args[row.attr][0])
                elif type(attribute) == list:
                    value = long(request.args[row.attr][0])
                elif type(attribute) == dict:
                    pass
                elif type(attribute) == Element:
                    value = Element(request.args[row.attr][0])
                else:
                    if row.set_field_fun:
                        log.bug("Tipo di funzione di impostazione degli argomenti di una request inesistente: %s" % row.set_field_fun)
                    else:
                        log.bug("Tipo di dato per il posting automatico non supportato: %s" % type(attribute))
                    continue

                if value != attribute:
                    print("autoset_form_args -> row.attr: %s" % row.attr)  # (TT) devo vedere se funziona in generale, ed in particolare per le liste e i dizionari
                    setattr(data, row.attr, value)
                    dirty = True
        # Se il dato è stato modificato in qualche maniera aggiorna i dati di building
        if dirty:
            data = self.refresh_build_data(request, conn, db_name, data, key)  # (TT) si trovava in un altro punto del codice e l'ho spostato senza controllare
    #- Fine Metodo -

    def create_page(self, request, conn, db_name, data, key):
        page += """<h3>Crea o modifica un dato per il database %s:</h3>\n""" % db_name
        # Inizializza le righe del form con il navigatore di dati in testa
        form_rows = self.create_data_navigator(request, conn, db_name, data)
        # Aggiunge le prime 5 righe uguali per tutti i form di modifica dei dati
        form_rows.append(FormRow("Approvato", "approved", readonly=True))
        form_rows.append(FormRow("Creatori", "creators", readonly=True))
        form_rows.append(FormRow("Revisori", "revisors", readonly=True))
        form_rows.append(FormRow("Data di creazione", "created_time", read_only=True))
        form_rows.append(FormRow("Data di revisione", "revised_time", read_only=True))
        form_rows.append(FormRow("Commento", "comment", cols=42, rows=6))
        form_rows.append(FormRow("%s Il campo subito qui sotto è quello KEY, la chiave primaria, cioè il valore identificativo del dato:" % (
            create_tooltip(conn, self.tooltip_key_value_alert))))
        # Aggiunge le righe del form di modifica vero e proprio della pagina
        form_rows += self.form_rows
        # Aggiunge il bottone di submit:
        form_rows += FormButton("""<input type="submit" value="Controlla e Salva" onclick="document.getElementById('form_data').submit;" />""", attr="")
        # Ed infine aggiunge il il navigatore di dati in coda
        form_rows = self.create_data_navigator(request, conn, db_name, data)
        # Crea finalmente questo benedetto form
        form_action = "edit_%s.html" % db_name[0 : -1]
        if key:
            form_action += '?key="%s"' % key
        page += self.create_form(form_rows, "form_data", form_action, data, key)
        return page
    #- Fine Metodo -

    def create_form(self, form_rows, form_id, form_action, data, key, insert_value=True):
        """
        Passate le informazioni per la creazione di un form ne ritorna il codice
        html relativo.
        Come si può notare tutte le righe di un form devono avere la label, il
        resto degli attributi sono facoltativi, solo che per visualizzare
        message deve esistere anche field, non ci sono controlli specifici
        perché un form viene visualizzato a video e il programmatore si adegua
        di conseguenza.
        """
        page = """<form id="%s" name="%s" action="%s" method="post"><fieldset><table border="1">""" % (form_id, form_id, form_action)
        tabindex = 1
        for row in form_rows:
            row.label, tabindex = _add_tabindex(row.label, "<button ", tabindex)
            if not row.attr:
                page += """<tr><td colspan="%d">%s</td>""" % 3 if not row.message else 2, row.label
            else:
                # Se esiste row.field deve anche esistere il relativo attributo del dato
                if not hasattr(data, row.attr):
                    log.bug("Attributo %s nel dato %s inesistente" % (row.attr, repr(data)))
                # Inserisce progressivamente gli index dei vari input del form
                row.field, tabindex = _add_tabindex(row.field, "<input ", tabindex)
                row.field, tabindex = _add_tabindex(row.field, "<select ", tabindex)
                row.field, tabindex = _add_tabindex(row.field, "<textarea ", tabindex)
                # Inserisce la label evitando i due punti per gli <input />
                if not row.label.startswith("<input "):
                    colon = ":"
                else:
                    colon = ""
                # (TD) dovrei aggiunger l'attributi del tag label 'for' per
                # indicare a quale id di input si riferisce la label
                page += """<tr><td><label>%s</label>%s </td>""" % (row.label, colon)
                # Inserisce il field elaborato tramite tutte le informazione della FormRow
                page += """<td>%s</td>""" % row.create_field(data, insert_value)
                # Se esiste message allora è un messaggio di errore e lo colora in rosso
                if row.message:
                    page += """<td> <span style="color:red">%s</span></td>""" % row.message
                else:
                    # Altrimenti prova a pescarlo tra le variabili tooltip della
                    # pagina-risorsa creando un tooltip, difatti in messaggio sarà
                    # un aiuto
                    if hasattr(self, "tooltip_%s" % self.attr):
                        page += create_tooltip(getattr(self, "tooltip_%s" % self.attr))
            page += """</tr>"""
        page += """</table></fieldset></form>"""
        return page
    #- Fine Metodo -

    def create_data_navigator(self, request, conn, db_name, data):
        form_rows = []
        label_text  = """<table width="50%" align="center"><tr>"""
        label_text += """<td width="10%"><button name="previous" type="submit">&lt;&lt;</button></td>"""
        label_text += """<td width="10%"align="center"><button name="approve" type="submit">Dis/Approvalo</button><br>%s</td>""" % create_tooltip(conn, "Se ne avete i poteri potete approvare o disapprovare il dato, perchè magari non è gdr, perchè è troppo potente, per varie ragioni, meglio inserire un commento per chiarire le motivazioni.")
        label_text += """<td width="10%"align="center"><button name="delete" type="submit" onClick='comfirm("Vuoi veramente cancellare per sempre questo dato?");'>Distruggilo</button><br>%s</td>""" % create_tooltip(conn, "Una volta che un dato viene distrutto è per sempre, quindi pensateci bene prima di farlo, al limite se ne avete i poteri segnalatelo come non approvato e/o inserite un commento sulla dubbia utilità del dato.")  # (bb) pare che l'onClick non funzioni con gli input ma solo con i link.. devo pensare ad una soluzione
        label_text += """<td width="10%"><button name="next" type="submit">&gt;&gt;</button></td>"""
        label_text += """</tr></table>"""
        row1 = FormLabel(label_text, attr="")
        form_rows.append(row1)
        if request.method == "POST":
            err_msg = data.get_error_message()
            if err_msg == "":
                row2 = FormLabel("""<span style="color:green">Dato creato correttamente</span><br><br>""", attr="")
            else:
                row2 = FormLabel("""<span style="color:red">ERRORE: %s</span><br><br>""", attr="", message=err_msg)
            form_rows.append(row2)
        return form_rows
    #- Fine Metodo -

    def refresh_build_data(self, request, conn, db_name, data, key):
        """
        Aggiorna gli attributi riguardanti la creazione o la modifica del dato
        passato che ha come antenato una classe Data()
        """
        # Non lo aggiorna nel caso in cui non si stia salvando un dato.
        if request.method != "POST" or "save" not in request.args:
            return data
        # Non lo aggiorna nel caso in cui il dato non sia stato modificato.
        if key in database[db_name] and database[db_name][key] == data:
            return data
        # In tutti gli altri casi lo aggiorna
        if not data.creators:
            data.creators     = conn.account.name
            data.created_time = datetime.now()
        else:
            data.revisors     = conn.account.name
            data.revised_time = datetime.now()
        if conn.account.trust >= TRUST.IMPLEMENTOR:
            data.approved = True
        else:
            data.approved = False
        return data
    #- Fine Metodo -

    def redirect_to_previous(self, request, db_name, data, key, previous=True):
        # Recupera l'indice della posizione attuale nella lista ordinata dei dati
        datas_sorted = sort_datas(database[db_name], "key")
        index = 0
        for num, value in enumerate(datas_sorted):
            if value is database[db_name][key]:
                print("FINDED")
                index = num
                break
        print("index = ", index)
        # Recupera il dato da visualizzare prossimo o precedente a seconda
        if previous:
            if index - 1 >= 0:
                print("PREV A")  # (TT)
                data_to_show = datas_sorted[index - 1][1]
            else:
                print("PREV B")  # (TT)
                data_to_show = datas_sorted[-1][1]
        else:
            if index + 1 < len(datas_sorted):  # (TT) da provare a vedere che non salti qualche dato verso la fine
                print("NEXT A")  # (TT)
                data_to_show = datas_sorted[index + 1][1]
            else:
                print("NEXT B")  # (TT)
                data_to_show = datas_sorted[0][1]
        # Recupera il nome dell'attributo chiave del dato
        for attr_name in data.__dict__:
            if key == data[attr_name]:  # (??) perchè non mi va'?
                break
        # Recupera il dato da visualizzare e redirecta con l'attributo chiave trovato
        request.redirect("edit_%s.html?key=%s" % (db_name[0 : -1], getattr(data_to_show, attr_name)))
        request.finish()
        return server.NOT_DONE_YET
    #- Fine Metodo -

    def redirect_to_next(self, request, db_name, data, key):
        self.redirect_to_previous(request, db_name, data, key, previous=False)
    #- Fine Metodo -


# (TD) Da rimuovere una volta finito tutto riguardo alla gestione semi-automatica dei form
class FormRow(object):
    """
    Gestisce in maniera friendly le informazioni di una riga di form
    Tutte le righe vengono inserite in una lista che poi viene trasformata in
    codice html come tabella dalle create_form().
    """
    def __init__(self, label="", field="", message=""):
        self.label   = label
        self.field   = field
        self.message = message
    #- Fine Inizializzazione -

    def __repr__(self):
        return "FormRow istance: label=%s field=%s message=%s" % (self.label, self.field, self.message)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def create_tooltip(conn, content, symbol="(?)"):
    """
    Ritorna del codice html per creare una tooltip.
    """
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not content:
        log.bug("content non è un parametro valido: %r" % content)
        return ""

    if not symbol:
        log.bug("symbol non è un parametro valido: %r" % symbol)
        return ""

    # -------------------------------------------------------------------------

    tooltip_id = str(random.random())[2 : ]

    content = content.replace('"', "'")

    # Codice per la tooltip del pacchetto tools
    tooltip_html = '''<a href="#" id="tooltip_%s" this.style.cursor="help" onclick="alert%s(this);" title="%s">%s</a>''' % (
        tooltip_id, tooltip_id, content, symbol)
    tooltip_html += '''<script type="text/javascript">'''
    tooltip_html += '''$("#tooltip_%s").tooltip({position:"top right"});''' % tooltip_id
    tooltip_html += '''function alert%s() {''' % tooltip_id
    tooltip_html += '''alert("%s");''' % remove_colors(content.replace("\n", "\\n"))
    tooltip_html += '''}'''
    tooltip_html += '''</script>'''

    return tooltip_html
#- Fine Funzione -


def create_icon(icon_src, add_span=True):
    if not icon_src:
        icon_src = "blank.gif"

    span = ""
    if add_span:
        span = '''<span style="letter-spacing:-2px"> </span>'''

    return '''<img src="%s" width="16" height="16" class="icon" />%s''' % (icon_src, span)
#- Fine Funzione -


def send_audio(conn, audio_file, loop=True, auto_start=True):
    """
    Invia il codice html necessario a far sentire un mid o un wav.
    """
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not audio_file:
        log.bug("audio_file non è un parametro valido: %r" % audio_file)
        return ""

    # -------------------------------------------------------------------------

    if not conn.account:
        return ""

    # (TD) spostare il check nelle varie relative etichette
    if not audio_file.islower():
        log.bug("Il nome del file %s non è tutto minuscolo, controllare anche nella cartella apposita" % audio_file)
        return ""

    #loop_attr = ""
    #if loop:
    #    loop_attr = ''' loop="loop"'''

    #if audio_file.endswith(".ogg"):
    #    folder_name = "musics"
    #else:
    #    folder_name = "sounds"

    #return '''<audio src="%s/%s" autoplay="autoplay"%s></audio>''' % (folder_name, audio_file, loop_attr)

    # -------------------------------------------------------------------------
    # Vecchio codice per i browser html4, che andrò ad abbandonare:

    loop_attr = ""
    if audio_file.endswith(".mid"):
        folder = "musics"
        audio_type = "audio/midi"
        flag = OPTION.MUSIC
    else:
        folder = "sounds"
        audio_type = "audio/wav"
        flag = OPTION.SOUND

    if flag not in conn.account.options:
        return ""

    browser = conn.get_browser()
    if browser == "IE_6":  # (TT) e forse anche ie 7.0
        if loop:
            loop_attr = " loop=infinite"
        result = '''<bgsound src="%s/%s"%s>''' % (folder, audio_file, loop_attr)
    elif browser == "OPERA_9":  # (TT) Forse anche tra firefox 3.0 e firefox 3.5
        # Temo che il tag object non supporti il loop
        result = '''<object data="%s/%s" type="audio/x-ms-wma" autostart="%s" width="0" height="0"></object>''' % (
            folder, audio_file, str(auto_start).lower())
    else:
        if loop:
            loop_attr = " loop='true'"
        result = '''<embed src="%s/%s" width="0" height="0" hidden="true" autostart="%s" type="%s"%s>''' % (
            folder, audio_file, str(auto_start).lower(), audio_type, loop_attr)

    return result
#- Fine Funzione -


# (TD) inutilizzata per ora
#def colorify_value(value):
#    if type(value) == bool:
#        if value:
#            return "[green]True[close]"
#        else:
#            return "[red]False[close]"
#    elif value is None:
#        return "[darkcyan]None[close]"
#    else:
#        return html_escape("%r" % value)
##- Fine Funzione -


#- FUNZIONI CHE RIGUARDANO I FORM ----------------------------------------------

# (TD) da togliere dopo aver inserito dappertutto il nuovo sistema di FormRow
# (TD) No, il vecchio e nuovo sistema dei form lo abbandonerò a favore delle view
def create_form_row(form):
    """
    Crea una FormRow e la aggiunge alla lista di righe di form passata
    dopodiché la ritorna.
    """
    row = FormRow()
    form.append(row)
    return row
#- Fine Funzione -


def create_form(form_rows, form_id, action, legend_text="", border=0, show_label=True):
    """
    Passate le informazioni per la creazione di un form ne ritorna il codice
    html relativo.
    Come si può notare tutte le righe di un form devono avere la label, il resto
    degli attributi sono facoltativi, ma per poter far visualizzare message deve
    esistere anche field.
    """
    html = ['''<form id="%s" name="%s" action="%s" method="post"><fieldset>''' % (form_id, form_id, action)]
    if legend_text:
        html.append('''<legend>&nbsp;%s:&nbsp;</legend>''' % legend_text)
    if border:
        html.append('''<table border="1">''')
    else:
        html.append('''<table>''')
    tabindex = 1
    for row in form_rows[ : -1]:
        row.label, tabindex = _add_tabindex(row.label, "<button ", tabindex)
        if not row.field:
            html.append('''<tr><td colspan="3">%s</td>''' % row.label)
        else:
            row.field, tabindex = _add_tabindex(row.field, "<input ", tabindex)
            row.field, tabindex = _add_tabindex(row.field, "<select ", tabindex)
            row.field, tabindex = _add_tabindex(row.field, "<textarea ", tabindex)
            html.append('''<tr>''')
            if show_label:
                if row.label.startswith("<input "):
                    # Evita i due punti per gli input
                    html.append('''<td>%s </td>''' % row.label)
                else:
                    html.append('''<td>%s: </td>''' % row.label)
            html.append('''<td>%s</td>''' % row.field)
            if row.message:
                # Se il messaggio passato è un tooltip, evita di colorarlo in rosso
                if row.message.startswith("""<a class="tooltip" href="#">(?)<span>"""):
                    html.append('''<td> %s</td>''' % row.message)
                else:
                    html.append('''<td> <span style="color:red">%s</span></td>''' % row.message)
        html.append('''</tr>''')
    html.append('''</table></fieldset>''')
    html.append('''%s</form>''' % form_rows[-1].label)

    return "".join(html)
#- Fine Funzione -


def _add_tabindex(text, tag, tabindex):
    """
    Imposta correttamente il tabindex tra gli elementi del form.
    """
    position = 0
    while 1:
        position = text.lower().find(tag, position)
        if position == -1:
            break
        position += len(tag)
        text = "%s tabindex='%d' %s" % (text[ : position - 1], tabindex, text[position : ])
        tabindex += 1

    # Finito il ciclo ritorna il testo modificato e la tabindex incrementata
    return text, tabindex
#- Fine Funzione -


#- FUNZIONI CHE RIGUARDANO LE ENUMERAZIONI -------------------------------------

# (TD) no, questa cosa bisogna farla lato client e non lato server
def create_demi_line(conn):
    """
    Crea una linea con mezza altezza in maniera cross browser in maniera tale
    che venga inviato il minimo di caratteri.
    """
    # È normale per i mob e gli item che non hanno una connessione per giocare
    if not conn:
        return '''<br class="demi">'''

    # Controlla se sia stata passata un'istanza di Connection
    if conn.__class__.__name__ != "Connection":
        if conn.IS_PLAYER:
            conn = conn.get_conn()
            if not conn:
                return '''<br class="demi">'''
        else:
            return '''<br class="demi">'''

    # Con chrome bisogna creare uno span vuoto creando così una linea con
    # l'altezza dimezzata
    browser_code = conn.get_browser()
    if browser_code.startswith("CHROME"):
        return '''<span class="demi"> </span><br>'''
    else:
        return '''<br class="demi">'''
#- Fine Funzione -


def create_checklist_of_elements(checklist_name, element_to_check, attr="", elements=None):
    """
    Ritorna del codice html con la lista dei possibili elementi selezionabili
    con un input di tipo radio.
    L'argomento attr indica che deve stanpare, accanto ad ogni elemento, il
    valore dell'attributo dell'enumerazione passata; il tutto viene inserito
    in una tabella html per una maggiore leggibilità.
    """
    html = []

    if attr:
        html.append('''<table>''')

    if not elements:
        elements = element_to_check.enum.elements

    for element in elements:
        checked = ""
        if element_to_check and element.code == element_to_check.code:
            checked = ''' checked="checked"'''
        if attr:
            html.append('''<tr><td nowrap><input type="radio" name="%s" value="%s"%s /> %s</td><td>%s</td></tr>''' % (
                checklist_name, element.code, checked, element, getattr(element, attr)))
        else:
            html.append('''<input type="radio" name="%s" value="%s"%s /> %s<br>''' % (
                checklist_name, element.code, checked, element))

    if attr:
        html.append('''</table>''')

    return "".join(html)
#- Fine Funzione -


def create_checklist_of_flags(checklist_name, flags, attr="", elements=None, use_icons=False, avoid_elements=None):
    """
    Ritorna del codice html con la lista di elementi di una enumerazione
    checkati se contenuti nella flag passata.
    L'attributo attr funzione come per la create_checklist_of_elements
    """
    if not elements:
        elements = flags.enum.elements

    if not avoid_elements:
        avoid_elements = []

    html = []
    if attr:
        html.append('''<table>''')

    for n, element in enumerate(elements):
        if element in avoid_elements:
            continue
        checked = ""
        if element in flags:
            checked = ''' checked="checked"'''
        icon = ""
        onclick = ""
        if use_icons:
            icon = '''<img id="%d" src="%s" width="16px" height="16px" /> ''' % (n, element.icon)
            onclick = ''' onclick="$('#%d').fadeOut('fast').fadeIn('fast')"''' % n
        if attr:
            html.append('''<tr><td nowrap>%s<input type="checkbox" name="%s" value="%s"%s%s /> %s</td><td>%s</td></tr>''' % (
                icon, checklist_name, element.code, checked, onclick, element, getattr(element, attr)))
        else:
            html.append('''%s<input type="checkbox" name="%s" value="%s"%s%s /> %s<br>''' % (
                icon, checklist_name, element.code, checked, onclick, element))

    if attr:
        html.append('''</table>''')

    return "".join(html)
#- Fine Funzione -


def create_listdrop_of_elements(select_name, element_to_select, elements=None):
    """
    Ritorna del codice html con la lista dei possibili elementi
    selezionabili con una select.
    """
    if not elements:
        elements = element_to_select.enum.elements

    html = ['''<select name="%s">''' % select_name]
    for element in elements:
        selected = ""
        if element_to_select == element:
            selected = ''' selected="selected"'''
        html.append('''<option value="%s"%s>%s</option>''' % (element.code, selected, element))
    html.append('''</select>''')

    return "".join(html)
#- Fine Funzione -


def create_listdrop_of_colors(select_name, color_to_select, color_elements=None):
    """
    Ritorna una lista a menù di discesa contenente tutti i colori da
    poter scegliere.
    """
    if not color_elements:
        color_elements = COLOR.elements

    style = ""
    script = ""
    if color_to_select != COLOR.NONE:
        style = ''' style="%s"''' % color_to_select.get_bg_style()
    else:
        script = '''<script>changeSelectColor(document.getElementsByName("%s")[0])</script>''' % (
            select_name)

    html = ['''<select name="%s"%s onkeyup="changeSelectColor(this);" onchange="changeSelectColor(this);">''' % (
        select_name, style)]
    for color in color_elements:
        if color == COLOR.NONE or color.alternative:
            continue
        selected = ""
        if color_to_select == color:
            selected = ''' selected="selected"'''
        html.append('''<option style="%s" value="%s"%s>%s</option>''' % (
            color.get_bg_style(), color.code, selected, color))
    html.append('''</select>%s''' % script)

    return "".join(html)
#- Fine Funzione -


def create_listdrop_of_datas(select_name, list_of_datas, data_to_select=""):
    """
    Crea una listdrop con tutti i dati passati e il dato da selezionare.
    data_to_select deve essere una chiave formato stringa, di solito il codice
    dei valori che subclassano Data è sempre come stringa quindi non dovrebbero
    esserci problemi.
    """
    html = ['''<select name="%s">''' % select_name]
    for key in list_of_datas:
        selected = ""
        if data_to_select and data_to_select == key:
            selected = ''' selected="selected"'''
        html.append('''<option value="%s"%s>%s</option>''' % (key, selected, key))
    html.append('''</select>''')

    return "".join(html)
#- Fine Funzione -


def set_checked_flags(request, checklist_name, flags):
    """
    Imposta alla flag passata tutte le scelte postate da una lista di check
    creato solitamente tramite la create_checklist_of_flags()
    """
    for element in flags.enum.elements:
        if checklist_name in request.args and element.code in request.args[checklist_name]:
            flags += element.code
        else:
            flags -= element.code
#- Fine Funzione -
