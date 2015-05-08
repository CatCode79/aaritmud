# -*- coding: utf-8 -*-


#= COMMENTS ====================================================================

# TD - se qualcuno fa un touch di una extra prima del primo scramble ora crasha
# TD - caricare un oggetto premio invece del messaggio di STICAZZI
# TD - limitare ad uno il numero dei movimenti di un colore solo
# TD - invece di cambiare un solo colore con il successivo meglio random
# TD - invece di cambiare un solo colore cambiare anche quello adiacente

#= IMPORT ======================================================================

import random
from src.enums     import FLAG, TO
from src.commands.command_look  import look_an_entity

#= FUNZIONI ====================================================================

def before_touch(player, rompicapo, descr, detail, behavioured):

    #a seconda che si tocchi l'oggetto o una sua extra lancia
    #lo scramble con parametri diversi
    #nel primo caso scrambla tutto nel secondo caso cambia il colore di uno solo
    #dei tasselli
    if detail.IS_EXTRA:
        print "Extra Touched"
        scramble(rompicapo, player, detail.keywords)
        # Se la extra è quella della prima posizione
        #if "prima" not in detail.keywords:
            #print "Extra Prima Touched"
            #return False

    else:  scramble(rompicapo, player, "scramble_all")
    
def scramble(rompicapo, player, posizione):

    print "posizione: ", posizione

    color_db = ["[red]",
                "[yellow]",
                "[green]",
                "[blue]",
                "[darkviolet]"]

    if posizione == "scramble_all":
	color_1 = random.choice(color_db)
	color_2 = random.choice(color_db)
	color_3 = random.choice(color_db)
	color_4 = random.choice(color_db)
	color_5 = random.choice(color_db)
	
	sequence = [ color_1, color_2, color_3, color_4, color_5 ]
	rompicapo.specials["sequence"] = sequence
    else:
        if posizione == "prima":
            position = 0
        elif posizione == "seconda":
            position = 1
        elif posizione == "terza":
            position = 2
        elif posizione == "quarta":
            position = 3
        elif posizione == "quinta":
            position = 4

        #cambio di uno solo dei colori in relazione a quale delle 5 extra son usate
        touched_color = rompicapo.specials["sequence"].pop(position)
        next_color = color_db.index(touched_color)
        if next_color == 4: next_color = -1
        rompicapo.specials["sequence"].insert(position, color_db[next_color + 1])

        sequence = [ rompicapo.specials["sequence"][0], rompicapo.specials["sequence"][1], rompicapo.specials["sequence"][2], rompicapo.specials["sequence"][3], rompicapo.specials["sequence"][4] ]
    print rompicapo.specials["sequence"] 

    description = "Un rompicapo con decine di pezzi liberi di ruotare è l'omaggio ai partecipanti alla [gold]sesta apertura[close]! Per scombinarlo basta toccarlo. Le lettere formano la scritta:<br>"
    nice_things = "[white] ========= [close]"
    border = "<br>[white] =============================== [close]<br>"

    colored_description = border + nice_things + rompicapo.specials["sequence"][0] + "VI " + rompicapo.specials["sequence"][1] + "AP" + rompicapo.specials["sequence"][2] + "ER" + rompicapo.specials["sequence"][3] + "TU" + rompicapo.specials["sequence"][4] + "RA[close]" + nice_things + border
    rompicapo.descr = description + colored_description

    #controlla se si son ottenuti 5 colori uguali e se sono anche state ottenute tutte e 5
    #le diverse sequenze di colori
    if sequence[0] == sequence[1] == sequence[2] == sequence[3] == sequence[4]:
        if "achieved_colors" not in rompicapo.specials:
            rompicapo.specials["achieved_colors"] = ""
        if sequence[0] not in rompicapo.specials["achieved_colors"]:
            rompicapo.specials["achieved_colors"] += sequence[0]
            if ("[red]" in rompicapo.specials["achieved_colors"]
            and "[yellow]" in rompicapo.specials["achieved_colors"]
            and "[green]" in rompicapo.specials["achieved_colors"]
            and "[blue]" in rompicapo.specials["achieved_colors"] 
            and "[darkviolet]" in rompicapo.specials["achieved_colors"]):
                print "STICAZZI! YOU WIN"

        print rompicapo.specials["achieved_colors"]

        #if "[red]" in rompicapo.specials["achieved_colors"]:
        #print "c'è il rosso dentro alla cazzo di special"
        victory_descr = "In poche mosse riesci a ricombinarlo a dovere e te lo riguardi compiaciut$O\n" + colored_description

        player.act(victory_descr, TO.ENTITY, rompicapo)    
        player.act("$n sorride all'indirizzo di $N.", TO.OTHERS, rompicapo)    
        player.act("$n ti ha ricombinato.", TO.TARGET, rompicapo)    

        #rompicapo_keyword = player.get_keywords_attr(rompicapo).split()[0]
        #look_an_entity(player, rompicapo)

    else:
        player.act("Ti cimenti con $N scombinandone i colori.", TO.ENTITY, rompicapo)    
        player.act("$n ti scombina un poco cercando una combinazione cromatica decente.", TO.TARGET, rompicapo)    
        player.act("$n si cimenta con $N scombinandone i colori.", TO.OTHERS, rompicapo)    
