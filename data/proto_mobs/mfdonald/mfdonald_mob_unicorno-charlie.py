# -*- coding: utf-8 -*-

# Fonte della quest:
# http://www.youtube.com/watch?v=MOmyIHhew-A


#= IMPORT ======================================================================

import random
import re

from twisted.internet import reactor

from src.database import database
from src.log     import log
from src.utility import is_same

from src.enums import ENTITYPE

from src.commands.command_drop import command_drop
from src.commands.command_eat import command_eat
from src.commands.command_emote import command_emote
from src.commands.command_look import command_look
from src.commands.command_murmur import command_murmur
from src.commands.command_say import command_say
from src.commands.command_yell import command_yell
from src.commands.command_whisper import command_whisper


#= COSTANTI ====================================================================

# Questo regex pattern serve a rimuovere tutti i caratteri non alfabetici
# o spazi da una stringa e la vocale accentata 'ì' di un eventuale "sì"
ALFA_ONLY_PATTERN = re.compile("[^a-zA-Zì ]+")


#= FUNZIONI ====================================================================

def on_booting(charlie):
    # Concettualmente al riavvio del gioco è meglio raddoppiare i tempi di
    print "on_booting di charlie", charlie
    # reset in maniera tale che il giocatore abbia il tempo di "riprendersi"
    if charlie.specials:
        reset_call = reactor.callLater(random.randint(400, 600), reset_banana_quest, charlie)
        charlie.specials["start_charlie_banana_quest:reset_call"] = reset_call
#- Fine Funzione -


def on_shutdown(charlie):
    # Cancella i valori di specials da non rendere persistenti
    if  "start_charlie_banana_quest:reset_call" in charlie.specials:
         del(charlie.specials["start_charlie_banana_quest:reset_call"])
#- Fine Funzione -


def start_charlie_banana_quest(player, to_room):
    # La quest deve iniziare solo per i giocatori
    if not player.IS_PLAYER:
        return

    # Controlla se nella stanza c'è charlie
    charlie = None
    for mob in to_room.mobs:
        if mob.code.startswith("mfdonald_mob_unicorno-charlie"):
            charlie = mob.split_entity(1)
            break

    # Non è stato trovato nella stanza, esce
    if not charlie:
        return

    # Ignora il giocatore ogni tanto
    if random.randint(1, 3) == 1:
        return

    # Charlie tra qualche secondo implorerà il giocatore di aiutarlo
    reactor.callLater(random.randint(2, 4), beg_the_player, charlie, player)
#- Fine Funzione -


def beg_the_player(charlie, player):
    # Se charlie e il giocatore non si trovano più nella stessa zona allora esce
    if charlie.location != player.location:
        return

    to_say = "a %s *disperatamente* ti prego.. devi aiutarmi! Dimmi di sì!" % player.code
    command_say(charlie, to_say)

    # Charlieee entra in modalità quest
    # A volte serve salvarsi delle informazioni relative allo stato dei
    # gamescript in corso, per esempio in questo caso ad una quest.
    # Le parole chiave per identificare le differenti informazioni devono avere
    # lo stile che vedi sotto, una parte prefissa e unica preferibilmente per
    # tutti gli special (questo perché alcuni specials potrebbero essere salvati
    # tra gli specials del giocatore, creando conflitti se hanno la stessa
    # parola chiave).
    # Il valore da inserire alla parola chiave dello special è sempre una
    # stringa nel qual caso si voglia salvare il valore tra un boot ed un altro;
    # se serve inserire un valore numerico basta inserirlo come stringa e poi
    # convertirlo successivamente in numero.
    # Nell'esempio vengono salvate tre informazioni:
    # - lo status di sviluppo della quest
    # - il giocatore che è riuscito a prenotare la quest
    # - il conto delle banane da recuperare per charlie
    charlie.specials["charlie_banana_quest:status"] = "domanda"
    charlie.specials["charlie_banana_quest:player"] = player.code

    # Dopo un po' chiede nuovamente al giocatore di rispondere alla sua
    # richiesta di aiuto nel qual caso che il giocatore non abbia afferrato
    # l'indizio di quello che deve fare
    reactor.callLater(random.randint(15, 30), ask_for_answer, charlie, player)

    # Charlie non starà ad aspettare in eterno che il giocatore si decida a
    # iniziare la quest, se dopo un po' di tempo lo status della quest non
    # è cambiato allora gli specials vengono azzerati
    reset_call = reactor.callLater(random.randint(60, 90), reset_banana_quest, charlie)
    charlie.specials["charlie_banana_quest:reset_call"] = reset_call
#- Fine Funzione -


def ask_for_answer(charlie, player):
    # Controlla se la quest non sia già stata resettata oppure avanzata
    if ("charlie_banana_quest:status" not in charlie.specials
    or charlie.specials["charlie_banana_quest:status"] != "domanda"):
        return

    if charlie.location != player.location:
        return

    suffix = ""
    if random.randint(1, 4) == 1:
        suffix = " Ti prego!"

    to_say = "a %s *disperato* Dimmi di sì!%s" % (player.code, suffix)
    command_say(charlie, to_say)

    # Glielo richiede a ruota fino a che il giocatore risponde sì! Fastidioso? :P
    reactor.callLater(random.randint(15, 30), ask_for_answer, charlie, player)
