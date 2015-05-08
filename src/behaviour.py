# -*- coding: utf-8 -*-

"""
Modulo riguardante i behaviour dei Mob e degli Item, ovvero dei comportamenti
automatici inviati di tanto in tanto.
"""


#= IMPORT ======================================================================

import datetime
import numbers
import random

from src.config       import config
from src.element      import Flags
from src.engine       import engine
from src.enums        import CONTAINER, DIR, DOOR, ENTITYPE, FLAG, RACE, ROOM, SECTOR
from src.database     import database
from src.interpret    import interpret_or_echo
from src.log          import log
from src.loop         import UnstoppableLoop
from src.miml         import MIML_SEPARATOR
from src.utility      import (copy_existing_attributes, to_capitalized_words,
                              multiple_arguments)
from src.web_resource import create_tooltip

from src.commands.command_north     import command_north
from src.commands.command_northeast import command_northeast
from src.commands.command_east      import command_east
from src.commands.command_southeast import command_southeast
from src.commands.command_south     import command_south
from src.commands.command_southwest import command_southwest
from src.commands.command_west      import command_west
from src.commands.command_northwest import command_northwest
from src.commands.command_up        import command_up
from src.commands.command_down      import command_down
from src.commands.command_open      import command_open
from src.commands.command_close     import command_close
from src.commands.command_enter     import command_enter
from src.commands.command_exit      import command_exit


#= COSTANTI ====================================================================

DIR_COMMANDS = {DIR.NORTH     : command_north,
                DIR.NORTHEAST : command_northeast,
                DIR.EAST      : command_east,
                DIR.SOUTHEAST : command_southeast,
                DIR.SOUTH     : command_south,
                DIR.SOUTHWEST : command_southwest,
                DIR.WEST      : command_west,
                DIR.NORTHWEST : command_northwest,
                DIR.UP        : command_up,
                DIR.DOWN      : command_down}


#= VARIABILI ===================================================================

# Variabili che tengono traccia dell'utilizzo dei behaviour, tali informazioni
# vengono stampate allo shutdown del Mud
item_behaviour_tracker      = {}
mob_behaviour_tracker       = {}
room_behaviour_tracker      = {}
room_item_behaviour_tracker = {}
room_mob_behaviour_tracker  = {}


#= CLASSI ======================================================================

