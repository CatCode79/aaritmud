# -*- coding: utf-8 -*-

"""
Modulo del comando buy, che serve a comprare qualche cosa da un negoziante.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.enums      import OPTION, SHOP, TO
from src.gamescript import check_trigger
from src.grammar    import grammar_gender
from src.log        import log
from src.utility    import one_argument, quantity_argument

from src.entitypes.money import pretty_money_value, can_afford, give_moneys


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[yellow]comprare[close]",
         "noun"       : "[yellow]comprarlo[close]",
         "you2"       : "[yellow]comprarti[close]",
         "you"        : "[yellow]compri[close]",
         "it"         : "[yellow]compra[close]"}


#= FUNZIONI ====================================================================

# (TD) manca del codice per la gestione delle mascotte
# (TD) se la mascotte ha un livello maggiore del giocatore allora diminuirgli
# le stats ed avvisare il giocatore
def command_buy(entity, argument="", verbs=VERBS, behavioured=False):
    """
    Permette di comprare entità da un commerciante.
    """
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_buy")
            entity.send_output(syntax, break_line=False)
        return False

    # Ricava la quantità di entità da comprare
    quantity, argument = quantity_argument(argument)
    arg, argument = one_argument(argument)

    # Cerca specificatamente il negoziante con l'argomento passato
    if argument:
        dealer = entity.find_entity_extensively(argument, quantity=quantity)
        if not dealer:
            entity.act("Non trovi nessun negoziante chiamato [white]%s[close]." % argument, TO.ENTITY)
            entity.act("$n sembra cercare qualcuno da cui %s qualcosa." % verbs["infinitive"], TO.OTHERS)
            return False
        if not dealer.shop:
            entity.act("$N non sembra essere un negoziante da cui %s qualcosa." % verbs["infinitive"], TO.ENTITY, dealer)
            entity.act("$n si accorge che $N non è un negoziante da cui %s qualcosa." % verbs["infinitive"], TO.OTHERS, dealer)
            entity.act("$n si accorge che tu non sei un negoziante da cui %s qualcosa." % verbs["infinitive"], TO.TARGET, dealer)
            return False
    # Altrimenti cerca il primo negoziante che si trova nella locazione del giocatore
    else:
        for dealer in entity.location.iter_contains():
            if dealer.shop:
                break
        else:
            entity.act("Qui non trovi nessun [white]negoziante[close].", TO.ENTITY)
            entity.act("$n non sembra trovare qualcuno da cui %s qualcosa." % verbs["infinitive"], TO.OTHERS)
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

    # Ricava il magazzino del negoziante
    storage = dealer.shop.get_storage(dealer)
    if not storage:
        if dealer.shop.proto_storages and dealer.shop.proto_storages[0].IS_MOB:
            from_where = "da chi"
        else:
            from_where = "da dove"
        entity.act("Non puoi %s nulla da $N perché non ha %s prendere la mercanzia!" % (verbs["infinitive"], from_where), TO.ENTITY, dealer)
        entity.act("$n non può %s nulla da $N perché non ha %s prendere la mercanzia!" % (verbs["infinitive"], from_where), TO.OTHERS, dealer)
        entity.act("$n non può %s nulla perché non hai %s prendere la mercanzia!" % (verbs["you2"], from_where), TO.TARGET, dealer)
        return False

    # Cerca l'oggetto voluto nel magazzino del negoziante
    target = dealer.find_entity(arg, location=storage)
    if not target:
        descr = ""
        if SHOP.DISPENSER in dealer.shop.types:
            descr = "tra i prodotti esposti nel distributore"
        else:
            descr = "nella mercanzia esposta"
        entity.act("Non trovi nessun [white]%s[close] %s." % (arg, descr), TO.ENTITY, dealer)
        entity.act("$n non trova tra gli oggetti esposti da $N una [white]cosa[close] in particolare.", TO.OTHERS, dealer)
        entity.act("$n non trova tra i tuoi oggetti esposti una [white]cosa[close] in particolare.", TO.TARGET, dealer)
        return False

    if quantity != 1 and SHOP.DISPENSER in dealer.shop.types:
        entity.act("Non riesci in alcuni modo a %s %d quantità di $a da $N." % verbs["infinitive"], TO.ENTITY, dealer, target)
        entity.act("$n non riesce in alcun modo a %s $a in quantità maggiore di una da $N." % verbs["infinitive"], TO.OTHERS, dealer, target)
        entity.act("$n non riesce in alcun modo a %s $a in quantità maggiore di una da te." % verbs["infinitive"], TO.TARGET, dealer, target)
        entity.act("$n non riesce in alcun modo a %s in quantità maggiore di una da $a." % verbs["you2"], TO.TARGET, target, dealer)
        return False

    # Controlla se in magazzino vi sia la quantità voluta dell'oggetto da comprare
    if quantity == 0:
        quantity = target.quantity
    elif target.quantity < quantity:
        entity.act("Puoi %s solo %d quantità di $N da $a, riprova più tardi." % (verbs["infinitive"], target.quantity), TO.ENTITY, target, dealer)
        entity.act("$n può %s solo %d quantità di $N da $a." % (verbs["infinitive"], target.quantity), TO.OTHERS, target, dealer)
        entity.act("$n può %s da $a solo in %d quantità." % (verbs["you2"], target.quantity), TO.TARGET, target, dealer)
        entity.act("$n può %s $a da te solo in %d quantità." % (verbs["infinitive"], target.quantity), TO.TARGET, dealer, target)
        return False

    buyable = dealer.shop.get_buyable(target)
    if not buyable:
        entity.act("Ti accorgi che $N non è nel listino delle cose possibili da %s." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n si accorge che $N non è nel listino delle cose possibili da %s." % verbs["infinitive"], TO.OTHERS, target)
        entity.act("$n si accorge che non sei nel listino delle cose possibili da %s." % verbs["infinitive"], TO.TARGET, target)
        return False

    price, discount = buyable.get_price(target, quantity=quantity)
    pretty_price = pretty_money_value(price, extended=True)

    # Controlla se il giocatore possa comprare un determinato articolo
    if not can_afford(target.value * quantity, entity, race=dealer.race):
        dealer.shop.send_cannot_afford_messages(entity, target, dealer, verbs, quantity, pretty_price)
        return False

    # Controlla se il giocatore può portare il peso dell'oggetto con sé
    if not entity.can_carry_target(target, quantity=quantity):
        if quantity <= 1:
            entity.act("$N è troppo pesante perché tu possa portarl$O assieme alle tue cose.", TO.ENTITY, target, dealer)
            entity.act("$N è troppo pesante perché $n lo possa portare assieme alle sue cose.", TO.OTHERS, target, dealer)
            entity.act("Sei troppo pesante perché $n ti possa portare assieme alle sue cose.", TO.TARGET, target, dealer)
            # l'act TO.OTHERS fa da 4° messaggio per dealer
        else:
            plural = grammar_gender(target, masculine="i", feminine="e")
            entity.act("%d $N sono troppo pesanti perché tu possa portarl%s assieme alle tue cose." % (quantity, plural), TO.ENTITY, target, dealer)  # (GR) plurare di $N
            entity.act("%d $N sono troppo pesanti perché $n l%s possa portare assieme alle sue cose." % (quantity, plural), TO.OTHERS, target, dealer)  # (GR) plurare di $N
            entity.act("Siete troppo pesanti perché $n vi possa portare assieme alle sue cose.", TO.TARGET, target, dealer)
            # l'act TO.OTHERS fa da 4° messaggio per dealer
        return False

    force_return = check_trigger(entity, "before_buy", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "before_buying", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_bought", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True

    dealer.shop.send_buy_messages(entity, target, dealer, verbs, quantity, pretty_price, discount)

    give_moneys(entity, dealer, price, race=dealer.race)
    target = target.from_location(quantity)
    target.to_location(entity)

    # Dona un po' di esperienza ai giocatori che hanno comprato per la prima
    # volta l'entità
    if entity.IS_PLAYER:
        if target.prototype.code in entity.bought_entities:
            entity.bought_entities[target.prototype.code] += 1
        else:
            entity.bought_entities[target.prototype.code] = 1
            reason = "per aver comprato per la prima volta %s" % target.get_name(looker=entity)
            entity.give_experience(target.level*10, reason=reason)

    force_return = check_trigger(entity, "after_buy", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "after_buying", entity, dealer, target, quantity, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_bought", entity, dealer, target, quantity, behavioured)
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

    syntax += "buy <oggetto o creatura da comprare>\n"
    syntax += "buy <quantità da comprare> <oggetto o creatura da comprare>\n"
    syntax += "buy <oggetto o creatura da comprare> (commerciante se più di uno nella stanza)\n"
    return syntax
#- Fine Funzione -
