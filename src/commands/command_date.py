# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import time

from src.calendar   import calendar
from src.config     import config
from src.engine     import engine
from src.enums      import TRUST
from src.gamescript import check_trigger
from src.log        import log
from src.game       import game_loop


#= FUNZIONI ====================================================================

def command_date(entity, argument="", behavioured=False):
    # Normale se questo comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    force_return = check_trigger(entity, "before_date", entity, behavioured)
    if force_return:
        return True

    weekday = calendar.get_weekday()

    # Non vengono visualizzati i minuti perché quando si utilizza questo
    # comando è come se si stesse facendo una stima del momento e quindi
    # non c'è precisione
    admin_minute = ""
    if entity.trust >= TRUST.MASTER:
        admin_minute = " {e %d minut%s}" % (calendar.minute, "o" if calendar.minute == 1 else "i")

    entity.send_output("Sono le ore %d%s del giorno %d, %s, nel mese %s." % (
        calendar.hour, admin_minute, calendar.day, weekday.description, calendar.month.description))
    entity.send_output("È la stagione %s e l'anno è il %d." % (
        calendar.get_season().adjective, calendar.year))

    # (TD) gestione degli anniversari e dei compleanni

    if entity.trust > TRUST.PLAYER:
        entity.send_output("\n")
        # (TD) far visualizzare queste info anche in una pagina web a parte
        # quindi ci vorrà una funzione a parte che ritorni una lista con riga
        # per riga il contenuto di questa parte
        entity.send_to_admin("Ora Locale Server: %s" % time.ctime())
        entity.send_to_admin("Ora dell'avvio del Mud: %s" % engine.booting_time)
        days    = (game_loop.elapsed_seconds / (24*3600))
        hours   = (game_loop.elapsed_seconds % 24) / 3600
        minutes = (game_loop.elapsed_seconds % 3600) / 60
        seconds = (game_loop.elapsed_seconds % 60)
        if days == 0:
            days = ""
        elif days == 1:
            days = " %d giorno" % days
        else:
            days = " %d giorni" % days
        if hours == 0:
            hours = ""
        elif hours == 1:
            hours = " %d ora" % hours
        else:
            hours = " %d ore" % hours
        if minutes == 0:
            minutes = ""
        elif minutes == 1:
            minutes = " %d minuto" % minutes
        else:
            minutes = " %d minuti" % minutes
        if seconds != 0 and game_loop.elapsed_seconds != seconds:
            conjunction_and = " e"
        else:
            conjunction_and = ""
        if seconds == 0:
            seconds = ""
        elif seconds == 1:
            seconds = " 1 secondo"
        else:
            seconds = " %d secondi" % seconds
        entity.send_to_admin("%s è up da:%s%s%s%s%s" % (
           config.game_name, days, hours, minutes, conjunction_and, seconds))

    force_return = check_trigger(entity, "after_date", entity, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "date\n"
#- Fine Funzione -
