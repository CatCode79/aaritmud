# -*- coding: utf-8 -*-

"""
Modulo che contiene il codice relativo il movimento direzione di base delle
entità.
"""

#= IMPORT ======================================================================

import random
import time

from src.affect     import is_affected
from src.color      import remove_colors, color_first_upper
from src.config     import config
from src.enums      import DIR, DOOR, EXIT, OPTION, POSITION, ROOM, SEX, TO
from src.gamescript import check_trigger
from src.log        import log
from src.interpret  import translate_input
from src.utility    import copy_existing_attributes, put_final_dot, pretty_list

from src.commands.command_flee import command_flee
from src.commands.command_open import command_open


#= CLASSI ======================================================================

class EntityMoveSuperclass(object):
    def move(self, direction, behavioured=False, following=False, fleeing=False, fall_number=0):
        """
        Se possibile muove l'entità verso la direzione voluta.
        """
        if not direction:
            log.bug("direction non è un parametro valido: %r" % direction)
            return False

        if fall_number < 0 or fall_number > 10000:
            log.bug("fall_number non è un parametro valido: %d" % fall_number)
            return False

        # ---------------------------------------------------------------------

        self = self.split_entity(1)

        if self.location.IS_ITEM:
            self.send_output("Devi uscire da %s prima di poter andare a %s." % (
                self.location, direction))
            return False

        if self.location.IS_ACTOR:
            self.send_output("Devi uscire dall'inventario di %s prima di poter andare a %s." % (
                self.location, direction))
            return False

        if self.position < POSITION.STAND:
            self.send_output("Devi almeno essere in piedi per poter andare a %s." % direction)
            return False

        drunk, mount_drunk = self.has_drunk_walking()
        drunk_direction = None
        mount_drunk_direction = None
        if fall_number == 0:
            if drunk:
                drunk_direction.randomize()
            if mount_drunk:
                mount_drunk_direction.randomize()

        # Se non è possibile andare da quella parte e non vi è nemmeno una porta
        # stampa dei messaggi appositi.
        # (TD) visto che per ora non ci si può ubriacare evito i messaggi per il drunk walking
        if drunk and not mount_drunk:
            if drunk_direction not in self.location.exits or EXIT.DIGGABLE in self.location.exits[drunk_direction].flags:
                return False
        elif drunk and mount_drunk:
            # Quando sia cavalcatura e padrone sono ubriachi sceglie a caso
            # la direzione 'ubriaca' tra le due
            if random.randint(0, 1) == 0:
                choised_direction = mount_drunk_direction
            else:
                choised_direction = drunk_direction
            if choised_direction not in self.location.exits or EXIT.DIGGABLE in self.location.exits[choised_direction].flags:
                return False
        elif not drunk and mount_drunk:
            if mount_drunk_direction not in self.location.exits or EXIT.DIGGABLE in self.location.exits[mount_drunk_direction].flags:
                return False
        else:
            if direction not in self.location.exits or EXIT.DIGGABLE in self.location.exits[direction].flags:
                self.send_output("Non ti è possibile andare verso %s." % direction)
                return False

        # Se l'uscita ha una porta e questa è chiusa blocca il percorso o
        # controlla se sia per caso una finestra
        door = self.location.get_door(direction)
        if door:
            # Se l'uscita è una finestra non c'è modo di oltrepassarla a meno
            # che non sia una porta-finestra
            # (TD) è un controllo da effettuare quando avrò creato gli oggetti, per ora fatto alla buona
            if door.door_type and DOOR.WINDOW in door.door_type.flags:
                self.send_output("Non c'è nessuna porta verso %s ma una finestra." % direction)
                return False

            # (TD) Se l'uscita è una porta e questa è chiusa ci si va' contro
            # a meno che non abbia attivato l'opzione AUTO_OPEN, in quel caso
            # apre la porta automaticamente
            if self != door and door.door_type and DOOR.CLOSED in door.door_type.flags:
                if door.door_type and DOOR.SECRET in door.door_type.flags:
                    self.send_output("Non ti è possibile andare verso %s." % direction)
                    return False
                else:
                    # Se l'uscita è una porta liscia liscia ed apribile andandoci
                    # contro la porta verrà aperta automatica tramite l'opzione
                    # AUTO_OPEN; lo stesso controllo viene effettuato più sotto
                    if (self.IS_PLAYER and OPTION.AUTO_OPEN in self.account.options
                    and DOOR.LOCKED     not in door.door_type.flags
                    and DOOR.NO_USE_DIR not in door.door_type.flags):
                        if OPTION.ITALIAN in self.account.options:
                            return command_open(self, door.get_numbered_keyword(looker=self))
                        else:
                            return command_open(self, door.get_numbered_keyword(looker=self))
                    else:
                        self.send_output("Non puoi andare %s, c'è %s%s." % (direction.to_dir2, door.get_name(self), door.door_type.get_status(door.sex)))
                        return False

            reverse_door = self.location.get_door(direction, direct_search=False)
            if reverse_door:
                if reverse_door.door_type and DOOR.WINDOW in reverse_door.door_type.flags:
                    self.send_output("Non c'è nessuna porta verso %s ma una finestra." % direction)
                    return False

                if reverse_door.door_type and DOOR.CLOSED in reverse_door.door_type.flags:
                    if self != reverse_door and reverse_door.door_type and DOOR.SECRET in reverse_door.door_type.flags:
                        if (self.IS_PLAYER and OPTION.AUTO_OPEN in self.account.options
                        and DOOR.LOCKED     not in door.door_type.flags
                        and DOOR.NO_USE_DIR not in door.door_type.flags):
                            if OPTION.ITALIAN in self.account.options:
                                return command_open(self, direction.name)
                            else:
                                return command_open(self, direction.english)
                        else:
                            self.send_output("Non ti è possibile andare verso %s." % direction)
                            return False
                    else:
                        self.send_output("Non puoi andare %s, c'è %s%s." % (direction.to_dir2, reverse_door.get_name(self), reverse_door.door_type.get_status(reverse_door.sex)))
                        return False

        # Se l'entità è sotto charm e il suo padrone è nei paraggi questa
        # non può andarsene
        if (fall_number == 0 and is_affected(self, "charm")
        and self.owner() and self.location == self.owner().location):
            if self.master.sex == SEX.FEMALE:
                self.send_output("No! Non vuoi stare lontano dalla tua Padrona.")
            else:
                self.send_output("No! Non vuoi stare lontano dal tuo Padrone.")
            return False

        # (TD) Se l'area della nuova stanza è differente da quella precedente
        # cerca di inviare un *.mid tramite send_audio se questo esiste
        # (Vedere il bard per questo)
        pass

        # (TD) ci sono così tante cose da fare ancora che lascio perdere..
        # facciamo finta di nulla e facciamo passare sta povera entità..
        if fall_number == 0:
            pass

        # Finalmente trova la stanza di destinazione e muove l'entità laggiù
        # (TD) devo ricordarmi di aggiungere le due "direzioni ubriache"
        destination_room = self.location.get_destination_room(direction)
        if not destination_room:
            if self.IS_PLAYER:
                log.bug("destination inesistente partendo dalla stanza %s %d %d %d e andando verso %s" % (
                    self.area.code, self.location.x, self.location.y, self.location.z, direction))
            self.send_output("Non ti è possibile andare verso %s." % str(direction).lower())
            return False

        if (not following and self.IS_MOB    and EXIT.NO_MOB    in self.location.exits[direction].flags
        or  not following and self.IS_ITEM   and EXIT.NO_ITEM   in self.location.exits[direction].flags
        or  not following and self.IS_ROOM   and EXIT.NO_ROOM   in self.location.exits[direction].flags
        or                    self.IS_PLAYER and EXIT.NO_PLAYER in self.location.exits[direction].flags):
            self.act("Ti è proibito andare verso %s." % direction, TO.ENTITY)
            self.act("$n cerca di andare verso %s ma gli è proibito." % direction, TO.OTHERS)
            return False

        if (not following and self.IS_MOB    and ROOM.NO_MOB    in destination_room.flags
        or  not following and self.IS_ITEM   and ROOM.NO_ITEM   in destination_room.flags
        or  not following and self.IS_ROOM   and ROOM.NO_ROOM   in destination_room.flags
        or                    self.IS_PLAYER and ROOM.NO_PLAYER in destination_room.flags):
            self.act("Ti è proibito entrare in $N.", TO.ENTITY, destination_room)  # (GR)
            self.act("$n cerca di entrare in $N ma gli è proibito.", TO.OTHERS, destination_room)  # (GR)
            return False

        # Se si sta combattendo allora non si può muoversi normalmente
        # ma tramite il flee, automatico o meno
        if not fleeing and self.is_fighting() and self.get_opponent().location == self.location:
            if self.IS_PLAYER and OPTION.AUTO_FLEE in self.account.options:
                return command_flee(self, direction.english_nocolor)
            else:
                flee_translation = translate_input(self, "flee", "en")
                if not flee_translation:
                    log.bug("flee_translation non è valido: %r" % flee_translation)
                    flee_translation = "fuggi"
                javascript_code = '''javascript:parent.sendInput('%s');''' % flee_translation
                self.send_output('''Se vuoi andartene mentre stai combattendo, <a href="%s">fuggi</a>!''' % javascript_code)
                return False

        # Controlla se l'entità stia correndo, cioè se stia inviando comandi
        # di movimento con una certa frequenza
        running = False
        if self.last_movement:
            execution_time = time.time() - self.last_movement
            if execution_time <= config.running_step_time:
                running = True

        force_return = check_trigger(self, "before_move", self, self.location, direction, destination_room, running, behavioured)
        if force_return:
            return True
        force_return = check_trigger(self, "before_" + direction.trigger_suffix, self, self.location, direction, destination_room, running, behavioured)
        if force_return:
            return True
        for en in self.location.iter_contains(use_reversed=True):
            if en == self:
                continue
            force_return = check_trigger(en, "before_outcoming", self, self.location, direction, destination_room, en, running, behavioured)
            if force_return:
                return True
        for en in destination_room.iter_contains(use_reversed=True):
            force_return = check_trigger(en, "before_incoming", self, self.location, direction, destination_room, en, running, behavioured)
            if force_return:
                return True

        followers = self.get_followers_here()
        avoid_prompt = bool(followers)
        break_line = not avoid_prompt

        # Se arriva fin qui significa che alla direzione voluta c'è un'uscita
        exit = self.location.exits[direction]

        follower_names = []
        for follower in followers:
            follower_names.append(follower.get_name(self))

        if following:
            send_follow_entity_go_message(self.walker, self, direction, fleeing, running)
        elif exit.entity_message:
            self.act(exit.entity_message + "\n", TO.ENTITY, destination_room, self.location, direction.to_dir)
        else:
            self.act("%s %s.\n" % (self.go_verb_you(fleeing, running), direction.to_dir), TO.ENTITY)

        if following:
            send_follow_others_go_message(self.walker, self, direction, fleeing, running)
        elif exit.others_in_message:
            self.act(exit.others_in_message, TO.OTHERS, destination_room, self.location, direction.to_dir, avoid_prompt=avoid_prompt, break_line=break_line)
        else:
            self.act("$n %s %s." % (self.go_verb_it(fleeing, running), direction.to_dir), TO.OTHERS, avoid_prompt=avoid_prompt, break_line=break_line)

        # Per risparmiare in cpu esegue la modifica iterativa di tutti i
        # riferimenti area solo se ci si sta muovendo effettivamente da un'area
        # ad un'altra
        # (TT) Per ora l'use_look nel movimento è per i soli player, è una
        # scelta per diminuire i costi della cpu, ma potrebbe non essere
        # buona per il futuro quando ci saranno tutti i gamescript attivabili
        if self.location.area == destination_room.area:
            self = self.from_location(1, use_iterative_remove=False, use_repop=True)
            self.to_location(destination_room, use_look=True if self.IS_PLAYER else False, use_iterative_put=False)
        else:
            self = self.from_location(1, use_repop=True)
            self.to_location(destination_room, use_look=True if self.IS_PLAYER else False)

        # Messaggio aggiunto per rendere più chiaro a colui che viene seguito di esserlo
        if follower_names:
            send_follow_entity_come_message(self.walker, self, direction, fleeing, running, follower_names)

        if following:
            send_follow_others_come_message(self.walker, self, direction, fleeing, running)
        elif exit.others_out_message:
            self.act(exit.others_out_message, TO.OTHERS, destination_room, self.previous_location(), direction.reverse_dir.from_dir, avoid_prompt=avoid_prompt, break_line=break_line)
        else:
            self.act("$n %s %s." % (self.go_verb_it(fleeing, running), direction.reverse_dir.from_dir), TO.OTHERS, avoid_prompt=avoid_prompt, break_line=break_line)
            self.persistent_act.set_message("others", "$n %s %s." % (self.come_verb_it(fleeing, running), direction.reverse_dir.from_dir))

        # Esegue il movimento automatico anche per coloro che seguono entity
        for follower in followers:
            follower.move(direction, following=True)
            follower.send_prompt()

        if self.location.IS_ROOM and ROOM.DEATH_TRAP in self.location.flags:
            if self.IS_PLAYER:
                self.dies(teleport_corpse=True)
            else:
                # use_repop a True perché magari un builder inserisce una
                # entity reset in una DT
                self.extract(1, use_repop=True)

        # Imposta il tempo attuale per poter cronometrare il prossimo comando
        # di movimento e vedere se l'entità sta correndo o meno
        self.last_movement = time.time()

        force_return = check_trigger(self, "after_move", self, self.location, direction, destination_room, running, behavioured)
        if force_return:
            return True
        force_return = check_trigger(self, "after_" + direction.trigger_suffix, self, self.location, direction, destination_room, running, behavioured)
        if force_return:
            return True
        for en in self.previous_location().iter_contains(use_reversed=True):
            force_return = check_trigger(en, "after_outcoming", self, self.location, direction, destination_room, en, running, behavioured)
            if force_return:
                return True
        for en in destination_room.iter_contains(use_reversed=True):
            if en == self:
                continue
            force_return = check_trigger(en, "after_incoming", self, self.location, direction, destination_room, en, running, behavioured)
            if force_return:
                return True

        return True
    #- Fine Metodo -

    def go_verb_you(self, fleeing, running):
        if running:
            return self.run_verb_you()

        if self.walker and self.walker.go_verb_you:
            return self.walker.go_verb_you

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "Nuoti"

        if fleeing:
            return "Fuggi"

        return self.race.go_verb_you
    #- Fine Metodo -

    def go_verb_it(self, fleeing, running):
        if running:
            return self.run_verb_it()

        if self.walker and self.walker.go_verb_it:
            return self.walker.go_verb_it

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "nuota"

        if fleeing:
            return "fugge"

        return self.race.go_verb_it
    #- Fine Metodo -

    def come_verb_it(self, fleeing, running):
        if running:
            return self.runned_verb_it()
        
        if self.walker and self.walker.come_verb_it:
            return self.walker.come_verb_it

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "ha nuotato"

        # Gli altri nell'altra stanza non capiscono che sta correndo perché
        # sta fuggendo ma l'effetto è quello
        if fleeing:
            return self.run_verb_it()

        return self.race.come_verb_it
    #- Fine Metodo -

    def run_verb_you(self):
        if self.walker and self.walker.run_verb_you:
            return self.walker.run_verb_you

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "Nuoti velocemente"

        return self.race.run_verb_you
    #- Fine Metodo -

    def run_verb_it(self):
        if self.walker and self.walker.run_verb_it:
            return self.walker.run_verb_it

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "nuota velocemente"

        return self.race.run_verb_it
    #- Fine Metodo -

    def runned_verb_it(self):
        if self.walker and self.walker.runned_verb_it:
            return self.walker.runned_verb_it

        if self.location.IS_ROOM and ROOM.UNDERWATER in self.location.flags:
            return "ha nuotato velocemente"

        return self.race.runned_verb_it
    #- Fine Metodo -


