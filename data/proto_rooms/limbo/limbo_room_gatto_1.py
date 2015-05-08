# -*- coding: utf_8 -*-


#= IMPORT ======================================================================

import random


#= FUNZIONI ====================================================================

def before_move(entity, from_room, direction, to_room, running, behavioured):
    '''
    Se qualcuno prova ad uscire da questa stanza potrebbe starnutire per colpa
    dei peli di gatto. Mrà! Mrà!
    '''
    if random.randint(1, 50) == 1:
        entity.send_output("Un ciuffo di [white]peli di gatto svolazzante[close] ti passa vicino al naso facendoti snarnutire.")
        entity.act("Un ciuffo di [white]peli di gatto svolazzante[close] passa vicino al naso di $n facendol$o starnutire.")
# - Fine della Funzione -
