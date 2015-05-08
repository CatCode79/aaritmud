# -*- coding: utf-8 -*-
 
#= DESCRIZIONE =================================================================
 
# - Dai un pesce alla gatta e lei in tutta risposta ti vomita una palla di pelo
#   e alla fine si mangia il pesce che le hai portato.
# - Se però ciò che le dai è qualcosa che ha a che fare con gli agrumi ti 
#   attacca senza troppi complimenti.

 
#= IMPORT ======================================================================
 
import random

from src.defer   import defer_random_time
from src.enums   import TO, ENTITYPE, RACE, FLAG
from src.item    import Item
from src.utility import is_same, multiple_arguments

from src.commands.command_eat import command_eat

 
#= COSTANTI ====================================================================
 
PROTO_FUR_CODE = "villaggio-zingaro_item_quest-palla-pelo"
PESO_MASSIMO = 1000


#= FUNZIONI ====================================================================

def before_giving(player, pesce, gatto, direction, behavioured):
    if not player.IS_PLAYER:
        player.act("$N ti soffia e fa come per graffiarti, non sei una compagnia desiderabile.", TO.ENTITY, gatto)
        player.act("$N, con il pelo ritto sulla schiena, scaccia $n in malomodo.", TO.OTHERS, gatto)
        player.act("$n ti si avvicina un po' troppo per i tuoi gusti e lo scacci senza troppi complimenti.", TO.TARGET, gatto)
        return True

    pesce_keywords = multiple_arguments(pesce.get_keywords_attr(looker=gatto))
    if is_same(pesce_keywords, ("agrumi", "agrume", "arance", "arancia", "limone", "limoni", "bergamotto", "mandarino", "mandarini", "pompelmo", "pompelmi", "cedro", "cedri", "mandarancio", "mandaranci", "lime")):
        num_rand = random.randint(1, 100)
        if num_rand < 75:
            player.act("$N ti attacca in un raptus di furia assassina!", TO.ENTITY, gatto)
            player.act("Apparentemente senza ragione $N attacca $n.", TO.OTHERS, gatto)
            player.act("Quel pazzo di $n ha tentato di darti un agrume, la dovrà pagare!", TO.TARGET, gatto)
            player.life -= give_damage(player)
            return True
        else:
            player.act("$N sguaina le unghie e tenta di attaccarti ma fortunatamente manca il colpo.", TO.ENTITY, gatto)
            player.act("$N fa uno scatto verso $n come per attaccarlo ma la zampata non va a buon fine.", TO.OTHERS, gatto)
            player.act("Tenti di attacare $n ma non ci riesci", TO.TARGET, gatto)
            return True

    if not pesce.entitype == ENTITYPE.FOOD or not is_same(pesce_keywords, ("pesce", "pesci")):
        player.act("$N storce i baffi schizzinoso.", TO.ENTITY, gatto)
        player.act("$n tenta inutilmente di dare qualcosa a $N che lo snobba schizzinoso.", TO.OTHERS, gatto)
        player.act("$n tenta di propinarti qualcosa che anche un cane rifiuterebbe.", TO.TARGET, gatto)
        return True

    if pesce.weight > PESO_MASSIMO:
        player.act("$N ti guarda perplesso dopo aver valutato il peso di ciò che gli vorresti dare.", TO.ENTITY, gatto)
        player.act("Noti uno strano gioco di sguardi tra $N e $n.", TO.OTHERS, gatto)
        player.act("$n cerca di darti qualcosa di veramente troppo pesante per te.", TO.TARGET, gatto)
        return True

    for content in gatto.iter_contains(use_reversed=True):
        if FLAG.INGESTED in content.flags:
            if content.entitype == ENTITYPE.FOOD:
                player.act("$N rifiuta il cibo che gli offri, d'evessere sazio!", TO.ENTITY, gatto)
                player.act("$n vorrebbe dare qualcosa a $N che però non sembra interessato..", TO.OTHERS, gatto)
                player.act("$n vorrebbe ingozzarti, la tua dignità di impedisce di far la figura del maiale all'ingrasso..", TO.TARGET, gatto)
                return True
            else:
                content.extract(1)
                return True

    palla = Item(PROTO_FUR_CODE)
    defer_random_time(1, 3, puke_hairs, gatto, player, palla)
    defer_random_time(4, 5, fish_eat, player, gatto, pesce)
#- Fine Funzione


def fish_eat(player, gatto, pesce):
    """
    Cerca la keyword di ciò che mangerà il gatto
    """
    # Può capitare poiché questa funzione è deferrata
    if not player or not gatto or not pesce:
        return

    numbered_keyword = pesce.get_numbered_keyword(looker=player)
    command_eat(gatto, first_keyword)
    # (TD) volendo questi messaggi si possono utilizzare come messaggi di eat
    # personalizzati, bisognerebbe impostarli temporaneamente, se non già
    # esistenti, nella struttura food_type del pesce
    #player.act("\n$N trangugia tutto con una voracità inaudita.\n", TO.ENTITY, gatto)
    #player.act("Il cibo è appena passabile ma tifingi soddistatto finendolo in un sol boccone.", TO.TARGET, gatto)
    #player.act("\nVedi $N mangiare qualcosa con un tal voracità che forse anche tu ne vorresti un po'.\n", TO.OTHERS, gatto)
#- Fine Funzione


def puke_hairs(gatto, player, palla):
    """
    Inietta la palla di pelo.
    """
    # Può capitare poiché questa funzione è deferrata
    if not gatto or not player or not palla:
        return

    palla.inject(gatto.location)

    gatto.act("\n$n pare soffocare, ma alla fine vomita una bavosa palla di pelo e ti guarda con risentimento.", TO.ENTITY, player)
    gatto.act("\n$n pare soffocare, ma alla fine vomita qualcosa di peloso e bagnato.", TO.OTHERS, player)
    gatto.act("Vomiti un'enorme palla di pelo.", TO.TARGET, player)
#- Fine Funzione


def give_damage(player):
    damage = random.randint(1, 15)
    if player.life <= damage:
        damage = 0
    return damage
#- Fine Funzione
