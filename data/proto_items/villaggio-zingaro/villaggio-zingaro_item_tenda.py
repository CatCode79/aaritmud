# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.enums import FLAG, TO


#= FUNZIONI ====================================================================

def before_get(entity, target, location, behavioured):
    target.flags -= FLAG.NO_LOOK_LIST
