# -*- coding: utf-8 -*-

"""
Modulo contenente la classe contenente tutti i metodi di act, cioè una
funzione che invia dell'output ai giocatori che rapprensentano delle azioni
le cui stringhe sono composte da dei tag $ che rappresentano varie entità.
"""

#= IMPORT ======================================================================

from src.calendar    import calendar
from src.color       import color_first_upper, remove_colors
from src.config      import config
from src.defer       import defer
from src.enums       import FLAG, GRAMMAR, HAND, OPTION, POSITION, RACE, SEX, TO, TRUST
from src.find_entity import INSTANCE, COUNTER
from src.grammar     import grammar_gender, clean_and_add_article
from src.interpret   import translate_input
from src.log         import log
from src.utility     import put_final_dot, format_for_admin, pretty_list


#= CLASSI ======================================================================

class Act(object):
    # (TD) devo implementare ancora la show_on_location
    def act(self, message, to, target=None, aux1=None, aux2=None, show_on_location=False, send_to_location=None, avoid_prompt=False, break_line=True):
        """
        Serve ad inviare un messaggio d'azione di un'entità a tutte le entità
        bersaglio che possono vedere l'azione.
        Il messaggio può contenere determinati tipi di codice che vanno
        sostituiti secondo specifiche regole di template.
        Se si passa il parametro to come TO.OTHERS e il parametro target valido
        allora TO.OTHERS funziona come lo smaug-like TO.NOTARGET, ovvero invia
        i messaggi a tutti gli altri tranne che al target.
        """
        if not message:
            log.bug("message non è un parametro valido: %r (to: %r, target: %r)" % (
                message, to.code, target.code if target else "None"))
            return

        if not to:
            log.bug("to non è un parametro valido: %r" % to)
            return

        if not target and to == TO.TARGET:
            log.bug("target non è un parametro valido %r con to %r" % (target, to.code))
            return

        # ---------------------------------------------------------------------

        # Se il messaggio di act non deve essere inviato allora esce
        if "no_send" in message.lower():
            return

        if hasattr(self, "account") and self.account and OPTION.LESS_COLORS in self.account.options:
            message = remove_colors(message)

        # (TD) Se il mob o l'oggetto devono rimanere segreti e se to non è TO_CHAR allora ritorna
        pass

        if send_to_location:
            entity_location = send_to_location
        else:
            entity_location = self.location
        if not entity_location and to not in (TO.ENTITY, TO.TARGET):
            log.bug("entity_location non è valida per entity %s" % self.code)
            return

        # A seconda dell'argomento passato 'to' prepara una lista di others a
        # cui far visualizzare il messaggio
        if to == TO.ENTITY:
            others = [self, ]
        elif to == TO.TARGET:
            others = [target, ]
        elif to == TO.OTHERS:
            others = entity_location.players + entity_location.mobs + entity_location.items
            if self in others:
                others.remove(self)
            elif not send_to_location:
                log.bug("self %s not nella lista others composta da %d elementi (location=%s) (to=%s): %s (%s %s %d)" % (
                    self.code, len(others), entity_location, to, message, FLAG.EXTRACTED in self.flags, FLAG.WEAKLY_EXTRACTED in self.flags, self.quantity))
            # Non è un errore che target non sia valido qui, dipende se il
            # TO.OTHERS è inteso a tutti, oppure a tutti tranne il target,
            # nell'ultimo caso si passa appunto il target
            if target in others:
                others.remove(target)
            if aux1 in others:
                others.remove(aux1)
            if aux2 in others:
                others.remove(aux2)
        elif to == TO.ADMINS:
            # (TD) ma qui per lo switch non è che dovrò creare una lista others
            # uguale a quella dell'elemento TO.OTHERS?
            others = list(entity_location.players)
            if self in others:
                others.remove(self)
            message = format_for_admin(message)
        elif to == TO.AREA:
            # (BB)
            others = entity_location.area.players + entity_location.area.mobs + entity_location.area.items
            others.remove(self)
        else:
            log.bug("Controllo sul to %s mancante per ricavare others" % to)
            return

        # Prepara il messaggio sostituendo i tag non dipendenti dal punto di
        # vista di entità che lo leggeranno
        if "$" in message:
            message = self.replace_act_tags(message, target=target)

        # Prepara il messaggio di act persistente
        if not send_to_location and to in (TO.ENTITY, TO.OTHERS, TO.TARGET):
            if not self.persistent_act:
                self.persistent_act = PersistentAct(self)
            self.persistent_act.set_message(to.get_mini_code(), message, target, aux1, aux2)

        for other in others:
            # Capita, per esempio, con il comando dig
            if other.IS_ROOM:
                continue

            # Evita i far vedere i giocatori in incognito
            if self.incognito:
                if other.trust <= TRUST.PLAYER:
                    continue
                else:
                    other.send_to_admin("\nAnche se %s è in incognito vedi l'act" % self.name, break_line=False)

            # Salta gli other che stanno dormendo, a meno che non siano admin
            if other.IS_ACTOR and other.position <= POSITION.SLEEP:
                if other.trust > TRUST.PLAYER:
                    other.send_output("{Anche se stai dormendo vedi o senti:}")
                else:
                    continue

            if to == TO.ADMINS and other.trust <= TRUST.PLAYER:
                continue

            if "$" in message:
                result_message = self.replace_act_tags_name(message, other, target, aux1, aux2, send_to_location)
            else:
                result_message = message

            # (TD) Se other ha un trigger relativo all'act controlla se la frase
            # possa attivare un gamescript
            pass

            if "[" in result_message:
                result_message = color_first_upper(result_message)
            result_message = put_final_dot(result_message)

            if to != TO.ENTITY:
                result_message = "\n" + result_message
            other.send_output(result_message, break_line=break_line)
            if to != TO.ENTITY and not avoid_prompt:
                other.send_prompt()
    #- Fine Metodo -

    def replace_act_tags(self, message, target=None):
        """
        Metodo che esegue un replace intelligente dei tag relativi alla act
        se viene
        """
        if not message:
            log.bug("message non è un parametro valido: %s" % message)
            return ""

        # ---------------------------------------------------------------------

        if "no_send" in message.lower():
            return message

        if "$" not in message:
            return message

        # Il tag $o in Bard era $x
        # (TT) pensare se spostare questo replace di tag e i due sottostanti
        # nella replace_act_tags_name facendoli variare a seconda di quello che
        # uno vede di default (self e/o target potrebbero essere invisibili)
        message = message.replace("$o", grammar_gender(self))

        # Il tag $lui in Bard era $i
        if "$lui" in message:
            if ". $lui" in message:
                message = message.replace(". $lui",  ". %s" % grammar_gender(self, "Lui", "Lei"))
            if "! $lui" in message:
                message = message.replace("! $lui",  "! %s" % grammar_gender(self, "Lui", "Lei"))
            if "? $lui" in message:
                message = message.replace("? $lui",  "? %s" % grammar_gender(self, "Lui", "Lei"))
            if ".\n$lui" in message:
                message = message.replace(".\n$lui", ".\n%s" % grammar_gender(self, "Lui", "Lei"))
            if "!\n$lui" in message:
                message = message.replace("!\n$lui", "!\n%s" % grammar_gender(self, "Lui", "Lei"))
            if "?\n$lui" in message:
                message = message.replace("?\n$lui", "?\n%s" % grammar_gender(self, "Lui", "Lei"))
            if message[ : 4] == "$lui":
                message = message.replace("$lui", grammar_gender(self, "Lui", "Lei"))
            elif message[ : 5] == "\n$lui":
                message = message.replace("\n$lui", "\n" + grammar_gender(self, "Lui", "Lei"))
            else:
                message = message.replace("$lui", grammar_gender(self, "lui", "lei"))

        # Il tag $gli in Bard era $m
        if "$gli" in message:
            if ". $gli" in message:
                message = message.replace(". $gli",  ". %s" % grammar_gender(self, "Gli", "Le"))
            if "! $gli" in message:
                message = message.replace("! $gli",  "! %s" % grammar_gender(self, "Gli", "Le"))
            if "? $gli" in message:
                message = message.replace("? $gli",  "? %s" % grammar_gender(self, "Gli", "Le"))
            if ".\n$gli" in message:
                message = message.replace(".\n$gli", ".\n%s" % grammar_gender(self, "Gli", "Le"))
            if "!\n$gli" in message:
                message = message.replace("!\n$gli", "!\n%s" % grammar_gender(self, "Gli", "Le"))
            if "?\n$gli" in message:
                message = message.replace("?\n$gli", "?\n%s" % grammar_gender(self, "Gli", "Le"))
            if message[ : 4] == "$gli":
                message = message.replace("$gli", grammar_gender(self, "Gli", "Le"))
            elif message[ : 5] == "\n$gli":
                message = message.replace("\n$gli", "\n" + grammar_gender(self, "Gli", "Le"))
            else:
                message = message.replace("$gli", grammar_gender(self, "gli", "le"))

        if self.IS_ACTOR:
            self_race = self.race
            self_hand = self.hand
        elif self.IS_ITEM:
            self_race = self.race
            self_hand = HAND.RIGHT

        # Tag relativi a mani e piedi della razza di self
        # (TT) pensare se spostare questa parte nella replace_act_tags_name
        # per non far vedere che tipo di mani o piedi ha un'entità invisibile
        # (TD) per ora le parti del corpo non hanno colori, quindi basta la
        # capitalize, fare attenzione a possibili problemi futuri nel qual caso
        # si utilizzino i colori
        if "$hands" in message:
            if ". $hands" in message:
                message = message.replace(". $hands",  ". %s" % self.skin_colorize(self_race.hands.capitalize()))
            if "! $hands" in message:
                message = message.replace("! $hands",  "! %s" % self.skin_colorize(self_race.hands.capitalize()))
            if "? $hands" in message:
                message = message.replace("? $hands",  "? %s" % self.skin_colorize(self_race.hands.capitalize()))
            if ".\n$hands" in message:
                message = message.replace(".\n$hands", ".\n%s" % self.skin_colorize(self_race.hands.capitalize()))
            if "!\n$hands" in message:
                message = message.replace("!\n$hands", "!\n%s" % self.skin_colorize(self_race.hands.capitalize()))
            if "?\n$hands" in message:
                message = message.replace("?\n$hands", "?\n%s" % self.skin_colorize(self_race.hands.capitalize()))
            if message[ : 6] == "$hands":
                message = message.replace("$hands", self.skin_colorize(self_race.hands.capitalize()))
            elif message[ : 7] == "\n$hands":
                message = message.replace("\n$hands", "\n" + self.skin_colorize(self_race.hands.capitalize()))
            else:
                message = message.replace("$hands", self.skin_colorize(self_race.hands))

        if "$hand1" in message:
            if ". $hand1" in message:
                message = message.replace(". $hand1",  ". %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if "! $hand1" in message:
                message = message.replace("! $hand1",  "! %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if "? $hand1" in message:
                message = message.replace("? $hand1",  "? %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if ".\n$hand1" in message:
                message = message.replace(".\n$hand1", ".\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if "!\n$hand1" in message:
                message = message.replace("!\n$hand1", "!\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if "?\n$hand1" in message:
                message = message.replace("?\n$hand1", "?\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            if message[ : 6] == "$hand1":
                message = message.replace("$hand1", "%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            elif message[ : 7] == "\n$hand1":
                message = message.replace("\n$hand1", "\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand))
            else:
                message = message.replace("$hand1", "%s %s" % (self.skin_colorize(self_race.hand), self_hand))

        if "$hand2" in message:
            if ". $hand2" in message:
                message = message.replace(". $hand2",  ". %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if "! $hand2" in message:
                message = message.replace("! $hand2",  "! %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if "? $hand2" in message:
                message = message.replace("? $hand2",  "? %s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if ".\n$hand2" in message:
                message = message.replace(".\n$hand2", ".\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if "!\n$hand2" in message:
                message = message.replace("!\n$hand2", "!\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if "?\n$hand2" in message:
                message = message.replace("?\n$hand2", "?\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            if message[ : 6] == "$hand2":
                message = message.replace("$hand2", "%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            elif message[ : 7] == "\n$hand2":
                message = message.replace("\n$hand2", "\n%s %s" % (self.skin_colorize(self_race.hand.capitalize()), self_hand.reverse))
            else:
                message = message.replace("$hand2", "%s %s" % (self.skin_colorize(self_race.hand), self_hand.reverse))

        if "$hand" in message:
            if ". $hand" in message:
                message = message.replace(". $hand",  ". %s" % self.skin_colorize(self_race.hand.capitalize()))
            if "! $hand" in message:
                message = message.replace("! $hand",  "! %s" % self.skin_colorize(self_race.hand.capitalize()))
            if "? $hand" in message:
                message = message.replace("? $hand",  "? %s" % self.skin_colorize(self_race.hand.capitalize()))
            if ".\n$hand" in message:
                message = message.replace(".\n$hand", ".\n%s" % self.skin_colorize(self_race.hand.capitalize()))
            if "!\n$hand" in message:
                message = message.replace("!\n$hand", "!\n%s" % self.skin_colorize(self_race.hand.capitalize()))
            if "?\n$hand" in message:
                message = message.replace("?\n$hand", "?\n%s" % self.skin_colorize(self_race.hand.capitalize()))
            if message[ : 5] == "$hand":
                message = message.replace("$hand", self.skin_colorize(self_race.hand.capitalize()))
            elif message[ : 6] == "\n$hand":
                message = message.replace("\n$hand", "\n" + self.skin_colorize(self_race.hand.capitalize()))
            else:
                message = message.replace("$hand", self.skin_colorize(self_race.hand))

        if "Ai tuoi $feet" in message:
            message = message.replace("Ai tuoi $feet", self_race.feet2.capitalize())
        if "ai tuoi $feet" in message:
            message = message.replace("ai tuoi $feet", self_race.feet2)

        if "$feet" in message:
            if ". $feet" in message:
                message = message.replace(". $feet",  ". %s" % self.skin_colorize(self_race.feet.capitalize()))
            if "! $feet" in message:
                message = message.replace("! $feet",  "! %s" % self.skin_colorize(self_race.feet.capitalize()))
            if "? $feet" in message:
                message = message.replace("? $feet",  "? %s" % self.skin_colorize(self_race.feet.capitalize()))
            if ".\n$feet" in message:
                message = message.replace(".\n$feet", ".\n%s" % self.skin_colorize(self_race.feet.capitalize()))
            if "!\n$feet" in message:
                message = message.replace("!\n$feet", "!\n%s" % self.skin_colorize(self_race.feet.capitalize()))
            if "?\n$feet" in message:
                message = message.replace("?\n$feet", "?\n%s" % self.skin_colorize(self_race.feet.capitalize()))
            if message[ : 5] == "$feet":
                message = message.replace("$feet", self.skin_colorize(self_race.feet.capitalize()))
            elif message[ : 6] == "\n$feet":
                message = message.replace("\n$feet", "\n" + self.skin_colorize(self_race.feet.capitalize()))
            else:
                message = message.replace("$feet", self.skin_colorize(self_race.feet))

        if "$foot" in message:
            if ". $foot" in message:
                message = message.replace(". $foot",  ". %s" % self.skin_colorize(self_race.foot.capitalize()))
            if "! $foot" in message:
                message = message.replace("! $foot",  "! %s" % self.skin_colorize(self_race.foot.capitalize()))
            if "? $foot" in message:
                message = message.replace("? $foot",  "? %s" % self.skin_colorize(self_race.foot.capitalize()))
            if ".\n$foot" in message:
                message = message.replace(".\n$foot", ".\n%s" % self.skin_colorize(self_race.foot.capitalize()))
            if "!\n$foot" in message:
                message = message.replace("!\n$foot", "!\n%s" % self.skin_colorize(self_race.foot.capitalize()))
            if "?\n$foot" in message:
                message = message.replace("?\n$foot", "?\n%s" % self.skin_colorize(self_race.foot.capitalize()))
            if message[ : 5] == "$foot":
                message = message.replace("$foot", self.skin_colorize(self_race.foot.capitalize()))
            elif message[ : 6] == "\n$foot":
                message = message.replace("\n$foot", "\n" + self.skin_colorize(self_race.foot.capitalize()))
            else:
                message = message.replace("$foot", self.skin_colorize(self_race.foot))

        if not self.IS_ITEM and "$skin" in message:
            if ". $skin" in message:
                message = message.replace(". $skin",  ". %s" % self.skin_colorize(self_race.skin.capitalize()))
            if "! $skin" in message:
                message = message.replace("! $skin",  "! %s" % self.skin_colorize(self_race.skin.capitalize()))
            if "? $skin" in message:
                message = message.replace("? $skin",  "? %s" % self.skin_colorize(self_race.skin.capitalize()))
            if ".\n$skin" in message:
                message = message.replace(".\n$skin", ".\n%s" % self.skin_colorize(self_race.skin.capitalize()))
            if "!\n$skin" in message:
                message = message.replace("!\n$skin", "!\n%s" % self.skin_colorize(self_race.skin.capitalize()))
            if "?\n$skin" in message:
                message = message.replace("?\n$skin", "?\n%s" % self.skin_colorize(self_race.skin.capitalize()))
            if message[ : 5] == "$skin":
                message = message.replace("$skin", self.skin_colorize(self_race.skin.capitalize()))
            elif message[ : 6] == "\n$skin":
                message = message.replace("\n$skin", "\n" + self.skin_colorize(self_race.skin.capitalize()))
            else:
                message = message.replace("$skin", self.skin_colorize(self_race.skin))

        if not self.IS_ITEM and "$tongue" in message:
            if ". $tongue" in message:
                message = message.replace(". $tongue",  ". %s" % self_race.tongue.capitalize())
            if "! $tongue" in message:
                message = message.replace("! $tongue",  "! %s" % self_race.tongue.capitalize())
            if "? $tongue" in message:
                message = message.replace("? $tongue",  "? %s" % self_race.tongue.capitalize())
            if ".\n$tongue" in message:
                message = message.replace(".\n$tongue", ".\n%s" % self_race.tongue.capitalize())
            if "!\n$tongue" in message:
                message = message.replace("!\n$tongue", "!\n%s" % self_race.tongue.capitalize())
            if "?\n$tongue" in message:
                message = message.replace("?\n$tongue", "?\n%s" % self_race.tongue.capitalize())
            if message[ : 7] == "$tongue":
                message = message.replace("$tongue", self_race.tongue.capitalize())
            elif message[ : 8] == "\n$tongue":
                message = message.replace("\n$tongue", "\n" + self_race.tongue.capitalize())
            else:
                message = message.replace("$tongue", self_race.tongue)

        # Tag relativi alla traduzione dinamica di un input
        # (TD) utilizzare invece le regex?
        if "$t" in message:
            message = replace_act_tags_translate(message, "$t", entity=self)
        if "$T" in message:
            message = replace_act_tags_translate(message, "$T", entity=self)

        if target:
            # Il tag $O in Bard era $X
            if "$O" in message:
                message = message.replace("$O", grammar_gender(target))

            # Il tag $LUI in Bard era $I
            if "$LUI" in message:
                if ". $LUI" in message:
                    message = message.replace(". $LUI",  ". %s" % grammar_gender(target, "Lui",  "Lei"))
                if "! $LUI" in message:
                    message = message.replace("! $LUI",  "! %s" % grammar_gender(target, "Lui",  "Lei"))
                if "? $LUI" in message:
                    message = message.replace("? $LUI",  "? %s" % grammar_gender(target, "Lui",  "Lei"))
                if ".\n$LUI" in message:
                    message = message.replace(".\n$LUI", ".\n%s" % grammar_gender(target, "Lui",  "Lei"))
                if "!\n$LUI" in message:
                    message = message.replace("!\n$LUI", "!\n%s" % grammar_gender(target, "Lui",  "Lei"))
                if "?\n$LUI" in message:
                    message = message.replace("?\n$LUI", "?\n%s" % grammar_gender(target, "Lui",  "Lei"))
                if message[ : 4] == "$LUI":
                    message = message.replace("$LUI", grammar_gender(target, "Lui", "Lei"))
                elif message[ : 5] == "\n$LUI":
                    message = message.replace("\n$LUI", "\n" + grammar_gender(target, "Lui", "Lei"))
                else:
                    message = message.replace("$LUI", grammar_gender(target, "lui", "lei"))

            # Il tag $GLI in Bard era $M
            if "$GLI" in message:
                if ". $GLI" in message:
                    message = message.replace(". $GLI",  ". %s" % grammar_gender(target, "Gli", "Le"))
                if "! $GLI" in message:
                    message = message.replace("! $GLI",  "! %s" % grammar_gender(target, "Gli", "Le"))
                if "? $GLI" in message:
                    message = message.replace("? $GLI",  "? %s" % grammar_gender(target, "Gli", "Le"))
                if ".\n$GLI" in message:
                    message = message.replace(".\n$GLI", ".\n%s" % grammar_gender(target, "Gli", "Le"))
                if "!\n$GLI" in message:
                    message = message.replace("!\n$GLI", "!\n%s" % grammar_gender(target, "Gli", "Le"))
                if "?\n$GLI" in message:
                    message = message.replace("?\n$GLI", "?\n%s" % grammar_gender(target, "Gli", "Le"))
                if message[ : 4] == "$GLI":
                    message = message.replace("$GLI", grammar_gender(target, "Gli", "Le"))
                elif message[ : 5] == "\n$GLI":
                    message = message.replace("\n$GLI", "\n" + grammar_gender(target, "Gli", "Le"))
                else:
                    message = message.replace("$GLI", grammar_gender(target, "gli", "le"))

            if target.IS_ACTOR:
                target_race = target.race
                target_hand = target.hand
            elif target.IS_ITEM:
                target_race = target.race
                target_hand = HAND.RIGHT

            if "$HANDS" in message and not target.IS_ROOM:
                if ". $HANDS" in message:
                    message = message.replace(". $HANDS",  ". %s" % target.skin_colorize(target_race.hands.capitalize()))
                if "! $HANDS" in message:
                    message = message.replace("! $HANDS",  "! %s" % target.skin_colorize(target_race.hands.capitalize()))
                if "? $HANDS" in message:
                    message = message.replace("? $HANDS",  "? %s" % target.skin_colorize(target_race.hands.capitalize()))
                if ".\n$HANDS" in message:
                    message = message.replace(".\n$HANDS", ".\n%s" % target.skin_colorize(target_race.hands.capitalize()))
                if "!\n$HANDS" in message:
                    message = message.replace("!\n$HANDS", "!\n%s" % target.skin_colorize(target_race.hands.capitalize()))
                if "?\n$HANDS" in message:
                    message = message.replace("?\n$HANDS", "?\n%s" % target.skin_colorize(target_race.hands.capitalize()))
                if message[ : 6] == "$HANDS":
                    message = message.replace("$HANDS", target.skin_colorize(target_race.hands.capitalize()))
                elif message[ : 7] == "\n$HANDS":
                    message = message.replace("\n$HANDS", "\n" + target.skin_colorize(target_race.hands.capitalize()))
                else:
                    message = message.replace("$HANDS", target.skin_colorize(target_race.hands))

            if "$HAND1" in message and not target.IS_ROOM:
                if ". $HAND1" in message:
                    message = message.replace(". $HAND1",  ". %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if "! $HAND1" in message:
                    message = message.replace("! $HAND1",  "! %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if "? $HAND1" in message:
                    message = message.replace("? $HAND1",  "? %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if ".\n$HAND1" in message:
                    message = message.replace(".\n$HAND1", ".\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if "!\n$HAND1" in message:
                    message = message.replace("!\n$HAND1", "!\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if "?\n$HAND1" in message:
                    message = message.replace("?\n$HAND1", "?\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                if message[ : 6] == "$HAND1":
                    message = message.replace("$HAND1", "%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                elif message[ : 7] == "\n$HAND1":
                    message = message.replace("\n$HAND1", "%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand))
                else:
                    message = message.replace("$HAND1", "%s %s" % (target.skin_colorize(target_race.hand), target_hand))

            if "$HAND2" in message and not target.IS_ROOM:
                if ". $HAND2" in message:
                    message = message.replace(". $HAND2",  ". %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if "! $HAND2" in message:
                    message = message.replace("! $HAND2",  "! %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if "? $HAND2" in message:
                    message = message.replace("? $HAND2",  "? %s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if ".\n$HAND2" in message:
                    message = message.replace(".\n$HAND2", ".\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if "!\n$HAND2" in message:
                    message = message.replace("!\n$HAND2", "!\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if "?\n$HAND2" in message:
                    message = message.replace("?\n$HAND2", "?\n%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                if message[ : 6] == "$HAND2":
                    message = message.replace("$HAND2", "%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                elif message[ : 7] == "\n$HAND2":
                    message = message.replace("\n$HAND2", "%s %s" % (target.skin_colorize(target_race.hand.capitalize()), target_hand.reverse))
                else:
                    message = message.replace("$HAND2", "%s %s" % (target.skin_colorize(target_race.hand), target_hand.reverse))

            # Tag relativi a mani e piedi della razza di target
            if "$HAND" in message and not target.IS_ROOM:
                if ". $HAND" in message:
                    message = message.replace(". $HAND",  ". %s" % target.skin_colorize(target_race.hand.capitalize()))
                if "! $HAND" in message:
                    message = message.replace("! $HAND",  "! %s" % target.skin_colorize(target_race.hand.capitalize()))
                if "? $HAND" in message:
                    message = message.replace("? $HAND",  "? %s" % target.skin_colorize(target_race.hand.capitalize()))
                if ".\n$HAND" in message:
                    message = message.replace(".\n$HAND", ".\n%s" % target.skin_colorize(target_race.hand.capitalize()))
                if "!\n$HAND" in message:
                    message = message.replace("!\n$HAND", "!\n%s" % target.skin_colorize(target_race.hand.capitalize()))
                if "?\n$HAND" in message:
                    message = message.replace("?\n$HAND", "?\n%s" % target.skin_colorize(target_race.hand.capitalize()))
                if message[ : 5] == "$HAND":
                    message = message.replace("$HAND", target.skin_colorize(target_race.hand.capitalize()))
                elif message[ : 6] == "\n$HAND":
                    message = message.replace("\n$HAND", "\n" + target.skin_colorize(target_race.hand.capitalize()))
                else:
                    message = message.replace("$HAND", target.skin_colorize(target_race.hand))

            if "$FEET" in message and not target.IS_ROOM:
                if ". $FEET" in message:
                    message = message.replace(". $FEET",  ". %s" % target.skin_colorize(target_race.feet.capitalize()))
                if "! $FEET" in message:
                    message = message.replace("! $FEET",  "! %s" % target.skin_colorize(target_race.feet.capitalize()))
                if "? $FEET" in message:
                    message = message.replace("? $FEET",  "? %s" % target.skin_colorize(target_race.feet.capitalize()))
                if ".\n$FEET" in message:
                    message = message.replace(".\n$FEET", ".\n%s" % target.skin_colorize(target_race.feet.capitalize()))
                if "!\n$FEET" in message:
                    message = message.replace("!\n$FEET", "!\n%s" % target.skin_colorize(target_race.feet.capitalize()))
                if "?\n$FEET" in message:
                    message = message.replace("?\n$FEET", "?\n%s" % target.skin_colorize(target_race.feet.capitalize()))
                if message[ : 5] == "$FEET":
                    message = message.replace("$FEET", target.skin_colorize(target_race.feet.capitalize()))
                elif message[ : 6] == "\n$FEET":
                    message = message.replace("\n$FEET", "\n" + target.skin_colorize(target_race.feet.capitalize()))
                else:
                    message = message.replace("$FEET", target.skin_colorize(target_race.feet))

            if "$FOOT" in message and not target.IS_ROOM:
                if ". $FOOT" in message:
                    message = message.replace(". $FOOT",  ". %s" % target.skin_colorize(target_race.foot.capitalize()))
                if "! $FOOT" in message:
                    message = message.replace("! $FOOT",  "! %s" % target.skin_colorize(target_race.foot.capitalize()))
                if "? $FOOT" in message:
                    message = message.replace("? $FOOT",  "? %s" % target.skin_colorize(target_race.foot.capitalize()))
                if ".\n$FOOT" in message:
                    message = message.replace(".\n$FOOT", ".\n%s" % target.skin_colorize(target_race.foot.capitalize()))
                if "!\n$FOOT" in message:
                    message = message.replace("!\n$FOOT", "!\n%s" % target.skin_colorize(target_race.foot.capitalize()))
                if "?\n$FOOT" in message:
                    message = message.replace("?\n$FOOT", "?\n%s" % target.skin_colorize(target_race.foot.capitalize()))
                if message[ : 5] == "$FOOT":
                    message = message.replace("$FOOT", target.skin_colorize(target_race.foot.capitalize()))
                elif message[ : 6] == "\n$FOOT":
                    message = message.replace("\n$FOOT", "\n" + target.skin_colorize(target_race.foot.capitalize()))
                else:
                    message = message.replace("$FOOT", target.skin_colorize(target_race.foot))

            if "$SKIN" in message and not target.IS_ROOM:
                if ". $SKIN" in message:
                    message = message.replace(". $SKIN",  ". %s" % target.skin_colorize(target.race.skin.capitalize()))
                if "! $SKIN" in message:
                    message = message.replace("! $SKIN",  "! %s" % target.skin_colorize(target.race.skin.capitalize()))
                if "? $SKIN" in message:
                    message = message.replace("? $SKIN",  "? %s" % target.skin_colorize(target.race.skin.capitalize()))
                if ".\n$SKIN" in message:
                    message = message.replace(".\n$SKIN", ".\n%s" % target.skin_colorize(target.race.skin.capitalize()))
                if "!\n$SKIN" in message:
                    message = message.replace("!\n$SKIN", "!\n%s" % target.skin_colorize(target.race.skin.capitalize()))
                if "?\n$SKIN" in message:
                    message = message.replace("?\n$SKIN", "?\n%s" % target.skin_colorize(target.race.skin.capitalize()))
                if message[ : 5] == "$SKIN":
                    message = message.replace("$SKIN", target.skin_colorize(target.race.skin.capitalize()))
                elif message[ : 6] == "\n$SKIN":
                    message = message.replace("\n$SKIN", "\n" + target.skin_colorize(target.race.skin.capitalize()))
                else:
                    message = message.replace("$SKIN", target.skin_colorize(target.race.skin))

            if "$TONGUE" in message and not target.IS_ROOM:
                if ". $TONGUE" in message:
                    message = message.replace(". $TONGUE",  ". %s" % target.race.tongue.capitalize())
                if "! $TONGUE" in message:
                    message = message.replace("! $TONGUE",  "! %s" % target.race.tongue.capitalize())
                if "? $TONGUE" in message:
                    message = message.replace("? $TONGUE",  "? %s" % target.race.tongue.capitalize())
                if ".\n$TONGUE" in message:
                    message = message.replace(".\n$TONGUE", ".\n%s" % target.race.tongue.capitalize())
                if "!\n$TONGUE" in message:
                    message = message.replace("!\n$TONGUE", "!\n%s" % target.race.tongue.capitalize())
                if "?\n$TONGUE" in message:
                    message = message.replace("?\n$TONGUE", "?\n%s" % target.race.tongue.capitalize())
                if message[ : 5] == "$TONGUE":
                    message = message.replace("$TONGUE", target.race.tongue.capitalize())
                elif message[ : 6] == "\n$TONGUE":
                    message = message.replace("\n$TONGUE", "\n" + target.race.tongue.capitalize())
                else:
                    message = message.replace("$TONGUE", target.race.tongue)

        # Tag relativi al calendario
        if "$day_week" in message:
            day_week = str(calendar.get_weekday())
            # Prima di tutti il $day_week per non confonderlo con il $day
            if ". $day_week" in message:
                message = message.replace(". $day_week",  ". %s" % color_first_upper(day_week))
            if "! $day_week" in message:
                message = message.replace("! $day_week",  "! %s" % color_first_upper(day_week))
            if "? $day_week" in message:
                message = message.replace("? $day_week",  "? %s" % color_first_upper(day_week))
            if ".\n$day_week" in message:
                message = message.replace(".\n$day_week", ".\n%s" % color_first_upper(day_week))
            if "!\n$day_week" in message:
                message = message.replace("!\n$day_week", "!\n%s" % color_first_upper(day_week))
            if "?\n$day_week" in message:
                message = message.replace("?\n$day_week", "?\n%s" % color_first_upper(day_week))
            if message[ : 9] == "$day_week":
                message = message.replace("$day_week", color_first_upper(day_week))
            elif message[ : 10] == "\n$day_week":
                message = message.replace("\n$day_week", "\n" + color_first_upper(day_week))
            else:
                message = message.replace("$day_week", day_week)

        if "$minute" in message:
            message = message.replace("$minute", str(calendar.minute))
        if "$hour" in message:
            message = message.replace("$hour", str(calendar.hour))
        if "$day":
            message = message.replace("$day", str(calendar.day))
        if "$year":
            message = message.replace("$year", str(calendar.year))

        if "$month" in message:
            month = str(calendar.month).capitalize()
            if ". $month" in message:
                message = message.replace(". $month",  ". %s" % color_first_upper(month))
            if "! $month" in message:
                message = message.replace("! $month",  "! %s" % color_first_upper(month))
            if "? $month" in message:
                message = message.replace("? $month",  "? %s" % color_first_upper(month))
            if ".\n$month" in message:
                message = message.replace(".\n$month", ".\n%s" % color_first_upper(month))
            if "!\n$month" in message:
                message = message.replace("!\n$month", "!\n%s" % color_first_upper(month))
            if "?\n$month" in message:
                message = message.replace("?\n$month", "?\n%s" % color_first_upper(month))
            if message[ : 6] == "$month":
                message = message.replace("$month", color_first_upper(month))
            elif message[ : 7] == "\n$month":
                message = message.replace("\n$month", "\n" + color_first_upper(month))
            else:
                message = message.replace("$month", str(calendar.month))

        if "$season" in message:
            season = str(calendar.get_season())
            if ". $season" in message:
                message = message.replace(". $season",  ". %s" % color_first_upper(season))
            if "! $season" in message:
                message = message.replace("! $season",  "! %s" % color_first_upper(season))
            if "? $season" in message:
                message = message.replace("? $season",  "? %s" % color_first_upper(season))
            if ".\n$season" in message:
                message = message.replace(".\n$season", ".\n%s" % color_first_upper(season))
            if "!\n$season" in message:
                message = message.replace("!\n$season", "!\n%s" % color_first_upper(season))
            if "?\n$season" in message:
                message = message.replace("?\n$season", "?\n%s" % color_first_upper(season))
            if message[ : 7] == "$season":
                message = message.replace("$season", color_first_upper(season))
            elif message[ : 8] == "\n$season":
                message = message.replace("\n$season", "\n" + color_first_upper(season))
            else:
                message = message.replace("$season", season)

        return message
    #- Fine Metodo -

    def replace_act_tags_name(self, message, looker=None, target=None, aux1=None, aux2=None, send_to_location=None, formatted_name=False, use_number_argument=True):
        if not message:
            log.bug("message non è un parametro valido: %r" % message)
            return ""

        # ---------------------------------------------------------------------

        if "$" not in message:
            return message

        if "$n" in message:
            # (TD) se si fa un send_to_location allora il soggetto è lontano, a
            # meno che non sia una porta, in futuro probabilmente imposterò
            # almeno la location della porta, quindi questa parte cambierà
            if send_to_location and self.location:
                if ". $n" in message:
                    message = message.replace(". $n", ". Qualcuno")
                if "! $n" in message:
                    message = message.replace("! $n", "! Qualcuno")
                if "? $n" in message:
                    message = message.replace("? $n", "? Qualcuno")
                if ".\n$n" in message:
                    message = message.replace(".\n$n", ".\nQualcuno")
                if "!\n$n" in message:
                    message = message.replace("!\n$n", "!\nQualcuno")
                if "?\n$n" in message:
                    message = message.replace("?\n$n", "?\nQualcuno")
                if message[ : 2] == "$n":
                    message = message.replace("$n", "Qualcuno")
                elif message[ : 3] == "\n$n":
                    message = message.replace("\n$n", "\nQualcuno")
                else:
                    message = message.replace("$n", "qualcuno")
            else:
                name = self.get_name(looker=looker)
                if ". $n" in message:
                    message = message.replace(". $n",  ". %s" % color_first_upper(name))
                if "! $n" in message:
                    message = message.replace("! $n",  "! %s" % color_first_upper(name))
                if "? $n" in message:
                    message = message.replace("? $n",  "? %s" % color_first_upper(name))
                if ".\n$n" in message:
                    message = message.replace(".\n$n", ".\n%s" % color_first_upper(name))
                if "!\n$n" in message:
                    message = message.replace("!\n$n", "!\n%s" % color_first_upper(name))
                if "?\n$n" in message:
                    message = message.replace("?\n$n", "?\n%s" % color_first_upper(name))
                if message[ : 2] == "$n":
                    message = message.replace("$n", color_first_upper(name))
                elif message[ : 3] == "\n$n":
                    message = message.replace("\n$n", "\n" + color_first_upper(name))
                else:
                    message = message.replace("$n", name)

        if target and "$N" in message:
            if formatted_name and not target.IS_ROOM:
                name = target.get_formatted_name(looker, use_number_argument=use_number_argument, show_icon=False)
            else:
                name = target.get_name(looker=looker)
            if ". $N" in message:
                message = message.replace(". $N",  ". %s" % color_first_upper(name))
            if "! $N" in message:
                message = message.replace("! $N",  "! %s" % color_first_upper(name))
            if "? $N" in message:
                message = message.replace("? $N",  "? %s" % color_first_upper(name))
            if ".\n$N" in message:
                message = message.replace(".\n$N", ".\n%s" % color_first_upper(name))
            if "!\n$N" in message:
                message = message.replace("!\n$N", "!\n%s" % color_first_upper(name))
            if "?\n$N" in message:
                message = message.replace("?\n$N", "?\n" % color_first_upper(name))
            if message[ : 2] == "$N":
                message = message.replace("$N", color_first_upper(name))
            elif message[ : 3] == "\n$N":
                message = message.replace("\n$N", "\n" + color_first_upper(name))
            else:
                message = message.replace("$N", name)

        if aux1 and "$a" in message:
            try:
                name = aux1.get_name(looker=looker)
            except AttributeError:
                # Allora aux1 dovrebbe essere una stringa
                message = message.replace("$a", str(aux1))
            else:
                if ". $a" in message:
                    message = message.replace(". $a",  ". %s" % color_first_upper(name))
                if "! $a" in message:
                    message = message.replace("! $a",  "! %s" % color_first_upper(name))
                if "? $a" in message:
                    message = message.replace("? $a",  "? %s" % color_first_upper(name))
                if ".\n$a" in message:
                    message = message.replace(".\n$a", ".\n%s" % color_first_upper(name))
                if "!\n$a" in message:
                    message = message.replace("!\n$a", "!\n%s" % color_first_upper(name))
                if "?\n$a" in message:
                    message = message.replace("?\n$a", "?\n%s" % color_first_upper(name))
                if message[ : 2] == "$a":
                    message = message.replace("$a", color_first_upper(name))
                elif message[ : 3] == "\n$a":
                    message = message.replace("\n$a", "\n" + color_first_upper(name))
                else:
                    message = message.replace("$a", name)

        if aux2 and "$A" in message:
            try:
                name = aux2.get_name(looker=looker)
            except AttributeError:
                # Allora aux2 dovrebbe essere una stringa
                message = message.replace("$A", str(aux2))
            else:
                if ". $A" in message:
                    message = message.replace(". $A",  ". %s" % color_first_upper(name))
                if "! $A" in message:
                    message = message.replace("! $A",  "! %s" % color_first_upper(name))
                if "? $A" in message:
                    message = message.replace("? $A",  "? %s" % color_first_upper(name))
                if ".\n$A" in message:
                    message = message.replace(".\n$A", ".\n%s" % color_first_upper(name))
                if "!\n$A" in message:
                    message = message.replace("!\n$A", "!\n%s" % color_first_upper(name))
                if "?\n$A" in message:
                    message = message.replace("?\n$A", "?\n%s" % color_first_upper(name))
                if message[ : 2] == "$A":
                    message = message.replace("$A", color_first_upper(name))
                elif message[ : 3] == "\n$A":
                    message = message.replace("\n$A", "\n" + color_first_upper(name))
                else:
                    message = message.replace("$A", name)

        if self.location and "$l" in message:
            name = self.location.get_name(looker=looker)
            if ". $l" in message:
                message = message.replace(". $l",  ". %s" % color_first_upper(name))
            if "! $l" in message:
                message = message.replace("! $l",  "! %s" % color_first_upper(name))
            if "? $l" in message:
                message = message.replace("? $l",  "? %s" % color_first_upper(name))
            if ".\n$l" in message:
                message = message.replace(".\n$l", ".\n%s" % color_first_upper(name))
            if "!\n$l" in message:
                message = message.replace("!\n$l", "!\n%s" % color_first_upper(name))
            if "?\n$l" in message:
                message = message.replace("?\n$l", "?\n%s" % color_first_upper(name))
            if "in $l" in message and not self.location.IS_PLAYER:
                # (TD) se name è il nome di persona allora il replace è
                # semplicemente "in" come il check soprastante relativo all'IS_PLAYER
                genre = GRAMMAR.FEMININE if self.location.sex == SEX.FEMALE else GRAMMAR.MASCULINE
                message = message.replace("in $l", clean_and_add_article(name, GRAMMAR.PREPOSITION_IN, genre=genre))
            if message[ : 2] == "$l":
                message = message.replace("$l", color_first_upper(name))
            elif message[ : 3] == "\n$l":
                message = message.replace("\n$l", "\n" + color_first_upper(name))
            else:
                message = message.replace("$l", name)

        if target and "$L" in message and not target.IS_ROOM and target.location:
            name = target.location.get_name(looker=looker)
            if ". $L" in message:
                message = message.replace(". $L",  ". %s" % color_first_upper(name))
            if "! $L" in message:
                message = message.replace("! $L",  "! %s" % color_first_upper(name))
            if "? $L" in message:
                message = message.replace("? $L",  "? %s" % color_first_upper(name))
            if ".\n$L" in message:
                message = message.replace(".\n$L", ".\n%s" % color_first_upper(name))
            if "!\n$L" in message:
                message = message.replace("!\n$L", "!\n%s" % color_first_upper(name))
            if "?\n$L" in message:
                message = message.replace("?\n$L", "?\n%s" % color_first_upper(name))
            if message[ : 2] == "$L":
                message = message.replace("$L", color_first_upper(name))
            elif message[ : 3] == "\n$L":
                message = message.replace("\n$L", "\n" + color_first_upper(name))
            else:
                message = message.replace("$L", name)

        if self.previous_location and self.previous_location() and "$p" in message:
            name = self.previous_location().get_name(looker=looker)
            if ". $p" in message:
                message = message.replace(". $p",  ". %s" % color_first_upper(name))
            if "! $p" in message:
                message = message.replace("! $p",  "! %s" % color_first_upper(name))
            if "? $p" in message:
                message = message.replace("? $p",  "? %s" % color_first_upper(name))
            if ".\n$p" in message:
                message = message.replace(".\n$p", ".\n%s" % color_first_upper(name))
            if "!\n$p" in message:
                message = message.replace("!\n$p", "!\n%s" % color_first_upper(name))
            if "?\n$p" in message:
                message = message.replace("?\n$p", "?\n%s" % color_first_upper(name))
            if message[ : 2] == "$p":
                message = message.replace("$p", color_first_upper(name))
            elif message[ : 3] == "\n$p":
                message = message.replace("\n$p", "\n" + color_first_upper(name))
            else:
                message = message.replace("$p", name)

        if target and not target.IS_ROOM and target.previous_location and target.previous_location() and "$P" in message:
            name = target.previous_location().get_name(looker=looker)
            if ". $P" in message:
                message = message.replace(". $P",  ". %s" % color_first_upper(name))
            if "! $P" in message:
                message = message.replace("! $P",  "! %s" % color_first_upper(name))
            if "? $P" in message:
                message = message.replace("? $P",  "? %s" % color_first_upper(name))
            if ".\n$P" in message:
                message = message.replace(".\n$P", ".\n%s" % color_first_upper(name))
            if "!\n$P" in message:
                message = message.replace("!\n$P", "!\n%s" % color_first_upper(name))
            if "?\n$P" in message:
                message = message.replace("?\n$P", "?\n%s" % color_first_upper(name))
            if message[ : 2] == "$P":
                message = message.replace("$P", color_first_upper(name))
            elif message[ : 3] == "\n$P":
                message = message.replace("\n$P", "\n" + color_first_upper(name))
            else:
                message = message.replace("$P", name)

        # Ritorna i nomi in elenco delle entità visibili in una locazione.
        # Nonostante la $i sia minuscola fa riferimento sempre a target.
        if target and "$i" in message:
            contains = []
            list_of_entites = target.get_list_of_entities(looker)
            for en in list_of_entites:
                if not looker.can_see(en[INSTANCE]):
                    continue
                if FLAG.NO_LOOK_LIST in en[INSTANCE].flags and looker.trust <= TRUST.PLAYER:
                    continue
                if en[COUNTER] > 1:
                    contains.append("%s (%d)" % (en[INSTANCE].get_name(looker=looker), en[COUNTER]))
                else:
                    if FLAG.NO_LOOK_LIST in en[INSTANCE].flags:
                        contains.append(en[INSTANCE].get_name(looker=looker) + format_for_admin("no_look_list"))
                    else:
                        contains.append(en[INSTANCE].get_name(looker=looker))
            if contains:
                contains = pretty_list(contains).strip()
            else:
                contains = "nulla"

            if ". $i" in message:
                message = message.replace(". $i",  ". %s" % color_first_upper(contains))
            if "! $i" in message:
                message = message.replace("! $i",  "! %s" % color_first_upper(contains))
            if "? $i" in message:
                message = message.replace("? $i",  "? %s" % color_first_upper(contains))
            if ".\n$i" in message:
                message = message.replace(".\n$i", ".\n%s" % color_first_upper(contains))
            if "!\n$i" in message:
                message = message.replace("!\n$i", "!\n%s" % color_first_upper(contains))
            if "?\n$i" in message:
                message = message.replace("?\n$i", "?\n%s" % color_first_upper(contains))
            if message[ : 2] == "$i":
                message = message.replace("$i", color_first_upper(contains))
            elif message[ : 3] == "\n$i":
                message = message.replace("\n$i", "\n" + color_first_upper(contains))
            else:
                message = message.replace("$i", contains)

        # Ritorna il nome dell'entità che pesa di più in una locazione
        if target and "$I" in message:
            weights = []
            list_of_entites = target.get_list_of_entities(looker)
            for en in list_of_entites:
                if not looker.can_see(en[INSTANCE]):
                    continue
                weights.append(en[COUNTER] * en[INSTANCE].get_total_weight())

            contains = []
            if weights:
                maximum = max(weights)
                maximum_entity = list_of_entites[weights.index(maximum)][INSTANCE]
                if FLAG.NO_LOOK_LIST in maximum_entity.flags:
                    if looker.trust <= TRUST.PLAYER:
                        contains = []
                    else:
                        contains = [maximum_entity.get_name(looker=looker) + format_for_admin("no_look_list")]
                else:
                    contains = [maximum_entity.get_name(looker=looker)]

            interactable_entities = list(target.iter_only_interactable_entities(use_can_see=True))
            for ie in interactable_entities:
                if FLAG.NO_LOOK_LIST in ie.flags:
                    if looker.trust <= TRUST.PLAYER:
                        continue
                    name = ie.get_name(looker=looker) + format_for_admin("no_look_list")
                else:
                    name = ie.get_name(looker=looker)
                if name not in contains:
                    contains.append(name)

            if contains:
                contains = pretty_list(contains).strip()
            else:
                contains = "nulla"

            if ". $I" in message:
                message = message.replace(". $I",  ". %s" % color_first_upper(contains))
            if "! $I" in message:
                message = message.replace("! $I",  "! %s" % color_first_upper(contains))
            if "? $I" in message:
                message = message.replace("? $I",  "? %s" % color_first_upper(contains))
            if ".\n$I" in message:
                message = message.replace(".\n$I", ".\n%s" % color_first_upper(contains))
            if "!\n$I" in message:
                message = message.replace("!\n$I", "!\n%s" % color_first_upper(contains))
            if "?\n$I" in message:
                message = message.replace("?\n$I", "?\n%s" % color_first_upper(contains))
            if message[ : 2] == "$I":
                message = message.replace("$I", color_first_upper(contains))
            elif message[ : 3] == "\n$I":
                message = message.replace("\n$I", "\n" + color_first_upper(contains))
            else:
                message = message.replace("$I", contains)

        # Ritornano rispettivamente la parola chiave di entity e quella
        # del target
        if "$k" in message:
            message = message.replace("$k", self.get_numbered_keyword(looker=looker))
        if target and "$K" in message:
            message = message.replace("$K", target.get_numbered_keyword(looker=looker))

        return message
    #- Fine Metodo -

    def sex_replacer(self, argument, is_subject=True):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return ""

        # -------------------------------------------------------------------------

        if is_subject:
            if self.sex == SEX.FEMALE:
                return argument.replace("$o", "a")
            else:
                return argument.replace("$o", "o")
        else:
            if self.sex == SEX.FEMALE:
                return argument.replace("$O", "a")
            else:
                return argument.replace("$O", "o")
    #- Fine Metodo -


class PersistentAct(object):
    """
    La persistenza dell'azione.
    Praticamente si salva le informazioni di un messaggio di act relativo una
    entità, ed eventualmente anche il corrispettivo messaggio di act per gli
    altri e/o per il target, e lo invia al posto della long dell'entità che
    ha eseguito l'azione se un giocatore entro un limite di tempo abbastanza
    breve eseguirà il look dopo l'azione.
    """
    def __init__(self, entity=None):
        self.entity_message       = ""  # Messaggio di act entità utilizzato come long
        self.entity_args          = []  # Argomenti da passare ai metodi di act per il messaggio entity
        self.others_message       = ""  # Messaggio di act others utilizzato come long
        self.others_args          = []  # Argomenti da passare ai metodi di act per il messaggio others
        self.target_message       = ""  # Messaggio di act target utilizzato come long
        self.target_args          = []  # Argomenti da passare ai metodi di act per il messaggio target
        self.deferred_destruction = None

        # Deferred relativa alla distruzione di quest'istanza
        if entity:
            # (TD) al limite per i mob inserire un secondo invece che due?
            self.deferred_destruction = defer(config.persistent_act_seconds, self.destruction, entity)
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %r" % (super(PersistentAct, self).__repr__(), self.entity_args)
    #- Fine Metodo -

    def get_persistent_message(self, entity, looker, use_number_argument=True):
        if self.entity_args and looker == entity:
            message = entity.replace_act_tags_name(
                self.entity_message,
                looker,
                self.entity_args[0],
                self.entity_args[1],
                self.entity_args[2],
                formatted_name=True,
                use_number_argument=use_number_argument)
            return message
        elif self.target_args and looker == self.target_args[0]:
            message = entity.replace_act_tags_name(
                self.target_message,
                looker,
                self.target_args[0],
                self.target_args[1],
                self.target_args[2],
                formatted_name=True,
                use_number_argument=use_number_argument)
            return message
        elif self.others_args:
            message = entity.replace_act_tags_name(
                self.others_message,
                looker,
                self.others_args[0],
                self.others_args[1],
                self.others_args[2],
                formatted_name=True,
                use_number_argument=use_number_argument)
            return message

        return ""
    #- Fine Metodo -

    def set_message(self, to_code, message, target=None, aux1=None, aux2=None):
        setattr(self, to_code + "_message", message)
        setattr(self, to_code + "_args", [target, aux1, aux2])
    #- Fine Metodo -

    def destruction(self, entity):
        # È normale che entity qui sia None, significa che è stato estratto
        # prima che la deferred scattasse e impostato poi a None dalle funzioni
        # di deferred
        if not entity:
            return
        self.__init__()
        entity.persistent_act = None
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def replace_act_tags_translate(message, replace_act_tag, entity=None):
    if not message:
        log.bug("message non è un parametro valido: %r" % message)
        return

    if not replace_act_tag:
        log.bug("message non è un parametro valido: %r" % replace_act_tag)
        return

    # Se entity non è un parametro valido allora il giocatore probabilmente
    # si trova in una pagina web non connessa al gioco

    # -------------------------------------------------------------------------

    t_position = len(message)
    while 1:
        t_position = message.rfind(replace_act_tag, 0, t_position - 1)
        if t_position == -1:
            break;
        char_position = t_position + 2
        input = ""
        while char_position < len(message):
            if message[char_position] in (" \n\r\t.,;:!?-_'=)(/&%$£\"[]<>#@°§+*\\{}~"):
                break
            input += message[char_position]
            char_position += 1

        if input:
            translation = translate_input(entity, input, "en", [True, ])
            if replace_act_tag == "$t":
                message = "%s[limegreen]%s[close]%s" % (message[ : t_position], translation, message[char_position : ])
            else:
                message = "%s%s%s" % (message[ : t_position], translation, message[char_position : ])

    return message
#- Fine Funzione -
