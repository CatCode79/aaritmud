# -*- coding: utf-8 -*-

#= DESCRIPTION =================================================================

# la Tessi è un mob stanziale che si trasforma in barbagianni per alcune ore
# della notte. Durante tale periodo la sua interazione con pg si limita a
# qualche stridio
# Quando un pg guarda la Tessi, essa propone al pg di fargli ritrovare il suo
# fermaglio. Se il pg accetta vengono generati un fermaglio un bozzolo e un
# ragno fermaglio in bozzolo che segue ragno e tutto messo nel labirinto di
# pietra sotto al villaggio (accessibile via portale "enter pozzo").
# Per un certo tempo la Tessi aspetta che qualcuno le riporti il fermaglio
# (che sia chi ha startato la quest o qualcun altro)
# aprendo il bozzolo (container_one_time) compare un mob (nugolo ragnetti) che
# attacca.

# Il premio quest è un medaglione (container) con una pomata che se presa si
# indossa alle mani. Essa è una key per aprire il muro di rovi oltre il quale
# c'è il vero premio quest.

# Indizi per la quest sono:
# - apprendista tagliapietre che ti parla del muro di rovi
# - quaderno nascosto dietro secret del villaggio con storia di oltre i rovi
# - in locanda si sente nel brusio che la tessi mette alla prova avventurieri
# - nel pozzo un esserino, guardato si lamenta di un ragno ladro di luccichini


#= IMPORT ======================================================================

import random
import re

from src.database import database
from src.defer    import defer, defer_random_time, defer_if_possible
from src.enums    import RACE, TO
from src.item     import Item
from src.mob      import Mob
from src.social   import get_target_implicetely
from src.utility  import copy_existing_attributes, is_same

from src.commands.command_drop import command_drop
from src.commands.command_give import command_give
from src.commands.command_say  import command_say
from src.commands.command_yell import command_yell


#= COSTANTI ====================================================================

ALFA_ONLY_PATTERN = re.compile("[^a-zA-Zì ]+")

TESSI_PROTO_CODE          = "villaggio-zingaro_mob_test-tessi"
RAGNO_PROTO_CODE          = "villaggio-zingaro_mob_ragno-grotta"
BOZZOLO_PROTO_CODE        = "villaggio-zingaro_item_bozzolo"
FERMAGLIO_PROTO_CODE      = "villaggio-zingaro_item_quest-fermacapelli"
FAKE_FERMAGLIO_PROTO_CODE = "villaggio-zingaro_item_quest-fake-fermacapelli"

MEDAGLIONE_PROTO_CODE = "villaggio-zingaro_item_medaglione"
UNGUENTO_PROTO_CODE   = "villaggio-zingaro_item_unguento-01"

ROOM_PROTO_CODE       = "villaggio-zingaro-maze_room_tana-ragno"

BARBAGIANNI_PROTO = database["proto_mobs"]["villaggio-zingaro_mob_tessitrice-barbagianni"]
TESSITRICE_PROTO  = database["proto_mobs"]["villaggio-zingaro_mob_tessitrice"]


#= FUNZIONI ====================================================================

def on_sunrise(test_tessi):
    # La copia di attributi copia anche la variabile location
    # e tale variabile è None per mob non in game

    location = test_tessi.location
    copy_existing_attributes(TESSITRICE_PROTO, test_tessi, except_these_attrs=["code", "items", "mobs", "players"])
    test_tessi.after_copy_existing_attributes()
    test_tessi.location = location

    print "villaggio-zingaro_mob_test-tessi - >>>  On Sunrise done  <<<"
    location.act("\nIl fiero rapace, straziato dal dolore, si è trasformato...")
#- Fine Funzione -


def on_midnight(test_tessi):
    location = test_tessi.location
    copy_existing_attributes(BARBAGIANNI_PROTO, test_tessi, except_these_attrs=["code", "items", "mobs", "players"])
    test_tessi.after_copy_existing_attributes()
    test_tessi.location = location

    print "villaggio-zingaro_mob_test-tessi - >>>  On Sunset done  <<<"
    location.act("\nLa tessitrice, lacerata dal dolore, si è trasformata in un rapace.")
