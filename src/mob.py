# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica dei Mob, base anche della classe Player.
"""


#= IMPORT ======================================================================

import math
import random

from src.affect     import is_affected
from src.behaviour  import BehaviourUpdaterSuperclass
from src.calendar   import calendar
from src.config     import config
from src.color      import remove_colors
from src.database   import database
from src.entity     import ProtoEntity, create_random_entity
from src.element    import Element
from src.engine     import engine
from src.enums      import (COLOR, CONSTELLATION, DAMAGE, DIR, AFFECT, FLAG,
                            HAND, HAIRTYPE, LANGUAGE, MONTH, PART, POSITION,
                            RACE, SEX, STYLE, TO, TRUST, VIRTUE, WAY)
from src.gamescript import check_trigger
from src.log        import log
from src.name       import create_random_name
from src.utility    import copy_existing_attributes


#= COSTANTI ====================================================================

# (TD) probabilmente queste bisognerà spostarle lato enumerazione CONDITION
LIGHT_CONDITION   = 16
MEDIUM_CONDITION  = 8
SERIOUS_CONDITION = 0
MAX_CONDITION     = 100


#= CLASSI ======================================================================

class ProtoMob(ProtoEntity):
    """
    Classe che gestisce il prototipo di un Mob.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoEntity.VOLATILES + []
    MULTILINES  = ProtoEntity.MULTILINES + []
    SCHEMA      = {"behaviour"    : ("src.behaviour", "MobBehaviour"),
                   "height"       : ("", "measure")}
    SCHEMA.update(ProtoEntity.SCHEMA)
    REFERENCES  = {}
    REFERENCES.update(ProtoEntity.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoEntity.WEAKREFS)

    IS_AREA   = False
    IS_DESCR  = True
    IS_ROOM   = False
    IS_EXIT   = False
    IS_WALL   = False
    IS_ACTOR  = True
    IS_MOB    = True
    IS_ITEM   = False
    IS_PLAYER = False
    IS_EXTRA  = False
    IS_PROTO  = True

    ACCESS_ATTR   = "proto_mobs"
    CONSTRUCTOR   = None  # Classe Mob una volta che viene definita a fine modulo

    def __init__(self, code=""):
        super(ProtoMob, self).__init__()

        self.code           = code or ""
        self.height         = 0
        self.constellation  = Element(CONSTELLATION.NONE)  # Costellazione sotto cui è nato il mob
        self.virtue         = Element(VIRTUE.NONE)  # Virtù che il mob segue principalmente
        self.hand           = Element(HAND.NONE)  # Indica quale mano utilizza preferibilmente
        self.hometown       = ""  # Area che il mob o il pg considera come propria casa
        self.group_name     = ""  # Nome del gruppo in cui fa parte, fanno parte tutti i mob che lo hanno uguale
        self.voice_emote    = ""  # Stringa che ne descrive la voce nel canale rpg_channel()
        self.voice_potence  = 50  # Potenza della voce, 0 o meno significa aver perso la voce, per razze umanoidi i valori sono da 40 a 80, per razze 'minori' o 'maggiori' i valori possono variare e superare anche il 100
        self.parts          = {}  # Forma, materiale, vita, flags delle parti sono già di default a seconda delle razza, però si possono cambiare anche a livello di file di area
        self.morph          = None  # Tipo di morph sotto cui il personaggio è affetto
        self.skill_messages = {}  # Dizionario dei messaggi personalizzati riguardanti le skill

        # Attributi
        self.strength       = 0
        self.endurance      = 0
        self.agility        = 0
        self.speed          = 0
        self.intelligence   = 0
        self.willpower      = 0
        self.personality    = 0
        self.luck           = 0

        # Condizioni
        self.thirst         = 0
        self.hunger         = 0
        self.sleep          = 0
        self.drunkness      = 0
        self.adrenaline     = 0
        self.mind           = 0  # Tale quale a quello dello smaug
        self.emotion        = 0  # Tale quale a quello dello smaug
        self.bloodthirst    = 0

        self.eye_color      = Element(COLOR.NONE)
        self.hair_color     = Element(COLOR.NONE)
        self.hair_length    = 0
        self.hair_type      = Element(HAIRTYPE.NONE)
        self.skin_color     = Element(COLOR.NONE)
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = super(ProtoMob, self).get_error_message()
        if msg:
            pass
        elif self.IS_MOB and "_mob_" not in self.code:
            msg = "code di mob senza l'identificativo _mob_ al suo interno"
        elif self.race.get_error_message(RACE, "race", allow_none=False) != "":
            return self.race.get_error_message(RACE, "race", allow_none=False)
        elif self.birth_day <= 0 or self.birth_day > config.days_in_month:
            return "birth_day errato: %d" % self.birth_day
        elif self.birth_month.get_error_message(MONTH, "birth_month") != "":
            return self.birth_month.get_error_message(MONTH, "birth_month")
        elif self.age < 0:
            return "age minore di zero: %d" % self.age
        elif self.height <= 0:
            msg = "altezza minore o uguale a zero: %s" % self.height
        elif self.constellation.get_error_message(CONSTELLATION, "constellation") != "":
            msg = self.constellation.get_error_message(CONSTELLATION, "constellation")
        elif self.virtue.get_error_message(VIRTUE, "virtue") != "":
            msg = self.virtue.get_error_message(VIRTUE, "virtue")
        elif self.hometown and self.hometown not in database["areas"]:
            msg = "hometown inesistente tra i codici delle aree: %s" % self.hometown
        elif self.group_name and self.group_name not in database["groups"]:
            msg = "group_name inesistente tra i nomi dei gruppi: %s" % self.group_name
        elif self.strength <= 0 or self.strength > config.max_stat_value:
            msg = "strength non è tra zero e %d: %d" % (config.max_stat_value, self.strength)
        elif self.endurance <= 0 or self.endurance > config.max_stat_value:
            msg = "endurance non è tra zero e %d: %d" % (config.max_stat_value, self.endurance)
        elif self.agility <= 0 or self.agility > config.max_stat_value:
            msg = "agility non è tra zero e %d: %d" % (config.max_stat_value, self.agility)
        elif self.speed <= 0 or self.speed > config.max_stat_value:
            msg = "speed non è tra zero e %d: %d" % (config.max_stat_value, self.speed)
        elif self.intelligence <= 0 or self.intelligence > config.max_stat_value:
            msg = "intelligence non è tra zero e %d: %d" % (config.max_stat_value, self.intelligence)
        elif self.willpower <= 0 or self.willpower > config.max_stat_value:
            msg = "willpower non è tra zero e %d: %d" % (config.max_stat_value, self.willpower)
        elif self.personality <= 0 or self.personality > config.max_stat_value:
            msg = "personality non è tra zero e %d: %d" % (config.max_stat_value, self.personality)
        elif self.luck <= 0 or self.luck > config.max_stat_value:
            msg = "luck non è tra zero e %d: %d" % (config.max_stat_value, self.luck)
        elif self.voice_potence < 0:
            msg = "voice_potence non può essere minore di zero: %s" % self.voice_potence
        # (TD) ricordarsi di aggiungere il controllo alle parts
        else:
            return ""

        if type(self) == ProtoMob:
            log.bug("(ProtoMob: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    def get_area_code(self):
        """
        Ritorna il codice dell'area carpendolo dal proprio codice.
        """
        if "_mob_" in self.code:
            return self.code.split("_mob_", 1)[0]
        else:
            log.bug("Codice errato per l'entità %s: %s" % (self.__class__.__name__, self.code))
            return ""
    #- Fine Metodo -


class Mob(ProtoMob, BehaviourUpdaterSuperclass):
    """
    Istanza di un Mob.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = ProtoMob.VOLATILES + ["prototype"]
    MULTILINES  = ProtoMob.MULTILINES + []
    SCHEMA      = {"specials"     : ("", "str")}
    SCHEMA.update(ProtoMob.SCHEMA)
    REFERENCES  = {"area" : ["areas"]}
    REFERENCES.update(ProtoMob.REFERENCES)
    WEAKREFS    = {}
    WEAKREFS.update(ProtoMob.WEAKREFS)

    ACCESS_ATTR = "mobs"
    IS_PROTO    = False
    CONSTRUCTOR = None  # Classe Mob una volta che viene definita a fine modulo

    # Qui non bisogna passare altri attributi oltre il code, perché altrimenti
    # offuscherebbero gli attributi prototype
    def __init__(self, code=""):
        super(Mob, self).__init__()
        BehaviourUpdaterSuperclass.__init__(self)

        self.code = ""
        self.prototype = None
        if code:
            self.reinit_code(code)
            copy_existing_attributes(self.prototype, self, except_these_attrs=["code"])
            self.after_copy_existing_attributes()

        # Eventuale inizializzazione dei punti
        if self.max_life == 0:
            self.max_life = config.starting_points
        if self.max_mana == 0:
            self.max_mana = config.starting_points
        if self.max_vigour == 0:
            self.max_vigour = config.starting_points
        if self.life == 0:
            self.life = self.max_life
        if self.mana == 0:
            self.mana = self.max_mana
        if self.vigour == 0:
            self.vigour = self.max_vigour

        if self.hand == HAND.NONE:
            self.hand = self.hand.randomize()

        # Variabili proprie di una istanza di mob:
        self.area            = None
        self.attack          = 1
        self.defense         = 1
        self.speaking        = Element(LANGUAGE.COMMON)  # Indica con quale linguaggio sta attualmente parlando il mob
        self.style           = Element(STYLE.NONE)  # Style di combattimento che sta utilizzando
        self.experience      = 0  # Esperienza accumulata prima di poter livellare
        self.mount           = None  # Indica quale mob o pg sta cavalcando
        self.mounted_by      = None  # Indica da quali mob o pg è cavalcato
        self.specials        = {}  # E' una lista di variabili speciali, possono essere utilizzate come delle flags, vengono aggiunte di solito nei gamescript
        self.reply           = None  # Entità a cui si può replicare
#       self.tracking        = Track()  # Serve quando il mob inizia a tracciare e cacciare una preda fuggita
        self.last_fight_time = None
        self.last_death_time = None

        # Contatori di statistica
        self.defeat_from_mob_counter    = 0  # Conteggio delle sconfitte
        self.defeat_from_item_counter   = 0  # Conteggio delle sconfitte
        self.defeat_from_player_counter = 0  # Conteggio delle sconfitte
        self.death_from_player_counter  = 0  # Conteggio delle sconfitte
        self.mob_defeated_counter       = 0  # Conteggio delle vittorie sui mob
        self.item_defeated_counter      = 0  # Conteggio degli oggetti distrutti
        self.player_defeated_counter    = 0  # Conteggio delle vittorie sui giocatori
        self.player_killed_counter      = 0  # Conteggio delle volte che viene ucciso un giocatore

        check_trigger(self, "on_init", self)
    #- Fine Inizializzazione -

    def get_error_message(self):
        msg = super(Mob, self).get_error_message()
        if msg:
            pass
        elif self.life < 0 or self.life > 9999:
            msg = "life non è tra zero e 9999: %d" % self.life
        elif self.mana < 0 or self.mana > 9999:
            msg = "mana non è tra zero e 9999: %d" % self.mana
        elif self.vigour < 0 or self.vigour > 9999:
            msg = "vigour non è tra zero e 9999: %d" % self.vigour
        elif self.max_life < 0 or self.max_life > 9999:
            msg = "life non è tra zero e 9999: %d" % self.max_life
        elif self.max_mana < 0 or self.max_mana > 9999:
            msg = "mana non è tra zero e 9999: %d" % self.max_mana
        elif self.max_vigour < 0 or self.max_vigour > 9999:
            msg = "vigour non è tra zero e 9999: %d" % self.max_vigour
        elif self.thirst < 0 or self.thirst > MAX_CONDITION:
            msg = "thirst non è tra zero e %s: %d" % (MAX_CONDITION, self.thirst)
        elif self.hunger < 0 or self.hunger > MAX_CONDITION:
            msg = "hunger non è tra zero e %s: %d" % (MAX_CONDITION, self.hunger)
        elif self.drunkness < 0 or self.drunkness > MAX_CONDITION:
            msg = "drunkness è tra 0 e %d: %d" % (MAX_CONDITION, self.drunkness)
        elif self.bloodthirst < 0 or self.bloodthirst > MAX_CONDITION:
            msg = "bloodthirst non è tra zero e %d: %d" % (MAX_CONDITION, self.bloodthirst)
        elif self.adrenaline < 0 or self.adrenaline > MAX_CONDITION:
            msg = "adrenaline non è tra zero e %d: %d" % (MAX_CONDITION, self.adrenaline)
        elif self.mind < 0 or self.mind > MAX_CONDITION:
            msg = "mind non è tra zero e %d: %d" % (MAX_CONDITION, self.mind)
        elif self.emotion < 0 or self.emotion > MAX_CONDITION:
            msg = "emotion non è tra zero e %d: %d" % (MAX_CONDITION, self.emotion)
        elif self.attack < 1:
            msg = "attack minore di 1: %d" % self.attack
        elif self.defense < 1:
            msg = "defense minore di 1: %d" % self.defense
        elif self.speaking.get_error_message(LANGUAGE, "speaking") != "":
            msg = self.speaking.get_error_message(LANGUAGE, "speaking")
        elif self.defeat_from_mob_counter < 0:
            msg = "defeat_from_mob_counter è un contatore, non può essere minore di 0: %d" % self.defeat_from_mob_counter
        elif self.defeat_from_item_counter < 0:
            msg = "defeat_from_item_counter è un contatore, non può essere minore di 0: %d" % self.defeat_from_item_counter
        elif self.defeat_from_player_counter < 0:
            msg = "defeat_from_player_counter è un contatore, non può essere minore di 0: %d" % self.defeat_from_player_counter
        elif self.death_from_player_counter < 0:
            msg = "death_from_player_counter è un contatore, non può essere minore di 0: %d" % self.death_from_player_counter
        elif self.mob_defeated_counter < 0:
            msg = "mob_defeated_counter è un contatore, non può essere minore di 0: %d" % self.mob_defeated_counter
        elif self.item_defeated_counter < 0:
            msg = "item_defeated_counter è un contatore, non può essere minore di 0: %d" % self.item_defeated_counter
        elif self.player_defeated_counter < 0:
            msg = "player_defeated_counter è un contatore, non può essere minore di 0: %d" % self.player_defeated_counter
        elif self.player_killed_counter < 0:
            msg = "player_killed_counter è un contatore, non può essere minore di 0: %d" % self.player_killed_counter
        elif self.style.get_error_message(STYLE, "style") != "":
            msg = self.style.get_error_message(STYLE, "style")
        elif self.mount and self.mount not in database.players and self.mount not in self.mobs:
            msg = "mount non è un player o un mob valido: %s" % self.mount
        elif self.mounted_by and self.mount not in database.players and self.mount not in self.mobs:
            msg = "mounted_by non è un player o un mob valido: %s" % self.mounted_by
        elif self.reply and self.reply not in database.players and self.reply not in database.mobs and self.reply not in database.items:
            msg = "reply non è un entità valida: %s" % self.reply
#       elif self.tracking.get_error_message() != "":
#           msg = self.tracking.get_error_message()
        else:
            return ""

        # Se arriva fino a qui ha trovato un errore
        if type(self) == Mob:
            log.bug("(Mob: code %s) %s" % (self.code, msg))
        return msg
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_strength_way(self):
        """
        Ritorna quale via l'actor sta seguendo, a seconda delle skill che
        conosce.
        """
        # (TD)
        return WAY.GLADIATOR
    #- Fine Metodo -

    def get_weak_way(self):
        """
        Ritorna quale via l'actor non sta seguendo, a seconda delle skill che
        conosce.
        """
        # (TD)
        return WAY.RUNIC
    #- Fine Metodo -

    def has_sight_sense(self):
        """
        Ritorna falso se il mob è cieco, di solito si utilizza questo metodo
        al posto della sintassi normale con l'operatore in per controllare
        un'entità non ci può vedere anche magicamente.
        Concettualmente sarebbe il contrario della funzione is_blind definita
        in molti Diku-like.
        """
        if self.trust >= TRUST.MASTER:
            return True

        if is_affected(self, "truesight"):
            return True

        if is_affected(self, "blind"):
            return False

        return True
    #- Fine Metodo -

    def has_hearing_sense(self):
        """
        Ritorna vero se l'entità è sorda.
        """
        # (TD)
        return True
    #- Fine Metodo -

    def has_smell_sense(self):
        """
        Ritorna vero se l'entità non è il possesso del senso dell'olfatto.
        """
        # (TD)
        return True
    #- Fine Metodo -

    def has_touch_sense(self):
        """
        Ritorna vero se l'entità non è il possesso della sensibilità del tocco.
        """
        # (TD)
        return True
    #- Fine Metodo -

    def has_taste_sense(self):
        """
        Ritorna vero se l'entità non è il possesso del senso del gusto.
        """
        # (TD)
        return True
    #- Fine Metodo -

    def has_sixth_sense(self):
        """
        Ritorna vero se l'entità non è il possesso di intuito, o sesto senso.
        """
        # (TD)
        return True
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def is_drunk(self, difficulty=1):
        """
        Esegue una specie di tiro di salvezza per vedere se l'entità è ubriaca
        o meno.
        L'argomento difficulty può essere un numero variabile ad indicare la
        difficoltà del controllo, maggiore è difficulty più probabile è che
        l'entità sia considerata ubriaca.
        """
        if difficulty <= 0 or difficulty > 10:
            log.bug("difficulty non è valido: %d" % difficulty)
            return False

        # ---------------------------------------------------------------------

        if random.randint(1, 100) < self.drunkness * difficulty:
            return True

        return False
    #- Fine Metodo -

    def has_drunk_walking(self):
        """
        Ritorna una coppia di valori, il primo indica se il mob ha l'andatura
        da ubriaco, il secondo indica se la propria cavalcatura ha l'andatura
        da ubriaco (sempre che il mob abbia una cavalcatura).
        """
        drunk = False
        mount_drunk = False

        if self.is_drunk() and self.position != POSITION.SHOVE and self.position != POSITION.DRAG:
            drunk = True
        if (self.mount and self.mount.is_drunk()
        and self.mount.position != POSITION.SHOVE and self.mount.position != POSITION.DRAG):
            mount_drunk = True

        return drunk, mount_drunk
    #- Fine Metodo -

    # (TD) skill per guadagnare più punti
    def update_points(self):
        # Recupero dei punti base

        # (bb) attenzione che questo dies potrebbe conflittare con quello del
        # ciclo di loop di fight, da rivedere
        if self.life <= 0:
            self.dies()
        elif self.life < self.max_life:
            self.gain_points("life")

        if self.mana < self.max_mana:
            self.gain_points("mana")

        if self.vigour < self.max_vigour:
            self.gain_points("vigour")
    #- Fine Metodo -

    def gain_points(self, name):
        """
        Aggiorna la quantità dei punti: vita, mana e vigore.
        """
        if not name:
            log.bug("name non è un parametro valido: %r" % name)
            return

        # ---------------------------------------------------------------------

        if self.is_fighting():
            return

        if self.position == POSITION.DEAD:
            gain = 0
        elif self.position == POSITION.MORTAL:
            gain = -random.randint(4, 16)
        elif self.position == POSITION.INCAP:
            gain = -random.randint(0, 4)
        elif self.position == POSITION.STUN:
            gain = random.randint(0, 1)
        elif self.position == POSITION.SLEEP:
            gain = random.randint(5, max(6, math.log(1 + self.level/3) * 9))
        elif self.position == POSITION.REST:
            gain = random.randint(4, max(5, math.log(1 + self.level/3) * 8))
        elif self.position == POSITION.SIT:
            gain = random.randint(3, max(4, math.log(1 + self.level/3) * 7))
        elif self.position == POSITION.KNEE:
            gain = random.randint(2, max(3, math.log(1 + self.level/3) * 6))
        else:
            # (TD) da pensare se il gain in piedi è da disattivare, tranne
            # che per i troll
            gain = random.randint(1, max(2, math.log(1 + self.level/3) * 4))

        points = getattr(self, name)
        max_points = getattr(self, "max_" + name)

        # Non si può guadagnare per volta più della metà della rimanenza dei punti
        if points >= 2:
            gain = min(gain, points / 2)
        else:
            # Caso particolare, la disperazione porta a piccole grazie!
            # (TD) aggiungere un messaggio e un check sulla fortuna invece del random.randint
            if gain > 0 and random.randint(1, 10) == 1:
                gain = random.randint(gain, gain * 2)

        # Se si ha fame o sete il guadagno dei punti è compromesso
        if gain > 0:
            if   self.hunger >= MAX_CONDITION - SERIOUS_CONDITION: gain  = 0
            elif self.hunger >= MAX_CONDITION - MEDIUM_CONDITION:  gain /= 2
            elif self.hunger >= MAX_CONDITION - LIGHT_CONDITION:   gain /= 4
            if   self.thirst >= MAX_CONDITION - SERIOUS_CONDITION: gain  = 0
            elif self.thirst >= MAX_CONDITION - MEDIUM_CONDITION:  gain /= 2
            elif self.thirst >= MAX_CONDITION - LIGHT_CONDITION:   gain /= 4

        # (TD) se si è avvelenati il guadagno della vita è compromesso

        # (TD) se si è sotto effetto di incantesimi o se ci si trova in un
        #  posto con clima ostile l'energia è compromessa

        # (TD) Se si è vampiri il guadagno dei punti cambia a seconda che sia giorno o notte

        # Capita quando si hanno dei punti sovra-restorati
        alternate_gain = max_points - points
        if gain > 0 and alternate_gain < 0 and -alternate_gain > gain * 2:
            alternate_gain /= 2

        setattr(self, name, max(0, points + min(gain, alternate_gain)))
    #- Fine Metodo -

    def update_conditions(self):
        # ---------------------------------------------------------------------
        # Modifica dello stato delle condizioni
        # (TD) probabilmente questo devo farlo una volta ogni minuto reale

        # (TD) (BB) per ora disattivata per via del baco sui reset che non
        # darebbero abbastanza cibo
        return
        is_alive = True
        if self.level > 1 and self.trust == TRUST.PLAYER:
            #if is_alive and self.thirst < MAX_CONDITION:
            #    self.gain_condition("thirst", +1)
            is_alive = self.gain_condition("hunger", +2)
            #if is_alive and self.drunkness > 0:
            #    self.gain_condition("drunkness", -1)
            #if is_alive and self.adrenaline > 0:
            #    self.gain_condition("adrenaline", -1)
            #if is_alive and self.bloodthirst < MAX_CONDITION:
            #    self.gain_condition("bloodthirst", +1)
            # (TD) da rivalutare e finire, magari farla solo come malus per le
            # morti, una delle due o tutte e due
            #self.gain_condition("mind")
            #self.gain_condition("emotion")

        if not is_alive:
            return
    #- Fine Metodo -

    def gain_condition(self, name, value):
        """
        Aggiorna lo stato delle condizioni (fame, sete, sonno...)
        """
        if not name:
            log.bug("name non è un parametro valido: %r" % name)
            return True

        if value < 0 or value > MAX_CONDITION:
            log.bug("name non è un parametro valido: %d" % value)
            return True

        # ---------------------------------------------------------------------

        # (TD) qui tutto cambia molto quando ci saranno le malattie del
        # vampirismo e della licantropia

        # (TD) Inserire anche dei modificato di value razziali

        condition = getattr(self, name)
        if condition < MAX_CONDITION:
            condition = max(0, min(condition + value, MAX_CONDITION))
            setattr(self, name, condition)

        is_alive = True
        if self.IS_PLAYER and name == "hunger":
            if condition >= MAX_CONDITION - SERIOUS_CONDITION:
                self.act("\n" + self.get_hunger_condition(), TO.ENTITY)
                self.act("$n sta languendo per la [orange]fame[close]!", TO.OTHERS)
                is_alive = self.damage(self, int(math.log(self.level) * 2), DAMAGE.HUNGER)
                self.send_prompt()
            elif condition >= MAX_CONDITION - MEDIUM_CONDITION:
                self.act("\n" + self.get_hunger_condition(), TO.ENTITY)
                self.act("Avverti lo stomaco di $n che [orange]brontola[close].", TO.OTHERS)
                is_alive = self.damage(self, int(math.log(self.level)), DAMAGE.HUNGER)
                self.send_prompt()
            elif condition >= MAX_CONDITION - LIGHT_CONDITION:
                self.act("\n" + self.get_hunger_condition(), TO.ENTITY)
                self.send_prompt()
                # Qui nessun messaggio di act per gli altri, per evitare spam

        return is_alive
    #- Fine Metodo -

    def skin_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        if self.skin_color == COLOR.NONE:
            return "[pink]%s[close]" % argument
        elif self.skin_color.web_name == config.text_color:
            return argument
        else:
            return "[%s]%s[close]" % (self.skin_color.web_name, argument)
    #- Fine Metodo -

    def eye_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        if self.eye_color == COLOR.NONE or self.eye_color.web_name == config.text_color:
            return argument
        else:
            return "[%s]%s[close]" % (self.eye_color.web_name, argument)
    #- Fine Metodo -

    def hair_colorize(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # ---------------------------------------------------------------------

        if self.hair_color == COLOR.NONE or self.hair_color.web_name == config.text_color:
            return argument
        else:
            return "[%s]%s[close]" % (self.hair_color.web_name, argument)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_thirst_condition(self):
        # (TD)
        return "Non hai [darkcyan]sete[close]"
    #- Fine Metodo -

    def get_hunger_condition(self):
        if self.hunger >= MAX_CONDITION - SERIOUS_CONDITION:
            return "Stai languendo per la [orange]FAME[close]!"
        elif self.hunger >= MAX_CONDITION - MEDIUM_CONDITION:
            return "Il tuo stomaco brontola per la [orange]fame[close]"
        elif self.hunger >= MAX_CONDITION - LIGHT_CONDITION:
            return "Hai [orange]fame[close]"
        else:
            return "Non hai [orange]fame[close]"
    #- Fine Metodo -

    def get_sleep_condition(self):
        # (TD)
        return "Non hai [blue]sonno[close]"
    #- Fine Metodo -

    def get_drunkness_condition(self):
        # (TD)
        return "Non sei [purple]ubriac$o[close]"
    #- Fine Metodo -

    def get_adrenaline_condition(self):
        # (TD)
        return "La tua [red]adrenalina[close] è sotto controllo"
    #- Fine Metodo -

    def get_mind_condition(self):
        # (TD)
        return ""
    #- Fine Metodo -

    def get_emotion_condition(self):
        # (TD)
        return ""
    #- Fine Metodo -

    def get_bloodthirst_condition(self):
        # (TD)
        return ""
    #- Fine Metodo -

    def dies(self, opponent=None, auto_loot=False, teleport_corpse=False):
        force_return = check_trigger(self, "before_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "before_dies", self, opponent)
            if force_return:
                return

        remains, use_repop = self.make_remains(auto_loot)

        # Attenzione che l'utilizzo di tali trigger potrebbero essere pericolosi
        # visto che sotto c'è un'extract
        force_return = check_trigger(self, "after_die", self, opponent)
        if force_return:
            return
        if opponent:
            force_return = check_trigger(opponent, "after_dies", self, opponent)
            if force_return:
                return

        self.extract(1, use_repop=use_repop)
    #- Fine Metodo -


class Track(object):
    # (TD) forse spostarlo in un altro modulo in futuro
    pass

    def get_error_message(self):
        # (TD)
        return ""
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def create_random_mob(mob=None, name="", level=0, race=RACE.NONE, sex=SEX.NONE, way=WAY.NONE):
    """
    Crea un nuovo mob con caratteristiche casuali.
    """
    if not name and name != "":
        log.bug("name non è un parametro valido: %r" % name)
        return None

    if level < 0 or level > config.max_level:
        log.bug("level non è un parametro valido: %d" % level)
        return None

    if not race:
        log.bug("race non è un parametro valido: %r" % race)
        return None

    if not sex:
        log.bug("sex non è un parametro valido: %r" % sex)
        return None

    if not way:
        log.bug("way non è un parametro valido: %r" % way)
        return None

    # ---------------------------------------------------------------------

    # Crea a caso un nome se non è stato passato
    if not name:
        name = create_random_name(race, sex)

    proto_mob_code = random.choice(database["proto_mobs"].keys())
    if not mob:
        mob = Mob(proto_mob_code)
    mob = create_random_entity(mob, name, level, race, sex)

    # (TD) tramite il way è possibile creare un set di skill adatte

    # Crea casualmente gli attributi di entità che non sono stati ancora
    # inizializzati dalla create_random_entity()
    mob.weight = random.randint(mob.race.weight_low, mob.race.weight_high)
    mob.height = random.randint(mob.race.height_low, mob.race.height_high)
    mob.age    = random.randint(mob.race.age_adolescence, mob.race.age_old)

    # (TD) Sceglie una descrizione casuale a seconda della razza del sesso e dell'età
    mob.descr       = ""
    mob.descr_night = ""

    # Punti
    mob.max_life      = random.randint(90, 110)
    mob.max_mana      = random.randint(90, 110)
    mob.max_vigour    = random.randint(90, 110)
    mob.life          = mob.max_life - random.randint(0, mob.max_life / 4)
    mob.mana          = mob.max_mana - random.randint(0, mob.max_mana / 4)
    mob.vigour        = mob.max_vigour - random.randint(0, mob.max_vigour / 4)

    # Attributi
    mob.strength      = random.randint(5, 95)
    mob.endurance     = random.randint(5, 95)
    mob.agility       = random.randint(5, 95)
    mob.speed         = random.randint(5, 95)
    mob.intelligence  = random.randint(5, 95)
    mob.willpower     = random.randint(5, 95)
    mob.personality   = random.randint(5, 95)
    mob.luck          = random.randint(5, 95)

    # Condizioni
    mob.thirst        = random.randint(0, 25)
    mob.hunger        = random.randint(0, 25)
    mob.drunkness     = random.randint(0, 25)
    mob.bloodthirst   = random.randint(0, 25)
    mob.adrenaline    = random.randint(0, 25)
    mob.mind          = random.randint(0, 25)
    mob.emotion       = random.randint(0, 25)

    # Imposta le altre variabili  # (TD) da migliorare
    mob.attack = random.randint(1, mob.level)
    mob.defense = random.randint(1, mob.level)

    mob.position.randomize(from_element=POSITION.REST, to_element=POSITION.STAND)
    mob.skills = create_random_skills(mob)
    mob.constellation.randomize()
    mob.voice_potence = random.randint(45, 55) + mob.level / 4

    if random.randint(0, 200) == 0:
        mob.flags += Element(FLAG.AMBIDEXTROUS)
    else:
        if random.randint(0, 3) == 0:
            mob.hand = Element(HAND.RIGHT)
        else:
            mob.hand = Element(HAND.LEFT)

    return mob
#- Fine Funzione -


def create_random_skills(mob):
    """
    """
    if not mob:
        log.bug("mob non è valido: %s" % mob)
        return

    # -------------------------------------------------------------------------

    skills = {}
    # (TD)
    return skills
#- Fine Funzione -


#= FINALIZE ====================================================================

ProtoMob.CONSTRUCTOR = Mob
Mob.CONSTRUCTOR = Mob
