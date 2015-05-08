# -*- coding: utf-8 -*-

"""
Sfogliando il diario c'è una probabilità che vengano "persi" dei pezzi.
Il danneggiamento è solo virtuale.
"""

#= IMPORT ======================================================================

import random


#= TRIGGER =====================================================================

def before_readed(entity, target, output, extra, behavioured):
    if random.randint(1, 9) == 1:
        name = target.get_name(looker=entity)
        if random.randint(1, 2) == 1:
            entity.send_output("Non riesci a manipolare con cura %s che si rovina un po'." % name)
        else:
            entity.send_output("Vedi cadere a terra un pezzettino ammuffito di %s." % name)
#- Fine Trigger -
