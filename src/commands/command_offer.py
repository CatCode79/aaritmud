# -*- coding: utf-8 -*-

"""
Comando che serve a vedere a quanto un mercante comprerebbe una certa entità
offerta dal giocatore.
"""

#= IMPORT ======================================================================

import math

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.enums      import OPTION, SHOP, TO
from src.gamescript import check_trigger
from src.log        import log
from src.utility    import one_argument, quantity_argument

from src.entitypes.money import pretty_money_value


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[gold]offrire[close]",
         "you2"       : "[gold]offrirti[close]",
         "you"        : "[gold]offri[close]",
         "it"         : "[gold]offre[close]",
         "it2"        : "[gold]offrergli[close]",
         "noun"       : "[gold]offerta[close]"}


#= FUNZIONI ====================================================================

def command_offer(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di vendere entità ai commercianti.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        for dealer in entity.location.iter_contains():
            if dealer.shop:
                break
        if SHOP.DISPENSER in dealer.shop.types:
            entity.act("Cerchi di %s qualcosa a $N ma ciò non è possibile perché quest'ultim$O è un distributore." % verbs["infinitive"], TO.ENTITY, dealer)
            entity.act("$n cerca di %s qualcosa a $N ma ciò non è possibile perché quest'ultim$O è un distributore." % verbs["infinitive"], TO.OTHERS, dealer)
            entity.act("$n cerca di %s qualcosa ma ciò non è possibile perché sei un distributore." % verbs["you2"], TO.TARGET, dealer, target)
            return False

        entity.send_output("Cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_offer")
            entity.send_output(syntax, break_line=False)
        return False

    # Ricava la quantità da offrire e poi l'eventuale valore facoltativo del negoziante
    quantity, argument = quantity_argument(argument)
    arg, argument = one_argument(argument)

    target = entity.find_entity(arg, quantity=quantity, location=entity)
    if not target:
        entity.act("Non trovi nessun [white]%s[close] da %s nel tuo inventario." % (arg, verbs["infinitive"]), TO.ENTITY)
        entity.act("$n sta cercando qualcosa senza trovarla" % verbs["infinitive"], TO.OTHERS)
        return False

    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Non puoi %s $N perché ne possiedi solo %d e non %d." % (verbs["infinitive"], target.quantity, quantity), TO.ENTITY, target)
        entity.act("$n sta cercando di ammucchiare un quantitativo voluto di $N per poterlo %s" % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n sta cercando di ammucchiarti per un quantitativo voluto per poterti %s" % verbs["infinitive"], TO.TARGET, target)
        return False

    if argument:
        dealer = entity.find_entity_extensively(argument)
        if not dealer:
            entity.act("Non trovi nessun negoziante chiamato [white]%s[close] a cui %s $N." % (argument, verbs["infinitive"]), TO.ENTITY, target)
            entity.act("$n sembra cercare qualcuno a cui %s $N." % verbs["infinitive"], TO.OTHERS, target)
            return False
        if not dealer.shop:
            entity.act("$N non sembra essere un negoziante a cui %s $a." % verbs["infinitive"], TO.ENTITY, dealer, target)
            entity.act("$n si accorge che $N non sembra essere un negoziante a cui %s $a." % verbs["infinitive"], TO.OTHERS, dealer, target)
            entity.act("$n si accorge che tu non sei un negoziante a cui %s $a." % verbs["infinitive"], TO.TARGET, dealer, target)
            return False
    else:
        for dealer in entity.location.iter_contains():
            if dealer.shop:
                break
        else:
            entity.act("Qui non trovi nessun negoziante a cui %s $N." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n non sembra trovare qualcuno a cui %s $N." % verbs["infinitive"], TO.OTHERS, target)
            return False

    # Controlla se il negoziante si trova in una locazione che fa, per lui, da negozio
    if not dealer.shop.in_location(dealer):
        entity.act("Non puoi %s nulla da $N se non si trova nel suo negozio." % verbs["infinitive"], TO.ENTITY, dealer)
        entity.act("$n non può %s nulla da $N se non si trova nel suo negozio." % verbs["infinitive"], TO.OTHERS, dealer)
        entity.act("$n non può %s nulla da te se non ti trovi nel tuo negozio." % verbs["infinitive"], TO.TARGET, dealer)
        return False

    # Indica che un'entità vuole interagire con il dealer
    if entity not in dealer.interactions:
        dealer.interactions.append(entity)

    if SHOP.DISPENSER in dealer.shop.types:
        entity.act("Cerchi di %s $a a $N ma ciò non è possibile perché quest'ultim$O è un distributore." % verbs["infinitive"], TO.ENTITY, dealer, target)
        entity.act("$n cerca di %s $a a $N ma ciò non è possibile perché quest'ultim$O è un distributore." % verbs["infinitive"], TO.OTHERS, dealer, target)
        entity.act("$n cerca di %s $a ma ciò non è possibile perché sei un distributore." % verbs["you2"], TO.TARGET, dealer, target)
        entity.act("$n cerca di %s a $N ma ciò non è possibile perché è un distributore." % verbs["you2"], TO.TARGET, target, dealer)
        return False

    sellable = dealer.shop.get_sellable(target)
    if not sellable:
        dealer.shop.send_uninterested_messages(entity, target, dealer)
        return False

    price = math.trunc((target.value * sellable.percent) / 100) * quantity
    if price <= 0:
        entity.act("$N guarda senza molto interesse $a: è senza valore!", TO.ENTITY, dealer, target)
        entity.act("$N guarda senza molto interesse $a mostrato da $n: è senza valore.", TO.OTHERS, dealer, target)
        entity.act("Guardi senza molto interesse $a mostrato da $n: è senza valore...", TO.TARGET, dealer, target)
        entity.act("$a ti guarda senza molto interesse: sei senza valore...", TO.TARGET, target, dealer)
        return False

    # Attenzione che qui target non è ancora la quantità giusta
    force_return = check_trigger(entity, "before_offer", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "before_offering", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_offered", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True

    pretty_price = pretty_money_value(price, extended=True)
    dealer.shop.send_offer_messages(entity, target, dealer, verbs, quantity, pretty_price)

    force_return = check_trigger(entity, "after_offer", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "after_offering", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_offered", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "sell <oggetto o creatura da comprare> (commerciante se più di uno nella stanza)\n"
#- Fine Funzione -
