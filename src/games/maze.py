# -*- coding: utf-8 -*-

"""
Modulo per la creazione di aree labirinto.
basato su:
http://xefer.com/maze-generator
"""

#= IMPORT ======================================================================

import math
import random

from src.calendar import calendar
from src.database import database
from src.exit     import Exit
from src.element  import Element
from src.enums    import AREA, DIR, WEEKDAY
from src.log      import log
from src.reset    import RoomReset
from src.room     import Destination
from src.utility  import is_number


#= COSTANTI ====================================================================

NORTH = 0
SOUTH = 1
WEST  = 2
EAST  = 3

DIRS   = [0, 1, 2, 3]  # Direction of neighbors
UNDIRS = [1, 0, 3, 2]  # Opposite direction
DELTA  = { "x" : [0, 0, -1, 1], "y" : [1, -1, 0, 0] }  # Offsets of neighbors


#= CLASSI ======================================================================

class Maze(object):
    """
    Classe relativa ad un labirinto.
    """
    PRIMARY_KEY = ""
    VOLATILES   = ["cells", "track_counter"]
    MULTILINES  = []
    SCHEMA      = {"passages"  : ("src.games.maze", "MazePassage"),
                   "dead_ends" : ("src.games.maze", "MazeDeadEnd")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, columns=0, rows=0, code_prefix=""):
        self.columns         = columns     # Numero di colonne totali del labirinto
        self.rows            = rows        # Numero di righe totali del labirinto
        self.code_prefix     = code_prefix # Prefisso del codice delle room utilizzate per il reset
        self.remake_hour     = -1          # In quale ora il maze viene ricreato
        self.remake_weekday  = Element(WEEKDAY.NONE)
        self.remake_message  = ""          # Messaggio di act a tutte le entità nel labirinto durante il relativo remake
        self.passages        = []          # Elenco dei passaggi: entrate, uscite o altre nicchie, collegate al labirinto attorno al suo bordo
        self.dead_ends       = []          # Elenco dei vicoli ciechi casualmente da inserire al posto di quelli standard

        # Variabili volatili
        self.cells         = []
        self.track_counter = 0  # Numero di room tracciate dall'algoritmo di creazione del maze
    #- Fine Inizializzazione -

    def get_error_message(self):
        if self.columns <= 1:
            return "colums non è valido: %d" % self.columns
        elif self.rows <= 1:
            return "rows non è valido: %d" % self.rows
        elif self.remake_hour < -1 and self.remake_hour > config.hours_in_day - 1:
            return "remake_hour non è un'ora rpg valida: %d (inserire da -1 a %d)" % (self.remake_hour, config.hours_in_day - 1)
        elif self.remake_weekday.get_error_message(WEEKDAY, "remake_weekday") != "":
            return self.remake_weekday.get_error_message(WEEKDAY, "remake_weekday")
        elif self.get_error_message_passages() != "":
            return self.get_error_message_passages()
        elif self.get_error_message_dead_ends() != "":
            return self.get_error_message_dead_ends()
        else:
            return ""
    #- Fine Metodo -

    def get_error_message_passages(self):
        for passage in self.passages:
            message = passage.get_error_message(self)
            if message:
                return message

        return ""
    #- Fine Metodo -

    def get_error_message_dead_ends(self):
        for dead_end in self.dead_ends:
            message = dead_end.get_error_message(self)
            if message:
                return message

        return ""
    #- Fine Metodo -

    def create(self, area):
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        # ---------------------------------------------------------------------

        # Mette il token(none), wall(4 * True) e visited(false) a tutte le room
        self.cells = [[MazeCell() for r in xrange(self.rows)] for c in xrange(self.columns)]
        self.track_counter = 0

        # A stack containing coordinates of the current cell and a scrambled
        # list of the direction to its neighbors
        shuffled = list(DIRS)
        random.shuffle(shuffled)

        # inizialmente contiene solo dati per una room: coordinate e la sequenza delle vicine scramblate
        stack = [StackElement(math.floor(random.random() * self.columns),
                              math.floor(random.random() * self.rows),
                              shuffled)]

        # Il loop deve iterare fino a che ha visitato tutte le celle, ma poiché
        # il depth first può anche tornare sui propri passi non basta farlo
        # iterare (self.rows * self.columns) volte
        while self.track_counter < (self.rows * self.columns):
            self.depth_first_search(stack)

        # Toglie i muri relativi ai vari passaggi fuori dai limiti della griglia
        # aprendo dei passi in questa maniera vengono correttamente caricate
        # le stanze a seconda delle uscite attorno
        for passage in self.passages:
            if passage.z != 0:
                continue
            coords = "%d %d %d" % (passage.x, passage.y, passage.z)
            if coords not in area.rooms:
                log.bug("Non esistono le coordinate %s nell'area %s (nel ciclo dei passages attorno)" % (coords, area.code))
                continue
            passage_room = area.rooms[coords]
            if passage.y == -1:
                self.cells[passage.x][0].wall[SOUTH] = False;
                if DIR.NORTH not in passage_room.exits:
                    passage_room.exits[DIR.NORTH] = Exit(DIR.NORTH)
            if passage.y == self.rows:
                self.cells[passage.x][self.rows - 1].wall[NORTH] = False;
                if DIR.SOUTH not in passage_room.exits:
                    passage_room.exits[DIR.SOUTH] = Exit(DIR.SOUTH)
            if passage.x == -1:
                self.cells[0][passage.y].wall[WEST] = False;
                if DIR.EAST not in passage_room.exits:
                    passage_room.exits[DIR.EAST] = Exit(DIR.EAST)
            if passage.x == self.columns:
                self.cells[self.columns - 1][passage.y].wall[EAST] = False;
                if DIR.WEST not in passage_room.exits:
                    passage_room.exits[DIR.WEST] = Exit(DIR.WEST)

        # Crea ed avvia i reset per l'area del labirinto
        self.create_resets(area)

        # Crea le aperture in alto e in basso per eventuali altri passaggi
        # Non esistendo delle descrizioni di stanze con uscite verso il basso
        # e verso l'alto è dato al giocatore fare attenzione a queste uscite
        # verso l'inizio o la fine del labirinto o altre nicchie.
        # Stesso discorso per l'aggiunta delle uscite diagonali per i 4 angoli
        # esterni.
        # Se la room relativa al passaggio non possiede l'uscita per arrivare
        # alla stanza del labirinto viene creata automaticamente.
        for passage in self.passages:
            if passage.z == 0:
                maze_coords = ""
                if passage.x == -1 and passage.y == -1:
                    maze_coords = "0 0 0"
                    maze_dir    = DIR.SOUTHWEST
                elif passage.x == -1 and passage.y == self.rows:
                    maze_coords = "0 %d 0" % self.rows - 1
                    maze_dir    = DIR.NORTHEAST
                elif passage.x == self.columns and passage.y == -1:
                    maze_coords = "%d 0 0" % self.columns - 1
                    maze_dir    = DIR.SOUTHEAST
                elif passage.x == self.columns and passage.y == self.rows:
                    maze_coords = "%d %d 0" % (self.columns - 1, self.rows - 1)
                    maze_dir    = DIR.NORTHEAST
                if maze_coords:
                    maze_room = area.rooms[maze_coords]
                    maze_room.exits[maze_dir] = Exit(maze_dir)
                    passage_coords = "%d %d %d" % (passage.x, passage.y, passage.z)
                    if passage_coords not in area.rooms:
                        log.bug("Non esistono le coordinate %s nell'area %s (nel ciclo dei passages negli angoli)" % (passage_coords, area.code))
                        continue
                    passage_room = area.rooms[passage_coords]
                    if maze_dir.reverse_dir not in passage_room.exits:
                        passage_room.exits[maze_dir.reverse_dir] = Exit(maze_dir.reverse_dir)
            else:
                passage_coords = "%d %d %d" % (passage.x, passage.y, passage.z)
                if passage_coords not in area.rooms:
                    log.bug("Non esistono le coordinate %s nell'area %s (nel ciclo dei passages nell'up & down)" % (passage_coords, area.code))
                    continue
                passage_room = area.rooms[passage_coords]
                maze_room = area.rooms["%d %d 0" % (passage.x, passage.y)]
                if passage.z == 1:
                    maze_room.exits[DIR.UP] = Exit(DIR.UP)
                    if DIR.DOWN not in passage_room.exits:
                        passage_room.exits[DIR.DOWN] = Exit(DIR.DOWN)
                else:
                    maze_room.exits[DIR.DOWN] = Exit(DIR.DOWN)
                    if DIR.UP not in passage_room.exits:
                        passage_room.exits[DIR.UP] = Exit(DIR.UP)

        # (TD) Ora provvede ad inserire casualmente i DeadEnds evitando
        # che questi tangino eventuali Passagges
        pass

        # Rimuove le informazioni delle MazeCell per pulizia
        self.cells = []
    #- Fine Metodo -

    def depth_first_search(self, stack):
        tail_element = stack[-1]
        x = tail_element.x
        y = tail_element.y
        neighbors = tail_element.neighbors

        # When all cells have been visited at least once, it's done
        if not self.cells[x][y].visited:
            self.cells[x][y].visited = True
            self.track_counter = self.track_counter +1

        # Stampa le coordinate della via seguita per la generazione del maze per
        # verificare che non restino celle non tracciate
        # When all cells have been visited at least once, it's done
        #print "(", x, ",", y, ")", "- room tracciate", self.track_counter

        # Look for a neighbor that is in the maze and hasn't been visited yet
        while len(neighbors) > 0:
            direction = neighbors.pop()
            if len(neighbors) == 0:
                stack.pop()  # All neighbors checked, done with this one

            dx = x + DELTA["x"][direction]
            dy = y + DELTA["y"][direction]
            if dx >= 0 and dy >= 0 and dx < self.columns and dy < self.rows:
                if self.cells[dx][dy].visited == False:
                    # Break down the wall between them. The new neighbor is
                    # added onto the stack and becomes the new current cell
                    self.cells[x][y].wall[direction] = False
                    self.cells[dx][dy].wall[UNDIRS[direction]] = False
                    shuffled = list(DIRS)
                    random.shuffle(shuffled)
                    new_element = StackElement(dx, dy, shuffled)
                    stack.append(new_element);
                    break;
    #- Fine Metodo -

    def create_resets(self, area):
        """
        Esegue il reset del labirinto con le stanze appositamente create per
        l'area.
        """
        for x in xrange(self.columns):
            for y in xrange(self.rows):
                wall = self.cells[x][y].wall
                           # [NORTH, SOUTH, WEST,  EAST  ]
                #print "x:%d y:%d NORTH:%s SOUTH:%s WEST:%s EAST:%s" % (x, y, wall[NORTH], wall[SOUTH], wall[WEST], wall[EAST])
                if   wall == [True,  False, True,  True ]:  code = "_sud"        # switch 1
                elif wall == [False, True,  True,  True ]:  code = "_nord"       # switch 1
                elif wall == [True,  True,  False, True ]:  code = "_ovest"
                elif wall == [True,  True,  True,  False]:  code = "_est"
                elif wall == [False, False, True,  True ]:  code = "_nord-sud"
                elif wall == [True,  True,  False, False]:  code = "_est-ovest"
                elif wall == [False, False, False, False]:  code = "_incrocio"
                elif wall == [True,  False, True,  False]:  code = "_sud-est"    # switch 2
                elif wall == [True,  False, False, True ]:  code = "_sud-ovest"  # switch 3
                elif wall == [False, True,  True,  False]:  code = "_nord-est"   # switch 2
                elif wall == [False, True,  False, True ]:  code = "_nord-ovest" # switch 3
                elif wall == [False, False, False, True ]:  code = "_3no-est"
                elif wall == [False, True,  False, False]:  code = "_3no-sud"    # switch 4
                elif wall == [False, False, True,  False]:  code = "_3no-ovest"
                elif wall == [True,  False, False, False]:  code = "_3no-nord"   # switch 4
                elif wall == [True,  True,  True,  True ]:  code = "_no" #; print wall
                else:
                    log.bug("Qui non dovrebbe mai passare: %s", wall)
                    continue
                room_reset = RoomReset()
                room_reset.proto_room = database["proto_rooms"][self.code_prefix + code]
                room_reset.destination = Destination(x, y, 0, area)
                area.room_resets.append(room_reset)

        # Una volta creati i reset li avvia
        area.defer_reset_events()
    #- Fine Metodo -

    def destroy(self, area):
        if not area:
            log.bug("area non è un parametro valido: %r" % area)
            return

        # ---------------------------------------------------------------------

        room_codes = []
        for passage in self.passages:
            room_codes.append(passage.proto_room.code)

        area.stop_reset_events(except_these=room_codes)
        area.room_resets = []
        area.extract_rooms(except_these=room_codes)
    #- Fine Metodo -

    def remake(self, area):
        # Ricava le entità da salvarsi e trasportare nel nuovo labirinto
        players = []
        for player in area.players:
            self.send_remake_message(player)
            player = player.from_location(1, use_repop=False)
            players.append(player)
        entities = []
        for entity in area.iter_contains(use_reversed=True):
            if not entity.location:
                log.bug("location dell'entità %s non è valido: %r" % (entity.code, entity.location))
                continue
            if not entity.IS_PLAYER and entity.location.IS_ROOM:
                self.send_remake_message(entity)
                entity = entity.from_location(entity.quantity, use_repop=False)
                entities.append(entity)

        # Distrugge il vecchio labirinto e ne crea uno nuovo
        self.destroy(area)
        self.create(area)

        # Sposta le entità salvate precedentemente nel nuovo labirinto
        for entity in players + entities:
            if entity.previous_location() and entity.previous_location().IS_ROOM:
                coords = "%d %d %d" % (entity.previous_location().x, entity.previous_location().y, entity.previous_location().z)
                if coords in area.rooms:
                    room = area.rooms[coords]
                else:
                    room = random.choice(area.rooms.values())
            else:
                room = random.choice(area.rooms.values())
            entity.to_location(room)
    #- Fine Metodo -

    def send_remake_message(self, entity):
        if self.remake_message == "no_send":
            return

        if self.remake_message:
            message = "\n" + self.remake_message
        else:
            message = "\nD'improvviso le aperture e i corridoi attorno a te si muovono come mischiandosi e ti ritrovi smarrit$o."

        entity.send_output(message)
        entity.send_prompt()
    #- Fine Metodo -


