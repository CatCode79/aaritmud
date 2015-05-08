# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di account.
"""


#= IMPORT ======================================================================

import operator

from src.account      import get_error_message_password, get_error_message_email, MAX_LEN_EMAIL
from src.color        import remove_colors
from src.config       import config
from src.element      import Flags
from src.enums        import OPTION, SEX
from src.web_resource import (WebResource, create_form_row, create_form, create_tooltip,
                              create_checklist_of_flags, set_checked_flags)


#= CLASSI ======================================================================

class AccountPage(WebResource):
    """
    Pagina web per la gestione dell'account con la lista dei personaggi.
    """
    TITLE = "Account"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        err_msg_password      = ""
        err_msg_new_password  = ""
        err_msg_new_password2 = ""
        err_msg_new_email     = ""
        # Se trova options negli argomenti della richiesta è stato cliccato
        # il bottone del form delle opzioni, altrimenti quello della modifica
        #dei dati dell'account
        if "password" in request.args:
            password      = request.args["password"][0]
            new_password  = request.args["new_password"][0]
            new_password2 = request.args["new_password2"][0]
            new_email     = request.args["new_email"][0].lower()
            # Controlla la validità degli argomenti inseriti nel form
            if (new_password or new_email) and password != conn.account.password:
                err_msg_password = "Non coincide con la password corrente, reinseriscila"
            if new_password:
                err_msg_new_password = get_error_message_password(new_password)
            if new_password != new_password2:
                err_msg_new_password2 = "Le nuove password non coincidono, reinseriscile"
                new_password  = ""
                new_password2 = ""
            # Non controlla nel qual caso si è inserito lo stesso indirizzo mail che
            # si aveva prima altrimenti indica errore di doppia mail
            if new_email and new_email != conn.account.email:
                err_msg_new_email = get_error_message_email(new_email)
            # Se tutto è corretto, e sono state inserite nuova pass o email, allora salva
            if (not err_msg_password and not err_msg_new_password
            and not err_msg_new_password2 and not err_msg_new_email):
                if new_password:
                    conn.account.password = new_password
                if new_email:
                    conn.account.email = new_email
            return self.create_page(request, conn, password, new_password, new_password2, new_email,
                err_msg_password, err_msg_new_password, err_msg_new_password2, err_msg_new_email)
        elif "options" in request.args:
            set_checked_flags(request, "options", conn.account.options)
            return self.create_page(request, conn)
        else:
            # Se vengono decheckate tutte le checkbox in request.args non
            # ci sarà nessuna "options", quindi qui resetta le options
            conn.account.options = Flags(OPTION.NONE)
            return self.create_page(request, conn)
    #- Fine Metodo -

    def create_page(self, request, conn, password="", new_password="", new_password2="", new_email="",
            err_msg_password="", err_msg_new_password="", err_msg_new_password2="", err_msg_new_email=""):
        # Prepara il form delle opzioni
        form_options = []
        row = create_form_row(form_options)
        row.label = "Opzioni dell'account"
        row.field = create_checklist_of_flags("options", conn.account.options, "description", use_icons=True, avoid_elements=[OPTION.SOUND, OPTION.MUSIC, OPTION.LOOP])
        row = create_form_row(form_options)
        row.label = '''<input type="submit" value="Salva le Opzioni" onclick="document.getElementById('form_options').submit();" />'''
        if request.method == "POST" and "options" in request.args:
            row.label += '''<span style="color:green"> Opzioni salvate.</span>'''

        # Prepara il form degli account
        form_account = []
        row = create_form_row(form_account)
        row.label = '''Password attuale %s''' % create_tooltip(conn, "Devi digitare la tua password corrente se vuoi cambiarla con una nuova o con un nuovo indirizzo mail. In questa maniera i tuoi dati privati non vengono cambiati da chicchessia nel caso tu giocassi in luoghi pubblici.")
        row.field = '''<input type="password" name="password" maxlength="%s" value="%s" style="width:11em;" />''' % (config.max_len_password, password)
        row = err_msg_password
        row = create_form_row(form_account)
        row.label = '''Nuova password'''
        row.field = '''<input type="password" name="new_password" maxlength="%s" value="%s" style="width:11em;" />''' % (config.max_len_password, new_password)
        if err_msg_new_password != "":
            row.message = err_msg_new_password
        elif err_msg_new_password2 != "":
            row.message = err_msg_new_password2
        row = create_form_row(form_account)
        row.label = '''Conferma la nuova password'''
        row.field = '''<input type="password" name="new_password2" maxlength="%s" value="%s" style="width:11em;" />''' % (config.max_len_password, new_password2)
        row = create_form_row(form_account)
        row.label   = '''Nuovo indirizzo mail %s''' % create_tooltip(conn, "Facoltativo.")
        row.field   = '''<input type="text" name="new_email" maxlength="%s" value="%s" style="width:11em;" />''' % (MAX_LEN_EMAIL, new_email)
        row.message = err_msg_new_email
        row = create_form_row(form_account)
        row.label = '''<input type="submit" value="Salva i Dati" onclick="document.getElementById('form_account').submit();" />'''

        if (request.method == "POST" and "options" not in request.args
        and err_msg_password == "" and err_msg_new_password == ""
        and err_msg_new_password2 == "" and err_msg_new_email == ""
        and password == "" and new_password == ""
        and new_password2 == "" and new_email == ""):
            row.label += '''<span style="color:green"> Account salvato.</span>'''

        # Crea la pagina html
        page  = ""

        page += create_form(form_options, "form_options", "account.html", "Modifica le opzioni del tuo account", show_label=False)
        page += '''<br>'''

        page += create_form(form_account, "form_account", "account.html", "Modifica i dati del tuo account")

        return page
    #- Fine Metodo -
