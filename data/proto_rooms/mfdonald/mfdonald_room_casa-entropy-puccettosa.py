# -*- coding: utf-8 -*-


#= IMPORT ======================================================================


from src.commands.command_say import command_say

import_path = "data.proto_mobs.mfdonald.mfdonald_mob_unicorno-charlie"
charlie_script_module = __import__(import_path, globals(), locals(), [""])


#= FUNZIONI ====================================================================

# In questo caso anche se passiamo i parametri to_room e from_direction non
# li utilizziamo perché quello di cui abbiamo bisogno è controllare se nella
# stanza raggiunta dal giocatore vi sia Charlieeeeeee!
# In realtà penso che sia meglio far triggare questa quest al after_look donando
# a charlieeeeee un po' di LookPlayer behaviour.
# Infatti charlie può muoversi e questo inficia sulle probabilità di avvio
# della quest, che può essere solo attivata da qui, tuttavia può essere una
# cosa voluta per alcuni mudscript
def after_move(entity, from_room, direction, to_room, running, behavioured):
    charlie_script_module.start_charlie_banana_quest(entity, to_room)
#- Fine Funzione -
