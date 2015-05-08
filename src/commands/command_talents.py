# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.log import log


#= FUNZIONI ====================================================================

def command_talents(entity, argument=""):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not entity.IS_PLAYER:
        entity.send_output("Non possiedi talenti particolari.")
        return True

    if entity.talents > 0:
        entity.send_output('''<script>$("#talents_title").parent().show(); $("#game_tabs").tabs({selected: 2});</script>''', break_line=False)
    else:
        entity.send_output("Attualmente non possiedi nessun talento in particolare, hai bisogno di più esperienza!")

    return True
#- Fine Funzione -
