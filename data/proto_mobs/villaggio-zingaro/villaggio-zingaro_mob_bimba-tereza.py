# -*- coding: utf-8 -*-

#= NOTE ========================================================================

# Descrizione dinamica del mob a seconda delle ore del giorno
# Si usano due trigger dei momenti della giornata e si fanno 4 o 5 defer


#= IMPORT ======================================================================

import random

from src.log      import log
from src.database import database
from src.enums    import TO, RACE, FLAG, ENTITYPE
from src.defer    import defer_random_time

from src.commands.command_say import command_say
from src.commands.command_eat import command_eat


#= COSTANTI ===================================================================

LOCANDIERA_PROTO_CODE = "villaggio-zingaro_mob_locandiera-dumitra-hangiu"

bimba_long_db = {1: "smangiucchia assonnata.",
                 2: "saltella scalmanata per la locanda.",
                 3: "mastica senza sosta.",
                 4: "impasta con incredibile impegno.",
                 5: "disegna tranquilla."}

bimba_descr_db = {1: "Una bimbetta con un mare di boccoli legati in due codini asimmetrici inzuppa un gigantesco biscotto in una tazzona di [white]latte[close]. La piccola bocchina tenta di azzannare voracemente il biscotto con l'unico risultato di spargere un mare di bricioline ovunque.",
                  2: "Un piccoletta corre freneticamente da una parte all'altra delle locanda; tocca tutto quello che le capita a tiro portando scompiglio e importunando i clienti.",
                  3: "Una bimba dai grandi [mediumaquamarine]occhioni[close] divora con foga tutto ciò che di commestibile le si presenta davanti,",
                  4: "Una bimbetta intenta ad impastare un pezzo di pasta, svolge questa attività con così grande impegno che non può fare a meno di far spucare una linguetta appuntita tra le labbra; in compenso tutto quello che le sta intorno è impiastricciato di piccoli pezzetti appiccicaticci.",
                  5: "A fine giornata finalmente questo piccolo terremoto si mette tranquillo e con fogli e colori disegna beata, sotto il tavolo però continua a sgambettare senza sosta."}

bimba_act_entity = {1: "[papayawhip]Zietta ti porta una tazza di latte caldo e biscotti a ti arruffa tutti i capelli con la mano.[close]",
                    2: "[papayawhip]Ti stiracchi e stropicci gli occhi..[close]",
                    3: "",
                    4: "[papayawhip]Zietta ti dà un pezzo di pasta e tu ti diverti un sacco giocandoci[close].",
                    5: "[papayawhip]Prendi un foglio e dei pastelli colorati, è ora di disegnare[close]."}        

bimba_act_other = {1: "[papayawhip]La locandiera porta una tazzone di latte caldo e biscotti a $n, poi, le accarezza dolcemente la testolina.[close]",
                   2: "[papayawhip]$n si sitracchia e si stropiccia gli occhi, pronta a portare scompiglio in locanda![close]",
                   3: "",
                   4: "[papayawhip]La locandiera porta porta un pezzo di pasta di pane a $n che si mette subito ad impastare.[close]",
                   5: "[papayawhip]$n corre tutta felice al suo tavolo impugnando un foglio e pastelli colorati.[close]"}        

pietanze_db = {1: "Ho tanta voglia di polpettine oggi!",
               2: "Mi porti della zuppa?",
               3: "Mmmm che buon profumo di sformato, ne voglio un po' anche io",
               4: "Gnam gnam budino!"}


#= FUNZIONI ===================================================================

def on_sunrise(bimba):
    defer_random_time(10, 100, change_mob, bimba, 1)
    defer_random_time(140, 240, change_mob, bimba, 2)
#- Fine Funzione -


def on_noon(bimba):
    defer_random_time(10, 110, change_mob, bimba, 3)
    defer_random_time(150, 240, change_mob, bimba, 4)
    defer_random_time(330, 440, change_mob, bimba, 2)
    defer_random_time(500, 590, change_mob, bimba, 5)
#- Fine Funzione -


def change_mob(bimba, num):
    # Normale che possa capitare visto che la funzione è deferrata
    if not bimba:
        return

    bimba.long = "$N " + bimba_long_db[num]
    bimba.descr = bimba_descr_db[num]

    if num != 3:
        bimba.act(bimba_act_entity[num], TO.ENTITY)
        bimba.act(bimba_act_other[num], TO.OTHERS)
        return

    locandiera = find_mob(LOCANDIERA_PROTO_CODE)
    if not locandiera:
        return

    num_rand = random.randint(1, 100)
    if num_rand < 25: 
        pietanza_label = pietanze_db[1]
    elif num_rand < 65:
        pietanza_label = pietanze_db[2]
    elif num_rand < 88:
        pietanza_label = pietanze_db[3]
    else:
        pietanza_label = pietanze_db[4]

    locandiera_keyword = locandiera.get_numbered_keyword(looker=bimba)
    to_say = "a %s Zietta, ho fame! %s" % (locandiera_keyword, pietanza_label)
    command_say(bimba, to_say)
#- Fine Funzione -


def find_mob(proto_code):
    for mob in database["mobs"].itervalues():
        if mob.prototype and mob.prototype.code == proto_code:
            return mob.split_entity(1)

    return None
#- Fine Funzione -


def before_giving(player, cibo, bimba, direction, behavioured):
    if player.IS_PLAYER or not player.race == RACE.TUAREG:
        to_say = "a %s La mia zietta mi ha detto di non accettare cibo dagli sconosciuti!" % player.code
        command_say(bimba, to_say)
        return True
    else:
        #print "pappa in arrivo"
        defer_random_time(1, 3, cibo_eat, cibo, bimba)
#- Fine Funzione -


def cibo_eat(cibo, bimba):
    # Può accadere visto che tale funzione è deferrata
    if not bimba:
        return

    if not cibo:
        to_say = "Non riesco a mangiare..."
        command_say(bimba, to_say)
        return

    numbered_keyword = cibo.get_numbered_keyword(looker=bimba)
    command_eat(bimba, numbered_keyword)
#- Fine Funzione -