#- Fine Funzione -


# Da notare che qui non è stato utilizzato il trigger after_listen_rpg_channel, che invece
# funziona per tutti i canali rpg, questo funziona ovviamente solo con il canale
# say.
# Il sistema è abbastanza grezzo, in futuro ci sarà il sistema dei dialoghi che
# permetterà un discorso più approfondito con la scelta di voci già pronte
# come risposta, tuttavia per quello che ci serve direi che va bene così
def after_listen_say(charlie, speaker, target, phrase, ask, exclaimi, behavioured):
    if not speaker.IS_PLAYER:
        return

    # Controlla se la quest non sia già stata resettata oppure avanzata
    if ("charlie_banana_quest:status" not in charlie.specials
    or charlie.specials["charlie_banana_quest:status"] != "domanda"):
        return

    # Ricava la frase ripulita dalla punteggiatura e non continua la quest fino
    # a che il giocatore non dice: sì
    phrase = ALFA_ONLY_PATTERN.sub("", phrase)
    if not is_same(phrase, "si"):
        return

    # Guarda il giocatore che ha risposto, brrrr, fa sempre senso vedere i mob
    # così "intelligenti"
    command_look(charlie, speaker.code)

    # Ignora coloro che hanno risposto ma che non sono stati scelti per la quest
    quest_player_code = charlie.specials["charlie_banana_quest:player"]
    if speaker.code != quest_player_code:
        quest_player = database["players"][quest_player_code]
        # Ricava il nome o la short per come lo vede charlie
        to_say = "a %s *concentrato* Grazie, ma no, grazie! Sto aspettando la risposta da %s." % (
            speaker.code, quest_player.get_name(charlie))
        command_say(charlie, to_say)
        return

    # Visto che il secondo stadio della missione si sta attivando cancella il
    # precedente reset che è meglio che sia reimpostato a fine funzione
    delete_charlie_reset_call(charlie)

    # Ecco un nuovo pollo da spennare! Finalmente il giocatore si è deciso a
    # rispondere!
    # Facciamo avanzare lo stato della quest e descriviamo quello che vogliamo
    charlie.specials["charlie_banana_quest:status"] = "cerca"

    to_say = "a %s *esasperato* Non ce la faccio più! Questi due unicorni mi stanno facendo impazzire!" % quest_player_code
    reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)

    to_say = "a %s Portami due banane, cosicché io possa sopportarli almeno per un po'.." % quest_player_code
    reactor.callLater(random.randint(4, 6), command_say, charlie, to_say)

    # (TT) questo è da snoopare.. forse non funziona il self say con parole chiave del nome
    to_murmur = "a self *pensieroso* Già! Con due banane potrei..."
    reactor.callLater(random.randint(20, 40), command_murmur, charlie, to_murmur)

    # Ecco qui, qui viene impostata la durata media della quest, ovvero quanto
    # charlie attenderà che il giocatore gli porti due banane
    reset_call = reactor.callLater(random.randint(200, 300), reset_banana_quest, charlie)
    charlie.specials["charlie_banana_quest:reset_call"] = reset_call
#- Fine Funzione -


