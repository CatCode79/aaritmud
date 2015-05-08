# -*- coding: utf-8 -*-

"""
Modulo per la gestione del comando che serve ad impugnare preferibilmente armi.
"""


#= IMPORT ======================================================================

from src.color        import color_first_upper
from src.command      import get_command_syntax
from src.element      import Flags
from src.enums        import FLAG, HAND, OPTION, PART, POSITION, ROOM, TO, TRUST, WEAPONFLAG
from src.gamescript   import check_trigger
from src.log          import log
from src.utility      import one_argument, is_number
from src.web_resource import create_tooltip


#= COSTANTI ====================================================================

VERBS = {"infinitive_min" : "impugnare",
         "infinitive"     : "impugnare nella $hand1",
         "infinitive_max" : "impugnare nella $hand1 e nella hand2",
         "you_min"        : "impugni",
         "you"            : "impugni nella $hand1",
         "you_max"        : "impugni nella $hand1 e nella hand2",
         "you2_min"       : "impugnarti",
         "you2"           : "impugnarti nella $hand1",
         "you2_max"       : "impugnarti nella $hand1 e nella hand2",
         "you3_min"       : "ti impugna",
         "you3"           : "ti impugna nella $hand1",
         "you3_max"       : "ti impugna nella $hand1 e nella hand2",
         "it_min"         : "impugna",
         "it"             : "impugna nella $hand1",
         "it_max"         : "impugna nella $hand1 e nella hand2",
         "self_min"       : "impugnarsi",
         "self"           : "impugnarsi nella $hand1",
         "self_max"       : "impugnarsi nella $hand1 e nella hand2",
         "participle"     : "impugnat$O"}

WIELD_VERBS = VERBS


#= FUNZIONI ====================================================================

