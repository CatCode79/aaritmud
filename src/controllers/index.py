# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina principale del sito.
"""


#= IMPORT ======================================================================

import string

from src.color        import remove_colors
from src.config       import config
from src.database     import database
from src.enums        import LOG
from src.log          import log
from src.new          import Comment
from src.utility      import is_number, pretty_date
from src.web_resource import WebResource


#= CLASSI ======================================================================

class IndexPage(WebResource):
    """
    Controller della homepage.
    """
    TITLE = "il Mud"

    PAGE_TEMPLATE = string.Template(open("src/views/index.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        from_number, to_number, message = self.get_from_to_numbers(request)
        if from_number == -1 or to_number == -1:
            return message

        # Viene creato un semilavorato in maniera tale che si possano eseguire
        # eventuali sostituzioni anche nel testo delle news
        semifinished = self.PAGE_TEMPLATE.safe_substitute({"news" : self.create_news(conn, from_number, to_number)})

        mapping = {"game_name"         : config.game_name,
                   "game_name_nocolor" : remove_colors(config.game_name),
                   "motto_nocolor"     : remove_colors(config.motto)}
        return string.Template(semifinished).safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if not request:
            log.bug("request non è un parametro valido: %r" % request)
            return ""

        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        # ---------------------------------------------------------------------

        if "new_code" in request.args and "comment_text" in request.args:
            new_code = request.args["new_code"][0]
            if new_code not in database["news"]:
                return "Non è stato passato un codice di new valido: %s" % new_code
            comment_text = request.args["comment_text"][0]
            if not comment_text:
                return "Non è stato passato un commento valido: %r" % comment_text
            comment = self.add_comment(conn, new_code, comment_text)
            return self.create_comment(comment)
        elif "new_code" in request.args:
            new_code = request.args["new_code"][0]
            if new_code in database["news"]:
                return self.create_comments(conn, new_code)
            else:
                return "Non è stato passato un codice di new valido: %s" % new_code
        elif "thumb_id" in request.args:
            thumb_id = request.args["thumb_id"][0]
            if thumb_id:
                return self.add_vote_to_new(conn, thumb_id)
            else:
                return "Non è stato passato un thumb_id valido"
        elif "from_number" in request.args or "to_number" in request.args:
            from_number, to_number, message = self.get_from_to_numbers(request)
            if from_number == -1 or to_number == -1:
                return message
            return self.create_news(conn, from_number, to_number)
        else:
            return "Non è stata passata nessuna azione di post valida"
    #- Fine Metodo -

    def get_from_to_numbers(self, request):
        if not request:
            log.bug("request non è un parametro valido: %r" % request)
            return ""

        # ---------------------------------------------------------------------

        from_number = 0
        if "from_number" in request.args:
            from_number = request.args["from_number"][0]
            if is_number(from_number):
                from_number = int(from_number)
                if from_number < 0:
                    return -1, -1, "Non è stato passato un from_number numerico maggiore o uguale a zero valido: %d" % from_number
            else:
                return -1, -1, "Non è stato passato un from_number valido: %d" % from_number

        to_number = config.news_to_show
        if "to_number" in request.args:
            to_number = request.args["to_number"][0]
            if is_number(to_number):
                to_number = int(to_number)
                if to_number < 0 or to_number < from_number:
                    return -1, -1, "Non è stato passato un to_number numerico maggiore di zero o maggiore e uguale di from_number: %d" % to_number
            else:
                return -1, -1, "Non è stato passato un to_number valido: %d" % to_number

        return from_number, to_number, ""
    #- Fine Metodo -

    def create_news(self, conn, from_number, to_number):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        if from_number < 0:
            log.bug("È stato passato un from_number con un valore minore di 0: %d" % to_number)
            return ""

        if to_number <= 0:
            log.bug("È stato passato un to_number con un valore minore o uguale a 0: %d" % to_number)
            return ""

        # ---------------------------------------------------------------------

        news = []

        n = 0
        for n, new_code in enumerate(reversed(sorted(database["news"]))):
            if n < from_number:
                continue
            if n > to_number:
                continue
            news.extend(self.create_new(conn, database["news"][new_code]))

        if n >= to_number and to_number - from_number > 1:
            if n >= to_number + config.news_to_show:
                message = "Visualizza le %d novità precedenti" % config.news_to_show
            elif n == to_number:
                message = "Visualizza l'ultima novità"
            else:
                message = "Visualizza le ultime %d novità" % ((n % config.news_to_show) + 1)
            news.append('''<a id="anchor" href="javascript:getNews(%d, %d)">%s</a>''' % (
                to_number+1, to_number + config.news_to_show, message))

        return "".join(news)
    #- Fine Metodo -

    def create_new(self, conn, new):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        if not new:
            log.bug("new non è un parametro valido: %r" % new)
            return ""

        # ---------------------------------------------------------------------

        accounts_up   = new.thumbs_up.split()
        accounts_down = new.thumbs_down.split()

        onclick_up   = ''' onclick="voteNew(this.id)"'''
        onclick_down = ''' onclick="voteNew(this.id)"'''
        title_up     = '''title="La novità mi piace"'''
        title_down   = '''title="La novità non mi piace"'''
        if not conn or not conn.account:
            thumb_src_up   = "graphics/thumb_up-blank.gif"
            thumb_src_down = "graphics/thumb_down-blank.gif"
            color_up       = " color:white; border:0px solid black"
            color_down     = " color:white; border:0px solid black"
            onclick_up     = ""
            onclick_down   = ""
            title_up       = '''title="Collegati al sito per dire che la novità ti piace"'''
            title_down     = '''title="Collegati al sito per dire che la novità non ti piace"'''
        elif conn.account.name in accounts_up:
            thumb_src_up   = "graphics/thumb_up.gif"
            thumb_src_down = "graphics/thumb_down-blank.gif"
            color_up       = " color:green;"
            color_down     = " color:white;"
        elif conn.account.name in accounts_down:
            thumb_src_up   = "graphics/thumb_up-blank.gif"
            thumb_src_down = "graphics/thumb_down.gif"
            color_up       = " color:white;"
            color_down     = " color:red;"
        else:
            thumb_src_up   = "graphics/thumb_up-blank.gif"
            thumb_src_down = "graphics/thumb_down-blank.gif"
            color_up       = " color:white;"
            color_down     = " color:white;"

        output = []

        output.append('''<div class="block">''')

        output.append('''<div class="block_title">''')
        output.append('''<div style="float:left">%s &nbsp;<span style="font-size:smaller;">(scritto in data %s da %s)</span></div>''' % (
            new.title, new.date, new.author))
        output.append('''<div style="text-align:right">''')
        if conn.account and not conn.account.name in new.thumbs_up and not conn.account.name in new.thumbs_down:
            output.append('''<span id="vote_me-%s">Votami: </span>''' % new.code)
        else:
            output.append('''<span id="vote_me-%s">Voti: </span>''' % new.code)
        output.append('''<input type="submit" id="thumbs_up-%s" style="background:url('%s') no-repeat left;%s" value="  +%d" %s%s />&nbsp;''' % (
            new.code, thumb_src_up, color_up, len(accounts_up), title_up, onclick_up))
        output.append('''<input type="submit" id="thumbs_down-%s" style="background:url('%s') no-repeat left;%s" value="  -%d" %s%s />&nbsp;''' % (
            new.code, thumb_src_down, color_down, len(accounts_down), title_down, onclick_down))
        output.append('''</div></div>''')  # chiude block_title

        output.append('''<div class="block_text">''')
        output.append('''<img class="tag" src="%s">''' % new.type.tag_image)
        output.append(new.text)
        output.append('''</div>''')

        if conn.account or len(new.comments) > 0:
            output.append('''<div class="block_title"><a href="javascript:toggleComments('%s');"><span id="comment_title_%s">Mostra Commenti (%d)</span></a></div>''' % (
                new.code, new.code, len(new.comments)))
            output.append('''<div class="block_text" style="display:none; align:center; text-align:center" id="comments_%s">''' % new.code)
            output.append('''</div>''')

        output.append('''</div><br><br>''')  # chiude block

        return output
    #- Fine Metodo -

    def add_comment(self, conn, new_code, comment_text):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        if not new_code:
            log.bug("new_code non è un parametro valido: %r" % new_code)
            return ""

        if not comment_text:
            log.bug("comment_text non è un parametro valido: %r" % comment_text)
            return ""

        # ---------------------------------------------------------------------

        new = database["news"][new_code]
        if not new:
            log.bug("new non valida con codice %s nel database delle news" % new_code)
            return

        comment = Comment()
        comment.author = conn.account.name
        comment.date   = pretty_date(clock=True)
        comment.text   = comment_text.strip()

        new.comments.append(comment)
        return comment
    #- Fine Metodo -

    def create_comments(self, conn, new_code):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        if not new_code:
            log.bug("new_code non è un parametro valido: %r" % new_code)
            return ""

        # ---------------------------------------------------------------------

        new = database["news"][new_code]
        if not new:
            log.bug("new non valida con codice %s nel database delle news" % new_code)
            return

        output = []
        output.append('''<div id="comments">''')
        for comment in new.comments:
            output.append(self.create_comment(comment, is_first=True if comment == new.comments[0] else False))
        output.append('''</div>''')

        if conn.account:
            output.append('''<div>''')
            if len(output) <= 3:
                output.append('''Ancora nessun commento per questa novità, vorresti scrivere qualcosa?<br>''')
            output.append('''<textarea id="comment_text" value="" style="width:50%" onkeyup="checkSubmit()"></textarea><br><br class="demi">''')
            output.append('''<input id="comment_submit" type="submit" value="Invia Commento" disabled="disabled" onclick="submitComment('%s')" /><br><br class="demi">''' % new_code)
            output.append('''<span id="comment_message"></span>''')
            output.append('''</div>''')

        return "".join(output)
    #- Fine Metodo -

    def create_comment(self, comment, is_first=False):
        if not comment:
            log.bug("comment non è un parametro valido: %r" % comment)
            return ""

        # ---------------------------------------------------------------------

        output = []
        if is_first:
            output.append('''<hr style="width:55%"><br class="demi">''')
        output.append('''<div name="comment" style="width:50%; text-align:left; margin:0 auto;">''')
        output.append('''[white]Commento di %s[close] (scritta %s)</span>:<br>''' % (comment.author, comment.date))
        output.append('''%s''' % comment.text)
        output.append('''</div>''')
        output.append('''<br class="demi"><hr style="width:55%"><br class="demi">''')

        return "".join(output)
    #- Fine Metodo -

    def add_vote_to_new(self, conn, thumb_id):
        if not conn:
            log.bug("conn non è un parametro valido: %r" % conn)
            return ""

        if not thumb_id:
            log.bug("thumb_id non è un parametro valido: %r" % thumb_id)
            return ""

        # ---------------------------------------------------------------------

        # È normale che non abbia un account valido se l'utente non è connesso
        if not conn.account:
            return ""

        # Ricava e controlla la validità delle informazioni passate
        try:
            attr_name, new_code = thumb_id.split("-")
        except ValueError:
            return "L'argomento thumb_id è senza il trattino: %s" % thumb_id

        if attr_name not in ("thumbs_up", "thumbs_down"):
            return "L'argomento attr_name non è valido: %s" % attr_name

        try:
            new = database["news"][new_code]
        except KeyError:
            return "Non esiste nessuna notizia con il codice %s" % new_code

        # Si assicura di rimuovere il voto nella lista opposta se questi è
        # stato impostato precedentemente
        if attr_name == "thumbs_up":
            reverse_attr_name = "thumbs_down"
        else:
            reverse_attr_name = "thumbs_up"
        reverse_accounts = getattr(new, reverse_attr_name).split()
        if conn.account.name in reverse_accounts:
            reverse_accounts.remove(conn.account.name)
            setattr(new, reverse_attr_name, " ".join(reverse_accounts))

        # Rimuove o imposta il nuovo voto nella lista relativa al voto scelto
        accounts = getattr(new, attr_name).split()
        if conn.account.name in accounts:
            accounts.remove(conn.account.name)
            setattr(new, attr_name, " ".join(accounts))
        else:
            accounts.append(conn.account.name)
            setattr(new, attr_name, " ".join(accounts))

        # La nuova immagine da utilizzare e il conteggio dei voti vengono
        # effettuati lato javascript
        return "ok"
    #- Fine Metodo -
