# -*- coding: utf-8 -*-

"""
Modulo per il forum del Mud.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.enums        import TRUST
from src.forum_db     import forum_db
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ForumPage(WebResource):
    TITLE = "Forum"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = False

    MINIMUM_TRUST_ON_GET  = TRUST.PLAYER
    MINIMUM_TRUST_ON_POST = TRUST.PLAYER

    PAGE_TEMPLATE = string.Template(open("src/views/forum.view").read())

    def create_square(self, request, conn):
        return ""
    #- Fine Metodo -

    def render_GET(self, request, conn):
        mapping = {"mud_name"      : config.game_name,
                   "player_forums" : self.create_forum_rows(request, conn, "player"),
                  #"clan_forums"   : self.create_forum_rows(request, conn, "clan"),
                   "admin_forums"  : self.create_forum_rows(request, conn, "admin")}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def create_forum_rows(self, request, conn, forum_type):
        if forum_type not in ("player", "clan", "admin"):
            log.bug("forum_type non è un parametro valido: %s" % forum_type)
            return ""

        # ---------------------------------------------------------------------

        rows = []

        forum_type += "_"
        for forum_table in forum_db.tables:
            if not forum_table.code.startswith(forum_type):
                continue
            rows.append('''<tr><td><img src="tags/%s.png" style="border:1px solid grey" /></td>''' % forum_table.code)
            rows.append('''<td valign="top" width="100%%"><a href="forum_threads.html?forum_code=%s" style="color:white; font-size:larger">%s</a><br>%s</td>''' % (forum_table.code, forum_table.name, forum_table.descr))
            rows.append('''<td>Discussioni:<br>%d<br>Messaggi:<br>%d</td>''' % (forum_db.get_threads_qty(forum_table.code), forum_db.get_visits_qty(forum_table.code)))
            last_thread = forum_db.get_last_thread(forum_table.code)
            if last_thread:
                rows.append('''<td style="min-width:12em; max-width:12em"><img src="graphics/%s.png"/><a href="thread.html?forum_code=%s&thread=%s%s">%s</a><br>Di %s<br>%s</td></tr>''' % (
                    forum_table.code, thread.get_icon(conn), thread.id, thread.get_post_id(conn), thread.subject, thread.author, thread.date))
            else:
                rows.append('''<td style="min-width:12em; max-width:12em; text-align:center">Nessuno</td></tr>''')

        return "".join(rows)
    #- Fine Metodo -
