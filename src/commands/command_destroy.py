# -*- coding: utf-8 -*-

"""
Comando che serve a distruggere gli oggetti.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.config     import config
from src.command    import get_command_syntax
from src.enums      import FLAG, OPTION, TO
from src.fight      import get_damage_verbs
from src.gamescript import check_trigger
from src.grammar    import grammar_gender
from src.interpret  import ActionInProgress, translate_input
from src.utility    import is_prefix, quantity_argument, one_argument, copy_existing_attributes

if config.reload_commands:
    reload(__import__("src.commands.command_attack", globals(), locals(), [""]))
from src.commands.command_attack import VERBS as ATTACK_VERBS


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[brown]distruggere[close]",
         "you2"       : "[brown]distruggerti[close]",
         "you"        : "[brown]distruggi[close]",
         "it"         : "[brown]distrugge[close]",
         "noun"       : "[brown]distruggerl%s[close]",
         "it"         : "[brown]distruggi[close]"}

VERBS2 = {"infinitive" : "[brown]rompere[close]",
          "you2"       : "[brown]romperti[close]",
          "you"        : "[brown]rompi[close]",
          "it"         : "[brown]rompe[close]",
          "noun"       : "[brown]romperl%s[close]",
          "it"         : "[brown]rompi[close]"}

DESTROY_SECONDS = 2.5


#= FUNZIONI ====================================================================

def command_destroy(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if entity.sended_inputs and is_prefix("romp", entity.sended_inputs[-1]):
        verbs = VERBS2

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_destroy")
            entity.send_output(syntax, destroy_line=False)
        return False

    # Solo gli oggetti animati possono utilizzare tale comando
    if entity.IS_ITEM and FLAG.CAN_DAMAGING not in entity.flags:
        entity.act("Non ti è possibile %s nulla di nulla.", TO.ENTITY)
        entity.act("$n sembra vibrare per un attimo... ma forse è stato un abbaglio.", TO.OTHERS)
        return False

    # Ricava l'eventuale quantità d'oggetti da raccogliere
    quantity, argument = quantity_argument(argument)
    arg, argument = one_argument(argument)

    target = entity.find_entity_extensively(arg, entity_tables=["items"], inventory_pos="first")
    if not target:
        target = entity.find_entity_extensively(arg, inventory_pos="first")
        if target:
            attack_translation = translate_input(entity, "attack", "en")
            javascript_code = '''javascript:parent.sendInput('%s %s');''' % (attack_translation, target.get_numbered_keyword(looker=entity))
            destroy_noun = verbs["noun"] % grammar_gender(target)
            attack_noun = ATTACK_VERBS["noun"] % grammar_gender(target)
            html_code = '''<a href="%s">%s</a>''' % (javascript_code, attack_noun)
            entity.act("$N non è un oggetto quindi non puoi %s, ma puoi sempre %s." % (destroy_noun, html_code), TO.ENTITY, target)
            entity.act("$n posa uno sguardo indagatore su $N.", TO.OTHERS, target)
            entity.act("$n posa uno sguardo indagatore su di te.", TO.TARGET, target)
        else:
            entity.act("Non riesci a trovare nessun [white]%s[close] da %s" % (arg, verbs["infinitive"]), TO.ENTITY)
            entity.act("$n cerca qualcosa che però non trova.", TO.OTHERS)
        return False

    # (TD) resistenza al comando se charmati

    # (TD) skill di forza bruta

    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Non puoi %s $N perché ve ne sono solo %d e non %d." % (verbs["infinitive"], target.quantity, quantity), TO.ENTITY, target)
        entity.act("$n sta cercando di ammucchiare un quantitativo voluto di $N per poterlo %s" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n sta cercando di ammucchiarti per un quantitativo voluto per %s" % ["you2"], TO.TARGET, target)
        return False

    # In questa maniera crea l'entità finale che verrà manipolata dai trigger
    # in maniera omogenea senza dover attendere la chiamata della from_location
    target = target.split_entity(quantity)

    force_return = check_trigger(entity, "before_destroy", entity, target, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_broken", entity, target, behavioured)
    if force_return:
        return True

    damage = damage_target(entity, target)
    index, dam_verb_you, dam_verb_it = get_destroy_verbs(damage)

    if target.life <= 0:
        end_destroy(entity, target, verbs, behavioured)
    else:
        messages = {
            "entity" : "%s $N." % dam_verb_you,
            "others" : "$n %s $N." % dam_verb_it,
            "target" : "$n ti %s." % dam_verb_it}
        send_destroy_messages(messages, "start_destroy", entity, target, verbs)
        if index != 0:
            entity.action_in_progress = ActionInProgress(DESTROY_SECONDS, continue_destroy, stop_destroy, entity, target, verbs, behavioured)

    return True
#- Fine Funzione -


def continue_destroy(entity, target, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    damage = damage_target(entity, target)
    index, dam_verb_you, dam_verb_it = get_destroy_verbs(damage)

    if target.life <= 0:
        end_destroy(entity, target, verbs, behavioured)
    else:
        messages = {
            "entity" : "%s $N." % dam_verb_you,
            "others" : "$n %s $N." % dam_verb_it,
            "target" : "$n ti %s." % dam_verb_it}
        send_destroy_messages(messages, "continue_destroy", entity, target, verbs, new_line=True)

        if index != 0:
            entity.action_in_progress = ActionInProgress(DESTROY_SECONDS, continue_destroy, stop_destroy, entity, target, verbs, behavioured)
#- Fine Funzione -


def end_destroy(entity, target, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    if target.quantity <= 1:
        messages = {
            "entity" : "%s $N." % color_first_upper(verbs["you"]),
            "others" : "$n %s $N." % verbs["it"],
            "target" : "$n ti %s." % verbs["it"]}
    else:
        messages = {
            "entity" : "%s $N, per un quantitativo di %d." % (color_first_upper(verbs["you"]), target.quantity),
            "others" : "$n %s $N, per un quantitativo di %d." % (verbs["it"], target.quantity),
            "target" : "$n ti %s, per un quantitativo di %d." % (verbs["it"], target.quantity)}
    send_destroy_messages(messages, "end_destroy", entity, target, verbs)

    target.dies(opponent=entity, quantity=target.quantity)

    # Il comando dona 1 punto xp per ogni oggetto distrutto, poca roba, ma
    # magari serve ad incoraggiare la pulizia da parte dei giocatori di entità
    # ormai inutili
    if entity.IS_PLAYER:
        reason = "per aver distrutto con successo %s" % target.get_name(looker=entity)
        entity.give_experience(1, reason=reason)

    force_return = check_trigger(entity, "after_destroy", entity, target, behavioured)
    if force_return:
        return
    force_return = check_trigger(target, "after_broken", entity, target, behavioured)
    if force_return:
        return
#- Fine Funzione -


def stop_destroy(entity, target, verbs, behavioured):
    """
    Funzione chiamata nel qual caso le deferLater vengano interrotte da un'altra
    azione interattiva dell'entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    messages = {
        "entity" : "Smetti di %s $N." % verbs["infinitive"],
        "others" : "$n smette di %s $N." % verbs["infinitive"],
        "target" : "$n smette di %s." % verbs["you2"]}
    send_destroy_messages(messages, "stop_destroy", entity, target, verbs)