#- Fine Funzione -


#-------------------------------------------------------------------------------

def before_look(player, tessi, descr, detail, use_examine, behavioured):
    if not player.IS_PLAYER:
        print "villaggio-zingaro_mob_test-tessi - >>> NO PLAYER <<<"
        return

    if "lookable" in tessi.specials and not tessi.specials["lookable"]:
        print "villaggio-zingaro_mob_test-tessi - >>> NON LOOK <<<"
        return

    if tessi.race == RACE.TUAREG:
        print "villaggio-zingaro_mob_test-tessi - >>> TUAREG <<<"
        defer_if_possible(1, 2, tessi, player, ask_help, tessi, player)
    else:
        print "villaggio-zingaro_mob_test-tessi - >>> BAGGIA <<<"
        to_say = "a %s skreee skreee!" % player.code
        defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say)

    tessi.specials["lookable"] = False
    defer_random_time(10, 12, lookable_again, tessi)
#- Fine Funzione -


def lookable_again(tessi):
    if not tessi:
        return
    tessi.specials["lookable"] = True
#- Fine Funzione -


def ask_help(tessi, player):
    if not tessi or not player:
        return

    print "villaggio-zingaro_mob_test-tessi - >>>  ask_help <<<"
    # (TD) calcolo del tempo rimanente per la quest già in corso

    if "player_on_quest" in tessi.specials and tessi.specials["player_on_quest"]:
        if player.code == tessi.specials["player_on_quest"]:
            to_say = "a %s *speranzosa* Hai novità riguardo al mio fermaglio scomparso?" % player.code
        else:
            to_say = "a %s *misteriosa* Gentile viandante che mi osservi, dai anche tu manforte agli avventurieri che si son offerti e stanno cercando il mio fermaglio. L'ho perduto mentre mi recavo al pozzo." % player.code
        command_say(tessi, to_say)
        return

    to_say = "a %s *misteriosa* Viandante, tu che poggi l'occhio su di me; sei dispost$o ad aiutarmi a recuperare il fermaglio che ho smarrito oggi?" % player.code
    command_say(tessi, to_say)
    tessi.specials["player_for_reply"] = player.code
    defer_random_time(30, 40, stop_waiting_for_reply, tessi, player)
#- Fine Funzione -


def stop_waiting_for_reply(tessi, player):
    if not tessi or not player:
        return

    tessi.specials["player_for_reply"] = ""
    if "player_on_quest" in tessi.specials and tessi.specials["player_on_quest"]:
        return

    if player.location == tessi.location:
        to_say = "a %s Mi par di capire che quindi non sei interessat$o." % player.code
    else:
        to_say = "Mi par di capire che nessuno sia interessat$o."
    command_say(tessi, to_say)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def after_nod(player, target, argument):
    nod_or_shake(player, target, "si")
#- Fine Funzione -


def after_shake(player, target, argument):
    nod_or_shake(player, target, "no")
#- Fine Funzione -


def nod_or_shake(player, target, argument):
    if not player.IS_PLAYER:
        return

    tessi = get_target_implicetely(player, target, TESSI_PROTO_CODE)
    if not tessi:
        return

    after_listen_say(tessi, player, tessi, argument)
#- Fine Funzione -


