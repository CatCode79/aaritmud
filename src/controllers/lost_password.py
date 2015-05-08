# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di rcupero della password dell'account.
"""


#= IMPORT ======================================================================

from src.account      import MAX_LEN_EMAIL
from src.color        import remove_colors
from src.config       import config
from src.database     import database
from src.grammar      import is_vowel
from src.mail         import mail
from src.web_resource import WebResource, create_form_row, create_form


#= CLASSI ======================================================================

# (TD) devo dare la possibilità di recuperare la password anche contattando gli
# admin
class LostPasswordPage(WebResource):
    TITLE = "Lost Password"

    def render_GET(self, request, conn):
        return self.create_page(request, conn, "", True)

    def render_POST(self, request, conn):
        # Ricava gli argomenti del form dalla richiesta
        email = ""
        if "email":
            email = request.args["email"][0].lower()

        if not email:
            return self.create_page(request, conn, "", False)

        # Cerca la mail tra quella degli account
        for account in database["accounts"].itervalues():
            if account.email == email:
                break
        else:
            return self.create_page(request, conn, email, False)

        preposition = "a"
        game_name = remove_colors(config.game_name)
        if is_vowel(game_name[0]):
            preposition = "ad"

        subject = "[%s] Richiesta di recupero utente e password." % game_name.upper()
        message  = "Nome utente: %s\n" % account.name
        message += "Password: %s\n" % account.password
        message += "Potete eseguire l'accesso %s %s dalla pagina:\n" % (preposition, game_name)
        message += "%s/login.html\n" % config.site_address
        mail.send(account.email, subject, message)

        return self.create_page(request, conn, email, True)
    #- Fine Metodo -

    def create_page(self, request, conn, email="", email_exist=True):
        # Prepara il form
        form = []
        row = create_form_row(form)
        row.label = '''Digita l'indirizzo mail che hai inserito quando hai creato l'account.'''
        row = create_form_row(form)
        row.label = '''Inserisci l'email'''
        row.field = '''<input type="text" name="email" maxlength="%s" value="%s" />''' % (MAX_LEN_EMAIL, email)
        if not email_exist:
            row.message = '''Indirizzo mail non trovato tra gli account del Mud'''
        row = create_form_row(form)
        row.label = '''<input type="submit" value="Invia la Mail" onclick="document.getElementById('form_lost_password').submit();" />'''
        if request.method == "POST" and email_exist:
            row.label += '''<br><br>'''
            row.label += '''Il Mud sta inviando l'email. Controlla tra qualche momento la tua casella di posta.<br>'''
            row.label += '''Torna alla pagina di accesso al Mud cliccando <a href="login.html">qui</a>.<br>'''

        # Crea la pagina html
        return create_form(form, "form_lost_password", "lost_password.html", "Recupera il nome e la password dell'account")
    #- Fine Metodo -