class Walker(object):
    """
    Classe che contiene le informazioni relative alle entità che camminano in
    maniera particolare.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment         = ""  # Commento relativo la struttura
        self.go_verb_you     = ""  # Verbo di movimento alla seconda persona
        self.go_verb_it      = ""  # Verbo di movimento alla terza persona
        self.come_verb_it    = ""  # Verbo di movimento al passato per i messaggi di persistenza dell'azione
        self.run_verb_you    = ""  # Verbo di corsa alla seconda persona
        self.run_verb_it     = ""  # Verbo di corsa alla terza persona
        self.runned_verb_it  = ""  # Verbo di corsa al passato per i messaggi di persistenza dell'azione
        self.follow_entity_go_message   = ""  # Messaggio di follow da inviare all'entità che segue prima dello spostamento
        self.follow_others_go_message   = ""  # Messaggio di follow da inviare a tutti gli altri prima che l'entità che segue si sposti
        self.follow_entity_come_message = ""  # Messaggio di follow da inviare all'entità dopo che ha eseguito lo spostamento
        self.follow_others_come_message = ""  # Messaggio di follow da inviare a tutti gli altri dopo che l'entità che segue si è spostata
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        # Tutti i campi sono facoltativi, però se la struttura esiste
        # almeno uno è atteso
        if (not self.go_verb_you and not self.go_verb_it and not self.come_verb_it
        and not self.run_verb_you and not self.run_verb_it and not self.runned_verb_it
        and not self.follow_entity_go_message and not self.follow_others_go_message and not self.follow_others_come_message):
            return "Era atteso almeno un attributo valido."
        elif self.go_verb_you and remove_colors(self.go_verb_you)[0].islower():
            return "go_verb_you non inizia con una maiuscola"
        elif self.run_verb_you and remove_colors(self.run_verb_you)[0].islower():
            return "run_verb_you non inizia con una maiuscola"

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Walker()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, walker2):
        if not walker2:
            return False

        if self.comment != walker2.comment:
            return False
        if self.go_verb_you != walker2.go_verb_you:
            return False
        if self.go_verb_it != walker2.go_verb_it:
            return False
        if self.come_verb_it != walker2.come_verb_it:
            return False
        if self.run_verb_you != walker2.run_verb_you:
            return False
        if self.run_verb_it != walker2.run_verb_it:
            return False
        if self.runned_verb_it != walker2.runned_verb_it:
            return False
        if self.follow_entity_go_message != walker2.follow_entity_go_message:
            return False
        if self.follow_others_go_message != walker2.follow_others_go_message:
            return False
        if self.follow_others_come_message != walker2.follow_others_come_message:
            return False

        return True
    #- Fine Metodo -


def send_follow_entity_go_message(walker, entity, direction, fleeing, running):
    # walker può essere None

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return

    # fleeing e running hanno valore di verità

    # -------------------------------------------------------------------------

    if walker and walker.follow_entity_go_message:
        message = walker.follow_entity_go_message
        if "%verb" in message:
            if message.startswith("%verb"):
                message = message.replace("%verb", color_first_upper(entity.go_verb_you(fleeing, running)))
            else:
                message = message.replace("%verb", entity.go_verb_you(fleeing, running).lower())
        if "%direction" in message:
            if message.startswith("%direction"):
                message = message.replace("%direction", color_first_upper(direction.to_dir))
            else:
                message = message.replace("%direction", direction.to_dir.lower())
    else:
        message = "\n%s %s seguendo $N." % (entity.go_verb_you(fleeing, running), direction.to_dir)

    entity.act("\n%s\n" % put_final_dot(message), TO.ENTITY, entity.guide)
#- Fine Metodo -


def send_follow_others_go_message(walker, entity, direction, fleeing, running):
    # walker può essere None

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return

    # fleeing e running hanno valore di verità

    # -------------------------------------------------------------------------

    if walker and walker.follow_others_go_message:
        message = walker.follow_others_go_message
        if "%verb" in message:
            if message.startswith("%verb"):
                message = message.replace("%verb", color_first_upper(entity.go_verb_it(fleeing, running)))
            else:
                message = message.replace("%verb", entity.go_verb_it(fleeing, running).lower())
        if "%direction" in message:
            if message.startswith("%direction"):
                message = message.replace("%direction", color_first_upper(direction.to_dir))
            else:
                message = message.replace("%direction", direction.to_dir.lower())
    else:
        message = "$n %s %s seguendo $N." % (entity.go_verb_it(fleeing, running), direction.to_dir)

    entity.act(put_final_dot(message), TO.OTHERS, entity.guide)
#- Fine Metodo -


def send_follow_entity_come_message(walker, entity, direction, fleeing, running, follower_names):
    # walker può essere None

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return

    # fleeing e running hanno valore di verità

    if not follower_names:
        log.bug("follower_names non è un parametro valido : %r" % follower_names)
        return

    # -------------------------------------------------------------------------

    if walker and walker.follow_entity_come_message:
        message = walker.follow_entity_come_message
        if "%verb" in message:
            if message.startswith("%verb"):
                message = message.replace("%verb", color_first_upper(entity.go_verb_it(fleeing, running)))
            else:
                message = message.replace("%verb", entity.go_verb_it(fleeing, running).lower())
        if "%direction" in message:
            if message.startswith("%direction"):
                message = message.replace("%direction", color_first_upper(direction.from_dir))
            else:
                message = message.replace("%direction", direction.from_dir.lower())
        if "%followers" in message:
            message = message.replace("%followers", pretty_list(follower_names))
    else:
        message = "Vieni seguit$o da %s." % pretty_list(follower_names)

    entity.act("\n" + put_final_dot(message), TO.ENTITY, entity.guide)
#- Fine Metodo -


def send_follow_others_come_message(walker, entity, direction, fleeing, running):
    # walker può essere None

    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not direction:
        log.bug("direction non è un parametro valido: %r" % direction)
        return

    # fleeing e running hanno valore di verità

    # -------------------------------------------------------------------------

    if walker and walker.follow_others_come_message:
        message = walker.follow_others_come_message
        if "%verb" in message:
            if message.startswith("%verb"):
                message = message.replace("%verb", color_first_upper(entity.come_verb_it(fleeing, running)))
            else:
                message = message.replace("%verb", entity.come_verb_it(fleeing, running).lower())
        if "%direction" in message:
            if message.startswith("%direction"):
                message = message.replace("%direction", color_first_upper(direction.from_dir))
            else:
                message = message.replace("%direction", direction.from_dir.lower())
    else:
        message = "$n %s %s seguendo $N." % (entity.come_verb_it(fleeing, running), direction.reverse_dir.from_dir)

    entity.act(put_final_dot(message), TO.OTHERS, entity.guide)
#- Fine Metodo -
