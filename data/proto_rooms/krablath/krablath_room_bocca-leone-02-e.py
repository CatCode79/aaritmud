# -*- coding: utf-8 -*-

#= DESCRIZIONE =================================================================

# queste room sono accessibili solo tramite altri script.
# una volta entrati se si supera il peso massimo consentito si viene teleportati
# alla base della pianta
# diversamente si viene sputati in room diverse a seconda della direzione scelta

# check fatti e problemi risolti:
# quit in room ->
#     aggiunto l'after touch
# ingressi multipli di pg via follow ->
#     il previous_location è messo a None per
#     le entità teleportate e lo script è inibito se riprocessa entità con il
#     previous_location a None
# accumulo item leggeri nelle room (ad esempio per drop)->
#     per eccesso di peso la room viene svuotata sempre di tutto.
#     nel caso venga sputato solo chi entra allora viene effettuato un
#     clean_room a fine script


#= IMPORT ======================================================================

import random

from src.defer import defer_random_time
from src.room  import Room, Destination, Exit
from src.enums import TO, DIR


#= COSTANTI ====================================================================

LIST_DIR_ONE = [DIR.SOUTH, DIR.NORTHEAST, DIR.EAST, DIR.SOUTHWEST]
LIST_DIR_TWO = [DIR.NORTH, DIR.SOUTHEAST, DIR.WEST, DIR.NORTHWEST]

MAX_WEIGHT = 151000


#= FUNZIONI ====================================================================

def after_touch(entity, target, descr, detail, behavioured):
    # Se qualcuno quitta dentro alla bocca di leone poi si trova nella room
    # senza exit e senza possibilità d'attivare lo script, quindi anche con
    # il touch ne esce vivo.
    ALL_DIR = LIST_DIR_ONE + LIST_DIR_TWO
    direction = random.choice(ALL_DIR)
    throw_down(entity, None, direction, detail)
#- Fine Funzione -


def after_move(entity, from_room, direction, to_room, running, behavioured):
    defer_random_time(4, 6, throw_down, entity, from_room, direction, to_room)
#- Fine Funzione -


def throw_down(entity, from_room, direction, to_room):
    # Normale essendo la funzione anche deferrata
    if not entity or not from_room or not to_room:
        return

    if not entity.previous_location:
        return

    room_weight = 0
    for content in to_room.iter_contains():
        #print "PESO in LOOP = ", room_weight, content.code     
        # funzione nuova del gatto che consente di predenere anche il peso
        # di content e non solo del suo peso trasportato
        room_weight += content.get_total_weight()
    #print "PESO ROOM = ", room_weight

    if room_weight > MAX_WEIGHT:
        #print "TUTTI GIÙ!!"
        bottom_room = Destination(-3, 0, 0, "krablath").get_room()
        if bottom_room:
            entity.act("\nIl fiore non ti regge e voli giù con tutto il suo contenuto.\n", TO.ENTITY)
            to_room.act("Vedi qualcuno o qualcosa cadere verso il basso.\n")
            for content in to_room.iter_contains(use_reversed=True):
                #print content.previous_location.code
                content = content.from_location(content.quantity)
                #print "DA SCARICARE", content.code
                content.to_location(bottom_room, use_look=True)
                #print content.previous_location.code
                content.previous_location = None

    elif direction in LIST_DIR_ONE:
        # In piazza del villaggio
        #print "ENTRATI!", direction
        destination_room = Destination(-2, -2, 0, "villaggio-zingaro").get_room()
        really_spit(entity, destination_room, to_room)
    elif direction in LIST_DIR_TWO:
        #print "ENTRATI!", direction
        destination_room = Destination(-2, -1, -4, "villaggio-zingaro").get_room()
        really_spit(entity, destination_room, to_room)
#- Fine Funzione -


def really_spit(entity, destination_room, to_room):
    if destination_room and entity.location:
        #print "VOLO"
        entity.act("\nIl fiore si contrae in uno spasmo e poi ti sputa lontano.\n", TO.ENTITY)
        entity.act("Anche $n viene sputato assieme a te.", TO.OTHERS)
        entity = entity.from_location(entity.quantity)
        entity.to_location(destination_room, use_look=True)
        entity.previous_location = None
        clean_room(entity, to_room, destination_room)
#- Fine Funzione -


def clean_room(entity, to_room, destination_room):
    for content in to_room.iter_contains(use_reversed=True):
        to_room.act("\n[red]rimozione di te $n della monnezza![close]")
        to_room.act("[red]rimozione di te $n della monnezza![close]")
        content = content.from_location(content.quantity)
        content.to_location(destination_room, use_look=True)
        content.previous_location = None
#- Fine Funzione -