def after_listen_say(tessi, player, target, phrase, behavioured):
    if not player.IS_PLAYER:
        return

    # Nel qual caso il giocatore stia parlando con qualcun'altro esce
    if target and target != tessi:
        return

    # Se la tessitrice non è in modalità questosa esce
    if tessi.race == RACE.BIRD:
        return

    # Se la tessitrice non è in attesa di risposta allora esce
    if "player_for_reply" not in tessi.specials or not tessi.specials["player_for_reply"]:
        return

    # Si assicura che il giocatore che ha parlato sia quello che ha attivato la quest
    if player.code != tessi.specials["player_for_reply"]:
        return

    phrase = ALFA_ONLY_PATTERN.sub("", phrase)
    if is_same(phrase, "no"):
        defer_random_time(1, 2, stop_waiting_for_reply, tessi, player)
        return

    if not is_same(phrase, ("si", "certo")):
        return

    print "villaggio-zingaro_mob_test-tessi -  tessi ", tessi.code
    tessi.specials["player_for_reply"] = ""

    print "villaggio-zingaro_mob_test-tessi - >>> ora cerco una room <<<"
    room = find_room(ROOM_PROTO_CODE)
    if not room:
        print "villaggio-zingaro_mob_test-tessi - >>> nessuna room trovata per testtessi. Exit  <<<"
        to_say = "a %s *imbarazzata* Uh, oh... ora ricordo dove ho messo il fermaglio; perdonami, tutto risolto." % player.code
        defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say)
        tessi.specials["player_on_quest"] = ""
        return

    ragno     = inject_if_inexist_on_area(RAGNO_PROTO_CODE, room)
    bozzolo   = inject_if_inexist_on_area(BOZZOLO_PROTO_CODE, room)
    fermaglio = inject_if_inexist_on_area(FERMAGLIO_PROTO_CODE, bozzolo)

    to_say_1 = "a %s *compiaciuta* Ti ringrazio! Ricordo d'aver smarrito il fermaglio tornando qui dopo aver bevuto al pozzo." % player.code
    to_say_2 = "a %s Non impiegare più di tre giorni nella ricerca, se tornerai in tempo verrai ricompensat$o." % player.code
    defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say_1)
    defer_if_possible(3, 4, tessi, player, command_say, tessi, to_say_2)
    tessi.specials["player_on_quest"] = player.code
    start_quest_timer(player, tessi)
#- Fine Funzione -


def start_quest_timer(player, tessi):
    # 8640s sono tre giorni rpg e oltre due ore e mezza rl
    defer(8640, reset_quest, tessi)
    #defer(8640, reset_quest, player, tessi)
#- Fine Funzione -


def find_room(proto_code):
    """
    Ricava una sola random room dal database del mud tramite prototipo.
    """
    rooms = []
    for room in database["rooms"].itervalues():
        #print room.prototype.code, proto_code
        if room.prototype.code == proto_code:
            rooms.append(room)
            print "villaggio-zingaro_mob_test-tessi - >>> Room ragno trovata  <<< ", room

    if rooms:
        return random.choice(rooms)
    else:
        return None
#- Fine Funzione -


# (GATTO) Attenzione, forse non è esattamente quello che si sarebbe voluto
def inject_if_inexist_on_area(proto_code, location):
    type = proto_code.split("_")[1]

    # Se trova già un'entità esistente nell'area della locazione la recupera per la quest
    # (TD) attenzione che per ora ignora il fatto che vi possano essere più
    # entità in gioco, magari non in quest'area
    for entity in getattr(location.area, type + "s"):
        if not entity.IS_PLAYER and entity.prototype.code == proto_code:
            return entity.split_entity(1)

    if type == "mob":
        entity = Mob(proto_code)
    else:
        entity = Item(proto_code)
    entity.inject(location)
    return entity
#- Fine Funzione -


#-------------------------------------------------------------------------------

def before_giving(player, item, tessi, direction, behavioured):
    if tessi.race == RACE.BIRD:
        to_say = "a %s skreee skreee!" % player.get_numbered_keyword(tessi)
        command_say(tessi, to_say)
        return True

    if not player.IS_PLAYER:
        to_say = "a %s Sei gentile, ma non posso accettare." % player.get_numbered_keyword(tessi)
        defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say)
        return True

    for proto_fermaglio in database["proto_items"].itervalues():
        if proto_fermaglio.code == FERMAGLIO_PROTO_CODE:
            proto_fermaglio.split_entity(1)
            break
    else:
        print ">>> niente fermaglio nel database <<<"
        to_say = "a %s *imbarazzata* C'è stato un problema, mi spiace ma non c'è più il mio fermaglio! La ricerca va abbandonata." % player.code
        defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say)
        tessi.specials["player_on_quest"] = ""
        return True

    if proto_fermaglio.code != item.prototype.code:
        to_say = "a %s *rabbuiata* Non è questo quello che ho smarrito, mi dispiace." % player.code
        defer_if_possible(1, 2, tessi, player, command_say, tessi, to_say)
        return True

    if "player_on_quest" not in tessi.specials:
        return True

    if not tessi.specials["player_on_quest"]:
        print ">>> di qui non si dovrebbe passare a meno che qualche admin abbia creato item <<<"
        return True

    # Se il giocatore che porta il fermaglio non è quello della quest la
    # tessitrice lo accetta lo stesso ma non viene dato nessun reward
    if player.code != tessi.specials["player_on_quest"]:
        original_player = database["players"][tessi.specials["player_on_quest"]]
        to_say = "a %s *sorpresa* Ma tu non sei %s..." % (player.code, original_player.get_name(player))
        defer_if_possible(1, 1, tessi, player, command_say, tessi, to_say)
        #return False

    quest_reward(player, item, tessi)
    return False
