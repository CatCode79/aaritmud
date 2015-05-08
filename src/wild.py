# -*- coding: utf-8 -*-

"""
Modulo per la gestione della wilderness.
"""


#= IMPORT ======================================================================

import math

import Image  # PIL library

from src.calendar import calendar
from src.database import database
from src.exit     import Exit
from src.enums    import DIR, DOOR, EXIT, LOG, TRUST, SECTOR
from src.log      import log


#= COSTANTI ====================================================================

MAP_DIRECTIONS = (DIR.NORTHWEST, DIR.NORTH, DIR.NORTHEAST, DIR.WEST, None, DIR.EAST, DIR.SOUTHWEST, DIR.SOUTH, DIR.SOUTHEAST)


#= VARIABILI ===================================================================

# Altezza e larghezza della wild, vengono calcolati leggendo l'immagine
wild_height = -1
wild_width  = -1

# Queste tre liste verranno poi convertite in tuple una volta caricati i dati
wild_altitudes = []
wild_sectors   = []
#wild_nations  = []

# Dizionario coi colori relativi alle altitudini
altitude_colors = {
     (  0,   0,  68) : -15,  # Oceani, mari o laghi
     (  0,  17, 102) : -14,
     (  0,  51, 136) : -13,
     (  0,  85, 170) : -12,
     (  0, 119, 187) : -11,
     (  0, 153, 221) : -10,
     (  0, 204, 255) :  -9,
     ( 34, 221, 255) :  -8,
     ( 68, 238, 255) :  -7,
     (102, 255, 255) :  -6,
     (119, 255, 255) :  -5,
     (136, 255, 255) :  -4,
     (153, 255, 255) :  -3,
     (170, 255, 255) :  -2,
     (187, 255, 255) :  -1,
     (  0,  68,   0) :   0,  # Settori di pianura, poco sopra il livello del mare
     ( 34, 102,   0) :   1,
     ( 34, 136,   0) :   2,
     (119, 170,   0) :   3,
     (187, 221,   0) :   4,  # Settori di collina
     (255, 187,  34) :   5,
     (238, 170,  34) :   6,
     (221, 136,  34) :   7,
     (204, 136,  34) :   8,  # Settori di montagna
     (187, 102,  34) :   9,
     (170,  85,  34) :  10,
     (153,  85,  34) :  11,
     (136,  68,  34) :  12,  # Settori d'alta montagna
     (119,  51,  34) :  13,
     ( 85,  51,  17) :  14,
     ( 68,  34,   0) :  15}

# Dizionario coi colori relativi ai settori
sector_colors = {
    (  0,   0,  68) : SECTOR.SEA,
    (  0,  17, 102) : SECTOR.SEA,
    (  0,  51, 136) : SECTOR.SEA,
    (  0,  85, 170) : SECTOR.SEA,
    (  0, 119, 187) : SECTOR.SEA,
    (  0, 153, 221) : SECTOR.SEA,
    (  0, 204, 255) : SECTOR.SEA,
    ( 34, 221, 255) : SECTOR.SEA,
    ( 68, 238, 255) : SECTOR.SEA,
    (102, 255, 255) : SECTOR.SEA,
    (119, 255, 255) : SECTOR.SEA,
    (136, 255, 255) : SECTOR.SEA,
    (153, 255, 255) : SECTOR.SEA,
    (170, 255, 255) : SECTOR.SEA,
    (187, 255, 255) : SECTOR.SEA,
    (  0,  68,   0) : SECTOR.PLAIN,
    ( 34, 102,   0) : SECTOR.PLAIN,
    ( 34, 136,   0) : SECTOR.PLAIN,
    (119, 170,   0) : SECTOR.PLAIN,
    (187, 221,   0) : SECTOR.HILL,
    (255, 187,  34) : SECTOR.HILL,
    (238, 170,  34) : SECTOR.HILL,
    (221, 136,  34) : SECTOR.HILL,
    (204, 136,  34) : SECTOR.MOUNTAIN,
    (187, 102,  34) : SECTOR.MOUNTAIN,
    (170,  85,  34) : SECTOR.MOUNTAIN,
    (153,  85,  34) : SECTOR.MOUNTAIN,
    (136,  68,  34) : SECTOR.HIGHMOUNTAIN,
    (119,  51,  34) : SECTOR.HIGHMOUNTAIN,
    ( 85,  51,  17) : SECTOR.HIGHMOUNTAIN,
    ( 68,  34,   0) : SECTOR.HIGHMOUNTAIN}


#= CLASSI ======================================================================

