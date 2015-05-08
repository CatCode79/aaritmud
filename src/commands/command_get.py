# -*- coding: utf-8 -*-

"""
Permette di raccogliere un oggetto o prenderlo da un contenitore.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.enums      import CONTAINER, DOOR, FLAG, OPTION, ROOM, TO, TRUST
from src.grammar    import grammar_gender
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import (one_argument, reverse_one_argument, quantity_argument,
                            is_same, is_prefix, is_number)

from src.entitypes.corpse import CORPSE_DESCRS

if config.reload_commands:
    reload(__import__("src.commands.command_open", globals(), locals(), [""]))
from src.commands.command_open import command_open


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[orange]prendere[close]",
         "noun"       : "[orange]prenderlo[close]",
         "you"        : "[orange]prendi[close]",
         "you2"       : "[orange]prenderti[close]",
         "self"       : "[orange]prendersi[close]",
         "it"         : "[orange]prende[close]"}

VERBS2 = {"infinitive" : "[brown]raccogliere[close]",
          "noun"       : "[brown]raccoglierlo[close]",
          "you"        : "[brown]raccogli[close]",
          "you2"       : "[brown]raccoglierti[close]",
          "self"       : "[orange]raccogliersi[close]",
          "it"         : "[brown]raccoglie[close]"}


#= FUNZIONI ====================================================================

def command_get(entity, argument="", verbs=VERBS, behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    # (TD) Fare altrimenti il passaggio d'argomento verboso per il get e take,
    # creando il command_take?
    if entity.sended_inputs and is_prefix("racco", entity.sended_inputs[-1]):
        verbs = VERBS2

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_get")
            entity.send_output(syntax, break_line=False)
        return False

    original_argument = argument

    # Ricava l'eventuale quantità d'oggetti da raccogliere
    quantity, argument = quantity_argument(argument)
    arg1, argument = one_argument(argument)

    # (TD) Controllo sul mental state dell'entità

    # Rimuove l'eventuali parole opzionali
    from_descr = ""
    if argument and is_prefix(argument, ("da ", "from ")):
        from_descr = "da"
        dummy_arg2, argument = one_argument(argument)

    if argument:
        location = entity.find_entity_extensively(argument, quantity=quantity)
        # (TD) sperimentale, utilizzarlo in altri comandi se va bene
        # Qui si cerca di risolvere il parsing di un eventuale argomento di
        # questo tipo: prendi camicia a tunica cassa
        if not location:
            arg1, argument = reverse_one_argument(original_argument)
            if is_number(arg1):
                quantity = int(arg1)
                arg1, argument = one_argument(argument)
            location = entity.find_entity_extensively(argument, quantity=quantity)
        if not from_descr:
            from_descr = "su"  # (bb)
    else:
        location = entity.location
        if entity.location.IS_ROOM:
            if not from_descr:
                from_descr = "in"
        else:
            if not from_descr:
                from_descr = "da"

    if not location or (location.is_secret_door() and argument and len(argument) < config.min_secret_arg_len):
        entity.act("Non riesci a trovare nessun [white]%s[close] da cui %s [white]%s[close]." % (argument, verbs["infinitive"], arg1), TO.ENTITY)
        entity.act("$n sta cercando di %s qualcosa dentro qualcos'altro, ma senza molto successo." % verbs["infinitive"], TO.OTHERS)
        return False

    if not location.IS_ROOM and location.container_type and CONTAINER.CLOSED in location.container_type.flags:
        execution_result = False
        if entity.IS_PLAYER and entity.account and OPTION.AUTO_OPEN in entity.account.options:
            execution_result = command_open(entity, location.get_numbered_keyword(looker=entity))
        if not execution_result:
            entity.act("Cerchi di %s %s da $N ma l$O trovi chius$O." % (verbs["infinitive"], arg1), TO.ENTITY, location)
            entity.act("$n cerca di %s %s da $N ma l$O trova chius$O." % (verbs["infinitive"], arg1), TO.OTHERS, location)
            entity.act("$n cerca di %s %s ma ti trova chius$O." % (verbs["you2"], arg1), TO.TARGET, location)
            return False

    if argument:
        avoid_equipment = True
        if location.IS_ITEM:
            avoid_equipment = False
        target = entity.find_entity(arg1, location=location, avoid_equipment=avoid_equipment)
    else:
        target = entity.find_entity_extensively(arg1, inventory_pos="last")

    if ((location.IS_ACTOR and not location.container_type and entity.location != location)
    or (not target and location.IS_ITEM and not location.container_type)
    or (target and location.IS_ITEM and not location.container_type and len(target.wear_mode) <= 0)):
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Anche se non è un contenitore lo puoi manipolare comunque")
        else:
            entity.act("Non riesci a %s %s da $N." % (verbs["infinitive"], arg1), TO.ENTITY, location)
            entity.act("Non riesce a %s nulla da $N." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("Non riesce a %s nulla da te." % verbs["infinitive"], TO.TARGET, location)
            return False

    if not target or (target.is_secret_door() and len(arg1) < config.min_secret_arg_len):
        if location.IS_ROOM:
            entity.act("Non riesci a trovare nessun [white]%s[close] da %s." % (arg1, verbs["infinitive"]), TO.ENTITY)
            entity.act("$n sta cercando qualcosa, ma senza molto successo.", TO.OTHERS)
        else:
            entity.act("Non riesci a trovare nessun [white]%s[close] da %s %s $N." % (arg1, verbs["infinitive"], from_descr), TO.ENTITY, location)
            entity.act("$n sta cercando qualcosa dentro $N, ma senza molto successo.", TO.OTHERS, location)
        return False

    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Non puoi %s $N perché ve ne sono solo %d e non %d." % (verbs["infinitive"], target.quantity, quantity), TO.ENTITY, target)
        entity.act("$n sta cercando di ammucchiare un quantitativo voluto di $N per poterlo %s" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n sta cercando di ammucchiarti per un quantitativo voluto per poterti %s" % verbs["infinitive"], TO.TARGET, target)
        return False

    # Di default si raccoglie da terra
    if not location:
        location = entity.location

    force_return = check_trigger(target, "before_try_to_get", entity, target, location, behavioured)
    if force_return:
        return True

    if target == entity:
        entity.act("Cerchi di %s da sol$o... impossibile!" % verbs["you2"], TO.ENTITY)
        entity.act("$n cerca di %s da sol$o... sarà dura che ce la faccia!" % verbs["self"], TO.OTHERS)
        return False

    if target.location == entity:
        entity.act("Cerchi di %s $N ma ti accorgi di averl$O già con te." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s $N ma si accorge di averl$O già con sé." % verbs["infinitive"], TO.OTHERS, target)
        return False

    # Controlla che il peso ((TD) e lo spazio) attualmente trasportato dall'entità
    # permetta o meno il get
    # (TD) il bard aveva anche il can_carry_number
    if not entity.can_carry_target(target, quantity=quantity):
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Riesci comunque a %s %s anche se è troppo pesante per te." % (
                verbs["infinitive"], target.get_name(entity)))
        else:
            entity.act("Non puoi %s $N, non riesci a portare con te tutto quel peso." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n non può %s $N, non riesce a portare con sé tutto quel peso." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n non può %s, non riesce a portare con sé tutto il tuo peso." % verbs["you2"], TO.TARGET, target)
            return False

    # Evita di far rubare a meno che non ci si trovi proprio nell'inventario della vittima
    if location.IS_PLAYER and location != entity.location:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli da un giocatore anche se non potresti")
        else:
            entity.act("Cerchi di %s qualcosa da $a, ma ti fermi prima di compiere un [gray]furto[close]." % verbs["infinitive"], TO.ENTITY, target, location)
            entity.act("$n cerca di %s qualcosa da $N, tuttavia si ferma prima di compiere un [gray]furto[close]." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("\n$n cerca di %s qualcosa da $a, ma si ferma prima di compiere un [gray]furto[close]." % verbs["you2"], TO.TARGET, target, location)
            entity.act("\n$n cerca di %s qualcosa, tuttavia si ferma prima di compiere un [gray]furto[close]." % verbs["you2"], TO.TARGET, location, target)
            return False

    # Se non è passato del tempo il cadavere non è lootabile
    if target.corpse_type and target.corpse_type.was_player and target.corpse_type.decomposition_rpg_hours <= len(CORPSE_DESCRS):
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli da un cadavere di giocatore anche se non potresti")
        else:
            entity.act("Cerchi di %s qualcosa da $a, ma ti fermi prima di compiere un [gray]furto[close]." % verbs["infinitive"], TO.ENTITY, target, location)
            entity.act("$n cerca di %s qualcosa da $N, tuttavia si ferma prima di compiere un [gray]furto[close]." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("\n$n cerca di %s qualcosa da $a, ma si ferma prima di compiere un [gray]furto[close]." % verbs["you2"], TO.TARGET, target, location)
            entity.act("\n$n cerca di %s qualcosa, tuttavia si ferma prima di compiere un [gray]furto[close]." % verbs["you2"], TO.TARGET, location, target)
            return False

    if FLAG.NO_GET in target.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli l'oggetto anche se è NO_GET")
        else:
            entity.act("Cerchi di $a $N... ma [darkgray]senza successo[close].", TO.ENTITY, target, verbs["infinitive"])
            entity.act("$n cerca di $a $N... [darkgray]senza successo[close].", TO.OTHERS, target, verbs["infinitive"])
            entity.act("$n cerca di $a... [darkgray]senza successo[close].", TO.TARGET, target, verbs["you2"])
            if not location.IS_ROOM:
                entity.act("$n cerca di $a $N da te... [darkgray]senza successo[close].", TO.TARGET, target, verbs["infinitive"])
            return False

    if location.IS_ROOM and ROOM.NO_GET in location.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli l'oggetto anche se la stanza è NO_GET")
        else:
            entity.act("Cerchi di %s $N, tuttavia una [royalblue]forza misteriosa[close] del luogo respinge la tua $hand." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, tuttavia una [royalblue]forza misteriosa[close] del luogo sembra respingere la sua $hand." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("\n$n cerca di %s, tuttavia una [royalblue]forza misteriosa[close] del luogo sembra respingere la sua $hand." % verbs["you2"], TO.TARGET, target)
            return False

    if not location.IS_ROOM and location == entity.location and len(target.wear_mode) > 0:
        entity.act("Stai per %s $N svestendo $a, ma poi ti fermi, non è proprio il caso." % verbs["infinitive"], TO.ENTITY, target, location)
        entity.act("$ sembra voler %s $N svestendo $a, ma poi si ferma." % verbs["infinitive"], TO.OTHERS, target, location)
        entity.act("$n sembra voler %s $N da te, ma poi si ferma." % verbs["infinitive"], TO.TARGET, target, location)
        return False

    if FLAG.BURIED in target.flags:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli l'oggetto anche se è BURIED rimuovendo tale flag")
        else:
            log.bug("Oggetto buried gettabile da un giocatore senza trust: %s" % target.code)
            return False

    # Ricava l'attributo corretto
    if target.IS_PLAYER:
        if entity.trust > TRUST.PLAYER:
            entity.send_to_admin("Raccogli il giocatore anche se non potresti")
        else:
            entity.act("Cerchi di %s $N, ma ti fermi per [indianred]rispetto[close] nei suoi confronti." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n cerca di %s $N, tuttavia si ferma per [indianred]rispetto[close] nei suoi confronti." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("\n$n cerca di %s, tuttavia si ferma per [indianred]rispetto[close] nei tuoi confronti." % verbs["you2"], TO.TARGET, target)
            if not location.IS_ROOM:
                entity.act("$n cerca di %s $a da te, tuttavia si ferma per [indianred]rispetto[close] nei tuoi e suoi confronti." % verbs["infinitive"], TO.TARGET, location, target)
            return False

    # Nel caso l'oggetto era addosso ad un altro oggetto (è meglio tenere
    # queste righe di codice prima del check del trigger before_get visto
    # che a volte negli script vengono modificate le flag di wear)
    if len(target.wear_mode) > 0:
        target.wear_mode.clear()
        target.under_weared = None

    # In questa maniera crea l'entità finale che verrà manipolata dai trigger
    # in maniera omogenea senza dover attendere la chiamata della from_location
    target = target.split_entity(quantity)

    force_return = check_trigger(entity, "before_get", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_getted", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "before_get_from_location", entity, target, location, behavioured)
    if force_return:
        return True

    if quantity <= 1:
        entity.act("%s $N da $a." % color_first_upper(verbs["you"]), TO.ENTITY, target, location)
        entity.act("$n %s $N da $a." % verbs["it"], TO.OTHERS, target, location)
        entity.act("$n ti %s da $a." % verbs["it"], TO.TARGET, target, location)
    else:
        entity.act("%s $N, per una quantità di %d, da $a." % (color_first_upper(verbs["you"]), quantity), TO.ENTITY, target, location)
        entity.act("$n %s $N, per una quantità di %d, da $a." % (verbs["it"], quantity), TO.OTHERS, target, location)
        entity.act("$n ti %s, per una quantità di %d, da $a." % (verbs["it"], quantity), TO.TARGET, target, location)
    if not location.IS_ROOM:
        entity.act("$n ti %s qualcosa." % verbs["it"], TO.TARGET, location)

    target = target.from_location(quantity)
    target.to_location(entity)

    # Nel caso sia un seme e fosse stato un admin a gettarlo:
    target.flags -= FLAG.BURIED
    # (TT) forse questo pezzo di codice andrebbe meglio in from_location
    if target.seed_type:
        target.seed_type.stop_growth()
    if target.plant_type:
        target.plant_type.stop_growth()

    # Se il comando get è stato eseguito tramite un behaviour allora l'oggetto
    # raccolto ha una probabilità di essere purificato, queste righe di codice
    # devono trovarsi DOPO la chiamata alla to_location, che esegue una pulizia
    # della deferred relativa alla purificazione
    if behavioured:
        target.start_purification(config.purification_rpg_hours)

    force_return = check_trigger(entity, "after_get", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_getted", entity, target, location, behavioured)
    if force_return:
        return True
    force_return = check_trigger(location, "after_get_from_location", entity, target, location, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "get <nome oggetto o creatura>\n"
    syntax += "get <nome oggetto o creatura> <nome contenitore>\n"

    return syntax
#- Fine Funzione -
