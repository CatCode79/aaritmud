# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random
import re

from src.database import database
from src.defer    import defer_if_possible, defer, defer_random_time
from src.enums    import FLAG, TO
from src.item     import Item
from src.mob      import Mob
from src.utility  import is_infix

from src.commands.command_say import command_say


#= COSTANTI ====================================================================

ALFA_ONLY_PATTERN = re.compile("[^a-zA-Zì ]+")

GOLEM_PROTO_CODE = {"paglia"   :   "novizi2_mob_golem-paglia",
                    "pergamena":   "novizi2_mob_golem-pergamena",
                    "corda"    :   "novizi2_mob_golem-corda",
                    "legno"    :   "novizi2_mob_golem-legno",
                    "carne"    :   "novizi2_mob_golem-carne",
                    "cuoio"    :   "novizi2_mob_golem-cuoio",
                    "argilla"  :   "novizi2_mob_golem-argilla"}

ITEM_PROTO_CODE = {"paglia"   :   "ikea_item_covone-paglia",
                   "pergamena":   "ikea_item_pergamena",
                   "corda"    :   "torreelementi_item_corda_elfica",
                   "legno"    :   "ikea_item_bastoni-mucchio",
                   "carne"    :   "ikea_item_carne-scarti",
                   "cuoio"    :   "ikea_item_cuoio-pezzi",
                   "argilla"  :   "ikea_item_argilla"}

PHRASES =         {"paglia"   :   "$n compone $N in una sagoma aliena",
                   "pergamena":   "$n piega sapientemente $N in forma di scimmia",
                   "corda"    :   "$n annoda svogliatamente $N per darle corpo",
                   "legno"    :   "$n incrocia $N in modo bizzarro",
                   "carne"    :   "$n dispone $N con trascurata minuziosità",
                   "cuoio"    :   "$n ammonticchia $N senza molta convinzione",
                   "argilla"  :   "$n modella $N in una figura umanoide"}

WAKE_UP =         {"paglia"   :   "una brezza accarezza $n che non smette di muoversi anche quando il vento si è seduto.",
                   "pergamena":   "$n comincia a gemere in uno stropiccìo animato.",
                   "corda"    :   "$n si muove come dotata di vita propria.",
                   "legno"    :   "$n si alzano a fatica assumendo posizione eretta.",
                   "carne"    :   "$n si animano di una vita che però vita non è.",
                   "cuoio"    :   "$n a guisa di armatura si drizzan in un barlume di vita.",
                   "argilla"  :   "$n comincia a muovere i primi umidi passi."}

STAT =            {"paglia"   :   [0.2, -4, 1],
                   "pergamena":   [0.4, -3, 1],
                   "corda"    :   [0.6, -2, 1],
                   "legno"    :   [0.8, -1, 1],
                   "carne"    :   [1.0,  0, 1],
                   "cuoio"    :   [1.2,  1, 1],
                   "argilla"  :   [1.4,  2, 1]}


#= FUNZIONI ====================================================================
# modellarono la terra e crearono una figura di dimensioni umane: il Golem.
# Quando ebbero finito il rabbino disse ad uno dei suoi alunni: "Hai un carattere di fuoco.
# gira attorno al golem per sette volte e recita ad alta voce le parole sacre.".
# Durante il primo giro la terra bagnata cominciò ad asciugarsi, durante il secondo giro,
# il golem cominciò a sprigionare calore, finchè durante il settimo giro divenne incandescente"
# "ora vai tu che hai carattere d'acqua.." disse ad un secondo studente il rabbino.
# lo studente recità le formule magiche e la massa incadescente cominciò a raffreddarsi.
# Durante il settimo giro il corpo del golem aveva il colore e la temperatura della pelle umana.
# Poi il rabbino stesso cominciò a girare sette volte attorno a golem pronunciando le parole sacre.
# Dopo sette giri si fermò e mise un pezzetto sacro di pergamena con dei simboli segreti nella bocca del golem.
# Allora il corpo del golem cominciò a tremare, gli occhi si aprirono e si sedette.