#- Fine Funzione -


def damage_target(entity, target):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return 0

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return 0

    # -------------------------------------------------------------------------

    if target.material_percentages:
        material = target.material_percentages.get_major_material()
        if material.hardness == 100:
            damage = 0
        elif material.hardness == -1:
            # Non avere impostato l'hardness ad un materiale sarebbe visto
            # come errore, ma qui siamo un po' permissivi visto che la
            # distruzione di entità serve anche a ripulire la RAM del gioco.
            # Vista l'anomalia della cosa al posto di life utilizzo max_life
            # tanto per confondere un po' di più le cose :P
            damage = target.max_life
        elif target.life <= material.hardness:
            # In questa maniera gli oggetti piccoli, cioè con tanta life,
            # vengono distrutti in un round solo
            damage = target.life
        else:
            damage = target.max_life / material.hardness
            # Per un maggior realismo diminuisce il danno se il numero di
            # target è più di uno
            damage = damage / target.quantity

    # (TD) utilizzare la skill che provoca danni maggiorati

    if entity.IS_PLAYER:  dam_vs_item = config.dam_plr_vs_item
    elif entity.IS_MOB:   dam_vs_item = config.dam_mob_vs_item
    elif entity.IS_ITEM:  dam_vs_item = config.dam_item_vs_item
    if dam_vs_item != 100:
        damage = (damage * dam_vs_item) / 100

    target.life = max(0, target.life - damage)
    return damage
#- Fine Funzione -


def get_destroy_verbs(damage):
    if damage < 0:
        log.bug("damage non è un parametro valido: %d" % damage)
        return "", ""

    # -------------------------------------------------------------------------

    index, verb_you, verb_it = get_damage_verbs(damage)
    # Per il comando destroy formatta meglio il messaggio Manchi/manca
    if index == 0:
        return 0, "Non riesci a scalfire", "non riesce a scalfire"

    return index, verb_you, verb_it
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "destroy\n"
    syntax += "destroy <oggetto>\n"

    return syntax
