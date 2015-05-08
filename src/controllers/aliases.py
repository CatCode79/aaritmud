# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di gestione degli alias.
"""


#= IMPORT ======================================================================

import string

from src.account      import Alias
from src.color        import remove_colors, colors_to_html
from src.config       import config
from src.utility      import sort_datas
from src.web_resource import WebResource, create_form_row, create_form


#= CLASSI ======================================================================

class AliasesPage(WebResource):
    """
    Pagina utilizzata per gestire gli alias dell'account.
    """
    TITLE = "Aliases"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MAX_NEW_ALIASES = 10

    def render_GET(self, request, conn):
        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        aliases = {}

        # Ricava gli argomenti del form dalla richiesta
        for arg in request.args:
            if arg.startswith("name_"):
                alias = Alias()
                alias.name   = request.args["name_%s"   % arg[len("name_")  : ]][0].lower().strip()
                alias.action = request.args["action_%s" % arg[len("name_")  : ]][0].strip()

                if alias.name:
                    alias.name = remove_colors(alias.name)
                if " " in alias.action:
                    input, argument = alias.action.split(None, 1)
                    alias.action = "%s %s" % (remove_colors(input), argument)

                if alias.name and alias.action:
                    aliases[alias.name] = alias

            # (TD) unire questa parte alla parte sopra che è praticamente uguale
            if arg.startswith("new_name_"):
                alias = Alias()
                alias.name   = request.args["new_name_%s"   % arg[len("new_name_") : ]][0].lower().strip()
                alias.action = request.args["new_action_%s" % arg[len("new_name_")  : ]][0].strip()

                if alias.name:
                    alias.name = remove_colors(alias.name)
                if " " in alias.action:
                    input, argument = alias.action.split(None, 1)
                    alias.action = "%s %s" % (remove_colors(input), argument)

                if alias.name and alias.action:
                    aliases[alias.name] = alias

        # Sostituisce gli aliases vecchi con quelli ricavati dal post
        conn.account.aliases = aliases
        return self.create_page(request, conn)
    #- Fine Metodo -

    # (TD) Da qualche parte, quando rifarò la pagina, dovrò controllare che il
    # nome dell'alias non sia un numero, altrimenti il tutto conflitta con il
    # sistema dei dialoghi
    def create_page(self, request, conn):
        # Prepara il form
        form = []
        row = create_form_row(form)
        row.label = "Alias"
        row.field = "Azione"

        # Prepara tutti gli alias in ordine alfabetico
        for alias_name, alias in sort_datas(conn.account.aliases, "name"):
            row = create_form_row(form)
            row.label = '''<input type="text" name="name_%s" maxlength="16" value="%s" />''' % (
                alias.name, alias.name)
            row.field = '''<input type="text" name="action_%s" maxlength="256" size="64" value="%s" />''' % (
                alias.name, colors_to_html(alias.action))
            if request.method == "POST":
                row.message = ""

        # Cerca di creare tot spazi vuoti per l'inserimento di nuovi alias a meno
        # che non abbia già raggiunto il massimo di alias per account
        counter = 0
        while counter < self.MAX_NEW_ALIASES and len(conn.account.aliases) + counter < config.max_aliases:
            row = create_form_row(form)
            row.label = '''<input type="text" name="new_name_%s" maxlength="16" />''' % counter
            row.field = '''<input type="text" name="new_action_%s" maxlength="256" size="64" />''' % counter
            counter += 1
        row = create_form_row(form)
        row.label = '''<input type="submit" value="Salva gli Alias" onclick="document.getElementById('form_aliases').submit();" />'''
        if request.method == "POST":
            row.label += '''<span style="color:green"> Alias salvati.</span>'''

        # Crea la pagina html
        page = ""

        page += '''<h3>Alias:</h3>'''
        page += "<p>"
        page += '''Un Alias è un'abbreviazione formata da una parola che chiama un comando con più argomenti che di solito si utilizzano frequentemente.<br>'''
        page += '''Per esempio se inserisci nel campo alias <span style="color:limegreen">pp</span> e nel campo azione <span style="color:limegreen">prendi pane</span> ogni volta che scriverai <span style="color:limegreen">pp</span> il Mud lo interpreterà come <span style="color:limegreen">prendi pane</span>.<br>'''
        page += '''Inoltre se invierai al Mud degli argomenti dopo l'alias questi verranno aggiunti anche al comando esteso, quindi:<br>'''
        page += '''<span style="color:limegreen">pp dal tavolo</span> verrà interpretato dal gioco come <span style="color:limegreen">prendi pane dal tavolo</span>.<br>'''
        page += "<p>"
        if config.max_aliases == 0:
            page += '''L'inserimento degli alias è disattivo.'''
        else:
            page += create_form(form, "form_aliases", "aliases.html", "Imposta i tuoi Alias")
        page += '''<br>%s alias creati su un massimo di %s<br>''' % (len(conn.account.aliases), config.max_aliases)

        return page
    #- Fine Metodo -