#- Fine Funzione -



def new_scramble(rompicapo, player, posizione):
    print posizione
    description = "Un rompicapo con decine di pezzi liberi di ruotare è l'omaggio ai partecipanti alla [gold]sesta apertura[close]! Per scombinarlo basta toccarlo. Le lettere formano la scritta:<br>"
    nice_things = "[white] ========= [close]"
    border = "<br>[white] =============================== [close]<br>"

    RED        = 0
    YELLOW     = 1
    GREEN      = 2
    BLUE       = 3
    DARKVIOLET = 4

    COLOR = [0, 1, 2, 3, 4]

    COLORSTRING = ["[red]",
                      "[yellow]",
                      "[green]",
                      "[blue]",
                      "[darkviolet]"]

    COL1 = random.choice(COLORS)
    COL2 = random.choice(COLORS)
    COL3 = random.choice(COLORS)
    COL4 = random.choice(COLORS)
    COL5 = random.choice(COLORS)

    colored_description = border + nice_things + COLORSTRING.COL1 + "VI " + COLORSTRING.COL2 + "AP" + COLORSTRING.COL3 + "ER" + COLORSTRING.COL4 + "TU" + COLORSTRING.COL5 + "RA[close]" + nice_things + border
    rompicapo.descr = description + colored_description

    if COL1 == COL2 == COL3 == COL4 == COL5:
        if "achieved_colors" not in rompicapo.specials:
            rompicapo.specials["achieved_colors"] = ""
        if COL1 not in rompicapo.specials["achieved_colors"]:
            rompicapo.specials["achieved_colors"] += color_1
            if ("[red]" in rompicapo.specials["achieved_colors"]
            and "[yellow]" in rompicapo.specials["achieved_colors"]
            and "[green]" in rompicapo.specials["achieved_colors"]
            and "[blue]" in rompicapo.specials["achieved_colors"] 
            and "[darkviolet]" in rompicapo.specials["achieved_colors"]):
                print "STICAZZI!"

        print rompicapo.specials["achieved_colors"]

        #if "[red]" in rompicapo.specials["achieved_colors"]:
        #print "c'è il rosso dentro alla cazzo di special"
        victory_descr = "In poche mosse riesci a ricombinarlo a dovere e te lo riguardi compiaciut$O\n" + colored_description

        player.act(victory_descr, TO.ENTITY, rompicapo)    
        player.act("$n sorride all'indirizzo di $N.", TO.OTHERS, rompicapo)    
        player.act("$n ti ha ricombinato.", TO.TARGET, rompicapo)    

        #rompicapo_keyword = player.get_keywords_attr(rompicapo).split()[0]
        #look_an_entity(player, rompicapo)

    else:
        player.act("Ti cimenti con $N scombinandone i colori.", TO.ENTITY, rompicapo)    
        player.act("$n ti scombina un poco cercando una combinazione cromatica decente.", TO.TARGET, rompicapo)    
        player.act("$n si cimenta con $N scombinandone i colori.", TO.OTHERS, rompicapo)    
#- Fine Funzione -