#- Fine Funzione -


def quest_reward(player, item, tessi):
    if tessi.location != player.location:
        to_say = "a %s %s, ma dove scappi? Non vuoi la ricompensa dopo tanto affanno? Vabbè!" % (player.code, player.name)
        command_say(tessi, to_say)
        return

    # (GATTO) il valore forse è da tarare
    experience = 100 * max(1, player.level / 2)
    player.experience += experience
    player.send_output("Guadagni [white]%d[close] di esperienza!" % experience)

    tessi.specials["player_on_quest"] = ""
    #to_say = "Quest False"
    #command_say(tessi, to_say)

    to_say_1 = "a %s È proprio il mio fermacapelli! Dopo tanto affanno ecco a te un piccolo presente come ringraziamento." % player.code
    defer_if_possible(1, 1, tessi, player, command_say, tessi, to_say_1)

    # Poiché un'iniezione silenziosa di un oggetto ad un giocatore non è molto
    # friendly allora dà il medaglione alla tessitrice e quest'ultima lo dà
    # al giocatore tramite un give
    medaglione = Item(MEDAGLIONE_PROTO_CODE)
    unguento   = Item(UNGUENTO_PROTO_CODE)
    medaglione.inject(tessi)
    unguento.inject(medaglione)
    defer_if_possible(2, 2, tessi, player, give_reward, tessi, medaglione, player)

    to_say_2 = "a %s Adoperalo con saggezza, solo quando saprai che farne perché potrai utilizzarlo una sola volta." % player.code
    defer_if_possible(3, 3, tessi, player, command_say, tessi, to_say_2)

    defer(4, reset_quest, tessi)
#- Fine Funzione -


def give_reward(tessi, medaglione, player):
    if not tessi or not medaglione or not player:
        return

    execution_result = command_give(tessi, "%s %s" % (medaglione.get_numbered_keyword(tessi), player.get_numbered_keyword(tessi)))
    if not execution_result:
        # La causa più tipica (non bacosa) per cui il give non vada a buon fine
        # è perché il giocatore ha un peso trasportato troppo grande
        command_say(tessi, "a %s Non riesco a dartel$o, te lo lascio per terra." % player.code)
        execution_result = command_drop(tessi, medaglione.get_numbered_keyword(tessi))
        if not execution_result:
            command_say(tessi, "a %s *sospirando* Arrivati a questo punto a mali estremi, estremi rimedi... Ecco! Dovresti averlo in inventario." % player.code)
            medaglione = medaglione.from_location(1)
            medaglione.to_location(player)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def reset_quest(tessi):
    """
    Elimina tutte le entità relative la quest: ragni, bozzoli e sostituisce
    eventuali fermagli addosso ai giocatori.
    """
    if not tessi:
        return

    bozzolo = find_item(BOZZOLO_PROTO_CODE)
    while bozzolo:
        print ">>> removing bozzolo<<< ", bozzolo.code
        player_container = bozzolo.get_player_carrier()
        #print ">>> <<< : ", player_container.code
        if player_container:
            player_container.act("\nHai come una sensazione di vuoto, ma poi passa.", TO.ENTITY)
            #player_container.act("Cipolla to others", TO.TARGET)
            player_container.act("$N si rabbuia per un secondo e poi si ricompone.", TO.OTHERS)
        bozzolo.extract(1)
        bozzolo = find_item(BOZZOLO_PROTO_CODE)

    ragno = find_mob(RAGNO_PROTO_CODE)
    while ragno:
        print ">>> removing ragno<<< ", ragno.code
        # (GATTO) sì, ma sarebe da testare che un pg picchi un ragno durante
        # questo extract, mi sa che cosa brutte accadrebbero
        ragno.extract(1)
        ragno = find_mob(RAGNO_PROTO_CODE)

    reset_fermaglio()

    tessi.specials["lookable"] = True
    tessi.specials["player_for_reply"] = ""
    tessi.specials["player_on_quest"] = ""