def command_wield(entity, argument="", verbs=VERBS, behavioured=False, command_name="wield"):
    """
    Permette di prendere un oggetto nella mano secondaria o, se quest'ultima
    è occupata, in quella primaria.
    """
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    if command_name not in ("wield", "hold"):
        log.bug("command_name non è un parametro valido: %r" % command_name)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_wield")
            entity.send_output(syntax, break_line=False)
        return False

    # (TD) Controllo sul mental state dell'entità

    target = entity.find_entity(argument, location=entity)
    if not target:
        entity.act("Non riesci a trovare nessun [white]%s[close] da %s." % (argument, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sembra voler %s qualcosa che non trova." % verbs["infinitive"], TO.OTHERS)
        return False

    if target == entity:
        entity.act("Cerchi di %s da sol$o... impossibile!" % verbs["you2_min"], TO.ENTITY)
        entity.act("$n cerca di %s da sol$o... sarà dura!" % verbs["self_min"], TO.OTHERS)
        return False

    if FLAG.NO_HOLD in target.flags:
        if entity.trust >= TRUST.MASTER:
            entity.send_to_admin("Raccogli l'oggetto anche se è NO_HOLD")
        else:
            entity.act("Cerchi di $a $N... ma [darkgray]senza successo[close].", TO.ENTITY, target, verbs["infinitive"])
            entity.act("$n cerca di $a $N... [darkgray]senza successo[close].", TO.OTHERS, target, verbs["infinitive"])
            entity.act("\n$n cerca di $a... [darkgray]senza successo[close].", TO.TARGET, target, verbs["you"])
            return False

    if ((    entity.location.IS_ROOM and ROOM.NO_HOLD in entity.location.flags)
    or  (not entity.location.IS_ROOM and FLAG.NO_HOLD in entity.location.flags)):
        if entity.trust >= TRUST.MASTER:
            entity.send_to_admin("Raccogli l'oggetto anche se la stanza è NO_HOLD")
        else:
            entity.act("Cerchi di %s $N, tuttavia una [royalblue]forza misteriosa[close] del luogo l$o respinge." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, tuttavia una [royalblue]forza misteriosa[close] del luogo sembra respingerl$o." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("\n$n cerca di %s, tuttavia una [royalblue]forza misteriosa[close] del luogo sembra respingerl$o." % verbs["you2"], TO.TARGET, target)
            return False

    already_use_hold = entity.get_holded_entity()
    already_use_wield = entity.get_wielded_entity()
    if already_use_hold and already_use_wield:
        entity.act("Non puoi, hai tutte e due le $hands occupate per poter %s $N." % verbs["infinitive_min"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N ma ha tutte e due le $hands occupate." % verbs["infinitive_min"], TO.OTHERS, target)
        entity.act("\n$n cerca di %s ma ha tutte e due le $hands occupate." % verbs["you2_min"], TO.TARGET, target)
        return False

    # Si salva quali mani si stanno utilizzando per l'operazione
    if command_name == "wield":
        if already_use_wield:
            if already_use_wield.weapon_type and WEAPONFLAG.TWO_HANDS in already_use_wield.weapon_type.flags:
                hands = [HAND.RIGHT, HAND.LEFT]
            else:
                if entity.IS_ITEM:
                    hands = [HAND.RIGHT]
                else:
                    hands = [entity.hand.reverse]
        else:
            if entity.IS_ITEM:
                hands = [HAND.LEFT]
            else:
                hands = [entity.hand]
    else:
        if already_use_hold:
            if already_use_hold.weapon_type and WEAPONFLAG.TWO_HANDS in already_use_hold.weapon_type.flags:
                hands = [HAND.RIGHT, HAND.LEFT]
            else:
                if entity.IS_ITEM:
                    hands = [HAND.LEFT]
                else:
                    hands = [entity.hand]
        else:
            if entity.IS_ITEM:
                hands = [HAND.RIGHT]
            else:
                hands = [entity.hand.reverse]

    # Raccoglie i dati per una successiva gestione generica dei due comandi
    if command_name == "wield":
        first_hand_to_use = "$hand1"
        second_hand_to_use = "$hand2"
        already_use_check = already_use_wield
        already_use_flag = PART.HOLD
        normal_flag = PART.WIELD
        if target.level > entity.level:
            tooltip = create_tooltip(entity.get_conn(), "Ciò significa che il suo livello è troppo alto rispetto al tuo", "{?}")
            entity.act("Senti che non potrai usufruire al meglio del danno di $N. %s" % tooltip, TO.ENTITY, target)
            entity.act("$n non si sente a suo agio con in mano $N.", TO.OTHERS, target)
            entity.act("$n non si sente a suo agio con te in mano.", TO.TARGET, target)
    else:
        first_hand_to_use = "$hand2"
        second_hand_to_use = "$hand1"
        already_use_check = already_use_hold
        already_use_flag = PART.WIELD
        normal_flag = PART.HOLD

    # Gestione delle armi a due mani
    if command_name == "wield" and target.weapon_type and WEAPONFLAG.TWO_HANDS in target.weapon_type.flags and (already_use_hold or already_use_wield):
        entity.act("Non puoi, devi avere tutte e due le $hands libere per poter %s $N." % WIELD_VERBS["infinitive_min"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N ma non ha tutte e due le $hands libere." % WIELD_VERBS["infinitive_min"], TO.OTHERS, target)
        entity.act("\n$n cerca di %s ma non ha tutte e due le $hands libere." % WIELD_VERBS["you2_min"], TO.TARGET, target)
        return False
    if len(hands) == 2:
        entity.act("Non puoi, hai tutte e due le $hands occupate per poter %s $N." % WIELD_VERBS["infinitive_min"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N ma ha tutte e due le $hands occupate." % WIELD_VERBS["infinitive_min"], TO.OTHERS, target)
        entity.act("\n$n cerca di %s ma ha tutte e due le $hands occupate." % WIELD_VERBS["you2_min"], TO.TARGET, target)
        return False

    force_return = check_trigger(entity, "before_" + command_name, entity, target, hands, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_" + command_name + "ed", entity, target, hands, behavioured)
    if force_return:
        return True

    # Gli oggetti non hanno le mani, quindi utilizzano dei verbi non specifici
    if entity.IS_ITEM:
        entity.act("%s $N." % (color_first_upper(verbs["you_min"])), TO.ENTITY, target)
        entity.act("$n %s $N." % (verbs["it_min"]), TO.OTHERS, target)
        entity.act("\n$n %s" % (verbs["you3_min"]), TO.TARGET, target)
        if already_use_check:
            target.wear_mode = Flags(already_use_flag)
        else:
            target.wear_mode = Flags(normal_flag)
    elif target.weapon_type and WEAPONFLAG.TWO_HANDS in target.weapon_type.flags:
        entity.act("%s $N con tutte e due le $hands." % color_first_upper(verbs["you_min"]), TO.ENTITY, target)
        entity.act("$n %s $N con tutte e due le $hands." % verbs["it_min"], TO.OTHERS, target)
        entity.act("\n$n %s con tutte e due le $hands," % verbs["you3_min"], TO.TARGET, target)
        target.wear_mode = Flags(normal_flag, already_use_flag)
    elif already_use_check:
        entity.act("Cerchi di %s con la %s $N ma essendo già occupata utilizzi la %s." % (
            verbs["infinitive_min"], first_hand_to_use, second_hand_to_use), TO.ENTITY, target)
        entity.act("$n cerca di %s $N con la %s ma essendo già occupata utilizza la %s." % (
            verbs["infinitive_min"], first_hand_to_use, second_hand_to_use), TO.OTHERS, target)
        entity.act("\n$n cerca di %s con la %s ma essendo già occupata utilizza la %s." % (
            verbs["you2_min"], first_hand_to_use, second_hand_to_use), TO.TARGET, target)
        target.wear_mode = Flags(already_use_flag)
    else:
        entity.act("%s $N con la %s." % (color_first_upper(verbs["you_min"]), first_hand_to_use), TO.ENTITY, target)
        entity.act("$n %s $N con la %s." % (verbs["it_min"], first_hand_to_use), TO.OTHERS, target)
        entity.act("\n$n %s con la %s" % (verbs["you3_min"], first_hand_to_use), TO.TARGET, target)
        target.wear_mode = Flags(normal_flag)

    for affect in target.affects:
        affect.apply()

    # Poiché l'entità è stata impugnata forse ha un valore nel gioco e non
    # verrà quindi purificata
    if target.deferred_purification:
        target.stop_purification()

    # Serve a cambiare il wear mode dell'oggetto allo stato originario
    if target.repop_later:
        target.deferred_repop = target.repop_later.defer_check_status()

    force_return = check_trigger(entity, "after_" + command_name, entity, target, hands, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_" + command_name + "ed", entity, target, hands, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "wield <nome arma o oggetto>\n"
#- Fine Funzione -