# Da notare i return True per evitare di accettare qualsiasi cosa
def before_giving(player, banana, charlie, direction, behavioured):
    if not player.IS_PLAYER:
        to_say = "a %s *concentrato* Grazie, ma no, grazie! Non accetto nulla da chicchessia." % player.get_keywords_attr().split()[0]
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        return True

    command_look(charlie, player.code)

    # Charlie non ha iniziato a dare nessuna quest
    if "charlie_banana_quest:status" not in charlie.specials:
        to_say = "a %s *impensierito* Grazie, ma no, grazie! Non accetto mai caramelle da sconosciuti." % (player.code)
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        to_say = "a %s Sai, da quanto ho perso un rene..." % (player.code)
        reactor.callLater(random.randint(3, 4), command_whisper, charlie, to_say)
        return True

    quest_player_code = charlie.specials["charlie_banana_quest:player"]
    quest_player = database["players"][quest_player_code]
    quest_player_name = quest_player.get_name(charlie)

    quest_status = charlie.specials["charlie_banana_quest:status"]
    if quest_status == "domanda":
        to_say = "a %s *concentrato* Grazie, ma no, grazie! Sto attendendo che %s si decida a rispondermi." % (
            player.code, quest_player_name)
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        return True

    # Controlla che l'entità che dà sia il giocatore della quest
    if player.code != quest_player_code:
        to_say = "a %s Grazie, ma no, grazie! Sto aspettando delle banane da parte di %s." % (
            player.code, quest_player_name)
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        return True

    # Controlla se l'oggetto dato sia una banana, lo fa in maniera grezza, prima
    # di tutto controlla se sia un cibo, e poi ne controlla la short
    if not banana.entitype == ENTITYPE.FOOD:
        to_say = "a %s *critico* Questa cosa non mi sembra del cibo, figuriamoci una banana!" % quest_player_code
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        return True
        
    if not is_same(("banana", "banane"), banana.short.split()) and not is_same(("banana", "banane"), banana.short_night.split()):
        to_say = "a %s *disinteressato* Sono convinto che sia buono, ma ora non ho fame, ho bisogno di banane!" % quest_player_code
        reactor.callLater(random.randint(1, 2), command_say, charlie, to_say)
        return True

    # Charlie decide che l'oggetto dato è abbastanza bananoso e lo accetta
    if charlie.specials["charlie_banana_quest:status"] != "banana" and is_same("banana", banana.short.split()):
        to_yell = "a %s *sorpreso* Eccone una! Ora mi serve anche l'altra!" % quest_player_code
        reactor.callLater(random.randint(1, 2), command_yell, charlie, to_yell)
        charlie.specials["charlie_banana_quest:status"] = "banana"
    else:
        charlie.specials["charlie_banana_quest:status"] = "completa"
        # Ora che la quest è completa ne blocca un eventuale reset, fino a
        # quando le banane non si sciolgono
        delete_charlie_reset_call(charlie)

        to_yell = "a %s *al settimo cielo* Sei il mio salvatore! Finalmente con queste banane potrò sopportare questi due!" % quest_player_code
        reactor.callLater(random.randint(1, 2), command_yell, charlie, to_yell)
        to_emote = "con la $hand destra si mette una banana nell'orecchio destra"
        reactor.callLater(random.randint(4, 6), command_emote, charlie, to_emote)
        to_emote = "con la $hand sinistra si mette una banana nell'orecchio sinistra"
        reactor.callLater(random.randint(7, 9), command_emote, charlie, to_emote)
        to_say = "a self *sollevato* finalmente non li sento più..."
        reactor.callLater(random.randint(10, 13), command_say, charlie, to_say)

        # Tra un po' di tempo le banane si squaglieranno e quindi charlie
        # dovrà di nuovo affidarsi a qualche alla bontà di qualche player
        reactor.callLater(random.randint(3600, 4800), you_are_not_the_banana_king, charlie)
#- Fine Funzione -


def you_are_not_the_banana_king(charlie):
    command_say(charlie, "*disperato mentre le banane nelle sue orecchie si sciolgono* Oh no! Non ancora!")
    reset_banana_quest(charlie)
#- Fine Funzione -


def reset_banana_quest(charlie):
    player_is_here = False
    quest_player_code = ""
    if "charlie_banana_quest:player" in charlie.specials:
        quest_player_code = charlie.specials["charlie_banana_quest:player"]
        quest_player = database["players"][quest_player_code]
        for player in charlie.location.players:
            if player.code == quest_player_code:
                player_is_here = True
                break

    if "charlie_banana_quest:status" in charlie.specials:
        quest_status = charlie.specials["charlie_banana_quest:status"]
        if quest_status == "domanda":
            if player_is_here:
                to_say = "a %s *sconsolato* O beh, chiederò a qualchedun altro." % quest_player_code
            else:
                to_say = "a self *sconsolato* O beh, chiederò a qualchedun altro."
            command_say(charlie, to_say)
        elif quest_status == "cerca":
            if player_is_here:
                to_say = "a %s *impaziente* Ci stai mettendo troppo tempo, lasciamo perdere le banane.." % quest_player_code
            elif quest_player_code:
                to_say = "a self *impaziente* %s ci sta mettendo troppo tempo, lasciamo perdere le banane.." % quest_player.get_name(charlie)
            else:
                to_say = "a self *impaziente* La persona che mi doveva aiutare ci sta mettendo troppo tempo, lasciamo perdere le banane.."
            command_say(charlie, to_say)
            banana = charlie.find_entity("banan", charlie, ["items"])
            if banana:
                choice = random.randint(1, 6)
                if choice == 1:
                    reactor.callLater(random.randint(2, 4), command_drop, charlie, "banan")
                elif choice <= 3:
                    reactor.callLater(random.randint(2, 4), command_eat, charlie, "banan")

    # Cancelliamo anche le variabili speciali della quest
    if "charlie_banana_quest:status" in charlie.specials:
        del(charlie.specials["charlie_banana_quest:status"])
    if "charlie_banana_quest:player" in charlie.specials:
        del(charlie.specials["charlie_banana_quest:player"])
    if "charlie_banana_quest:reset_call" in charlie.specials:
        del(charlie.specials["charlie_banana_quest:reset_call"])
#- Fine Funzione -


def delete_charlie_reset_call(charlie):
    reset_call = charlie.specials["charlie_banana_quest:reset_call"]
    if reset_call:
        #reset_call.cancel()
        reset_call.pause()
        reset_call = None
    del(charlie.specials["charlie_banana_quest:reset_call"])
#- Fine Funzione -

