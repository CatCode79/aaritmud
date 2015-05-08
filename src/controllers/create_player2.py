# -*- coding: utf-8 -*-

"""
Secondo modulo per la gestione della pagina di creazione di un nuovo personaggio.
"""


#= IMPORT ======================================================================

import random

from twisted.web import server

from src.account      import get_error_message_name
from src.color        import color_first_upper, remove_colors
from src.config       import config
from src.database     import database
from src.element      import Element
from src.enums        import COLOR, HAIRTYPE, HAND, RACE, TRUST
from src.web_resource import (WebResource, create_form_row, create_form,
                              create_checklist_of_elements, create_listdrop_of_elements,
                              create_listdrop_of_colors, create_tooltip)


#= CLASSI ======================================================================

class CreatePlayer2Page(WebResource):
    """
    Pagina web per la creazione di un nuovo personaggio.
    """
    TITLE = "Crea Personaggio"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    def render_GET(self, request, conn):
        #if conn.player and conn.player.code in database["players"]:
        #    return "\nImpossibile creare il personaggio %s perché già esistente.\n" % conn.player.name

        # Se si sta cercando di caricare la seconda pagina di creazione del pg
        # senza aver iniziato a crearlo realmente allora redirecta alla prima
        if not conn.new_player:
            request.redirect("create_player1.html")
            request.finish()
            return server.NOT_DONE_YET

        # All'inizio prepara dei valori casuali
        # (TD) ci sarebbero da utilizzare dei widget +/-
        age    = random.randint(conn.new_player.race.age_adolescence,   conn.new_player.race.age_old)
        height = random.randint(conn.new_player.race.height_low,        conn.new_player.race.height_high)
        weight = random.randint(conn.new_player.race.weight_low / 1000, conn.new_player.race.weight_high / 1000)

        return self.create_page(request, conn, age=age, height=height, weight=weight)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if not conn.new_player:
            return '''Per qualche errore sul server il personaggio non è stato creato, oppure è stato già creato, controlla la pagina con <a href="players.html">i tuoi personaggi</a>.'''

        # Ricava gli argomenti del form dalla richiesta
        age = 0
        if "age" in request.args:
            age = request.args["age"][0]

        height = 0
        if "height" in request.args:
            height = request.args["height"][0]

        weight = 0
        if conn.new_player.race.weight_low > 1000:
            if "weight" in request.args:
                weight = request.args["weight"][0]
        else:
            weight = random.randint(conn.new_player.race.weight_low, conn.new_player.race.weight_high)

        hair_color = None
        hair_type = None
        hair_length = 0
        if conn.new_player.race.have_hair:
            if "hair_color" in request.args:
                hair_color = Element(request.args["hair_color"][0])

            if "hair_type" in request.args:
                hair_type = Element(request.args["hair_type"][0])

            if "hair_length" in request.args:
                hair_length = request.args["hair_length"][0]

        eye_color = ""
        if "eye_color" in request.args:
            eye_color = Element(request.args["eye_color"][0])

        skin_color = ""
        if "skin_color" in request.args:
            skin_color = Element(request.args["skin_color"][0])

        hand = ""
        if "hand" in request.args:
            hand = Element(request.args["hand"][0])

        name = ""
        if "name" in request.args:
            name = request.args["name"][0]

        # Controlla la validità degli argomenti inseriti nel form
        err_msg_age = ""
        try:
            age = int(age)
        except ValueError:
            err_msg_age = "L'età deve essere un numero che indica gli anni vissuti dal tuo personaggio"
        else:
            if age < conn.new_player.race.age_adolescence or age > conn.new_player.race.age_old:
                err_msg_age = "I limiti dell'età, relativamente alla razza da te scelta, sono tra %d e %d." % (
                    conn.new_player.race.age_adolescence, conn.new_player.race.age_old)

        err_msg_height = ""
        try:
            height = int(height)
        except ValueError:
            err_msg_height = "L'altezza deve essere un numero in centimetri"
        else:
            if height < conn.new_player.race.height_low or height > conn.new_player.race.height_high:
                err_msg_height = "I limiti dell'altezza, relativamente alla razza da te scelta, sono tra %d e %d" % (
                    conn.new_player.race.height_low, conn.new_player.race.height_high)

        err_msg_weight = ""
        if conn.new_player.race.weight_low > 1000:
            try:
                weight = int(weight)
            except ValueError:
                err_msg_weight = "Il peso deve essere un numero in chili"
            else:
                if weight < conn.new_player.race.weight_low / 1000 or weight > conn.new_player.race.weight_high / 1000:
                    err_msg_weight = "I limiti del peso, relativamente alla razza da te scelta, sono tra %d e %d" % (
                        conn.new_player.race.weight_low / 1000, conn.new_player.race.weight_high / 1000)

        err_msg_haircolor = ""
        err_msg_hairtype = ""
        err_msg_hairlength = ""
        if conn.new_player.race.have_hair:
            if not hair_color:
                err_msg_haircolor = "Scegli il colore di capelli che vuoi dare al tuo personaggio."
                hair_color = COLOR.NONE

            if not hair_type:
                err_msg_hairtype = "Scegli il tipo di tagli di capelli che vuoi per il tuo personaggio."
                hair_type = HAIRTYPE.NONE

            try:
                hair_length = int(hair_length)
            except ValueError:
                err_msg_hairlength = "La lunghezza dei capelli deve essere un numero in centimentri."
            else:
                if hair_length < 0 or hair_length >= conn.new_player.race.height_low:
                    err_msg_hairlength = "La lunghezza dei capelli deve essere un numero tra lo 0 e %d" % (
                        conn.new_player.race.height_low / 2)

        err_msg_eyecolor = ""
        if not eye_color:
            err_msg_eyecolor = "Scegli il colore degli occhi che vuoi dare al tuo personaggio"
            eye_color = COLOR.NONE

        err_msg_skin_color = ""
        if not skin_color:
            err_msg_skin_color = "Scegli il colore della pelle che vuoi dare al tuo personaggio"
            skin_color = COLOR.NONE

        err_msg_hand = ""
        if not hand:
            err_msg_hand = "Scegli qual'è la %s principale del tuo futuro personaggio" % conn.new_player.race.hand
            hand = HAND.NONE

        err_msg_name = ""
        if name:
            name = color_first_upper(name)
            err_msg_name = get_error_message_name(name, False, "players")
        else:
            err_msg_name = "Inserisci il nome del personaggio che vuoi interpretare."

        # Se non ci sono stati errori allora inserisce i dati scelti dal
        # giocatore nell'oggetto personaggio che sta creando e continua
        # la creazione
        if (not err_msg_age and not err_msg_height and not err_msg_weight
        and not err_msg_haircolor and not err_msg_hairtype and not err_msg_hairlength
        and not err_msg_eyecolor and not err_msg_skin_color and not err_msg_hand and not err_msg_name):
            conn.new_player.age         = age
            conn.new_player.birth_month = conn.new_player.constellation.month
            conn.new_player.birth_day   = random.randint(1, config.days_in_month)
            conn.new_player.height      = height
            if conn.new_player.race.weight_low > 1000:
                conn.new_player.weight  = weight * 1000
            else:
                conn.new_player.weight  = weight
            conn.new_player.hair_color   = hair_color
            conn.new_player.hair_type    = hair_type
            conn.new_player.hair_length  = hair_length
            conn.new_player.eye_color    = eye_color
            conn.new_player.skin_color  = skin_color
            conn.new_player.hand        = hand
            conn.new_player.name        = name
            conn.new_player.code        = remove_colors(name)

            # Se vi era un giocatore connesso al gioco allora lo sconnette
            # per poi connettersi con quello nuovo
            if conn.player and conn.player.game_request:
                conn.player.send_output("\n\nConnessione chiusa per la creazione di un nuovo personaggio.")
                conn.player.game_request.finish()

            # Se ha terminato di distribuire tutti i punti allora procede alla
            # creazione e all'inserimento in gioco del nuovo personaggio
            conn.account.player                        = conn.new_player
            conn.account.players[conn.new_player.code] = conn.new_player
            conn.player                                = conn.new_player
            conn.player.account                        = conn.account
            database["players"][conn.new_player.code]  = conn.new_player
            conn.new_player                            = None

            # Se c'è solo il nuovo personaggio nel database allora gli dona
            # il massimo dei permessi
            if len(database["players"]) == 1:
                conn.player.trust = TRUST.IMPLEMENTOR

            # Internet Explorer non riesce a gestire qualche cosa e non si connette
            # direttamente in gioco
            if conn.get_browser().startswith("IE"):
                request.redirect("chaplayersml")
            else:
                request.redirect("game_interface.html?pg_code=%s" % conn.player.code)
            request.finish()
            return server.NOT_DONE_YET

        return self.create_page(request, conn,
                                age, height, weight, hair_color, hair_type, hair_length, eye_color, skin_color, hand, name,
                                err_msg_age, err_msg_height, err_msg_weight, err_msg_haircolor, err_msg_hairtype, err_msg_hairlength, err_msg_eyecolor, err_msg_skin_color, err_msg_hand, err_msg_name)
    #- Fine Metodo -

    # (TD) penso che al posto dei singoli attributi possa passare una Player() creato a nuovo
    def create_page(self, request, conn,
                    age=0, height=0, weight=0, hair_color=COLOR.NONE, hair_type=HAIRTYPE.NONE, hair_length=0, eye_color=COLOR.NONE, skin_color=COLOR.NONE, hand=HAND.NONE, name="",
                    err_msg_age="", err_msg_height="", err_msg_weight="", err_msg_haircolor="", err_msg_hairtype="", err_msg_hairlength="", err_msg_eyecolor="", err_msg_skin_color="", err_msg_hand="", err_msg_name=""):
        # Prepara il form con i dati per la creazione di un nuovo personaggio
        form = []
        row = create_form_row(form)
        row.label   = '''Età'''
        row.field   = '''<input type="text" name="age" maxlength="3" size="6" value="%s" />''' % age
        row.message = err_msg_age

        row = create_form_row(form)
        row.label   = '''Altezza (cm)'''
        row.field   = '''<input type="text" name="height" maxlength="3" size="6" value="%s" />''' % height
        row.message = err_msg_height

        if conn.new_player.race.weight_low > 1000:
            row = create_form_row(form)
            row.label   = '''Peso (kg)'''
            row.field   = '''<input type="text" name="weight" maxlength="3" size="6" value="%s" />''' % weight
            row.message = err_msg_weight

        if conn.new_player.race.have_hair:
            row = create_form_row(form)
            row.label   = '''Colore dei capelli'''
            row.field   = create_listdrop_of_colors("hair_color", hair_color)
            row.message = err_msg_haircolor

            row = create_form_row(form)
            row.label   = '''Tipo di capelli'''
            row.field   = create_listdrop_of_elements("hair_type", hair_type)
            row.message = err_msg_hairtype

            row = create_form_row(form)
            row.label   = '''Lunghezza dei capelli (cm)'''
            row.field   = '''<input type="text" name="hair_length" maxlength="3" size="6" value="%s" />''' % hair_length
            row.message = err_msg_hairlength

        row = create_form_row(form)
        row.label   = '''Colore degli occhi'''
        row.field   = create_listdrop_of_colors("eye_color", eye_color)
        row.message = err_msg_eyecolor

        row = create_form_row(form)
        row.label   = '''Colore della %s''' % "pelle/pelo"
        row.field   = create_listdrop_of_colors("skin_color", skin_color)
        row.message = err_msg_skin_color

        row = create_form_row(form)
        row.label   = '''%s principale''' % color_first_upper(str(conn.new_player.race.hand))
        row.field   = create_listdrop_of_elements("hand", hand)
        row.message = err_msg_hand

        # (TD) utilizzo della mano destra o sinistra

        row = create_form_row(form)
        # (TD) dire che i nomi si possono colorare
        # (BB) fino a che non si risolve il problema degli accenti, o non si utilizza python 3.0 questa storia degli accenti la possiamo dimenticare
        #row.label   = '''Nome %s''' % create_tooltip(conn, "Puoi inserirvi un numero contenuto di vocali accentate.")
        row.label   = '''Nome'''
        row.field   = '''<input type="text" name="name" maxlength="%s" value="%s" onkeydown="$(this.parentNode).prev().text('');" />''' % (config.max_len_name, name)
        row.message = err_msg_name

        row = create_form_row(form)
        row.label   = '''<input type="submit" value="Continua..." onclick="document.getElementById('form_create_player_2').submit();" />'''

        # Crea la pagina html
        return create_form(form, "form_create_player_2", "create_player2.html", "Crea un nuovo Personaggio")
    #- Fine Metodo -
