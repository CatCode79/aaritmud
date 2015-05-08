# -*- coding: utf-8 -*-

"""
Controller della pagina web per la gestione delle opzioni di config.
"""

#= IMPORT ======================================================================

import copy
import json
import string

from src.config       import config, CONFIG_OPTIONS, SUPPORTED_COMPRESSIONS
from src.element      import Flags
from src.enums        import LOG, TRUST
from src.log          import log
from src.utility      import square_bracket_to_html_entities
from src.web_resource import WebResource, create_tooltip


#= CLASSI ======================================================================

class ConfigOptionsPage(WebResource):
    TITLE = "Config Options"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/config_options.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        disabled = ""
        if conn.account.trust < TRUST.IMPLEMENTOR:
            disabled = ''' disabled="disabled"'''

        mapping = {"config_filename"     : config.filename,
                   "site_section"        : self.create_config_options("SITE", disabled, conn),
                   "server_section"      : self.create_config_options("SERVER", disabled, conn),
                   "mail_section"        : self.create_config_options("MAIL", disabled, conn),
                   "game_section"        : self.create_config_options("GAME", disabled, conn),
                   "time_section"        : self.create_config_options("TIME", disabled, conn),
                   "log_section"         : self.create_config_options("LOG", disabled, conn),
                   "development_section" : self.create_config_options("DEVELOPMENT", disabled, conn),
                   "disabled"            : disabled}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_config_options(self, section_name, disabled, conn):
        rows = ['''<table>''']

        for option in CONFIG_OPTIONS:
            if option.section != section_name:
                continue

            value = getattr(config, option.name)
            if not option.online:
                input = str(value)
            elif hasattr(self, "create_" + option.name):
                input = getattr(self, "create_" + option.name)(option, value, disabled)
            elif option.getter == "get":
                value = str(value)
                if value:
                    value = square_bracket_to_html_entities(value)
                size = ""
                if len(value) > 16:
                    size = ''' size="64"'''
                input = '''<input type="text" id="%s" name="%s" value="%s"%s%s />''' % (option.name, option.name, value, size, disabled)
            elif option.getter in ("getint", "getfloat"):
                input = '''<input type="number" id="%s" name="%s" value="%d"%s />''' % (option.name, option.name, value, disabled)
            elif option.getter == "getboolean":
                checked = ""
                if value:
                   checked = ''' checked="checked"'''
                input = '''<input type="checkbox" id="%s" name="%s"%s%s />''' % (option.name, option.name, checked, disabled)
            elif option.getter == "getemail":
                input = '''<input type="email" id="%s" name="%s" value="%s"%s />''' % (option.name, option.name, value, disabled)
            else:
                log.bug("getter non definito per l'opzione %s: %s" % (option.name, option.getter))
                continue

            tooltip = create_tooltip(conn, option.minihelp)
            rows.append('''<tr><td>%s %s:</td><td>%s</td><td id="%s_error" style="color:red"></td></tr>''' % (option.name, tooltip, input, option.name))

        rows.append('''</table>''')
        return "".join(rows)
    #- Fine Metodo -

    def create_compression_mode(self, option, value, disabled):
        html = []

        html.append('''<select id="%s" name="%s"%s>''' % (option.name, option.name, disabled))
        for mode in SUPPORTED_COMPRESSIONS:
            selected = ""
            if mode == value:
                selected = ''' selected="selected"'''
            html.append('''<option value="%s"%s>%s</option>''' % (mode, selected, mode))
        html.append('''</select>''')

        return "".join(html)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if conn.account.trust == TRUST.MASTER:
            message = ["Non è possibile modificare le opzioni di config da parte di Amministratori con trust %s" % conn.account.trust]
            return json.dumps(message, separators=(',',':'))

        write_config = False
        if "write_config" in request.args and request.args["write_config"][0] == "1":
            write_config = True

        # Si copia gli attributi del config attuale, cosicché se quelli nuovi
        # sono stati impostati erroneamente dal client verranno sostituiti
        # da questi qui
        original_config_attrs = copy.copy(config.__dict__)

        # Impostata tutte le opzioni di config come le ha scelte il client
        for option in CONFIG_OPTIONS:
            if option.getter in ("get", "getemail"):
                if option.name not in request.args:
                    log.bug("opzione %s non inviata al server." % option.name)
                    continue
                setattr(config, option.name, request.args[option.name][0])
            elif option.getter in ("getint", "getfloat"):
                if option.name not in request.args:
                    log.bug("opzione %s non inviata al server." % option.name)
                    continue
                try:
                    if option.getter == "getint":
                        value = int(request.args[option.name][0])
                    else:
                        value = float(request.args[option.name][0])
                except ValueError:
                    log.bug("opzione %s con un valore non numerico: %s" % (option.name, request.args[option.name]))
                    continue
                setattr(config, option.name, value)
            elif option.getter == "getboolean":
                if option.name in request.args:
                    setattr(config, option.name, True)
                else:
                    setattr(config, option.name, False)
            else:
                log.bug("getter non definito per l'opzione %s: %s" % (option.name, option.getter))
                continue

        # Finalizza il file di config e se vi sono degli errori li invia
        #ritornando allo stadio iniziale
        config.finalize()
        errors = list(config.iter_all_error_messages())
        if errors:
            config.__dict__ = original_config_attrs
            return json.dumps(errors, separators=(',',':'))

        if write_config:
            config.save()
            log.save("Salvataggio del file di configurazione %s effettuato dall'apposita pagina web." % config.filename)

        return json.dumps("[]", separators=(',',':'))
    #- Fine Metodo -
