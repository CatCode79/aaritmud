# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di creazione di un nuovo account.
"""


#= IMPORT ======================================================================

from twisted.web import server

from src.account      import (Account, get_error_message_name, get_error_message_password,
                              get_error_message_email, MAX_LEN_EMAIL)
from src.config       import config
from src.database     import database
from src.element      import Flags
from src.enums        import OPTION, TRUST
from src.web_resource import WebResource, create_form_row, create_form, create_tooltip


#= CLASSI ======================================================================

class CreateAccountPage(WebResource):
    """
    Pagina web per la creazione di un nuovo account.
    """
    TITLE = "Create Account"

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        # Ricava gli argomenti del form dalla richiesta
        name = ""
        if "name" in request.args:
            name = request.args["name"][0].capitalize()

        password = ""
        if "password" in request.args:
            password  = request.args["password"][0]

        password2 = ""
        if "password2" in request.args:
            password2 = request.args["password2"][0]

        email = ""
        if email in request.args:
            email = request.args["email"][0].lower()

        # Controlla la validità degli argomenti inseriti nel form
        err_msg_name      = get_error_message_name(name, False)
        err_msg_password  = get_error_message_password(password)
        err_msg_password2 = ""
        err_msg_email     = get_error_message_email(email)
        if password != password2:
            err_msg_password2 = "Le password non coincidono, reinseriscile"
            password  = ""
            password2 = ""

        # Se i dati sono corretti crea l'account e passa alla pagina della sua gestione
        if (err_msg_name == "" and err_msg_password == ""
        and err_msg_password2 == "" and err_msg_email == ""):
            conn.account               = Account(name)
            database["accounts"][name] = conn.account
            conn.account.password      = password
            conn.account.email         = email
            conn.account.options       = Flags(OPTION.NEWBIE, OPTION.ITALIAN, OPTION.AUTO_GOLD, OPTION.AUTO_SPLIT, OPTION.AUTO_LOOT, OPTION.AUTO_OPEN, OPTION.MAP, OPTION.COMET)

            # Se c'è solo il nuovo account nel database allora gli dona
            # il massimo dei permessi
            if len(database["accounts"]) == 1:
                conn.account.trust = TRUST.IMPLEMENTOR

            request.redirect("players.html")
            request.finish()
            return server.NOT_DONE_YET
        return self.create_page(request, conn, name, password, password2, email,
            err_msg_name, err_msg_password, err_msg_password2, err_msg_email)
    #- Fine Metodo -

    def create_page(self, request, conn, name="", password="", password2="", email="",
            err_msg_name="", err_msg_password="", err_msg_password2="", err_msg_email=""):
        # Prepara il form
        form = []
        row = create_form_row(form)
        row.label   = "Nome dell'account"
        row.field   = '''<input type="text" name="name" maxlength="%s" value="%s" />''' % (config.max_len_name, name)
        row.message = err_msg_name
        row = create_form_row(form)
        row.label = "Password dell'account %s" % create_tooltip(conn, "La password dell'account devi conoscerla tu e tu soltanto.<br>Nessun amministratore ti domanderà la password per nessun motivo.<br>Ricordatelo, così da evitare persone che si spacciano amministratori del<br>Mud per rubarti la password.")
        row.field = '''<input type="password" name="password" maxlength="%s" value="%s" />''' % (config.max_len_password, password)
        if err_msg_password:
            row.message = err_msg_password
        elif err_msg_password2:
            row.message = err_msg_password2
        row = create_form_row(form)
        row.label = "Conferma della password"
        row.field = '''<input type="password" name="password2" maxlength="%s" value="%s" />''' % (config.max_len_password, password2)
        row = create_form_row(form)
        row.label = "Indirizzo mail %s" % create_tooltip(conn, "L'inserimento è facoltativo.<br>L'indirizzo mail viene utilizzato per il recupero di nome e password dell'account<br>oppure dagli amministratori del Mud per contattarti riguardo a novità, raduni,<br>sondaggi o casi urgenti.<br>Non viene né venduto né utilizzato per inviare spam.")
        row.field = '''<input type="text" name="email" maxlength="%s" value="%s" />''' % (MAX_LEN_EMAIL, email)
        row.message = err_msg_email
        row = create_form_row(form)
        row.label = '''<input type="submit" value="Crea l'Account" onclick="document.getElementById('form_create_account').submit();" />'''

        # Crea la pagina html
        page = ""

        page += '''<h3>Crea un nuovo account:</h3>'''
        page += '''Esso conterrà le tue opzioni di gioco e la lista dei tuoi personaggi con cui giocare.<br><br>'''
        page += create_form(form, "form_create_account", "create_account.html")

        return page
    #- Fine Metodo -
