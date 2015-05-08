# -*- coding: utf-8 -*-


#= TODO LIST ===================================================================

# (TD) Caricare un oggetto premio invece del messaggio di STICAZZI
#      (farei in modo che se un pg vince, e tocca un'altra volta il coso, perde
#       l'oggetto vittoria, cmq in realta'  io potenzierei semmai l'oggetto
#       rubiko, cosa infattibile visto che non ci sono ancora gli affect, pero'
#       ce lo vedo il rubikoso potenziato in mano ai pg che se toccato per
#       sbaglio un altra volta perde i poteri fino a che non viene rifatto
#       il tutto; e' un metodo anti invio comando touch a manetta)
# (TD) Limitare ad uno il numero dei movimenti di un colore solo
# (TD) Invece di cambiare un solo colore con il successivo meglio renderlo casuale


#= IMPORT ======================================================================

import random

from src.defer import defer
from src.enums import FLAG, TO
from src.item  import Item
from src.log   import log

from src.commands.command_look import look_an_entity


#= COSTANTI ====================================================================

PRICE_PROTO_CODES = [ "novizi2_item_premio-rompicapo-algiz",
                      "novizi2_item_premio-rompicapo-naudiz",
                      "novizi2_item_premio-rompicapo-kaunan",
                      "novizi2_item_premio-rompicapo-wunjo" ]

COLOR_CODES = ["[red]",
               "[yellow]",
               "[green]",
               "[blue]",
               "[darkviolet]"]


#= FUNZIONI ====================================================================

def before_touch(player, rompicapo, descr, detail, behavioured):
    """
    A seconda che si tocchi l'oggetto o una sua extra lancia lo scramble con
    parametri diversi:
    ael primo caso scrambla tutto
    nel secondo caso cambia il colore del tassello indicato e del successivo.
    """
    if detail.IS_EXTRA:
        print "Extra Touched"
        return scramble(rompicapo, player, detail.keywords)
    else:
        scramble(rompicapo, player, "scramble_all")
#- Fine Funzione -


def scramble(rompicapo, player, posizione):
    print "posizione: ", posizione
    if "completed" not in rompicapo.specials:
        rompicapo.specials["completed"] = False

    # randomizza tutto se toccato o inizializza per la prima volta con una extra
    if posizione == "scramble_all" or "sequence" not in rompicapo.specials:
        color_1 = random.choice(COLOR_CODES)
        color_2 = random.choice(COLOR_CODES)
        color_3 = random.choice(COLOR_CODES)
        color_4 = random.choice(COLOR_CODES)
        color_5 = random.choice(COLOR_CODES)
        rompicapo.specials["sequence"] = [color_1, color_2, color_3, color_4, color_5]

    # Qui invece entra se è stata toccata una extra
    if posizione != "scramble_all":
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

        # Cambio di uno solo dei colori in relazione a quale delle 5 extra son usate
        touched_color = rompicapo.specials["sequence"].pop(position)
        next_color = COLOR_CODES.index(touched_color) + 1
        if next_color >= len(COLOR_CODES):
            next_color = 0
        rompicapo.specials["sequence"].insert(position, COLOR_CODES[next_color])

        # Cambia anche il colore della tessera successiva
        #if (position + 1) >= 5:
        if (position + 1) >= len(rompicapo.specials["sequence"]):
            position = -1
        near_color = rompicapo.specials["sequence"].pop(position+1)
        previous_color = COLOR_CODES.index(near_color) -1
        if previous_color < 0:
            previous_color = len(COLOR_CODES) -1
        rompicapo.specials["sequence"].insert(position+1, COLOR_CODES[previous_color])

    sequence = rompicapo.specials["sequence"]
    print sequence

    description = "Un rompicapo con decine di pezzi liberi di ruotare e' l'omaggio ai partecipanti alla [gold]sesta apertura[close]! Per scombinarlo basta toccarlo. Le lettere formano la scritta:<br>"
    nice_things = "[white] ========= [close]"
    border = "<br>[white] =============================== [close]<br>"

    colored_description = border + nice_things + rompicapo.specials["sequence"][0] + "VI " + rompicapo.specials["sequence"][1] + "AP" + rompicapo.specials["sequence"][2] + "ER" + rompicapo.specials["sequence"][3] + "TU" + rompicapo.specials["sequence"][4] + "RA[close]" + nice_things + border
    rompicapo.descr = description + colored_description

    # Controlla se si son ottenuti 5 colori uguali e se sono anche state
    # ottenute tutte e 5 le diverse sequenze di colori
    if sequence[0] == sequence[1] == sequence[2] == sequence[3] == sequence[4]:
        if "achieved_colors" not in rompicapo.specials:
            rompicapo.specials["achieved_colors"] = ""
        if sequence[0] not in rompicapo.specials["achieved_colors"]:
            rompicapo.specials["achieved_colors"] += sequence[0]
            if ("[red]"        in rompicapo.specials["achieved_colors"]
            and "[yellow]"     in rompicapo.specials["achieved_colors"]
            and "[green]"      in rompicapo.specials["achieved_colors"]
            and "[blue]"       in rompicapo.specials["achieved_colors"]
            and "[darkviolet]" in rompicapo.specials["achieved_colors"]):
                if rompicapo.specials["completed"] == False:
                    location = rompicapo.location
                    defer(1, carica_regalo, player, location, rompicapo)
                    rompicapo.specials["completed"] = True
                    print "STICAZZI! YOU WIN"

        print rompicapo.specials["achieved_colors"]

        #if "[red]" in rompicapo.specials["achieved_colors"]:
        #print "c'e' il rosso dentro alla cazzo di special"
        victory_descr = "In poche mosse riesci a ricombinarlo a dovere e te lo riguardi compiaciut$O\n" + colored_description

        player.act(victory_descr, TO.ENTITY, rompicapo)
        player.act("$n sorride all'indirizzo di $N.", TO.OTHERS, rompicapo)
        player.act("$n ti ha ricombinato.", TO.TARGET, rompicapo)
        return True

        #rompicapo_keyword = player.get_keywords_attr(rompicapo).split()[0]
        #look_an_entity(player, rompicapo)

    else:
        player.act("Ti cimenti con $N scombinandone i colori.", TO.ENTITY, rompicapo)
        player.act("$n ti scombina un poco cercando una combinazione cromatica decente.", TO.TARGET, rompicapo)
        player.act("$n si cimenta con $N scombinandone i colori.", TO.OTHERS, rompicapo)
        return False
#- Fine Funzione -


def carica_regalo(player, location, rompicapo):
    price = Item(random.choice(PRICE_PROTO_CODES))
    price.inject(location)
    player.act("\n[yellow]Hai appena concluso il rompicapo che dal nulla compare un premio![close]\n", TO.ENTITY, rompicapo)
    player.act("\n[yellow]$n fa uno scatto sorpreso all'apparire del premio per $N.[close]\n", TO.OTHERS, rompicapo)
    player.act("Gothcha!.", TO.TARGET, rompicapo)
    print "novizi2_item_rompicapo-colorato - YOU WIN"
#- Fine Funzione -
