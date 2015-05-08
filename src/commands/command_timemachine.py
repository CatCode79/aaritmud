# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.calendar import calendar
from src.command  import get_command_syntax
from src.config   import config
from src.enums    import TRUST, MONTH
from src.log      import log
from src.reset    import defer_all_reset_events, stop_all_reset_events
from src.utility  import is_same, multiple_arguments, is_number


#= FUNZIONI ====================================================================

def command_timemachine(entity, argument):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_timemachine")
        entity.send_output(syntax, break_line=False)
        return False

    minute = calendar.minute
    hour   = calendar.hour
    day    = calendar.day
    month  = calendar.month
    year   = calendar.year

    args = multiple_arguments(argument)

    # Permette di digitare il comando anche così: 'time machine'
    if is_same(args[0], "machine"):
        args = args[1 : ]

    if not args:
        syntax = get_command_syntax(entity, "command_timemachine")
        entity.send_output(syntax, break_line=False)
        return False

    if is_number(args[0]):
        minute = int(args[0])
    else:
        entity.send_output("Il primo argomento, relativo ai [white]minuti[close], dev'essere numerico e non: [green]%s[close]" % args[0])
        return False
    if minute < 0 or minute > config.minutes_in_hour - 1:
        entity.send_output("I minuti devono essere tra 0 e %d." % (config.minutes_in_hour - 1))
        return False

    if len(args) > 1:
        if is_number(args[1]):
            hour = int(args[1])
        else:
            entity.send_output("Il secondo argomento, relativo all'[white]ora[close], dev'essere numerico e non: [green]%s[close]" % args[1])
            return False
        if hour < 0 or hour > config.hours_in_day - 1:
            entity.send_output("L'ora dev'essere tra 0 e %d." % (config.hours_in_day - 1))
            return False

    if len(args) > 2:
        if is_number(args[2]):
            day = int(args[2])
        else:
            entity.send_output("Il terzo argomento, relativo al [white]giorno[close], dev'essere numerico e non: [green]%s[close]" % args[2])
            return False
        if day < 1 or day > config.days_in_month:
            entity.send_output("Il numero del giorno dev'essere tra 1 e %d." % config.days_in_month)
            return False

    if len(args) > 3:
        if is_number(args[3]):
            month = int(args[3])
        else:
            entity.send_output("Il quarto argomento, relativo al [white]mese[close], dev'essere numerico e non: [green]%s[close]" % args[3])
            return False
        if month < 1 or month > config.months_in_year:
            entity.send_output("Il numero del mese dev'essere tra 1 e %d." % config.months_in_year)
            return False
        month = MONTH.elements[month - 1]

    if len(args) > 4:
        if is_number(args[4]):
            year = int(args[4])
        else:
            entity.send_output("Il quinto argomento, relativo all'[white]anno[close], dev'essere numerico e non: [green]%s[close]" % args[4])
            return False

    if (minute == calendar.minute
    and hour == calendar.hour
    and day == calendar.day
    and month == calendar.month
    and year == calendar.year):
        entity.send_output("La data da impostare è la stessa di quella corrente!")
        return False

    stop_all_reset_events()

    calendar.minute = minute
    calendar.hour   = hour
    calendar.day    = day
    calendar.month  = month
    calendar.year   = year
    article = "le"
    if hour == 1:
        article = "la"
    entity.send_output("La nuova data impostata è: %s [white]%d[close] e [white]%d[close] del giorno [white]%d[close] del mese %s nell'anno [white]%d[close]" % (
        article, hour, minute, day, month, year))

    # Ora che è cambiata la data reinizializza tutti i reset
    defer_all_reset_events()
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "timemachine\n"
    syntax += "timemachine <minuti> (ore) (numero del giorno) (numero del mese) (anno)\n"

    return syntax
#- Fine Funzione -
