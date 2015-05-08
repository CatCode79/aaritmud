# -*- coding: utf-8 -*-

"""
Modulo per la creazione o modifica di un nuovo dato di account.
"""


#= IMPORT ======================================================================

from src.room         import ProtoRoom
from src.web_resource import EditResource, create_checklist_of_flags, create_listdrop_of_elements


#= CLASSI ======================================================================

class EditProtoRoomPage(EditResource):
    """
    Pagina web utilizzata per creare o modificare una stanza di prototipo.
    """
    TITLE = "Edit Proto Room"

    data_class = ProtoRoom
    data_key   = "code"

    # (TD) abbandonare il sistema de form ed utilizare una view
    form_rows = []

    tooltip_name = ""
    tooltip_password = ""
    tooltip_password_confirm = ""
    tooltip_email = ""
    tooltip_options = ""
    tooltip_trust = ""
    tooltip_players = ""