#- Fine Funzione -


#= CLASSI ======================================================================

class Destroy(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.comment                 = ""  # Commento
        self.start_destroy_entity    = ""  # Messaggio inviato all'entità che sta iniziando a distruggere qualcosa
        self.start_destroy_others    = ""  # Messaggio inviato a tutti coloro che possono vedere l'azione dell'inizio della rottura
        self.start_destroy_target    = ""  # Messaggio inviato all'entità su cui si ha iniziato l'azione di distruggere
        self.continue_destroy_entity = ""  # Messaggio inviato all'entità mentre sta continuando a distruggere qualcosa
        self.continue_destroy_others = ""  # Messaggio inviato a tutti coloro che vedono l'azione continuativa della rottura
        self.continue_destroy_target = ""  # Messaggio inviato all'entità che sta venendo in continuazione rotta
        self.end_destroy_entity      = ""  # Messaggio inviato all'entità mentre sta continuando a distruggere qualcosa
        self.end_destroy_others      = ""  # Messaggio inviato a tutti coloro che vedono l'azione continuativa della rottura
        self.end_destroy_target      = ""  # Messaggio inviato all'entità che sta venendo in continuazione rotta
        self.stop_destroy_entity     = ""  # Messaggio inviato all'entità che ha fermato l'atto di distruggere qualcosa
        self.stop_destroy_others     = ""  # Messaggio inviato a tutti coloro che vedono l'entità fermarsi nell'atto di distruggere qualcosa
        self.stop_destroy_target     = ""  # Messaggio inviato all'entità su cui viene fermato l'atto di distruggerla
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        # Tutti i campi sono facoltativi, però se la struttura esiste
        # almeno uno è atteso
        if (not self.start_destroy_entity and not self.start_destroy_others and not self.start_destroy_target
        and not self.continue_destroy_entity and not self.continue_destroy_others and not self.continue_destroy_target
        and not self.end_destroy_entity and not self.end_destroy_others and not self.end_destroy_target
        and not self.stop_destroy_entity and not self.stop_destroy_others and not self.stop_destroy_target):
            return "Era atteso almeno un attributo valido."

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Destroy()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, destroy2):
        if not destroy2:
            return False

        if self.comment != destroy2.comment:
            return False
        if self.start_destroy_entity != destroy2.start_destroy_entity:
            return False
        if self.start_destroy_others != destroy2.start_destroy_others:
            return False
        if self.start_destroy_target != destroy2.start_destroy_target:
            return False
        if self.continue_destroy_entity != destroy2.continue_destroy_entity:
            return False
        if self.continue_destroy_others != destroy2.continue_destroy_others:
            return False
        if self.continue_destroy_target != destroy2.continue_destroy_target:
            return False
        if self.end_destroy_entity != destroy2.end_destroy_entity:
            return False
        if self.end_destroy_others != destroy2.end_destroy_others:
            return False
        if self.end_destroy_target != destroy2.end_destroy_target:
            return False
        if self.stop_destroy_entity != destroy2.stop_destroy_entity:
            return False
        if self.stop_destroy_others != destroy2.stop_destroy_others:
            return False
        if self.stop_destroy_target != destroy2.stop_destroy_target:
            return False

        return True
    #- Fine Inizializzazione -


def send_destroy_messages(messages, message_type, entity, target, verbs, new_line=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return

    # new_line ha valore di verità

    # -------------------------------------------------------------------------

    for to in (TO.ENTITY, TO.OTHERS, TO.TARGET):
        to_mini_code = to.get_mini_code()
        attr_name = message_type + "_" + to_mini_code
        if target.destroy and getattr(target.destroy, attr_name):
            message = getattr(target.destroy, attr_name)
            if "%verb_you2" in message:
                message = message.replace("%verb_you2", verbs["you2"])
            if "%verb_you" in message:
                # Questo replace deve trovarsi dopo quello di verb_you2
                message = message.replace("%verb_you", verbs["you"])
            if "%verb_it" in message:
                message = message.replace("%verb_it", verbs["it"])
            if "%verb" in message:
                message = message.replace("%verb", verbs["infinitive"])
        else:
            message = messages[to_mini_code]

        if new_line:
            entity.act("\n" + color_first_upper(message), to, target)
        else:
            entity.act(color_first_upper(message), to, target)
    if new_line:
        entity.send_prompt()
#- Fine Funzione -
