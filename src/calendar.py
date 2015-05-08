# -*- coding: utf-8 -*-

"""
Modulo per la gestione del calendario rpg del gioco.
"""


#= IMPORT ======================================================================

import random

from src.gamescript import check_trigger
from src.config     import config
from src.element    import Element
from src.enums      import MONTH, ROOM, SEASON, WEEKDAY
from src.log        import log
from src.utility    import is_number


#= COSTANTI ====================================================================

ECHOES_DAWN =           ("[yellow]Comincia un nuovo giorno.[close]",
                         "[yellow]È un nuovo giorno.[close]",
                         "[yellow]Il cielo lentamente si rischiara, nell'alba di un nuovo giorno.[close]",
                         "[yellow]S'affaccia adagio il sole, al giorno appena nato.[close]")

ECHOES_DAWN_NO_SUN =    ("[yellow]Comincia un nuovo giorno.[close]",
                         "[yellow]È un nuovo giorno.[close]",
                         "[yellow]Il cielo lentamente si rischiara, nell'alba di un nuovo giorno.[close]",
                         "[yellow]S'affaccia adagio il sole, al giorno appena nato.[close]")

ECHOES_SUNRISE =        ("[orange]Il sole nasce di raggi tiepidi, sorgendo ad est...[close]",
                         "[orange]L'Oriente si rischiara: il sole sta sorgendo.[close]",
                         "[orange]Un sole fosco alza lo sguardo sul piatto dell'orizzonte...[close]",
                         "[orange]Un giorno nuovo saluta il mondo all'ascesa di un pallido sole...[close]")

ECHOES_SUNRISE_NO_SUN = ("[orange]Il sole nasce di raggi tiepidi, sorgendo ad est...[close]",
                         "[orange]L'Oriente si rischiara: il sole sta sorgendo.[close]",
                         "[orange]Un sole fosco alza lo sguardo sul piatto dell'orizzonte...[close]",
                         "[orange]Un giorno nuovo saluta il mondo all'ascesa di un pallido sole...[close]")

ECHOES_NOON =           ("[white]Il sole è alto nel cielo, l'intensità del suo diadema infuocato annuncia il mezzogiorno di luce...[close]",
                         "[white]La luce del sole è vigorosa, nel cielo disegna un bagliore acceso: è mezzogiorno.[close]")

ECHOES_NOON_NO_SUN =    ("[white]Il sole è alto nel cielo, l'intensità del suo diadema infuocato annuncia il mezzogiorno di luce...[close]",
                         "[white]La luce del sole è vigorosa, nel cielo disegna un bagliore acceso: è mezzogiorno.[close]")

ECHOES_SUNSET =         ("[red]L'occidente riluce dell'abbraccio infuocato del sole che tramonta...[close]",
                         "[red]L'orizzonte è tagliato dalla corona rossa del sole in tramonto...[close]",
                         "[red]Il cielo si dipinge d'oro rosso brillante, il sole ruotando adagio tramonta oltre lo sguardo...[close]",
                         "[red]Il sole finisce il suo viaggio portando i raggi splendenti nel sonno del tramonto...[close]")

ECHOES_SUNSET_NO_SUN =  ("[red]L'occidente riluce dell'abbraccio infuocato del sole che tramonta...[close]",
                         "[red]L'orizzonte è tagliato dalla corona rossa del sole in tramonto...[close]",
                         "[red]Il cielo si dipinge d'oro rosso brillante, il sole ruotando adagio tramonta oltre lo sguardo...[close]",
                         "[red]Il sole finisce il suo viaggio portando i raggi splendenti nel sonno del tramonto...[close]")

ECHOES_DUSK =           ("[royalblue]Il chiarore gentile della luna si diffonde attraverso il cielo, annunciando la sera...[close]",
                         "[royalblue]Mille punti di luci tenui occhieggiano nel cielo serale, contornando una pallida luna...[close]")

ECHOES_DUSK_NO_MOON =   ("[royalblue]Una notte senza traccia di luna ammanta il mondo con la sua ombra...[close]")