#- Fine Funzione -


def find_item(proto_code):
    """
    Ricava la room dal database del mud tramite prototipo.
    """
    for item in database["items"].itervalues():
        #print "Acciderbolina >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", item.proto
        #if not item:
        #    pass
         if item.prototype.code == proto_code:
            return item.split_entity(1)

    return None
#- Fine Funzione -


def find_mob(proto_code):
    """
    Ricava il mob dal database del mud tramite prototipo.
    """
    for mob in database["mobs"].itervalues():
        if mob.prototype.code == proto_code:
            return mob.split_entity(1)

    return None
#- Fine Funzione -


def reset_fermaglio():
    """
    Cerca le copie di fermagli e le rimuove, ma se son in inventario dei
    player li sostituisce con la fuffa.
    """
    for fermaglio in reversed(database["items"].values()):
        if fermaglio.prototype.code != FERMAGLIO_PROTO_CODE:
            continue
        if not fermaglio.location:
            fermaglio.extract(1)
        player_container = fermaglio.get_player_carrier()
        if player_container:
            location = fermaglio.location
            fermaglio.extract(1)
            dummy_fermaglio = Item(FAKE_FERMAGLIO_PROTO_CODE)
            dummy_fermaglio.inject(location)
        else:
            fermaglio.extract(1)
#- Fine Funzione -


#-------------------------------------------------------------------------------

def before_killed(player, tessi, attack, destroy, behavioured):
    return tessi_defence(player, tessi)
#- Fine Funzione -


def before_kicked(player, tessi, behavioured):
    return tessi_defence(player, tessi)
#- Fine Funzione -


def tessi_defence(player, tessi):
    if tessi.race == RACE.BIRD:
        player.act("$N si alza in volo mentre uno stormo di volatili t'investe in tutta la sua furia.", TO.ENTITY, tessi)
        player.act("tu che sei $N fai desistere $n!", TO.TARGET, tessi)
        player.act("$N si alza in volo evitando il colpo mentre uno stormo di volatili investe $n in tutta la sua furia.", TO.OTHERS, tessi)
        player.life -= give_damage(player)
    else:
        player.act("$N guarda verso di te con gli occhi bianchi alzando l'indice verso l'alto.\nDal cielo, uno stormo di volatili t'investe in tutta la sua furia.", TO.ENTITY, tessi)
        player.act("tu che sei $N fai desistere $n!", TO.TARGET, tessi)
        player.act("$N guarda verso $n alzando l'indice verso l'alto.\nDal cielo, uno stormo di volatili investe $n con furia cieca.", TO.OTHERS, tessi)
        player.life -= give_damage(player)
    return True
#- Fine Funzione -


def give_damage(player):
    damage = random.randint(1,15)
    if player.life <= damage:
        damage = 0
    return damage
#- Fine Funzione -


#-------------------------------------------------------------------------------

def on_booting(tessi):
#def on_reboot(tessi):
    """
    Se il mob viene reso persistente a metà quest controlla se ha le
    informazioni necessarie per riprenderla da zero, altrimenti la resetta.
    """
    if "player_on_quest" in tessi.specials and tessi.specials["player_on_quest"]:
        player = database["players"][tessi.specials["player_on_quest"]]
        start_quest_timer(player, tessi)
    else:
        reset_quest(tessi)
#- Fine Funzione -
