# -*- coding: utf-8 -*-

from src.commands     import command_dig

import_path = "data.proto_rooms.miniere-kezaf.miniere-kezaf_room_p1-02"
miniere_kezaf_room_module = __import__(import_path, globals(), locals(), [""])
before_dig = miniere_kezaf_room_module.before_dig
