# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina di creazione di un nuovo personaggio.
"""


#= IMPORT ======================================================================

from twisted.web import server

from src.config       import config
from src.element      import Element
from src.enums        import SEX, RACE, WAY, CONSTELLATION
from src.database     import database
from src.player       import Player
from src.web_resource import (WebResource, send_audio, create_form_row, create_form,
                              create_checklist_of_elements, create_tooltip)


#= CLASSI ======================================================================

class CreatePlayer1Page(WebResource):
    """
    Pagina web per la creazione di un nuovo personaggio.
    """
    TITLE = "Crea Personaggio"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    def render_GET(self, request, conn):
        #if conn.player and conn.player.code in database["players"]:
        #    if conn.player.game_request:
        #        return "\nImpossibile creare il personaggio %s perché già in gioco.\n" % conn.player.name
        #    else:
        #        # (TT) non dovrebbe capitare mai
        #        return "\nImpossibile creare il personaggio %s perché già in creazione.\n" % conn.player.name

        # Se un pg è connesso nel gioco allora lo sconnette prima di creare il
        # nuovo personaggio
        #if conn.player and conn.player.game_request:
        #    conn.player.send_output("\n\nConnessione chiusa per la creazione di un nuovo personaggio.")
        #    conn.close_game_request()

        if config.max_account_players == 0:
            return "Al momento non è possibile creare nuovi personaggi."

        return self.create_page(request, conn)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        #if conn.new_player and conn.new_player.code in database["players"]:
        #    return "\nImpossibile creare il personaggio %s perché già esistente.\n" % conn.new_player.name

        page = self.check_number_of_players(request, conn)
        if page:
            return page

        # Ricava gli argomenti del form dalla richiesta
        race = ""
        if "race" in request.args:
            race = Element(request.args["race"][0])

        sex = ""
        if "sex" in request.args:
            sex = Element(request.args["sex"][0])

        constellation = ""
        if "constellation" in request.args:
            constellation = Element(request.args["constellation"][0])

        # Controlla la validità degli argomenti inseriti nel form
        err_msg_race = ""
        if not race:
            err_msg_race = "Scegli la razza che vuoi interpretare"
            race = RACE.NONE
        else:
            # (TD) per ora gestisce la sessualità unica delle Frijen in maniera forzata
            if race == RACE.FRIJEN:
                sex = SEX.FEMALE

        err_msg_sex = ""
        if not sex:
            err_msg_sex = "Scegli la sessualità che vuoi interpretare"
            sex = SEX.NONE

        err_msg_constellation = ""
        if not constellation:
            err_msg_constellation = "Scegli la costellazione sotto cui il tuo personaggio è nato"
            constellation = CONSTELLATION.NONE

        # Se tutti gli argomenti del form sono validi crea il personaggio e
        # passa alla pagina di creazione successiva
        if not err_msg_race and not err_msg_sex and not err_msg_constellation:
            new_player = Player()
            new_player.race          = race
            new_player.sex           = sex
            new_player.constellation = constellation
            conn.new_player = new_player
            request.redirect("create_player2.html")
            request.finish()
            return server.NOT_DONE_YET

        return self.create_page(request, conn, race, sex, constellation,
                         err_msg_race, err_msg_sex, err_msg_constellation)
    #- Fine Metodo -

    # (TD) penso che al posto dei singoli attributi possa passare una Player() creato a nuovo
    def create_page(self, request, conn,
                    race=RACE.NONE, sex=SEX.NONE, constellation=CONSTELLATION.NONE,
                    err_msg_race="", err_msg_sex="", err_msg_constellation=""):
        # Prepara il form con i dati per la creazione di un nuovo personaggio
        form = []

        row = create_form_row(form)
        row.label   = "Razza %s" % create_tooltip(conn, "Scegli con cura la razza che vuoi interpretare, cambierà di molto sia il tuo modo di giocare e il modo di comportarti con gli altri.")
        row.field   = create_checklist_of_elements("race", race, "description", RACE.get_playable_races())
        row.message = err_msg_race

        # (TD) allowed sex razziale
        row = create_form_row(form)
        row.label   = "Sesso %s" % create_tooltip(conn, "Scegli la sessualità che vuoi interpretare.<br> Essa potrebbe influenzare di un poco alcuni bonus o malus a seconda della razza scelta.<br> Per esempio le femmine umane hanno un malus alla forza ma un bonus alla costituzione.")
        row.field   = create_checklist_of_elements("sex", sex)
        row.message = err_msg_sex

        row = create_form_row(form)
        row.label   = "Costellazione %s" % create_tooltip(conn, "Costellazione sotto cui sarà nato il tuo personaggio, oltre a dare dei bonus o malus essa determina casualmente anche il giorno e il mese di nascita.")
        row.field   = create_checklist_of_elements("constellation", constellation, "description")
        row.message = err_msg_constellation

        row = create_form_row(form)
        row.label   = '''<input type="submit" value="Continua..." onclick="document.getElementById('form_create_player_1').submit();" />'''

        # Crea la pagina html
        page = create_form(form, "form_create_player_1", "create_player1.html", "Crea un nuovo Personaggio", border=1)
        # (bb) questa musica devo spostarla in un frame nascosto esterno
        # in maniera tale che non venga stoppata, oppure toglierla del tutto
        # (che mi sa che è la cosa più semplice, utilizzarla per il diario)
        #page += send_audio(conn, "creation.mid", loop=True)
        return page
    #- Fine Metodo -

    def check_number_of_players(self, request, conn):
        if config.max_account_players == 0:
            return "La creazione di nuovi personaggi è disattiva."
        elif len(conn.account.players) >= config.max_account_players:
            return "Hai già creato il massimo di personaggi possibile.<br>"
        else:
            return ""
    #- Fine Metodo -