def after_smile(player, apprendista, argument):
    if not apprendista:
        return
    defer_if_possible(1, 2, apprendista, player, spiegazioni, apprendista, player)
#- Fine Funzione -


def after_wave(player, apprendista, argument):
    if not apprendista:
        return
    defer_if_possible(1, 2, apprendista, player, spiegazioni, apprendista, player)
#- Fine Funzione -


def after_listen_rpg_channel(apprendista, player, target, phrase, ask, exclaim, behavioured):
    if target != apprendista:
        return

    if "work_in_progress" in apprendista.specials and apprendista.specials["work_in_progress"]:
        return

    apprendista.specials["work_in_progress"] = True
    defer(10, change_status, apprendista)

    phrase = ALFA_ONLY_PATTERN.sub("", phrase)
    choosed_materials = []
    for materiale in ITEM_PROTO_CODE.keys():
        if is_infix(materiale, phrase):
            choosed_materials.append(materiale)
    if not choosed_materials:
        defer_if_possible(1, 2, target, player, spiegazioni, target, player)
    else:
        choosed_material = random.choice(choosed_materials)
        defer_random_time(1, 2, generate_item, apprendista, player, choosed_material, apprendista.location)
#- Fine Funzione -


def change_status(apprendista):
    # Normale che possa accadere visto che la funzione viene deferrata
    if not apprendista:
        return
    apprendista.specials["work_in_progress"] = False
#- Fine Funzione -


def spiegazioni(apprendista, player):
    # Normale che possa accadere visto che la funzione viene deferrata
    if not apprendista or not player:
        return

    if not player.IS_PLAYER:
        return

    to_say = "a %s *apprensivo* Io ti posso creare un golem per esercitarti a combattere ma mi devi dire di che materiale lo vuoi." % player.code
    command_say(apprendista, to_say)

    example = random.choice(ITEM_PROTO_CODE.keys())
    to_say = "a %s Per esempio potresti volerlo di %s." % (player.code, example)
    defer_if_possible(1, 2, apprendista, player, command_say, apprendista, to_say)
#- Fine Funzione -


def generate_item(apprendista, player, choosed_material, room):
    # Normale che possa accadere visto che la funzione viene deferrata
    if not apprendista or not player or not room:
        return

    to_say = "Uhm... un golem di %s... Cominciamo un po'..." % choosed_material
    command_say(apprendista, to_say)

    proto_item_code = ITEM_PROTO_CODE[choosed_material]
    item = Item(proto_item_code)
    item.flags += FLAG.NO_GET
    item.inject(room)

    # (bb) perché funzioni al meglio il sistema di persistent act qui bisogna
    # che esista anche il messaggio a TO.ENTITY, da aggiungere quindi
    apprendista.act(PHRASES[choosed_material], TO.OTHERS, item)
    defer_random_time(12, 20, generate_golem, apprendista, player, choosed_material, room, item)
#- Fine Funzione -


def generate_golem(apprendista, player, choosed_material, room, item):
    # Normale che possa accadere visto che la funzione viene deferrata
    if not apprendista or not player or not room or not item:
        return

    proto_mob_code = GOLEM_PROTO_CODE[choosed_material]
    mob = Mob(proto_mob_code)
    mob.inject(room)

    mob_calibration(mob, player, choosed_material)
   
    item.act(WAKE_UP[choosed_material], TO.OTHERS, mob)
    item.extract(1)
    apprendista.specials["work_in_progress"] = False
#- Fine Funzione -


def mob_calibration(mob, player, choosed_material):
    mob.max_life = int(0.5 + player.max_life * STAT[choosed_material][0])
    mob.life = mob.max_life

    # (TD) queste caratteristiche prossimamente verranno meno sostituite da delle skill
    mob.strength  = int(0.5 + player.strength  + STAT[choosed_material][1])
    mob.agility   = int(0.5 + player.agility   + STAT[choosed_material][1])
    mob.endurance = int(0.5 + player.endurance + STAT[choosed_material][1])
    mob.speed     = int(0.5 + player.speed     + STAT[choosed_material][1])
    mob.luck      = int(0.5 + player.luck      + STAT[choosed_material][1])
#- Fine Funzione -