class Wild(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.height = 0
        self.width  = 0
    #- Fine Inizializzazione -


#= FUNZIONI ====================================================================

def load_wild():
    """
    Carica l'immagine relative alla wild, le altitudini e i settori.
    """
    log.booting("-> altitudes")
    altitudes_file_path = "wild/altitudes.png"
    try:
        altitudes_image = Image.open(altitudes_file_path)
    except IOError:
        log.bug("Impossibile aprire l'immagine %s" % altitudes_file_path)
        return

    log.booting("-> sectors")
    sectors_file_path = "wild/sectors.png"
    try:
        sectors_image = Image.open(sectors_file_path)
    except IOError:
        log.bug("Impossibile aprire l'immagine %s" % sectors_file_path)
        return

    global wild_width
    global wild_height
    global wild_altitudes
    global wild_sectors

    wild_width = altitudes_image.size[0]
    wild_height = altitudes_image.size[1]
    # Inizializza le liste multidimensionali alla grandezza dell'immagine
    wild_altitudes = [[0 for y in xrange(wild_height)] for x in xrange(wild_width)]
    wild_sectors   = [[SECTOR.SEA for y in xrange(wild_height)] for x in xrange(wild_width)]

    # Ricava tutte le informazioni dai colori delle immagini
    for pixel in altitudes_image.getdata():
        if pixel in altitude_colors:
            # (BB) erroraccio per x e y
            wild_altitudes[x][y] = altitude_colors[pixel]
    for pixel in sectors_image.getdata():
        if pixel in sector_colors:
            # (BB) erroraccio per x e y
            wild_sectors[x][y] = sector_colors[pixel]

    # Converte le liste in tuple
    wild_altitudes = tuple(wild_altitudes)
    wild_sectors   = tuple(wild_sectors)
#- Fine Funzione -


def get_coords_around(entity, radius):
    """
    Ritorna una lista di coordinate in un raggio from-to attorno
    all'entità passata.
    """
    if not entity.location.IS_ROOM:
        log.bug("entity non si trova in una stanza: %s" % entity.location.get_name())
        yield (0, 0, 0)

    if radius == 0:
        yield (entity.location.x, entity.location.y, entity.location.z)
    else:
        # (TD) per i limiti laterali deve calcolare le coordinate dell'altro lato
        for x in xrange(entity.location.x - radius, entity.location.x + radius + 1):
            for y in xrange(entity.location.y - radius, entity.location.y + radius + 1):
                for z in xrange(entity.location.z - radius, entity.location.z + radius + 1):
                    # Salta le coordinate dell'entità stessa.
                    if (x, y, z) == (entity.location.x, entity.location.y, entity.location.z):
                        continue
                    yield (x, y, z)
#- Fine Funzione -


def get_distance(x1, y1, x2, y2):
    """
    Determina la distanza tra due coordinate in un piano bidimensionale.
    Serve per esempio per disegnare la parte visibile della wild in maniera
    circolare.
    """
    return get_distance_3d(x1, y1, 0, x2, y2, 0)
#- Fine Funzione -


def get_distance_3d(x1, y1, z1, x2, y2, z2):
    """
    Determina la distanza tra due coordinate in un piano tridimensionale.
    Serve per tante cose, di solito per controllare se una entità può colpire
    un'altra con attacchi a distanza.
    """
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dsquared = dx**2 + dy**2 + dz**2
    result = math.sqrt(dsquared)
    return result
#- Fine Funzione -


def calc_angle(x1, y1, x2, y2):
    """
    Calcola i gradi tra due coordinate usando l'arcotangente.
    """
    iNx1 = 0
    iNy1 = 0
    iNx2 = x2 - x1
    iNy2 = y2 - y1
    iNx3 = 0
    iNy3 = iNy2

    # Ritorna i gradi dei casi specifici
    if   iNx2 == 0 and iNy2 >  0:  return 0
    elif iNx2 == 0 and iNy2 <  0:  return 180
    elif iNy2 == 0 and iNx2 >  0:  return 90
    elif iNy2 == 0 and iNx2 <  0:  return 270
    elif iNx2 == 0 and iNy2 == 0:  return None  # Non bisogna mai passare coordinate che coincidono

    # Calcola i gradi tra le due coordinate
    distance_adjacent = get_distance(iNx1, iNy1, iNx3, iNy3)
    distance_opposite = get_distance(iNx3, iNy3, iNx2, iNy2)
    deg = math.degrees(math.atan2(distance_opposite, distance_adjacent))

    # Modifica il risultato in maniera tale da ritornare i gradi su una scala di
    # 360° con 0° a nord e senso orario
    if   iNx2 > 0 and iNy2 > 0:  return deg
    elif iNx2 > 0 and iNy2 < 0:  return 90 + ( 90 - deg )
    elif iNx2 < 0 and iNy2 > 0:  return 270 + ( 90 - deg )
    elif iNx2 < 0 and iNy2 < 0:  return 180 + deg
#- Fine Funzione -


def get_from_direction(x1, x2, y1, y2, z1, z2):
    """
    Ritorna la stringa contenente la direzione dalle coordinate x, y, z
    verso le coordinate in cui si trova l'entità.
    """
    # Se nelle coordinate cambia solo l'asse delle z ricava la direizone alta o bassa
    if x1 == x2 and y1 == y2:
        z_diff = z1 - z2
        if z_diff < -2:
            return "da molto in alto"
        elif z_diff < 0:
            return "dall'alto"
        elif z_diff == 0:
            return ""
        elif z_diff < 2:
            return "dal basso"
        else:
            return "da molto in basso"

    # Altrimenti ricava la direzione cardinale
    angle = calc_angle(x1, x2, y1, y2)
    if   angle >= 337.5 and angle <=  22.5:  return "da nord"
    elif angle >   22.5 and angle <   67.5:  return "da nordest"
    elif angle >=  67.5 and angle <= 112.5:  return "da est"
    elif angle >  112.5 and angle <  157.5:  return "da sudest"
    elif angle >= 157.5 and angle <= 202.5:  return "da sud"
    elif angle >  202.5 and angle <  237.5:  return "da sudovest"
    elif angle >= 237.5 and angle <= 292.5:  return "da ovest"
    elif angle >  292.5 and angle <  337.5:  return "da nordovest"
#- Fine Funzione -


def get_visual_radius(entity):
    """
    Ritorna l'attuale raggio di veduta dell'entità passata, cioè il numero
    di coordinate che può vedere in una determinata direzione.
    """
    if entity.trust >= TRUST.MASTER:
        return 8

    radius = 6
    if calendar.is_day():
        radius = 5
    elif calendar.is_night():
        radius = 3
        # (TD) aggiungere 1 per ogni tot di luminosità del personaggio, tramite torce, spade luminose o altro
    meteo = entity.area.meteo
    if meteo.is_raining_or_worse():
        radius -= 1
    return radius
#- Fine Funzione -


def create_wild_room(area, coords):
    if not area:
        log.bug("area non è un parametro valido: %r" % area)
        return False

    if not coords:
        log.bug("coords non è un parametro valido: %r" % coords)
        return False

    # -------------------------------------------------------------------------

    from src.room import Room

    if not area.wild:
        log.bug("Non è bene chiamare questa funzionese l'area non è una wild: %s" % area.code)
        return None

    global wild_width
    global wild_height
    global wild_altitudes
    global wild_sectors

    # Se le coordinate richieste sforano quelle della wild allora non crea la stanza
    x, y, z = coords.split()
    if int(x) >= area.wild.width:
        return None
    if int(y) >= area.wild.height:
        return None

    # (TD) da cambiare a seconda della tipologia di settore
    room = Room("limbo_room_void_1")
    for direction in (DIR.NORTH, DIR.EAST, DIR.SOUTH, DIR.WEST):
        room.exits[direction] = Exit(direction)
    room.inject_to_area(area, coords)

    return room
#- Fine Funzione -


def get_wild_exit_descr(entity, direction):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not direction or direction == DIR.NONE:
        log.bug("direction non è un parametro valido: %r" % direction)
        return ""

    # -------------------------------------------------------------------------

    # (TD)
    return direction.to_dir
#- Fine Funzione -


def create_wild_to_show(entity):
    """
    Crea la wild da visualizzare nel comando look.
    """
    wild_to_show = '''<span class="asciiart">'''
    last_back_color = "black"
    last_fore_color = "lightgray"

    radius = get_visual_radius(entity)
    for x in xrange(entity.location.x - radius, entity.location.x + radius):  # (TT) ci vorrà un più uno al max?
        if x < 0:
            x = wild_width - x
        if x > wild_width:
            x = x - wild_width
        for y in xrange(entity.location.y - radius, entity.location.y + radius):
            if y < 0:
                y = wild_height - y
            if y > wild_width:
                y = y - wild_width
            entities = []  # Lista delle entità trovate in una casella x,y di wild
            back_color = "black"
            fore_color = "lightgray"
            symbol = " "

            actors = []
            for z in xrange(entity.location.z - radius, entity.location.z + radius):
                # Salta le coordinate fuori dal raggio della visuale
                if (get_distance_3d(entity.location.x, entity.location.y, entity.location.z, x, y, z) > radius
                and not entity.trust >= TRUST.MASTER):
                    continue
                # Salta le entità sotto il livello del mare e sottoterra
                if z < 0 or z < wild_altitudes[x][y]:
                    continue
                coords = "%d %d %d" % (x, y, z)
                if coords in database["areas"]["nakilen"].rooms:
                    target_room = database["areas"]["nakilen"].rooms[coords]
                    actors += target_room.players + target_room.mobs

            # Se sono state trovate delle entità ricava il simbolo e il colore adatto
            if actors:
                if not fore_color:
                    # Colora se viene trovato uno del gruppo dell'entità
                    for someone in actors:
                        if someone.leader == entity.leader:
                            fore_color = "yellow"
                            break
                if  not fore_color:
                    # Se viene trovato un player li colorerà di rosso
                    for someone in actors:
                        fore_color = "lightred"
                        break
                if not fore_color:
                    # Se viene trovato qualcuno in cielo li colorerà ciano
                    for someone in actors:
                        if entity.location.z > wild_altitudes[x][y]:
                            fore_color = "lightcyan"
                            break
                # Conta quanti attori ci sono e ne ricava il simbolo tra 1 e 9 anche se più
                num = 0
                for someone in actors:
                    num += 1
                symbol = str(max(num, 9))

            # Cerca il colore di background adatto per il settore di wild
            if wild_sectors[x][y] == SECTOR.SEA:
                back_color = "blue"
            elif wild_sectors[x][y] == SECTOR.PLAIN:
                back_color = "lightgreen"
            elif wild_sectors[x][y] == SECTOR.HILLS:
                back_color = "green"
            elif wild_sectors[x][y] == SECTOR.MOUNTAIN:
                back_color = "brown"
            elif wild_sectors[x][y] == SECTOR.HIGHMOUNTAIN:
                back_color = "gray"
            else:
                log.bug("Settore non definito alle coordinate %d %d: %s" % (x, y, wild_sectors[x][y]))

            # Prepara colori e simboli da visualizzare
            if back_color != last_back_color:
                wild_to_show += "[background-color:%s]" % back_color
                last_back_color = back_color
            if fore_color != last_fore_color:
                wild_to_show += "[%s]" % fore_color
                last_fore_color = fore_color
            wild_to_show += symbol

        # Per ogni riga di coordinate x va' a capo
        wild_to_show += '''</span>\n'''

    return wild_to_show
#- Fine Funzione -


def create_visual_map(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    tiles = []

    counter = 0
    in_room = entity.get_in_room()
    tiles.append('''<div style="border:1px solid grey">''')
    for y in (in_room.y+1, in_room.y, in_room.y-1):
        for x in (in_room.x-1, in_room.x, in_room.x+1):
            coords = "%d %d %d" % (x, y, in_room.z)
            direction = MAP_DIRECTIONS[counter]
            destination_room = get_destination_room_for_tile(in_room, direction, coords)
            if destination_room:
                player_img = ""
                if not direction:
                    player_img = '''<img src="icons/player/default.png" border="0" style="position:absolute; top:8px; right:8px" />'''
                if destination_room.tile:
                    tile_src = destination_room.tile
                else:
                    tile_src = "sectors/%s.png" % destination_room.sector.get_mini_code()
                tiles.append('''<div style="float:left; position:relative"><img src="%s" border="0" />%s</div>''' % (tile_src, player_img))
            else:
                tiles.append('''<div style="float:left; position:relative"><img src="sectors/__blank__.png" /></div>''')
            counter += 1
        tiles.append('''<div style="clear:both"></div>''')
    tiles.append('''</div>''')

    return "".join(tiles)
#- Fine Funzione -


def get_destination_room_for_tile(in_room, direction, coords):
    # Se direction è None allora significa che sta controllando la stanza
    # in cui si trova il giocatore e fa vedere
    if not direction:
        return in_room

    # Se non vi è nessuna uscita alla direzione NON fa vedere
    if direction not in in_room.exits:
        return None

    # Se non si vuole elencare l'uscita NON fa vedere
    if EXIT.NO_LOOK_LIST in in_room.exits[direction].flags:
        return None

    # Se l'uscita ha una porta chiusa NON fa vedere
    door = in_room.get_door(direction)
    if door and door.door_type and DOOR.CLOSED in door.door_type.flags:
        return None

    # In tutti gli altri casi fa vedere
    return in_room.get_destination_room(direction)
#- Fine Funzione -
