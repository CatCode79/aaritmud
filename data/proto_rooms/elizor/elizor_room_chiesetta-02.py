# -*- coding: utf-8 -*-

#= COMMENT =====================================================================

# Script del mosaico
# usando una special stringa che separa i valori tramite virgola
# e poi li converti quando ti serve come una lista
# pieces = entity.specials["pieces"].split(",")
# viceversa quando ti serve salvarli, nell'on_shutdown per esempio
# entity.specials["pieces"] = ",".join(pieces)
# per il dizionario è un po' più complesso magari, o fai un doppio carattere di separazione, uno che separa la coppia key/value e l'altro che separa key e value
# oppure fai due liste distinte che poi unisci con...
# dictionary = dict(zip(keys, values))
# posso anche gestire le due liste in modo separato
# anche, dipende dai tuoi bisogni
# c'è un altro tipo oltre list e dict
# set
# funziona come una list, ma qualsiasi doppia, tripla, quadrupla etc etc occorrenza di elementi uguali viene rimossa e mantenuta una sola
# sostanzialmente i set sono gli insiemi in matematica
# se uno vuole una lista che abbia in sé una occorrenza di ogni elemento differente basta che faccia:
# lista_ripulita = list(set(lista_con_doppioni))


#= IMPORT ======================================================================

#import random
from src.web_resource import create_icon
from src.item import Item


#= COSTANTI ====================================================================

PROTO_TESSERA_CODE = "elizor_item_pezzo-mosaico-01"

icona_testo_001    = "icon/elizor-mosaic/mosaic-text-001.png"
icona_testo_002    = "icon/elizor-mosaic/mosaic-text-002.png"
icona_testo_003    = "icon/elizor-mosaic/mosaic-text-003.png"
icona_testo_004    = "icon/elizor-mosaic/mosaic-text-004.png"


#= FUNZIONI ====================================================================

def after_touch(entity, room, descr, detail, behavioured):
    tessera = Item(PROTO_TESSERA_CODE)
    tessera.icon = icona_testo_002
    tessera.inject(room)

def on_booting(room):
    if not room.specials:
        creale(room)

def creale(room):
    room.specials["icone_icone"] = ""

def after_smell(entity, room, descr, detail, behavioured):
    if not room.specials:
        creale(room)
    cerca_tessere(PROTO_TESSERA_CODE)

def cerca_tessere(proto_code):
    """
    Ricava gli item dal database del mud tramite prototipo.
    """
    cugi = []
    for item in database["items"].itervalues():
        if item.prototype.code == proto_code:
            cugi.append(item.split_entity(1))
            return cugi

    return None
#- Fine Funzione -
