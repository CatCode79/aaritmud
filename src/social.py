# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica dei social, alcuni di essi contengono del codice
personalizzato nella cartella src/socials.
"""


#= IMPORT ======================================================================

import random

from src.affect    import is_affected
from src.data      import Data
from src.database  import database
from src.element   import EnumElementDict, Element
from src.enums     import INTENTION, POSITION, RACE
from src.fight     import start_fight
from src.interpret import interpret
from src.log       import log


#= CLASSI ======================================================================

class Social(Data):
    """
    Gestisce un social.
    """
    PRIMARY_KEY = "fun_name"
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"racial_messages" : ("src.social", "SocialRacialMessage")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment         = ""
        self.fun_name        = ""  # Nome della funzione del comando legato al social
        self.intention       = Element(INTENTION.NONE)  # Tipologia di intenzione
        self.smiles          = ""  # Elenco degli smile supportati dal social
        self.expression      = ""  # Espressione relativa al'utilizzo degli smile
        self.racial_messages = EnumElementDict()
    #- Fine Inizializzazione -

    def get_error_message(self):
        if not self.fun_name:
            msg = "fun_name non valida: %r" % self.fun_name
        elif " " in self.fun_name:
            msg = "fun_name contiene degli spazi: <%s>" % self.fun_name
        elif self.intention.get_error_message(INTENTION, "intention") != "":
            msg = self.intention.get_error_message(INTENTION, "intention")
        elif ((    self.smiles and not self.expression)
        or    (not self.smiles and     self.expression)):
            msg = "smiles ed expression devono essere tutti e due vuoti oppure non vuoti"
        elif not self.racial_messages:
            msg = "Deve esistere almeno un messaggio razziale di social, di solito umano"
        elif RACE.HUMAN not in self.racial_messages:
            msg = "Deve esistere sempre il messaggio razziale di social degli umani"
        elif self._get_message_error_racial_message() != "":
            msg = self._get_message_error_racial_message()
        else:
            return ""

        log.bug("(Social: fun_name %s) %s" % (self.fun_name, msg))
        return msg
    #- Fine Metodo -

    def get_input_argument(self):
        return self.fun_name.split("_")[1]
    #- Fine Metodo -

    def _get_message_error_racial_message(self):
        """
        Controlla tutti i messaggi di social razziali
        """
        for racial_message in self.racial_messages.itervalues():
            msg = racial_message.get_error_message()
            if msg:
                return msg
        return ""
    #- Fine Metodo -

    def get_racial_message(self, entity, attr, target=None, possessive="", use_human=True):
        """
        Ricava il messaggio social razziale corretto.
        """
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        if not target and target is not None:
            log.bug("entity non è un parametro valido: %r" % target)
            return

        if possessive not in ("", "mio", "tuo", "suo"):
            log.bug("possessive non è un parametro valido: %r" % possessive)
            return

        # use_human ha valore di verità

        # -------------------------------------------------------------------------

        if entity.race in self.racial_messages:
            message = getattr(self.racial_messages[entity.race], attr)
        elif use_human:
            # I messaggi di social razziali degli umani devono esistere per forza
            message = getattr(self.racial_messages[RACE.HUMAN], attr)
        else:
            return ""

        if target and target.location == entity:
            message = message.replace("$N,", "$N, nel %s inventario," % possessive)
            message = message.replace("$N ", "$N, nel %s inventario, " % possessive)
            message = message.replace("$N.", "$N, nel %s inventario." % possessive)

        return message
    #- Fine Metodo -

    def send_to(self, sender, receiver=None):
        """
        Se receiver non è valido allora invia il social senza argomento.
        """
        # E' possibile che non siano valide per via della defer che
        # chiama questo metodo
        if not sender:
            return
        if not receiver:
            return

        modifier = 0
        if sender.position > POSITION.SLEEP and not is_affected(sender, "charm") and sender.is_original():
            # Modificatore comportamentale per i mob, un valore tra -10 e 10
            if receiver and sender.race in receiver.reputations:
                modifier = receiver.reputations[sender.race] / 10  # (TD)
            if self.intention == INTENTION.FRIENDLY:
                modifier += 5
            elif self.intention == INTENTION.AGGRESSIVE:
                modifier -= 5

        # Caso peggiorativo
        if receiver and modifier <= -10:
            if random.randint(0, 5) == 0:
                interpret(sender, "say a %s Te la sei proprio [red]andata a cercare[close]!" % receiver.get_numbered_keyword(looker=sender))
            start_fight(receiver, sender)
        # Casi non buoni
        elif modifier <= -5 and self.intention == INTENTION.AGGRESSIVE:
            self.send_with_same_intention(sender, receiver)
        # Casi neutrali
        elif -5 < modifier < 5 and self.intention == INTENTION.NEUTRAL:
            # Qui è voluto che capitino casi buffi, come ad esempio se si
            # annuisce potrebbe darsi che di risposti ci si becchi una vomitata.
            # Se si vuole un mud full-rpg forse è bene ritornare al posto di
            # questa riga sottostante
            self.send_with_same_intention(sender, receiver)
        # Casi migliorativi
        elif modifier >= 5 and self.intention == INTENTION.FRIENDLY:
            self.send_with_same_intention(sender, receiver)
    #- Fine Funzione -

    def send_with_same_intention(self, sender, receiver=None):
        """
        Invia un social a caso con la stessa intenzione.
        Se receiver non è valido allora invia il social senza argomento.
        """
        if not sender:
            log.bug("sender non è un parametro valido: %r" % sender)
            return

        # -------------------------------------------------------------------------

        # Il più delle volte invia lo stesso social in questione, altrimenti ne
        # cerca uno con intenzione simile
        if random.randint(0, 5) != 0:
            social_input = self.get_input_argument()
            if receiver:
                receiver_numbered_keyword = receiver.get_numbered_keyword(looker=sender)
                argument = "%s %s" % (social_input, receiver_numbered_keyword)
            else:
                argument = social_input
            interpret(sender, argument)
            return

        # Se il mud è stato appena creato potrebbe non avere ancora i social
        if not database["socials"]:
            return

        # Crea una lista con tutti i social con l'intenzione voluta
        socials = []
        for social in database["socials"].itervalues():
            if social.intention == self.intention:
                socials.append(social)

        # Potrebbe benissimo essere che non esistano ancora abbastanza social
        # per averne uno con quell'intenzione
        if not socials:
            return

        # Invia un social scelto a caso tra quelli voluti
        social = random.choice(socials)
        argument = social.fun_name.split("_")[1]
        if receiver:
            argument += " %s" % receiver.get_numbered_keyword(looker=sender)

        interpret(sender, argument)
    #- Fine Funzione -


class SocialRacialMessage(object):
    """
    Classe per la gestione dei messaggi dei social che vengono differenziati
    a seconda della razza.
    """
    PRIMARY_KEY = "race"
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment       = ""  # Eventuale commento relativo ai social razziali
        self.race          = RACE.NONE
        self.entity_no_arg = ""
        self.others_no_arg = ""
        self.entity_found  = ""
        self.others_found  = ""
        self.target_found  = ""
        self.entity_auto   = ""
        self.others_auto   = ""
    #- Fine Inizializzazione -

    def get_error_message(self):
        if self.race.get_error_message(RACE, "race") != "":
            return self.race.get_error_message(RACE, "race")

        if not self.entity_no_arg:
            return "entity_no_arg non valido (razza %s)" % self.race
        if not self.others_no_arg:
            return "other_no_arg non valido (razza %s)" % self.race
        if not self.entity_found:
            return "entity_found non valido (razza %s)" % self.race
        if not self.others_found:
            return "other_found non valido (razza %s)" % self.race
        if not self.target_found:
            return "target_found non valido (razza %s)" % self.race
        if ((    self.entity_auto and not self.others_auto)
        or  (not self.entity_auto and     self.others_auto)):
            return "entity_auto e others_auto devono essere tutti i due pieni oppure vuoti (razza %s)" % self.race

        return ""
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def get_target_implicetely(player, target, target_code):
    """
    Questa serve per cercare l'entità target nella stanza se questa per caso
    non è stata passata.
    Ciò serve per ricavare implicitamente il mob target dei social: alcune
    volte i giocatori rispondono ad una richiesta di un mob con un social
    generico (smile), senza inserire l'argomento aggiuntivo che farebbe puntare
    il social al mob (smile onirik), in alcuni casi è accettabile supporre
    che il social sia stato implicitamente indirizzato al mob e quindi questa
    funzioncina cerca e ritorna il mob adatto.
    """
    if target:
        contains = (target, )
    else:
        contains = player.location.iter_contains()

    for mob in contains:
        if mob.IS_PLAYER and mob.code == target_code:
            return mob
        elif not mob.IS_PLAYER and mob.prototype.code == target_code:
            return mob

    return None
#- Fine Funzione -