ECHOES_DUSK_FULL_MOON = ("[royalblue]Il chiarore della luna piena si diffonde attraverso il cielo, annunciando la sera...[close]",
                         "[royalblue]Mille punti di luci tenui occhieggiano nel cielo serale, contornando la luna piena...[close]")

ECHOES_MIDNIGHT =           ()

ECHOES_MIDNIGHT_NO_MOON =   ()

ECHOES_MIDNIGHT_FULL_MOON = ()


#= CLASSI ======================================================================

class Calendar(object):
    def __init__(self):
        self.minute = 0  # Minuto rpg
        self.hour   = 0  # Ora rpg
        self.day    = 1  # Giorno rpg
        self.month  = Element(MONTH.NONE)  # Mese rpg
        self.year   = 0  # Anno rpg
    #- Fine Inizializzazione -

    def get_error_message(self):
        # L'anno non ha bisogno di check perché può avere qualsiasi valore
        if self.minute < 0 or self.minute > config.minutes_in_hour - 1:
            msg = "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
        elif self.hour < 0 or self.hour > config.hours_in_day - 1:
            msg = "hour non è un valore valido: %d (dev'essere tra 0 e %d)" % (self.hour, config.hours_in_day)
        elif self.day <= 0 or self.day > config.days_in_month:
            msg = "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
        elif self.month.get_error_message(MONTH, "month") != "":
            msg = self.month.get_error_message(MONTH, "month")
        else:
            return ""

        # Se arriva fino a qui ha un messaggio di errore da inviare
        log.bug("(Calendar) %s" % msg)
        return msg
    #- Fine Metodo -

    def __str__(self):
        return "%d-%02d-%02d %02d:%02d" % (
            self.year, self.month.index, self.day, self.hour, self.minute)
    #- Fine Metodo -

    def load(self):
        filepath = "persistence/calendar.rpg"
        try:
            file = open(filepath, "r")
        except IOError:
            log.bug("Impossibile aprire il file %s in lettura" % filepath)
            return

        for line in file:
            if not line.strip():
                continue
            if line[0] == "#":
                continue
            break
        else:
            log.bug("Non è stato trovato nessuna riga valida al file %s" % filepath)
            file.close()
            return
        file.close()

        values = line.split()
        if len(values) != 5:
            log.bug("E' stato trovato un numero inatteso di valori al file %s: %d" % (filepath, len(values)))
            return

        if is_number(values[0]):
            self.minute = int(values[0])
        else:
            log.bug("minute del file %s non sono un numero valido: %s" % values[0])

        if is_number(values[1]):
            self.hour = int(values[1])
        else:
            log.bug("hour del file %s non sono un numero valido: %s" % values[1])

        if is_number(values[2]):
            self.day = int(values[2])
        else:
            log.bug("day del file %s non sono un numero valido: %s" % values[2])

        self.month = Element(values[3])

        if is_number(values[4]):
            self.year = int(values[4])
        else:
            log.bug("year del file %s non sono un numero valido: %s" % values[4])

        self.get_error_message()
    #- Fine Metodo -

    def save(self):
        filepath = "persistence/calendar.rpg"
        try:
            file = open(filepath, "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % filepath)
            return

        file.write("# minute hour day month year\n")
        file.write("%d %d %d %s %d\n" % (self.minute, self.hour, self.day, self.month.code, self.year))
        file.close()
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def is_day(self):
        if self.hour >= config.sunrise_hour and self.hour <= config.sunset_hour:
            return True
        return False
    #- Fine Metodo -

    def is_night(self):
        if self.hour < config.sunrise_hour or self.hour > config.sunset_hour:
            return True
        return False
    #- Fine Metodo -

    def get_weekday(self):
        """
        Ritorna il giorno corrente della settimana.
        """
        # (bb) (TD) Per ora ogni anno il calendario si resetta al primo giorno
        # della settimana anche se l'ultimo giorno dell'anno rpg precedente
        # non era l'ultimo giorno della settimana
        day_number  = (self.month.index + 1) * config.days_in_month
        day_number += self.day
        day_number %= len(WEEKDAY.elements) - 1

        return WEEKDAY.elements[day_number]
    #- Fine Metodo -

    def get_season(self):
        """
        Ritorna la stagione corrente.
        Le stagioni di "passaggio" durano 3 mesi, le altre 2 mesi.
        """
        if self.month == MONTH.TEN or self.month == MONTH.ONE:
            return SEASON.WINTER
        elif self.month == MONTH.TWO or self.month == MONTH.THREE or self.month == MONTH.FOUR:
            return SEASON.SPRING
        elif self.month == MONTH.FIVE or self.month == MONTH.SIX:
            return SEASON.SUMMER
        elif self.month == MONTH.SEVEN or self.month == MONTH.EIGHT or self.month == MONTH.NINE:
            return SEASON.AUTUMN

        log.bug("self.month non è valido: %r" % self.month)
        return SEASON.NONE
    #- Fine Metodo -

    def get_first_month_of_season(self, season=None):
        if not season:
            season = self.get_season()

        if   season == SEASON.WINTER:  return MONTH.TEN
        elif season == SEASON.SPRING:  return MONTH.TWO
        elif season == SEASON.SUMMER:  return MONTH.FIVE
        elif season == SEASON.AUTUMN:  return MONTH.SEVEN

        log.bug("Stagione mancante o errata: %r" % season)
        return MONTH.NONE
    #- Fine Metodo -

    def get_real_seconds_to(self, minute=-1, hour=-1, day=-1, month=MONTH.NONE, year=-1, force_advance=False):
        if minute < -1 or minute > config.minutes_in_hour:
            log.bug("minute non è un parametro valido: %d" % minute)
            return -1

        if hour < -1 or hour > config.hours_in_day:
            log.bug("hour non è un parametro valido: %d" % hour)
            return -1

        if day < -1 or day > config.days_in_month:
            log.bug("day non è un parametro valido: %d" % day)
            return -1

        if not month:
            log.bug("month non è un parametro valido: %r" % month)
            return -1

        if year < -1:
            log.bug("year non è un parametro valido: %d" % year)
            return -1

        # force_advance ha valore di verità

        # ---------------------------------------------------------------------

        if minute == -1:
            #minute_is_defined = False
            minute = self.minute
        else:
            #minute_is_defined = True
            pass

        if hour == -1:
            hour_is_defined = False
            hour = self.hour
        else:
            hour_is_defined = True

        if day == -1:
            day_is_defined = False
            day = self.day
        else:
            day_is_defined = True

        if month == MONTH.NONE:
            month_is_defined = False
            month = self.month
        else:
            month_is_defined = True

        if year == -1:
            #year_is_defined = False
            year = self.year
        else:
            #year_is_defined = True
            pass

        # ---------------------------------------------------------------------

        advance_a_day = False
        if not hour_is_defined and minute > self.minute:
            hour += 1
            # Le ore vanno da 0 al suo massimo escluso
            if hour >= config.hours_in_day:
                hour = 0
                advance_a_day = True

        advance_a_month = False
        if advance_a_day:
            day += 1
            # I giorni vanno da 1 al suo massimo incluso
            if day > config.days_in_month:
                day = 1
                advance_a_month = True

        if advance_a_month:
            month += 1
            # Se in una enumerazione sfora il massimo dei mesi rinizi dal
            # primo automaticamente (vedi cycle_on_last nel file element.py)
            if month == MONTH.ONE:
                year += 1

        # year non ha limite superiore per cui non c'è bisogno di controllarlo

        # ---------------------------------------------------------------------

        #print minute, hour, day, month.index, year, "-->",
        # (TD) Brrrr... lo so che fa schifo, ma per ora si tiene così fino a
        # che non si trova un po' di tempo per trovare una struttura smart
        if force_advance:
            if month < self.month:
                #print "A1",
                year += 1
            elif day < self.day and month <= self.month:
                if month_is_defined and month == self.month:
                    #print "B1",
                    year += 1
                else:
                    #print "B2",
                    month += 1
                    if month == MONTH.ONE:
                        #print "B3",
                        year += 1
            elif hour < self.hour and day <= self.day and month <= self.month:
                if day_is_defined and day == self.day:
                    if month_is_defined and month == self.month:
                        #print "C1",
                        year += 1
                    else:
                        #print "C2",
                        month += 1
                        if month == MONTH.ONE:
                            #print "C3",
                            year += 1
                else:
                    #print "C4",
                    day += 1
                    if day > config.days_in_month:
                        #print "C5",
                        day = 1
                        if month_is_defined and month == self.month:
                            #print "C6",
                            year += 1
                        else:
                            #print "C7",
                            month += 1
                            if month == MONTH.ONE:
                                #print "C8",
                                year += 1
            elif minute < self.minute and hour <= self.hour and day <= self.day and month <= self.month:
                if hour_is_defined and hour == self.hour:
                    if day_is_defined and day == self.day:
                        if month_is_defined and month == self.month:
                            #print "D1",
                            year += 1
                        else:
                            #print "D2",
                            month += 1
                            if month == MONTH.ONE:
                                #print "D3",
                                year += 1
                    else:
                        #print "D4",
                        day += 1
                        if day > config.days_in_month:
                            #print "D5",
                            day = 1
                            if month_is_defined and month == self.month:
                                #print "D6",
                                year += 1
                            else:
                                #print "D7",
                                month += 1
                                if month == MONTH.ONE:
                                    #print "D8",
                                    year += 1
                else:
                    #print "D9",
                    hour += 1
                    if hour >= config.hours_in_day:
                        #print "D10",
                        hour = 0
                        if day_is_defined and day == self.day:
                            if month_is_defined and month == self.month:
                                #print "D11",
                                year += 1
                            else:
                                #print "D12",
                                month += 1
                                if month == MONTH.ONE:
                                    #print "D13",
                                    year += 1
                        else:
                            #print "D14",
                            day += 1
                            if day > config.days_in_month:
                                #print "D15",
                                day = 1
                                if month_is_defined and month == self.month:
                                    #print "D16",
                                    year += 1
                                else:
                                    #print "D17",
                                    month += 1
                                    if month == MONTH.ONE:
                                        #print "D18",
                                        year += 1

        # ---------------------------------------------------------------------

        minutes  = (minute - self.minute)
        minutes += (hour - self.hour) * config.minutes_in_hour
        minutes += (day - self.day) * (config.minutes_in_hour * config.hours_in_day)
        minutes += (month.index - self.month.index) * (config.minutes_in_hour * config.hours_in_day * config.days_in_month)
        minutes += (year - self.year) * (config.minutes_in_hour * config.hours_in_day * config.days_in_month * config.months_in_year)

        #print "PROSSIMO RESET:%ss attuale:%d %d %d %d %d reset:%d %d %d %d %d %s %s %s" % (
        #    minutes * config.seconds_in_minute,
        #    self.minute, self.hour, self.day, self.month.index, self.year,
        #    minute, hour, day, month.index, year,
        #    hour_is_defined, day_is_defined, month_is_defined)
        return minutes * config.seconds_in_minute
    #- Fine Metodo -

    def update(self):
        first_day_of_month = False
        first_day_of_year  = False
        moment_type        = ""

        if self.minute < config.minutes_in_hour - 1:
            self.minute += 1
        else:
            self.minute = 0
            # Controlla il cambio dell'ora
            if self.hour < config.hours_in_day - 1:
                self.hour += 1
            else:
                self.hour = 0
                # Controlla il cambio del giorno
                if self.day < config.days_in_month:
                    self.day += 1
                else:
                    first_day_of_month = True
                    self.day = 1
                    # Controlla il cambio del mese
                    if self.month.index < len(MONTH.elements):
                        self.month += 1
                    else:
                        first_day_of_year = True
                        self.month = MONTH.ONE
                        self.year += 1
            if self.hour == config.dawn_hour:
                moment_type = "dawn"
            elif self.hour == config.sunrise_hour:
                moment_type = "sunrise"
            elif self.hour == config.noon_hour:
                moment_type = "noon"
            elif self.hour == config.sunset_hour:
                moment_type = "sunset"
            elif self.hour == config.dusk_hour:
                moment_type = "dusk"
            elif self.hour == config.midnight_hour:
                moment_type = "midnight"

        from src.database import database
        if moment_type:
            for area in database["areas"].itervalues():
                echoes = globals()["ECHOES_%s" % moment_type.upper()]

                # (TD) a seconda che nell'area vi sia bello o brutto tempo fa
                # vedere o meno il sole o la luna con messaggi appositi
                # E anche il sistema della luna piena
                area_echoes = getattr(area, "echoes_%s" % moment_type)
                if area_echoes:
                    echoes = area_echoes

                # Poiché esistono anche gli echoes personalizzabili per stanza
                # allora esegue una ricerca stanza per stanza
                for room in reversed(area.rooms.values()):
                    room_echoes = getattr(room, "echoes_%s" % moment_type)
                    if room_echoes:
                        echoes = room_echoes

                    # Se la stanza è interna allora non fa visualizzare i
                    # messaggi di echo di default, a meno che appunto non
                    # siano stati inseriti ad uopo per la stanza
                    if ROOM.INSIDE in room.flags and not room_echoes:
                        pass
                    elif echoes:
                        # Non esegue il random pg per pg per poter avere un
                        # messaggio unico almeno stanza per stanza
                        room.echo(random.choice(echoes))

                    # I check sui trigger
                    force_return = check_trigger(room, "on_" + moment_type, room)
                    if force_return:
                        continue
                    for content in room.iter_all_entities(use_reversed=True):
                        force_return = check_trigger(content, "on_" + moment_type, content)
                        if force_return:
                            break

        # A tutti fa visualizzare se il giorno è il primo dell'anno o del mese
        # (TD) in futuro anche il nome della settimana
        for player in database["players"].itervalues():
            if not player.game_request:
                continue
            if first_day_of_year:
                player.send_output("\nOggi è il [white]primo giorno[close] dell'anno %d!" % self.year)
                player.send_prompt()
            elif first_day_of_month:
                player.send_output("\nOggi è il [white]primo giorno[close] del mese %s." % self.month.description)
                player.send_prompt()
    #- Fine Metodo -


#class RpgDate(object):
#    def __init__(self):
#        self.minute = -1
#        self.hour   = -1
#        self.day    = -1
#        self.month  = Element(MONTH.NONE)
#        self.year   = -1
#    #- Fine dell'Inizializzazione -
#
#    def get_error_message(self):
#        if self.minute < -1 or self.minute > config.minutes_in_hour - 1:
#            return "minute non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.minute, config.minutes_in_hour - 1)
#        elif self.hour < 0 or self.hour > config.hours_in_day - 1:
#            return "hour non è un valore valido: %d (dev'essere tra -1 e %d)" % (self.hour, config.hours_in_day - 1)
#        elif self.day <= 0 or self.day > config.days_in_month:
#            return "day non è un valore valido: %s (dev'essere tra -1 e %s)" % (self.day, config.days_in_month)
#        elif self.month.get_error_message(MONTH, "month") != "":
#            return self.month.get_error_message(MONTH, "month")
#
#        return ""
#    #- Fine del Metodo -
#
#    def fread_the_line(self, file, line, attr):
#        if not file:
#            log.bug("file non è un parametro valido: %r" % file)
#            return
#
#        if not line:
#            log.bug("line non è un parametro valido: %r" % line)
#            return
#
#        if not attr:
#            log.bug("attr non è un parametro valido: %r" % attr)
#            return
#
#        # ---------------------------------------------------------------------
#
#        
#    #- Fine del Metodo -
#
#    def fwrite_the_line(self, file, label, indentation=""):
#        if not file:
#            log.bug("file non è un parametro valido: %r" % file)
#            return
#
#        if not label:
#            log.bug("label non è un parametro valido: %r" % label)
#            return
#
#        # -------------------------------------------------------------------------
#
#        
#    #- Fine del Metodo -


#= SINGLETON ===================================================================

calendar = Calendar()