class MazeCell(object):
    """
    Classe relativa ad una cella del labirinto.
    """
    def __init__(self):
        self.token   = None  # Reference to the div for when we're solving
        self.visited = False
        self.wall    = [True, True, True, True]
    #- Fine Inizializzazione -


class StackElement(object):
    """
    Elemento relativo alla lifo di generazione del labirinto.
    """
    def __init__(self, x, y, neighbors):
        self.x         = int(x)
        self.y         = int(y)
        self.neighbors = neighbors
    #- Fine Inizializzazione -


class MazePassage(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"proto_room"  : ["proto_rooms"]}
    WEAKREFS    = {}

    def __init__(self):
        self.x          = 0
        self.y          = 0
        self.z          = 0
        self.proto_room = None
    #- Fine Inizializzazione -

    def get_error_message(self, maze):
        if not self.proto_room:
            return "proto_room del passaggio %d %d %d non valida: %r" % (self.x, self.y, self.z, self.proto_room)

        if self.z != -1 and self.z != 0 and self.z != 1:
            return "coordinata z del passaggio %s non sui bordi" % self.proto_room.code

        if self.z == 0:
            if self.x >= 0 and self.x <= maze.columns - 1:
                if self.y != -1 and self.y != maze.rows:
                    return "coordinate x, y per il passaggio %s erano attese nel bordo superiore o inferiore, invece: %d %d" % (
                        self.proto_room.code, self.x, self.y)
            elif self.x == -1 or self.x == maze.columns:
                if self.y < -1 and self.y > maze.rows:
                    return "coordinate x, y per il passaggio %s erano attese nel bordo sinistro o destro, invece: %d %d" % (
                        self.proto_room.code, self.x, self.y)
            else:
                return "coordinate x, y del passaggio %s non sui bordi: %d %d" % (self.proto_room.code, self.x, self.y)
        else:
            if self.x < 0 or self.x >= maze.columns:
                return "coordinate x, y per il passaggio %s erano attese entro la superficie del labirinto, invece: %d %d" % (
                    self.proto_room.code, self.x, self.y)
            if self.y < 0 or self.y >= maze.rows:
                return "coordinate x, y per il passaggio %s erano attese entro la superficie del labirinto, invece: %d %d" % (
                    self.proto_room.code, self.x, self.y)

        return ""
    #- Fine Funzione -

    def fread_the_line(self, file, line, attr):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        values = line.split()

        if len(values) != 4:
            log.fread("Non sono stati ricavati 4 argomenti per il passaggio: %s" % line)
            return

        if not is_number(values[0]):
            log.fread("x non è una coordinata valida: %s" % values[0])
            return

        if not is_number(values[1]):
            log.fread("y non è una coordinata valida: %s" % values[1])
            return

        if not is_number(values[2]):
            log.fread("z non è una coordinata valida: %s" % values[2])
            return

        if not values[3]:
            log.fread("proto_room non è una codice di stanza prototipo valido: %r" % values[3])
            return

        self.x = int(values[0])
        self.y = int(values[1])
        self.z = int(values[2])
        self.proto_room = values[3]
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        file.write(indentation + label)
        file.write("%d %d %d %s\n" % (self.x, self.y, self.z, self.proto_room.code))
        file.write("\n")
    #- Fine Metodo -


class MazeDeadEnd(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"proto_room"  : ["proto_rooms"],
                   "proto_door"  : ["proto_items", "proto_mobs"]}
    WEAKREFS    = {}

    def __init__(self):
        self.proto_room = None  # Stanza che andrà al posto del vicolo cieco
        self.proto_door = None  # Opzionale, indica la porta con la quale chiudere il vicolo cieco
    #- Fine Inizializzazione -

    def get_error_message(self, maze):
        if not self.proto_room:
            return "proto_room di un vicolo cieco non valida: %r" % self.proto_room

        return ""
    #- Fine Funzione -

    def fread_the_line(self, file, line, attr):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        # (TD)
        return None
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        # (TD)
        pass
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def remake_mazes():
    for area in database["areas"].itervalues():
        if AREA.MAZE not in area.flags:
            continue
        if area.maze.remake_hour == -1:
            continue
        if calendar.hour != area.maze.remake_hour:
            continue
        if area.maze.remake_weekday != WEEKDAY.NONE and area.maze.remake_weekday != calendar.get_weekday():
            continue

        area.maze.remake(area)
#- Fine Funzione -