class _BehaviourHandler(object):
    """
    I metodi di questa classe sono un po' boiler plate, è per via di una
    questione prestazionale.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"random_do_inputs" : ("", "str")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __repr__(self):
        look_total      = get_total_percent(self, "look")
        listen_total    = get_total_percent(self, "listen")
        smell_total     = get_total_percent(self, "smell")
        touch_total     = get_total_percent(self, "touch")
        taste_total     = get_total_percent(self, "taste")
        intuition_total = get_total_percent(self, "intuition")
        wander_total    = get_total_percent(self, "wander")
        random_total    = get_total_percent(self, "random")

        return "%s: look=%d listen=%d smell=%d touch=%d taste=%d intuition=%d wander=%d random=%d" % (
            super(_BehaviourHandler, self).__repr__, look_total, listen_total, smell_total, touch_total, taste_total, intuition_total, wander_total, random_total)
    #- Fine Metodo -

    def get_error_message(self):
        if self.look < 0 or self.look > config.max_behaviour_probability:
            return "look dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look)
        if self.look_player < 0 or self.look_player > config.max_behaviour_probability:
            return "look_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_player)
        elif self.look_mob < 0 or self.look_mob > config.max_behaviour_probability:
            return "look_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_mob)
        elif self.look_item < 0 or self.look_item > config.max_behaviour_probability:
            return "look_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_item)
        elif self.look_self < 0 or self.look_self > config.max_behaviour_probability:
            return "look_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_self)
        elif self.look_at_races < 0 or self.look_at_races > config.max_behaviour_probability:
            return "look_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_at_races)
        elif self.look_at_races > 0 and not self.look_at_races_flags:
            return "look_at_races_flags deve avere impostata almeno una poiché flag look_at_races è %d" % self.look_at_races
        elif self.look_at_races_flags.get_error_message(RACE, "look_at_races_flags") != "":
            return self.look_at_races_flags.get_error_message(RACE, "look_at_races_flags")
        elif self.look_at_entitypes < 0 or self.look_at_entitypes > config.max_behaviour_probability:
            return "look_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_at_entitypes)
        elif self.look_at_entitypes > 0 and not self.look_at_entitypes_flags:
            return "look_at_entitypes_flags deve avere impostata almeno una poiché flag look_at_entitypes è %d" % self.look_at_entitypes
        elif self.look_at_entitypes_flags.get_error_message(ENTITYPE, "look_at_entitypes_flags") != "":
            return self.look_at_entitypes_flags.get_error_message(ENTITYPE, "look_at_entitypes_flags")
        elif self.look_direction < 0 or self.look_direction > config.max_behaviour_probability:
            return "look_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_direction)
        elif self.look_exit < 0 or self.look_exit > config.max_behaviour_probability:
            return "look_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_exit)
        elif self.look_wall < 0 or self.look_wall > config.max_behaviour_probability:
            return "look_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_wall)
        elif self.look_closed_door < 0 or self.look_closed_door > config.max_behaviour_probability:
            return "look_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_closed_door)
        elif self.look_extra < 0 or self.look_extra > config.max_behaviour_probability:
            return "look_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_extra)
        elif self.look_equipment < 0 or self.look_equipment > config.max_behaviour_probability:
            return "look_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_equipment)
        elif self.look_inventory < 0 or self.look_inventory > config.max_behaviour_probability:
            return "look_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.look_inventory)
        elif self.listen < 0 or self.listen > config.max_behaviour_probability:
            return "listen dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen)
        elif self.listen_player < 0 or self.listen_player > config.max_behaviour_probability:
            return "listen_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_player)
        elif self.listen_mob < 0 or self.listen_mob > config.max_behaviour_probability:
            return "listen_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_mob)
        elif self.listen_item < 0 or self.listen_item > config.max_behaviour_probability:
            return "listen_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_item)
        elif self.listen_self < 0 or self.listen_self > config.max_behaviour_probability:
            return "listen_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_self)
        elif self.listen_at_races < 0 or self.listen_at_races > config.max_behaviour_probability:
            return "listen_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_at_races)
        elif self.listen_at_races > 0 and not self.listen_at_races_flags:
            return "listen_at_races_flags deve avere impostata almeno una poiché flag listen_at_races è %d" % self.listen_at_races
        elif self.listen_at_races_flags.get_error_message(RACE, "listen_at_races_flags") != "":
            return self.listen_at_races_flags.get_error_message(RACE, "listen_at_races_flags")
        elif self.listen_at_entitypes < 0 or self.listen_at_entitypes > config.max_behaviour_probability:
            return "listen_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_at_entitypes)
        elif self.listen_at_entitypes > 0 and not self.listen_at_entitypes_flags:
            return "listen_at_entitypes_flags deve avere impostata almeno una poiché flag listen_at_entitypes è %d" % self.listen_at_entitypes
        elif self.listen_at_entitypes_flags.get_error_message(ENTITYPE, "listen_at_entitypes_flags") != "":
            return self.listen_at_entitypes_flags.get_error_message(ENTITYPE, "listen_at_entitypes_flags")
        elif self.listen_direction < 0 or self.listen_direction > config.max_behaviour_probability:
            return "listen_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_direction)
        elif self.listen_exit < 0 or self.listen_exit > config.max_behaviour_probability:
            return "listen_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_exit)
        elif self.listen_wall < 0 or self.listen_wall > config.max_behaviour_probability:
            return "listen_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_wall)
        elif self.listen_closed_door < 0 or self.listen_closed_door > config.max_behaviour_probability:
            return "listen_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_closed_door)
        elif self.listen_extra < 0 or self.listen_extra > config.max_behaviour_probability:
            return "listen_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_extra)
        elif self.listen_equipment < 0 or self.listen_equipment > config.max_behaviour_probability:
            return "listen_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_equipment)
        elif self.listen_inventory < 0 or self.listen_inventory > config.max_behaviour_probability:
            return "listen_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.listen_inventory)
        elif self.smell < 0 or self.smell > config.max_behaviour_probability:
            return "smell dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell)
        elif self.smell_player < 0 or self.smell_player > config.max_behaviour_probability:
            return "smell_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_player)
        elif self.smell_mob < 0 or self.smell_mob > config.max_behaviour_probability:
            return "smell_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_mob)
        elif self.smell_item < 0 or self.smell_item > config.max_behaviour_probability:
            return "smell_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_item)
        elif self.smell_self < 0 or self.smell_self > config.max_behaviour_probability:
            return "smell_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_self)
        elif self.smell_at_races < 0 or self.smell_at_races > config.max_behaviour_probability:
            return "smell_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_at_races)
        elif self.smell_at_races > 0 and not self.smell_at_races_flags:
            return "smell_at_races_flags deve avere impostata almeno una poiché flag smell_at_races è %d" % self.smell_at_races
        elif self.smell_at_races_flags.get_error_message(RACE, "smell_at_races_flags") != "":
            return self.smell_at_races_flags.get_error_message(RACE, "smell_at_races_flags")
        elif self.smell_at_entitypes < 0 or self.smell_at_entitypes > config.max_behaviour_probability:
            return "smell_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_at_entitypes)
        elif self.smell_at_entitypes > 0 and not self.smell_at_entitypes_flags:
            return "smell_at_entitypes_flags deve avere impostata almeno una poiché flag smell_at_entitypes è %d" % self.smell_at_entitypes
        elif self.smell_at_entitypes_flags.get_error_message(ENTITYPE, "smell_at_entitypes_flags") != "":
            return self.smell_at_entitypes_flags.get_error_message(ENTITYPE, "smell_at_entitypes_flags")
        elif self.smell_direction < 0 or self.smell_direction > config.max_behaviour_probability:
            return "smell_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_direction)
        elif self.smell_exit < 0 or self.smell_exit > config.max_behaviour_probability:
            return "smell_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_exit)
        elif self.smell_wall < 0 or self.smell_wall > config.max_behaviour_probability:
            return "smell_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_wall)
        elif self.smell_closed_door < 0 or self.smell_closed_door > config.max_behaviour_probability:
            return "smell_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_closed_door)
        elif self.smell_extra < 0 or self.smell_extra > config.max_behaviour_probability:
            return "smell_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_extra)
        elif self.smell_equipment < 0 or self.smell_equipment > config.max_behaviour_probability:
            return "smell_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_equipment)
        elif self.smell_inventory < 0 or self.smell_inventory > config.max_behaviour_probability:
            return "smell_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.smell_inventory)
        elif self.touch < 0 or self.touch > config.max_behaviour_probability:
            return "touch dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch)
        elif self.touch_player < 0 or self.touch_player > config.max_behaviour_probability:
            return "touch_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_player)
        elif self.touch_mob < 0 or self.touch_mob > config.max_behaviour_probability:
            return "touch_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_mob)
        elif self.touch_item < 0 or self.touch_item > config.max_behaviour_probability:
            return "touch_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_item)
        elif self.touch_self < 0 or self.touch_self > config.max_behaviour_probability:
            return "touch_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_self)
        elif self.touch_at_races < 0 or self.touch_at_races > config.max_behaviour_probability:
            return "touch_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_at_races)
        elif self.touch_at_races > 0 and not self.touch_at_races_flags:
            return "touch_at_races_flags deve avere impostata almeno una poiché flag touch_at_races è %d" % self.touch_at_races
        elif self.touch_at_races_flags.get_error_message(RACE, "touch_at_races_flags") != "":
            return self.touch_at_races_flags.get_error_message(RACE, "touch_at_races_flags")
        elif self.touch_at_entitypes < 0 or self.touch_at_entitypes > config.max_behaviour_probability:
            return "touch_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_at_entitypes)
        elif self.touch_at_entitypes > 0 and not self.touch_at_entitypes_flags:
            return "touch_at_entitypes_flags deve avere impostata almeno una poiché flag touch_at_entitypes è %d" % self.touch_at_entitypes
        elif self.touch_at_entitypes_flags.get_error_message(ENTITYPE, "touch_at_entitypes_flags") != "":
            return self.touch_at_entitypes_flags.get_error_message(ENTITYPE, "touch_at_entitypes_flags")
        elif self.touch_direction < 0 or self.touch_direction > config.max_behaviour_probability:
            return "touch_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_direction)
        elif self.touch_exit < 0 or self.touch_exit > config.max_behaviour_probability:
            return "touch_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_exit)
        elif self.touch_wall < 0 or self.touch_wall > config.max_behaviour_probability:
            return "touch_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_wall)
        elif self.touch_closed_door < 0 or self.touch_closed_door > config.max_behaviour_probability:
            return "touch_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_closed_door)
        elif self.touch_extra < 0 or self.touch_extra > config.max_behaviour_probability:
            return "touch_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_extra)
        elif self.touch_equipment < 0 or self.touch_equipment > config.max_behaviour_probability:
            return "touch_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_equipment)
        elif self.touch_inventory < 0 or self.touch_inventory > config.max_behaviour_probability:
            return "touch_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.touch_inventory)
        elif self.taste < 0 or self.taste > config.max_behaviour_probability:
            return "taste dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste)
        elif self.taste_player < 0 or self.taste_player > config.max_behaviour_probability:
            return "taste_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_player)
        elif self.taste_mob < 0 or self.taste_mob > config.max_behaviour_probability:
            return "taste_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_mob)
        elif self.taste_item < 0 or self.taste_item > config.max_behaviour_probability:
            return "taste_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_item)
        elif self.taste_self < 0 or self.taste_self > config.max_behaviour_probability:
            return "taste_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_self)
        elif self.taste_at_races < 0 or self.taste_at_races > config.max_behaviour_probability:
            return "taste_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_at_races)
        elif self.taste_at_races > 0 and not self.taste_at_races_flags:
            return "taste_at_races_flags deve avere impostata almeno una poiché flag taste_at_races è %d" % self.taste_at_races
        elif self.taste_at_races_flags.get_error_message(RACE, "taste_at_races_flags") != "":
            return self.taste_at_races_flags.get_error_message(RACE, "taste_at_races_flags")
        elif self.taste_at_entitypes < 0 or self.taste_at_entitypes > config.max_behaviour_probability:
            return "taste_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_at_entitypes)
        elif self.taste_at_entitypes > 0 and not self.taste_at_entitypes_flags:
            return "taste_at_entitypes_flags deve avere impostata almeno una poiché flag taste_at_entitypes è %d" % self.taste_at_entitypes
        elif self.taste_at_entitypes_flags.get_error_message(ENTITYPE, "taste_at_entitypes_flags") != "":
            return self.taste_at_entitypes_flags.get_error_message(ENTITYPE, "taste_at_entitypes_flags")
        elif self.taste_direction < 0 or self.taste_direction > config.max_behaviour_probability:
            return "taste_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_direction)
        elif self.taste_exit < 0 or self.taste_exit > config.max_behaviour_probability:
            return "taste_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_exit)
        elif self.taste_wall < 0 or self.taste_wall > config.max_behaviour_probability:
            return "taste_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_wall)
        elif self.taste_closed_door < 0 or self.taste_closed_door > config.max_behaviour_probability:
            return "taste_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_closed_door)
        elif self.taste_extra < 0 or self.taste_extra > config.max_behaviour_probability:
            return "taste_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_extra)
        elif self.taste_equipment < 0 or self.taste_equipment > config.max_behaviour_probability:
            return "taste_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_equipment)
        elif self.taste_inventory < 0 or self.taste_inventory > config.max_behaviour_probability:
            return "taste_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.taste_inventory)
        elif self.intuition < 0 or self.intuition > config.max_behaviour_probability:
            return "intuition dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition)
        elif self.intuition_player < 0 or self.intuition_player > config.max_behaviour_probability:
            return "intuition_player dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_player)
        elif self.intuition_mob < 0 or self.intuition_mob > config.max_behaviour_probability:
            return "intuition_mob dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_mob)
        elif self.intuition_item < 0 or self.intuition_item > config.max_behaviour_probability:
            return "intuition_item dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_item)
        elif self.intuition_self < 0 or self.intuition_self > config.max_behaviour_probability:
            return "intuition_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_self)
        elif self.intuition_at_races < 0 or self.intuition_at_races > config.max_behaviour_probability:
            return "intuition_at_races dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_at_races)
        elif self.intuition_at_races > 0 and not self.intuition_at_races_flags:
            return "intuition_at_races_flags deve avere impostata almeno una poiché flag intuition_at_races è %d" % self.intuition_at_races
        elif self.intuition_at_races_flags.get_error_message(RACE, "intuition_at_races_flags") != "":
            return self.intuition_at_races_flags.get_error_message(RACE, "intuition_at_races_flags")
        elif self.intuition_at_entitypes < 0 or self.intuition_at_entitypes > config.max_behaviour_probability:
            return "intuition_at_entitypes dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_at_entitypes)
        elif self.intuition_at_entitypes > 0 and not self.intuition_at_entitypes_flags:
            return "intuition_at_entitypes_flags deve avere impostata almeno una poiché flag intuition_at_entitypes è %d" % self.intuition_at_entitypes
        elif self.intuition_at_entitypes_flags.get_error_message(ENTITYPE, "intuition_at_entitypes_flags") != "":
            return self.intuition_at_entitypes_flags.get_error_message(ENTITYPE, "intuition_at_entitypes_flags")
        elif self.intuition_direction < 0 or self.intuition_direction > config.max_behaviour_probability:
            return "intuition_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_direction)
        elif self.intuition_exit < 0 or self.intuition_exit > config.max_behaviour_probability:
            return "intuition_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_exit)
        elif self.intuition_wall < 0 or self.intuition_wall > config.max_behaviour_probability:
            return "intuition_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_wall)
        elif self.intuition_closed_door < 0 or self.intuition_closed_door > config.max_behaviour_probability:
            return "intuition_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_closed_door)
        elif self.intuition_extra < 0 or self.intuition_extra > config.max_behaviour_probability:
            return "intuition_extra dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_extra)
        elif self.intuition_equipment < 0 or self.intuition_equipment > config.max_behaviour_probability:
            return "intuition_equipment dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_equipment)
        elif self.intuition_inventory < 0 or self.intuition_inventory > config.max_behaviour_probability:
            return "intuition_inventory dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.intuition_inventory)
        elif self.wander_direction < 0 or self.wander_direction > config.max_behaviour_probability:
            return "wander_direction dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_direction)
        elif self.wander_exit < 0 or self.wander_exit > config.max_behaviour_probability:
            return "wander_exit dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_exit)
        elif self.wander_wall < 0 or self.wander_wall > config.max_behaviour_probability:
            return "wander_wall dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_wall)
        elif self.wander_closed_door < 0 or self.wander_closed_door > config.max_behaviour_probability:
            return "wander_closed_door dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_closed_door)
        elif self.wander_area < 0 or self.wander_area > config.max_behaviour_probability:
            return "wander_area dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_area)
        elif self.wander_at_exits < 0 or self.wander_at_exits > config.max_behaviour_probability:
            return "wander_at_exits dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_at_exits)
        elif self.wander_at_exits > 0 and not self.wander_at_exits_flags:
            return "wander_at_exits_flags deve avere impostata almeno una poiché flag wander_at_exits è %d" % self.wander_at_exits
        elif self.wander_at_exits_flags.get_error_message(DIR, "wander_at_exits_flags") != "":
            return self.wander_at_exits_flags.get_error_message(DIR, "wander_at_exits_flags")
        elif self.wander_at_sectors.get_error_message(SECTOR, "wander_at_sectors") != "":
            return self.wander_at_sectors.get_error_message(SECTOR, "wander_at_sectors")
        elif self.wander_portal < 0 or self.wander_portal > config.max_behaviour_probability:
            return "wander_portal dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_portal)
        elif self.wander_enter_container < 0 or self.wander_enter_container > config.max_behaviour_probability:
            return "wander_enter_container dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_enter_container)
        elif self.wander_exit_container < 0 or self.wander_exit_container > config.max_behaviour_probability:
            return "wander_exit_container dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_exit_container)
        elif self.wander_self < 0 or self.wander_self > config.max_behaviour_probability:
            return "wander_self dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.wander_self)
        elif self.random_do < 0 or self.random_do > config.max_behaviour_probability:
            return "random_do dev'essere un numero tra 0 e %d, invece è: %d" % (config.max_behaviour_probability, self.random_do)
        elif self.random_do > 0 and not self.random_do_inputs:
            return "random_do_inputs vuoto con random_do a %d: %r" % (self.random_do, self.random_do_inputs)
        elif self.get_error_message_random_do_inputs() != "":
            return self.get_error_message_random_do_inputs()

        return ""
    #- Fine Metodo -

    def get_error_message_random_do_inputs(self):
        for random_do_input in self.random_do_inputs:
            if len(random_do_input) > config.max_google_translate:
                return "random_do_input %r più lungo di %d caratteri." % (random_do_input, config.max_google_translate)

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        """
        Il metodo viene implementato nelle classi specializzate.
        """
        raise NotImplementedError
    #- Fine Metodo -

    def equals(self, behaviour2):
        if not behaviour2:
            return False

        items1 = self.__dict__.items()
        items2 = behaviour2.__dict__.items()
        if len(items1) != len(items2):
            return False

        for attr_name, value in items1:
            if attr_name == "random_do_inputs":
                continue
            if not hasattr(behaviour2, attr_name):
                return False
            if value != getattr(behaviour2, attr_name):
                return False

        if len(self.random_do_inputs) != len(behaviour2.random_do_inputs):
            return False
        for input in self.random_do_inputs:
            for input2 in behaviour2.random_do_inputs:
                if input == input2:
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    # - Behaviour relativi ai 6 sensi ------------------------------------------

    def update_sense(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso nella locazione corrente.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name):
            execution = command_function(entity, "", behavioured=True)
            return execution

        return False
    #- Fine Metodo -

    def update_sense_player(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso sui giocatori nella locazione
        corrente.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_player"):
            # Tramite list viene eseguita una copia della lista, questo serve
            # perché il metodo _update_sense_to_target esegue dei remove agli
            # elementi
            entities = list(getattr(entity.location, "players"))

            # Se è una porta ed è anche dall'altra parte allora potrebbe
            # invece ricavare le entità dall'altra parte
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()
                    entities = list(getattr(destination_room, "players"))

            execution = self._update_sense_to_target(entity, entities, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_mob(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso sui mob nella locazione corrente.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_mob"):
            entities = list(getattr(entity.location, "mobs"))

            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()
                    entities = list(getattr(destination_room, "mobs"))

            execution = self._update_sense_to_target(entity, entities, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_item(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso sugli oggetti nella locazione
        corrente.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_item"):
            entities = list(getattr(entity.location, "items"))

            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()
                    entities = list(getattr(destination_room, "items"))

            execution = self._update_sense_to_target(entity, entities, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_self(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso su sé stessi.
        """
        # La flag NO_LOOK_LIST è intesa da utilizzare per rendere non visibili
        # subitamente le entità, ma comunque interagibili se uno cerca un po'
        # quindi il check viene eseguito per tutti i sensi, altrimenti un mob,
        # annusando un'entità, potrebbe involontariamente far scoprirne
        # l'esistenza
        if (FLAG.NO_LOOK_LIST not in entity.flags and entity.incognito
        and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_self")):
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            execution = self._update_sense_to_target(entity, [entity, ], input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_at_races(self, entity, input_name, command_function):
        """
        Comportamento che fa eseguire un senso alle entità di una determinata
        razza nella locazione corrente.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_at_races"):
            sensable_actors = []
            sense_at_races_flags = getattr(self, input_name + "_at_races_flags")

            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            for actor in entity.location.iter_contains(("mobs", "players")):
                if actor.race in sense_at_races_flags:
                    if entity.can_see(actor):
                        sensable_actors.append(actor)

            execution = self._update_sense_to_target(entity, sensable_actors, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_an_entitypes(self, entity, input_name, command_function):
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_at_entitypes"):
            sensable_actors = []
            sense_an_entitypes_flags = getattr(self, input_name + "_at_entitypes_flags")

            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            for item in entity.location.items:
                if item.entitype in sense_an_entitypes_flags:
                    if entity.can_see(item):
                        sensable_actors.append(item)

            execution = self._update_sense_to_target(entity, sensable_actors, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_direction(self, entity, input_name, command_function):
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if entity.location.IS_ROOM and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_direction"):
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            choised_direction = random.choice(DIR.elements)
            execution = self._update_sense_at_direction(entity, choised_direction, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_exit(self, entity, input_name, command_function):
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.exits
        and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_exit")):
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            directions = []
            for direction in entity.location.exits:
                door = entity.location.get_door(direction)
                if door and DOOR.CLOSED not in door.door_type.flags:
                    directions.append(direction)

            if directions:
                choised_direction = random.choice(directions)
                execution = self._update_sense_at_direction(entity, choised_direction, input_name, command_function)
                if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                    entity.to_reverse_hinges()
                return execution

        return False
    #- Fine Metodo -

    def update_sense_wall(self, entity, input_name, command_function):
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.walls
        and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_wall")):
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            choised_direction = random.choice(entity.location.walls.keys())
            execution = self._update_sense_at_direction(entity, choised_direction, input_name, command_function)
            if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                entity.to_reverse_hinges()
            return execution

        return False
    #- Fine Metodo -

    def update_sense_closed_door(self, entity, input_name, command_function):
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.exits
        and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_closed_door")):
            original_location = None
            if entity.door_type and random.randint(0, 1) == 1:
                destination_room, direction = entity.to_reverse_hinges()
                if destination_room:
                    original_location = entity.previous_location()

            directions = []
            for direction in entity.location.exits:
                door = entity.location.get_door(direction)
                if door and DOOR.CLOSED in door.door_type.flags:
                    directions.append(direction)

            if directions:
                choised_direction = random.choice(directions)
                execution =  self._update_sense_at_direction(entity, choised_direction, input_name, command_function)
                if original_location and original_location == entity.previous_location() and not entity.is_extracted():
                    entity.to_reverse_hinges()
                return execution

        return False
    #- Fine Metodo -

    def _update_sense_to_target(self, entity, entities, input_name, command_function):
        # Rimuove l'entità dalla lista perché il comportamento di guardare sé
        # stessi viene gestito separatamente
        if entity in entities:
            entities.remove(entity)
        if not entities:
            return False

        for target in reversed(entities):
            if not entity.can_see(target):
                entities.remove(target)
            # C'è un commento sopra relativo alla flag NO_LOOK_LIST che
            # potrebbe chiarire come mai viene utilizzata per tutti i sensi
            if FLAG.NO_LOOK_LIST in target.flags:
                entities.remove(target)

        if entities:
            target = random.choice(entities)
            equipment_targets = []
            inventory_targets = []
            search_in_inventory = False
            if not target.location:
                log.bug("target %s non è contenuto da nessuna parte" % target.code)
                return
            if not target.location.IS_ROOM and target.location.container_type and CONTAINER.CLOSED not in target.location.container_type.flags:
                search_in_inventory = True
            for en in target.iter_contains():
                if len(en.wear_mode) > 0:
                    equipment_targets.append(en)
                elif FLAG.INGESTED not in en.flags and FLAG.BURIED not in en.flags:
                    inventory_targets.append(en)
            numbered_keyword = target.get_numbered_keyword(looker=entity)
            if target.extras and hasattr(self, input_name + "_extra") and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_extra"):
                extra = random.choice(target.extras)
                command_function(entity, "%s %s" % (extra.keywords.split()[0], numbered_keyword), behavioured=True)
            elif equipment_targets and hasattr(self, input_name + "_equipment") and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_equipment"):
                equipped = random.choice(equipment_targets)
                command_function(entity, "%s %s" % (equipped.get_numbered_keyword(looker=entity), numbered_keyword), behavioured=True)
            elif inventory_targets and hasattr(self, input_name + "_inventory") and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_inventory"):
                inventory = random.choice(equipment_targets)
                command_function(entity, "%s %s" % (inventory.get_numbered_keyword(looker=entity), numbered_keyword), behavioured=True)
            else:
                command_function(entity, numbered_keyword, behavioured=True)
            return True

        return False
    #- Fine Metodo -

    def _update_sense_at_direction(self, entity, direction, input_name, command_function):
        extras = None
        if direction in entity.location.exits and entity.location.exits[direction].extras:
            extras = entity.location.exits[direction].extras
        elif direction in entity.location.walls and entity.location.walls[direction].extras:
            extras = entity.location.walls[direction].extras

        if extras and random.randint(1, config.max_behaviour_probability) <= getattr(self, input_name + "_extra"):
            extra = random.choice(extras)
            command_function(entity, "%s %s" % (direction.english_nocolor, extra.keywords.split()[0]), behavioured=True)
        else:
            command_function(entity, direction.english_nocolor, behavioured=True)

        return True
    #- Fine Metodo -

    # - Behaviour relativi al movimento ----------------------------------------

    def update_wander_direction(self, entity):
        """
        Azione di movimento in una direzione qualsiasi.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if entity.location.IS_ROOM and random.randint(1, config.max_behaviour_probability) <= self.wander_direction:
            direction = random.choice(DIR.elements)
            door = entity.location.get_door(direction)
            # Da finire il sistema delle closed door
#            if BEHAVIOUR.WANDER_DIRECTION_CLOSED_DOOR:
#                if not door or (DOOR.CLOSED in door.door_type.flags and DOOR.SECRET not in door.door_type.flags):
#                    return self._update_wander_at_direction(entity, direction)
#            else:
            if not door or (DOOR.CLOSED not in door.door_type.flags):
                return self._update_wander_at_direction(entity, direction)

        return False
    #- Fine Metodo -

    def update_wander_exit(self, entity):
        """
        Azione di movimento tra uscite reali.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.exits
        and random.randint(1, config.max_behaviour_probability) <= self.wander_exit):
            directions = []
            for direction in entity.location.exits:
                door = entity.location.get_door(direction)
                if not door or (DOOR.CLOSED not in door.door_type.flags):
                    directions.append(direction)
            if directions:
                choised_direction = random.choice(directions)
                return self._update_wander_at_direction(entity, choised_direction)

        return False
    #- Fine Metodo -

    def update_wander_wall(self, entity):
        # Azione di movimento tra le mura
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.walls
        and random.randint(1, config.max_behaviour_probability) <= self.wander_wall):
            direction = random.choice(entity.location.walls.keys())
            return self._update_wander_at_direction(entity, direction)

        return False
    #- Fine Metodo -

    def update_wander_closed_door(self, entity):
        """
        Azione di movimento tra le sole porte chiuse
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and entity.location.exits
        and random.randint(1, config.max_behaviour_probability) <= self.wander_closed_door):
            directions = []
            for direction in entity.location.exits:
                door = entity.location.get_door(direction)
                if door and DOOR.CLOSED in door.door_type.flags and DOOR.SECRET not in door.door_type.flags:
                    directions.append(direction)
            if directions:
                choised_direction = random.choice(directions)
                return self._update_wander_at_direction(entity, choised_direction)

        return False
    #- Fine Metodo -

    def update_wander_at_exits(self, entity):
        """
        Azione di movimento ad una determinata direzione.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        if (entity.location.IS_ROOM and self.wander_at_exits_flags
        and random.randint(1, config.max_behaviour_probability) <= self.wander_at_exits):
            directions = []
            for direction in entity.location.exits:
                door = entity.location.get_door(direction)
                if not door or (DOOR.CLOSED in door.door_type.flags and DOOR.SECRET not in door.door_type.flags):
                    directions.append(direction)
            if directions:
                direction = random.choice(directions)
                return self._update_wander_at_direction(entity, direction)

        return False
    #- Fine Metodo -

    def update_wander_portal(self, entity):
        """
        Azione di movimento nei portali.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        # È voluto che il wander_portal non esegua un check sul wander_area
        if random.randint(1, config.max_behaviour_probability) <= self.wander_portal:
            portals = []
            for target in entity.location.iter_contains():
                if not entity.can_see(target):
                    continue
                if target.entitype == ENTITYPE.PORTAL:
                    portals.append(target)
            if not portals:
                return False
            portal = random.choice(portals)
            if entity == portal and random.randint(1, config.max_behaviour_probability) > self.wander_self:
                return False
            portal_keyword = portal.get_numbered_keyword(looker=entity)
            command_enter(entity, portal_keyword)
            return True

        return False
    #- Fine Metodo -

    def update_wander_enter_container(self, entity):
        """
        Azione di movimento di entrare nei contenitori.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        # È voluto che il wander_enter_container non esegua un check sul wander_area
        if random.randint(1, config.max_behaviour_probability) <= self.wander_enter_container:
            containers = []
            for target in entity.location.iter_contains():
                if not entity.can_see(target):
                    continue
                if target.entitype == ENTITYPE.CONTAINER:
                    containers.append(target)
            if not containers:
                return False
            container = random.choice(containers)
            if entity == container and random.randint(1, config.max_behaviour_probability) > self.wander_self:
                return False
            container_keyword = container.get_numbered_keyword(looker=entity)
            command_enter(entity, container_keyword)
            return True

        return False
    #- Fine Metodo -

    def update_wander_exit_container(self, entity):
        """
        Azione di movimento di entrare dai contenitori.
        """
        if not entity.location:
            log.bug("location non è valida per %r: %r" % (entity, entity.location))

        # È voluto che il wander_exit_container non esegua un check sul wander_area
        if random.randint(1, config.max_behaviour_probability) <= self.wander_exit_container:
            containers = []
            for target in entity.location.iter_contains():
                if not entity.can_see(target):
                    continue
                if target.entitype == ENTITYPE.CONTAINER:
                    containers.append(target)
            if not containers:
                return False
            container = random.choice(containers)
            if entity == container and random.randint(1, config.max_behaviour_probability) > self.wander_self:
                return False
            container_keyword = container.get_numbered_keyword(looker=entity)
            command_exit(entity, container_keyword)
            return True

        return False
    #- Fine Metodo -

    def _update_wander_at_direction(self, entity, direction):
        if not direction or direction == DIR.NONE:
            log.bug("direction è un parametro non valido: %r" % direction)
            return False

        # ---------------------------------------------------------------------

        # Evita di far uscire l'entità dall'area se è il caso
        destination_room = entity.location.get_destination_room(direction)
        if destination_room:
            if destination_room.area != entity.location.area:
                if random.randint(1, config.max_behaviour_probability) > self.wander_area:
                    return False
            # Evita di andare in settori non voluti; questa parte di codice sballa
            # un po' la probabilità che entri un wander in direzioni valide,
            # tuttavia poiché già i behaviour sono pesantucci lato CPU è preferibile
            # che il controllo sia centralizzato qui piuttosto che calcolare
            # se le varie direzioni da cui pescare la casuale sia adatta o meno
            if self.wander_at_sectors and destination_room.sector not in self.wander_at_sectors:
                return False

        command_function = DIR_COMMANDS[direction]

        door = entity.location.get_door(direction)
        if door and DOOR.CLOSED in door.door_type.flags:
            # (TD) in futuro evitare di eseguire i comandi in rapida successione
            # e magari aspettare il codice di ritorno di ognuno per vedere se
            # eseguire quello successivo
            if DOOR.NO_USE_DIR in door.door_type.flags:
                argument = door.get_numbered_keyword(looker=entity)
                command_open(entity, argument)
                command_function(entity, "", behavioured=True)
                # (TD) (BB) Qui però se l'altro lato della porta ha una keyword
                # differente allora argument non è corretto e il comando non funziona
                command_close(entity, argument)
            else:
                command_open(entity, direction.english_nocolor)
                command_function(entity, "", behavioured=True)
                # (TT) (bb) qui però mi sa che con uscite con Destination il
                # reverse non serva ad un tubino.. però... da provare
                command_close(entity, direction.reverse_dir.english_nocolor)
        else:
            command_function(entity, "", behavioured=True)

        return True
    #- Fine Metodo -

    # - Altre tipologie di behaviour -------------------------------------------

    def update_random_do(self, entity):
        if self.random_do <= 0 or not self.random_do_inputs:
            return False

        if random.randint(1, config.max_behaviour_probability) > self.random_do:
            return False

        original_location = None
        if entity.door_type and random.randint(0, 1) == 1:
            destination_room, direction = entity.to_reverse_hinges()
            if destination_room:
                original_location = entity.previous_location()

        # Se l'input scelto a caso è un comando vero e proprio allora lo invia
        # come comando, altrimenti come messaggio di echo.
        argument = random.choice(self.random_do_inputs)
        interpret_or_echo(entity, argument, behavioured=True)

        if original_location and original_location == entity.previous_location() and not entity.is_extracted():
            entity.to_reverse_hinges()

        return True
    #- Fine Metodo -


class MobBehaviour(_BehaviourHandler):
    def __init__(self):
        super(MobBehaviour, self).__init__()

        self.look                         = 1  # Percentuale di look nella locazione
        self.look_player                  = 1  # Percentuale di look sui pg
        self.look_mob                     = 1  # Percentuale di look sui mob
        self.look_item                    = 1  # Percentuale di look sugli oggetti
        self.look_self                    = 1  # Percentuale di look su sé stessi
        self.look_at_races                = 0  # Percentuale relativa al look sulle razze
        self.look_at_races_flags          = Flags(RACE.NONE)  # Tipi di razze guardabili, se NONE tutte
        self.look_at_entitypes            = 0  # Percentuale relativa al look sulle entitype
        self.look_at_entitypes_flags      = Flags(ENTITYPE.NONE)  # Tipi di entità guardabili, se NONE tutte
        self.look_direction               = 1  # Percentuale di look su tutte le direzioni
        self.look_exit                    = 0  # Percentuale di look sulle uscite reali e aperte
        self.look_wall                    = 0  # Percentuale di look sui wall esistenti
        self.look_closed_door             = 0  # Percentuale di look sulle porte chiuse  # (TD) attenzione alle exit con flag in cui non si può utilizzare la direction
        self.look_extra                   = 1  # Percentuale di look sulle extra di uno dei look di cui sopra
        self.look_equipment               = 0  # Percentuale di look sui pezzi di equipaggiamento dell'entità guardata
        self.look_inventory               = 0  # Percentuale di look sui pezzi in inventario per i contenitori aperti

        self.listen                       = 1
        self.listen_player                = 1
        self.listen_mob                   = 1
        self.listen_item                  = 1
        self.listen_self                  = 1
        self.listen_at_races              = 0
        self.listen_at_races_flags        = Flags(RACE.NONE)
        self.listen_at_entitypes          = 0
        self.listen_at_entitypes_flags    = Flags(ENTITYPE.NONE)
        self.listen_direction             = 1
        self.listen_exit                  = 0
        self.listen_wall                  = 0
        self.listen_closed_door           = 0
        self.listen_extra                 = 1
        self.listen_equipment             = 0
        self.listen_inventory             = 0

        self.smell                        = 1
        self.smell_player                 = 1
        self.smell_mob                    = 1
        self.smell_item                   = 1
        self.smell_self                   = 1
        self.smell_at_races               = 0
        self.smell_at_races_flags         = Flags(RACE.NONE)
        self.smell_at_entitypes           = 0
        self.smell_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.smell_direction              = 1
        self.smell_exit                   = 0
        self.smell_wall                   = 0
        self.smell_closed_door            = 0
        self.smell_extra                  = 1
        self.smell_equipment              = 0
        self.smell_inventory              = 0

        self.touch                        = 1
        self.touch_player                 = 1
        self.touch_mob                    = 1
        self.touch_item                   = 1
        self.touch_self                   = 0
        self.touch_at_races               = 0
        self.touch_at_races_flags         = Flags(RACE.NONE)
        self.touch_at_entitypes           = 0
        self.touch_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.touch_direction              = 1
        self.touch_exit                   = 0
        self.touch_wall                   = 0
        self.touch_closed_door            = 0
        self.touch_extra                  = 1
        self.touch_equipment              = 0
        self.touch_inventory              = 0

        self.taste                        = 1
        self.taste_player                 = 1
        self.taste_mob                    = 1
        self.taste_item                   = 1
        self.taste_self                   = 1
        self.taste_at_races               = 0
        self.taste_at_races_flags         = Flags(RACE.NONE)
        self.taste_at_entitypes           = 0
        self.taste_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.taste_direction              = 1
        self.taste_exit                   = 0
        self.taste_wall                   = 0
        self.taste_closed_door            = 0
        self.taste_extra                  = 1
        self.taste_equipment              = 0
        self.taste_inventory              = 0

        self.intuition                    = 1
        self.intuition_player             = 1
        self.intuition_mob                = 1
        self.intuition_item               = 1
        self.intuition_self               = 1
        self.intuition_at_races           = 0
        self.intuition_at_races_flags     = Flags(RACE.NONE)
        self.intuition_at_entitypes       = 0
        self.intuition_at_entitypes_flags = Flags(ENTITYPE.NONE)
        self.intuition_direction          = 1
        self.intuition_exit               = 0
        self.intuition_wall               = 0
        self.intuition_closed_door        = 0
        self.intuition_extra              = 1
        self.intuition_equipment          = 0
        self.intuition_inventory          = 0

        self.wander_direction             = 1  # Percentuale di movimento in una direzione qualsiasi
        self.wander_exit                  = 0  # Percentuale di movimento in un'uscita reale
        self.wander_wall                  = 0  # Percentuale di movimento sui wall esistenti
        self.wander_closed_door           = 0  # Percentuale di movimento tra le porte chiuse e apribili
        self.wander_area                  = 0  # Percentuale di movimento tra aree
        self.wander_at_exits              = 0  # Percentuale di movimento sulle direzioni impostate
        self.wander_at_exits_flags        = Flags(DIR.NONE)  # Direzione in cui andrà con più probabilità
        self.wander_at_sectors            = Flags(SECTOR.NONE)  # Settori in cui può muoversi
        self.wander_portal                = 0  # Percentuale di movimento nei portali
        self.wander_enter_container       = 0  # Percentuale di movimento di entrata nei contenitori
        self.wander_exit_container        = 0  # Percentuale di movimento di uscita dai contenitori
        self.wander_self                  = 0  # Percentuale di enter/exit su sé stessi se si è un portale o un contenitore

        self.random_do                    = 0  # Percentuale di utilizzo di uno tra i comandi impostati in random_do_inputs
        self.random_do_inputs             = [] # Attributo che fa coppia con random_do
    #- Fine Inizializzazione -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = MobBehaviour()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -


class ItemBehaviour(_BehaviourHandler):
    def __init__(self):
        super(ItemBehaviour, self).__init__()

        self.look                         = 0
        self.look_player                  = 0
        self.look_mob                     = 0
        self.look_item                    = 0
        self.look_self                    = 0
        self.look_at_races                = 0
        self.look_at_races_flags          = Flags(RACE.NONE)
        self.look_at_entitypes            = 0
        self.look_at_entitypes_flags      = Flags(ENTITYPE.NONE)
        self.look_direction               = 0
        self.look_exit                    = 0
        self.look_wall                    = 0
        self.look_closed_door             = 0
        self.look_extra                   = 0
        self.look_equipment               = 0
        self.look_inventory               = 0

        self.listen                       = 0
        self.listen_player                = 0
        self.listen_mob                   = 0
        self.listen_item                  = 0
        self.listen_self                  = 0
        self.listen_at_races              = 0
        self.listen_at_races_flags        = Flags(RACE.NONE)
        self.listen_at_entitypes          = 0
        self.listen_at_entitypes_flags    = Flags(ENTITYPE.NONE)
        self.listen_direction             = 0
        self.listen_exit                  = 0
        self.listen_wall                  = 0
        self.listen_closed_door           = 0
        self.listen_extra                 = 0
        self.listen_equipment             = 0
        self.listen_inventory             = 0

        self.smell                        = 0
        self.smell_player                 = 0
        self.smell_mob                    = 0
        self.smell_item                   = 0
        self.smell_self                   = 0
        self.smell_at_races               = 0
        self.smell_at_races_flags         = Flags(RACE.NONE)
        self.smell_at_entitypes           = 0
        self.smell_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.smell_direction              = 0
        self.smell_exit                   = 0
        self.smell_wall                   = 0
        self.smell_closed_door            = 0
        self.smell_extra                  = 0
        self.smell_equipment              = 0
        self.smell_inventory              = 0

        self.touch                        = 0
        self.touch_player                 = 0
        self.touch_mob                    = 0
        self.touch_item                   = 0
        self.touch_self                   = 0
        self.touch_at_races               = 0
        self.touch_at_races_flags         = Flags(RACE.NONE)
        self.touch_at_entitypes           = 0
        self.touch_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.touch_direction              = 0
        self.touch_exit                   = 0
        self.touch_wall                   = 0
        self.touch_closed_door            = 0
        self.touch_extra                  = 0
        self.touch_equipment              = 0
        self.touch_inventory              = 0

        self.taste                        = 0
        self.taste_player                 = 0
        self.taste_mob                    = 0
        self.taste_item                   = 0
        self.taste_self                   = 0
        self.taste_at_races               = 0
        self.taste_at_races_flags         = Flags(RACE.NONE)
        self.taste_at_entitypes           = 0
        self.taste_at_entitypes_flags     = Flags(ENTITYPE.NONE)
        self.taste_direction              = 0
        self.taste_exit                   = 0
        self.taste_wall                   = 0
        self.taste_closed_door            = 0
        self.taste_extra                  = 0
        self.taste_equipment              = 0
        self.taste_inventory              = 0

        self.intuition                    = 0
        self.intuition_player             = 0
        self.intuition_mob                = 0
        self.intuition_item               = 0
        self.intuition_self               = 0
        self.intuition_at_races           = 0
        self.intuition_at_races_flags     = Flags(RACE.NONE)
        self.intuition_at_entitypes       = 0
        self.intuition_at_entitypes_flags = Flags(ENTITYPE.NONE)
        self.intuition_direction          = 0
        self.intuition_exit               = 0
        self.intuition_wall               = 0
        self.intuition_closed_door        = 0
        self.intuition_extra              = 0
        self.intuition_equipment          = 0
        self.intuition_inventory          = 0

        self.wander_direction             = 0
        self.wander_exit                  = 0
        self.wander_wall                  = 0
        self.wander_closed_door           = 0
        self.wander_area                  = 0
        self.wander_at_exits              = 0
        self.wander_at_exits_flags        = Flags(DIR.NONE)
        self.wander_at_sectors            = Flags(SECTOR.NONE)
        self.wander_portal                = 0
        self.wander_enter_container       = 0
        self.wander_exit_container        = 0
        self.wander_self                  = 0

        self.random_do                    = 0
        self.random_do_inputs             = []
    #- Fine Inizializzazione -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = ItemBehaviour()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -


# (TD) fare anche gli altri behaviour con l'attributo
# _cached_behaviour_draw_attrs al loro interno
class RoomBehaviour(object):
    PRIMARY_KEY = ""
    VOLATILES   = ["_cached_behaviour_draw_attrs"]
    MULTILINES  = []
    SCHEMA      = {"random_echo_texts" : ("", "str")}
    REFERENCES  = {}
    WEAKREFS    = {}

    BEHAVIOUR_DRAW = {"random_echo" : "update_random_echo"}

    def __init__(self):
        self.random_echo       = 0
        self.random_echo_texts = []

        # Attributi volatili
        self._cached_behaviour_draw_attrs = []
    #- Fine Metodo -

    def __repr__(self):
        random_total = get_total_percent(self, "random")
        return "%s: random=%d" % (super(_BehaviourHandler, self).__repr__, random_total)
    #- Fine Metodo -

    def get_error_message(self):
        if self.get_error_message_random_echo_texts() != "":
            return self.get_error_message_random_echo_texts()

        return ""
    #- Fine Metodo -

    def get_error_message_random_echo_texts(self):
        for random_echo_text in self.random_echo_texts:
            if len(random_echo_text) > config.max_google_translate:
                return "random_echo_text %r più lungo di %d caratteri." % (random_echo_text, config.max_google_translate)

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = RoomBehaviour()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, room_behaviour2):
        if not room_behaviour2:
            return False

        if self.random_echo != room_behaviour2.random_echo:
            return False

        if len(self.random_echo_texts) != len(behaviour2.random_echo_texts):
            return False
        for text in self.random_echo_texts:
            for text2 in room_behaviour2.random_echo_texts:
                if text == text2:
                    break
            else:
                return False

        if len(self._cached_behaviour_draw_attrs) != len(behaviour2._cached_behaviour_draw_attrs):
            return False
        for draw_attr in self._cached_behaviour_draw_attrs:
            for draw_attr2 in room_behaviour2._cached_behaviour_draw_attrs:
                if draw_attr == draw_attr2:
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def cache(self, room):
        # Prepara la lista di liste con coppie [nome attributo, valore] dei
        # comportamenti
        for attr_name in self.BEHAVIOUR_DRAW.keys():
            value = getattr(self, attr_name)
            if value > 0:
                self._cached_behaviour_draw_attrs.append([attr_name, value])

        # Ordina dal valore più piccolo a quello più grande, poi al posto
        # dei valori calcola in ordine il totale accumulato, l'ultimo elemento
        # è quello con il totale di tutti i valori dei comportamenti
        self._cached_behaviour_draw_attrs = sorted(self._cached_behaviour_draw_attrs, key=lambda cached: cached[1])
        values = []
        for cached in self._cached_behaviour_draw_attrs:
            values.append(cached[1])
            cached[1] = sum(values)

        # Aggiunge la stanza alla lista del ciclo di loop apposito
        room_behaviour_loop.behavioured_rooms.append(room)
    #- Fine Metodo -

    def update(self, room):
        # Ricava il totale di tutti i valori di comportamento impostati che si
        # trova come ultimo valore della struttura
        total = self._cached_behaviour_draw_attrs[-1][1]
        if total <= 0:
            log.bug("Il totale dei behaviour dell'entità %s non è un valore valido: %d" % (self.code, total))
            return

        # Con il meccanismo seguente si può pescare a caso in maniera
        # proporzionale al valore impostato al behaviour
        # (TD) provare ad inlinizzare il ciclo for per migliorare le prestazioni
        choiced_attr = ""
        casual_number = random.randint(0, total)
        for cached in self._cached_behaviour_draw_attrs:
            if cached[1] >= casual_number:
                choiced_attr = cached[0]
                break

        if not choiced_attr:
            log.bug("Non è stato scelto nessun attributo valido con casual_number %d e total %d all'entità %s" % (
                casual_number, total, room.code))
            return

        # Esegue infine il comportamento scelto casualmente
        behaviour_draw_value = self.BEHAVIOUR_DRAW[choiced_attr]
        action_executed = getattr(self, behaviour_draw_value)(room)

        # Tiene traccia su file delle statistiche d'esecuzione dei comportamenti
        if config.track_behaviours:
            key = "%s()" % (behaviour_draw_value)
            if key not in room_behaviour_tracker:
                room_behaviour_tracker[key] = [0, 0]
            if action_executed:
                room_behaviour_tracker[key][0] += 1
            room_behaviour_tracker[key][1] += 1
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def update_random_echo(self, room):
        if self.random_echo <= 0 or not self.random_echo_texts:
            return False

        if random.randint(1, config.max_behaviour_probability) > self.random_echo:
            return False

        # Sceglie a caso l'echo e lo invia
        text = random.choice(self.random_echo_texts)
        if MIML_SEPARATOR in text:
            text = room.parse_miml(text)
        if text:
            room.echo(text)

        return True
    #- Fine Metodo -


# (TD) classe sbagliata, farla come la RoomBehaviour
class BehaviourUpdaterSuperclass(object):
    """
    Classe contenente il metodo generico che sarà ereditato in ultima istanza
    dalle classi Mob, Item e simili per eseguire un update dei comportamenti
    di quelle entità.
    Questa classe alla fin fine viene Mixinata con Mob o con Item.
    """
    BEHAVIOUR_DRAW = {"look"                   : ["update_sense",                  "look", "command_look"],
                      "look_player"            : ["update_sense_player",           "look", "command_look"],
                      "look_mob"               : ["update_sense_mob",              "look", "command_look"],
                      "look_item"              : ["update_sense_item",             "look", "command_look"],
                      "look_self"              : ["update_sense_self",             "look", "command_look"],
                      "look_at_races"          : ["update_sense_at_races",         "look", "command_look"],
                      "look_at_entitypes"      : ["update_sense_an_entitypes",     "look", "command_look"],
                      "look_direction"         : ["update_sense_direction",        "look", "command_look"],
                      "look_exit"              : ["update_sense_exit",             "look", "command_look"],
                      "look_wall"              : ["update_sense_wall",             "look", "command_look"],
                      "look_closed_door"       : ["update_sense_closed_door",      "look", "command_look"],
                      "listen"                 : ["update_sense",                  "listen", "command_listen"],
                      "listen_player"          : ["update_sense_player",           "listen", "command_listen"],
                      "listen_mob"             : ["update_sense_mob",              "listen", "command_listen"],
                      "listen_item"            : ["update_sense_item",             "listen", "command_listen"],
                      "listen_self"            : ["update_sense_self",             "listen", "command_listen"],
                      "listen_at_races"        : ["update_sense_at_races",         "listen", "command_listen"],
                      "listen_at_entitypes"    : ["update_sense_an_entitypes",     "listen", "command_listen"],
                      "listen_direction"       : ["update_sense_direction",        "listen", "command_listen"],
                      "listen_exit"            : ["update_sense_exit",             "listen", "command_listen"],
                      "listen_wall"            : ["update_sense_wall",             "listen", "command_listen"],
                      "listen_closed_door"     : ["update_sense_closed_door",      "listen", "command_listen"],
                      "smell"                  : ["update_sense",                  "smell", "command_smell"],
                      "smell_player"           : ["update_sense_player",           "smell", "command_smell"],
                      "smell_mob"              : ["update_sense_mob",              "smell", "command_smell"],
                      "smell_item"             : ["update_sense_item",             "smell", "command_smell"],
                      "smell_self"             : ["update_sense_self",             "smell", "command_smell"],
                      "smell_at_races"         : ["update_sense_at_races",         "smell", "command_smell"],
                      "smell_at_entitypes"     : ["update_sense_an_entitypes",     "smell", "command_smell"],
                      "smell_direction"        : ["update_sense_direction",        "smell", "command_smell"],
                      "smell_exit"             : ["update_sense_exit",             "smell", "command_smell"],
                      "smell_wall"             : ["update_sense_wall",             "smell", "command_smell"],
                      "smell_closed_door"      : ["update_sense_closed_door",      "smell", "command_smell"],
                      "touch"                  : ["update_sense",                  "touch", "command_touch"],
                      "touch_player"           : ["update_sense_player",           "touch", "command_touch"],
                      "touch_mob"              : ["update_sense_mob",              "touch", "command_touch"],
                      "touch_item"             : ["update_sense_item",             "touch", "command_touch"],
                      "touch_self"             : ["update_sense_self",             "touch", "command_touch"],
                      "touch_at_races"         : ["update_sense_at_races",         "touch", "command_touch"],
                      "touch_at_entitypes"     : ["update_sense_an_entitypes",     "touch", "command_touch"],
                      "touch_direction"        : ["update_sense_direction",        "touch", "command_touch"],
                      "touch_exit"             : ["update_sense_exit",             "touch", "command_touch"],
                      "touch_wall"             : ["update_sense_wall",             "touch", "command_touch"],
                      "touch_closed_door"      : ["update_sense_closed_door",      "touch", "command_touch"],
                      "taste"                  : ["update_sense",                  "taste", "command_taste"],
                      "taste_player"           : ["update_sense_player",           "taste", "command_taste"],
                      "taste_mob"              : ["update_sense_mob",              "taste", "command_taste"],
                      "taste_item"             : ["update_sense_item",             "taste", "command_taste"],
                      "taste_self"             : ["update_sense_self",             "taste", "command_taste"],
                      "taste_at_races"         : ["update_sense_at_races",         "taste", "command_taste"],
                      "taste_at_entitypes"     : ["update_sense_an_entitypes",     "taste", "command_taste"],
                      "taste_direction"        : ["update_sense_direction",        "taste", "command_taste"],
                      "taste_exit"             : ["update_sense_exit",             "taste", "command_taste"],
                      "taste_wall"             : ["update_sense_wall",             "taste", "command_taste"],
                      "taste_closed_door"      : ["update_sense_closed_door",      "taste", "command_taste"],
                      "intuition"              : ["update_sense",                  "intuition", "command_intuition"],
                      "intuition_player"       : ["update_sense_player",           "intuition", "command_intuition"],
                      "intuition_mob"          : ["update_sense_mob",              "intuition", "command_intuition"],
                      "intuition_item"         : ["update_sense_item",             "intuition", "command_intuition"],
                      "intuition_self"         : ["update_sense_self",             "intuition", "command_intuition"],
                      "intuition_at_races"     : ["update_sense_at_races",         "intuition", "command_intuition"],
                      "intuition_at_entitypes" : ["update_sense_an_entitypes",     "intuition", "command_intuition"],
                      "intuition_direction"    : ["update_sense_direction",        "intuition", "command_intuition"],
                      "intuition_exit"         : ["update_sense_exit",             "intuition", "command_intuition"],
                      "intuition_wall"         : ["update_sense_wall",             "intuition", "command_intuition"],
                      "intuition_closed_door"  : ["update_sense_closed_door",      "intuition", "command_intuition"],
                      "wander_direction"       : ["update_wander_direction",       "", None],
                      "wander_exit"            : ["update_wander_exit",            "", None],
                      "wander_wall"            : ["update_wander_wall",            "", None],
                      "wander_closed_door"     : ["update_wander_closed_door",     "", None],
                      "wander_at_exits"        : ["update_wander_at_exits",        "", None],
                      "wander_portal"          : ["update_wander_portal",          "", None],
                      "wander_enter_container" : ["update_wander_enter_container", "", None],
                      "wander_exit_container"  : ["update_wander_exit_container",  "", None],
                      "random_do"              : ["update_random_do",              "", None]}

    def cache_behaviour(self, behaviour_attr_name):
        """
        Prepara la lista da cui scegliere a caso uno tra i comportamenti che
        hanno un valore maggiore di zero.
        Questo sistema di cache esiste perché altrimenti la getattr utilizzata
        su migliaia di entità ogni qualche secondi è CPU intesiva.
        """
        behaviour = getattr(self, behaviour_attr_name)
        if not behaviour:
            log.bug("Inatteso passaggio nel codice con behaviour non valido: %r" % behaviour)
            return

        # Prepara la lista di liste con coppie [nome attributo, valore] dei
        # comportamenti
        cached_behaviour_draw_attrs = []
        for attr_name, draw_value in self.BEHAVIOUR_DRAW.iteritems():
            value = getattr(behaviour, attr_name)
            if value > 0:
                cached_behaviour_draw_attrs.append([attr_name, value])
            # Per evitare casini di import vengono importati solo
            # successivamente i comandi
            if isinstance(draw_value[2], basestring):
                command_module = __import__("src.commands.%s" % draw_value[2], globals(), locals(), [""])
                draw_value[2] = getattr(command_module, draw_value[2])

        # Ordina dal valore più piccolo a quello più grande, poi al posto
        # dei valori calcola in ordine il totale accumulato, l'ultimo elemento
        # è quello con il totale di tutti i valori dei comportamenti
        cached_behaviour_draw_attrs = sorted(cached_behaviour_draw_attrs, key=lambda cached: cached[1])
        values = []
        for cached in cached_behaviour_draw_attrs:
            values.append(cached[1])
            cached[1] = sum(values)

        # È normale quando il builder ha definito tutti i behaviour a zero,
        # questo serve ad esplicitare che non si vogliono eventuali valori di
        # default superiori a zero definiti nelle classi di MobBehaviour e
        # ItemBehaviour
        if not cached_behaviour_draw_attrs:
            setattr(self, behaviour_attr_name, None)
        else:
            # L'Attributo per cachare viene creato solo se necessario; iniziando
            # con un underscore è automaticamente visto come volatile dalla fwrite
            # e quindi l'etichetta relativa non viene salvata nella persistenza
            
            if "_" in behaviour_attr_name:
                cached_attr_name = "_cached_behaviour_draw_attrs_" + behaviour_attr_name.split("_")[0]
            else:
                cached_attr_name = "_cached_behaviour_draw_attrs"
            setattr(self, cached_attr_name, cached_behaviour_draw_attrs)
    #- Fine Metodo -

    def update_behaviour(self):
        access_attr_singular = self.ACCESS_ATTR[:-1]

        behaviour_of_room = None
        if self.location.IS_ROOM:
            if FLAG.NO_ROOM_BEHAVIOUR in self.flags:
                return
            behaviour_of_room = getattr(self.location, access_attr_singular + "_behaviour")

        if not behaviour_of_room and not self.behaviour:
            log.bug("Inatteso passaggio nel codice con behaviour_of_room %r e behaviour %r per l'entità %s" % (
                behaviour_of_room, self.code))
            return

        if behaviour_of_room:
            behaviour = behaviour_of_room
            cached_behaviour_draw_attr_name = "_cached_behaviour_draw_attrs_" + access_attr_singular
            cached_behaviour_draw_attrs = getattr(self.location, cached_behaviour_draw_attr_name)
            behaviour_tracker = globals()["room_" + access_attr_singular + "_behaviour_tracker"]
        else:
            behaviour = self.behaviour
            cached_behaviour_draw_attr_name = "_cached_behaviour_draw_attrs"
            cached_behaviour_draw_attrs = self._cached_behaviour_draw_attrs
            behaviour_tracker = globals()[access_attr_singular + "_behaviour_tracker"]

        # Se self è una porta chiusa e segreta allora esce e non produce
        # behaviour altrimenti verrebbe scoperta
        if (self.door_type and self.is_hinged()
        and DOOR.CLOSED in self.door_type.flags
        and DOOR.SECRET in self.door_type.flags):
            return

        # Se c'è qualcuno da combattere nella stanza allora non esegue
        # il behaviour
        if self.IS_ACTOR and self.is_fighting():
            return

        # Se la porta è aperta allora esce e non produce behaviours perché
        # è "pacifico" che porte aperte passino in secondo piano a favore
        # delle uscite
        if self.is_hinged() and DOOR.CLOSED not in self.door_type.flags:
            return

        # Ricava il totale di tutti i valori di comportamento impostati che si
        # trova come ultimo valore della struttura
        try:
            total = cached_behaviour_draw_attrs[-1][1]
        except AttributeError:
            if self.location:
                details = "contenuto in %s " % self.location.code
            else:
                details = "non è dentro nulla "
            if self.door_type:
                details += "ed è una porta "
                if self.is_hinged():
                    details += "sui cardini "
                else:
                    details += "ma non sui cardini "
            else:
                details += "e non è una porta "
            details += "il %d %d %d %s %d" % (calendar.minute, caledar.hour, calendar.day, calendar.month, calendar.year)
            log.bug("%s (%s) non possiede l'attributo %s" % (self.code, details, cached_behaviour_draw_attr_name))
            return

        if total == 0:
            log.bug("Il totale dei behaviour è uguale a 0 nonostante sia definita l'etichetta per l'entità %s e il cached attr %s" % (
                self.code, cached_behaviour_draw_attr_name))
            return

        # Con il meccanismo seguente si può pescare a caso in maniera
        # proporzionale al valore impostato al behaviour
        # (TD) provare ad inlinizzare il ciclo for per prestazioni maggiori
        choiced_attr = ""
        casual_number = random.randint(0, total)
        for cached in cached_behaviour_draw_attrs:
            if cached[1] >= casual_number:
                choiced_attr = cached[0]
                break

        if not choiced_attr:
            log.bug("Non è stato scelto nessun attributo valido con casual_number %d e total %d all'entità %s" % (
                casual_number, total, self.code))
            return

        # Poiché vengono eseguiti dei comandi senza passare per la interpret
        # (dove c'è lo stesso controllo) si assicura che chi esegue l'azione
        # sia un'entità sola e non un mucchio fisico
        splitted = self.split_entity(1)

        # Esegue infine il comportamento scelto casualmente
        behaviour_draw_value = splitted.BEHAVIOUR_DRAW[choiced_attr]
        if behaviour_draw_value[1]:
            action_executed = getattr(behaviour, behaviour_draw_value[0])(splitted, behaviour_draw_value[1], behaviour_draw_value[2])
        else:
            action_executed = getattr(behaviour, behaviour_draw_value[0])(splitted)

        # Tiene traccia su file delle statistiche d'esecuzione dei comportamenti
        if config.track_behaviours:
            if behaviour_draw_value[1]:
                key = "%s(%s)" % (behaviour_draw_value[0], behaviour_draw_value[1])
            else:
                key = "%s()" % (behaviour_draw_value[0])
            if key not in behaviour_tracker:
                behaviour_tracker[key] = [0, 0]
            if action_executed:
                behaviour_tracker[key][0] += 1
            behaviour_tracker[key][1] += 1

        # Poiché i comandi di behaviour non vengono inviati tramite la send_input
        # allora bisogna effettuare il controllo che c'è anche nella interpreter
        if config.check_references and not database.reference_error_found:
            database.check_all_references()
    #- Fine Metodo -


# (TD) fare il loop separato anche per le altre tipologie di behaviour
class RoomBehaviourLoop(UnstoppableLoop):
    def __init__(self):
        super(RoomBehaviourLoop, self).__init__()
        self.paused = False  # Indica se questo ciclo è stato messo in pausa dal comando loop

        # Contiene la lista di tutte le entità che hanno dei RoomBehaviour,
        # serve a velocizzare il loop
        self.behavioured_rooms = []
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        if seconds == 0:
            seconds = config.room_behaviour_loop_seconds
        super(RoomBehaviourLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(RoomBehaviourLoop, self).stop()
        else:
            log.bug("Il RoomBehaviourLoop non è stato trovato attivo.")
    #- Fine Metodo -

    def cycle(self):
        if self.paused:
            return

        for behavioured_room in self.behavioured_rooms:
            if ROOM.EXTRACTED in behavioured_room.flags:
                log.bug("È stata trovata una room estratta nella lista delle behavioured_rooms del RoomBehaviourLoop: %s" % behavioured_room.code)
                continue
            if not behavioured_room.area:
                log.bug("È stata trovata una room senza area nella lista delle behavioured_rooms del RoomBehaviourLoop: %s" % behavioured_room.code)
                continue
            if behavioured_room.code not in database["rooms"]:
                log.bug("È stata trovata una room che non si trova nel database nella lista delle behavioured_rooms del RoomBehaviourLoop: %s" % behavioured_room.code)
                continue
            behavioured_room.room_behaviour.update(behavioured_room)
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def write_behaviour_tracker():
    global mob_behaviour_tracker
    global item_behaviour_tracker
    global room_behaviour_tracker
    global room_mob_behaviour_tracker
    global room_item_behaviour_tracker

    file_path = "log/behaviours.txt"
    try:
        behaviour_file = open(file_path, "w")
    except IOError:
        log.bug("Impossibile aprire il file %s in scrittura" % file_path)
        return

    now = datetime.datetime.now()
    date = "%dy_%dm_%dd_%dh_%dm_%ds" % (
        now.year, now.month, now.day, now.hour, now.minute, now.second)

    behaviour_file.write("MOB BEHAVIOURS %s\n" % date)
    for key in sorted(mob_behaviour_tracker):
        value = mob_behaviour_tracker[key]
        behaviour_file.write("%s: %d/%d\n" % (key, value[0], value[1]))

    behaviour_file.write("\nITEM BEHAVIOURS %s\n" % date)
    for key in sorted(item_behaviour_tracker):
        value = item_behaviour_tracker[key]
        behaviour_file.write("%s: %d/%d\n" % (key, value[0], value[1]))

    behaviour_file.write("\nROOM BEHAVIOURS %s\n" % date)
    for key in sorted(room_behaviour_tracker):
        value = room_behaviour_tracker[key]
        behaviour_file.write("%s: %d/%d\n" % (key, value[0], value[1]))

    behaviour_file.write("\nROOM MOB BEHAVIOURS %s\n" % date)
    for key in sorted(room_mob_behaviour_tracker):
        value = room_mob_behaviour_tracker[key]
        behaviour_file.write("%s: %d/%d\n" % (key, value[0], value[1]))

    behaviour_file.write("\nROOM ITEM BEHAVIOURS %s\n" % date)
    for key in sorted(room_item_behaviour_tracker):
        value = room_item_behaviour_tracker[key]
        behaviour_file.write("%s: %d/%d\n" % (key, value[0], value[1]))

    behaviour_file.write("\n")
    behaviour_file.close()
#- Fine Funzione -


def create_tooltip_behaviour(conn, behaviour, title, symbol):
    if not conn:
        if not engine.test_inputs_mode:
            log.bug("conn non è un parametro valido: %r" % conn)
        return ""

    if not behaviour:
        log.bug("behaviour non è un parametro valido: %r" % behaviour)
        return ""

    if not title:
        log.bug("title non è un parametro valido: %r" % title)
        return ""

    if not symbol:
        log.bug("symbol non è un parametro valido: %r" % symbol)
        return ""

    # -------------------------------------------------------------------------

    at_least_one_behaviour = False
    lines = []
    lines.append("[royalblue]%s[close]" % title)
    for attr in sorted(behaviour.__dict__):
        if attr[0] == "_":
            continue
        value = getattr(behaviour, attr)
        if value and str(value) and str(value) != "0":
            lines.append("[limegreen]%s[close]: %s" % (to_capitalized_words(attr), value))
            at_least_one_behaviour = True

    if at_least_one_behaviour:
        return create_tooltip(conn, "<br>".join(lines), symbol)
    else:
        return ""
#- Fine Funzione -


def get_total_percent(behaviour, prefix):
    total = 0

    for attr_name in behaviour.__dict__:
        if attr_name[0 : len(prefix)] != prefix:
            continue
        attr = getattr(behaviour, attr_name)
        if isinstance(attr, numbers.Number):
            total += attr

    return total
#- Fine Metodo -


#= SINGLETON ===================================================================

room_behaviour_loop = RoomBehaviourLoop()
