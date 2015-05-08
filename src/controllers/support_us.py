# -*- coding: utf-8 -*-

"""
Modulo per la pagina relativa alle informazione su come poter supportare Aarit.
"""


#= IMPORT ======================================================================

import string

from src.config       import config
from src.enums        import TRUST
from src.utility      import email_encoder
from src.web_resource import WebResource


#= CLASSI ======================================================================

class SupportUsPage(WebResource):
    TITLE = "Support Us"

    ACCOUNT_MUST_EXIST_IN_GET  = False
    ACCOUNT_MUST_EXIST_IN_POST = False

    MINIMUM_TRUST_ON_GET  = TRUST.PLAYER
    MINIMUM_TRUST_ON_POST = TRUST.PLAYER

    PAGE_TEMPLATE = string.Template(open("src/views/support_us.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        mapping = {"game_name" : config.game_name,
                   "email"     : email_encoder(config.email)}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
