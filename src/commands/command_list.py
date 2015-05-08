# -*- coding: utf-8 -*-

"""
Modulo del comando list, che serve a visualizzare la lista delle entità
comprabili di un negoziante.
"""

#= IMPORT ======================================================================

from src.color        import remove_colors
from src.enums        import SHOP, TO
from src.database     import database
from src.find_entity  import INSTANCE
from src.gamescript   import check_trigger
from src.interpret    import translate_input
from src.log          import log
from src.utility      import one_argument
from src.web_resource import create_tooltip, create_icon

from src.entitypes.money import pretty_money_icons, pretty_money_value


#= FUNZIONI ====================================================================

def command_list(entity, argument="", behavioured=False):
    """
    Permette di comprare entità da un commerciante.
    """
    # Può essere normale se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if argument:
        dealer = entity.find_entity_extensively(argument)
        if not dealer:
            entity.act("Non trovi nessun negoziante chiamato [white]%s[close]." % argument, TO.ENTITY)
            entity.act("$n sembra cercare qualcuno un negoziante.", TO.OTHERS)
            return False
        if not dealer.shop:
            entity.act("$N non sembra essere un negoziante.", TO.ENTITY, dealer)
            entity.act("$n crede erroneamente che $N sia un negoziante.", TO.OTHERS, dealer)
            entity.act("$n crede erroneamente che tu sia un negoziante.", TO.TARGET, dealer)
            return False
    # Altrimenti cerca il primo negoziante che si trova nella locazione del giocatore
    else:
        for dealer in entity.location.iter_contains():
            if dealer.shop:
                break
        else:
            entity.act("Qui non trovi nessun [white]negoziante[close].", TO.ENTITY)
            entity.act("$n non sembra trovare nessun negoziante qui intorno.", TO.OTHERS)
            return False

    in_location = dealer.shop.in_location(dealer)
    if not in_location and SHOP.DISPENSER not in dealer.shop.types:
        entity.act("$N non ti mostra la merce perché non si trova nel suo negozio.", TO.ENTITY, dealer)
        entity.act("$N non mostra la merce a $n perché non si trova nel suo negozio.", TO.OTHERS, dealer)
        entity.act("Non mostri la tua merce a $n perché non ti trovi nel tuo negozio.", TO.TARGET, dealer)
        return False

    # Indica che un'entità vuole interagire con il dealer
    if entity not in dealer.interactions:
        dealer.interactions.append(entity)

    storage = dealer.shop.get_storage(dealer)
    if not storage:
        if dealer.shop.proto_storages and dealer.shop.proto_storages[0].IS_MOB:
            from_where = "da chi"
        else:
            from_where = "da dove"
        entity.act("Non puoi avere la lista da $N perché non ha %s prendere la mercanzia!" % from_where, TO.ENTITY, dealer)
        entity.act("$n non può avere la lista da $N perché non ha %s prendere la mercanzia!" % from_where, TO.OTHERS, dealer)
        entity.act("$n non può avere la lista perché non hai %s prendere la mercanzia!" % from_where, TO.TARGET, dealer)
        return False

    if not dealer.shop.buyables:
        entity.send_output("%s non possiede nessuna mercanzia" % dealer.get_name(looker=entity))
        log.bug("Non è stato trovato nessun buyable impostato per %s" % dealer.code)
        return False

    # Controlla se il magazzino contiene almeno un oggetto comprabile dall'utente
    if dealer.shop.storage_is_empty(storage):
        entity.act("Ti accorgi che il negozio non possiede mercanzia, meglio tornare più tardi, dopo il rifornimento.", TO.ENTITY, dealer)
        entity.act("$n si accorge che il negozio non possiede mercanzia.", TO.OTHERS, dealer)
        entity.act("$n si accorge che il tuo negozio non possiede mercanzia.", TO.TARGET, dealer)
        return False

    force_return = check_trigger(entity, "before_list", entity, dealer, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "before_listed", entity, dealer, behavioured)
    if force_return:
        return True

    if SHOP.DISPENSER in dealer.shop.types:
        if not in_location:
            entity.act("Leggi su di una targetta la lista delle mercanzie di $N anche se non si trova nel suo negozio.", TO.OTHERS, dealer)
            entity.act("$n legge su di una targetta la lista delle mercanzie di $N anche se non si trova nel suo negozio.", TO.OTHERS, dealer)
            entity.act("$n legge la tua targetta con la lista delle mercanzie anche se non si trova nel suo negozio.", TO.TARGET, dealer)
        else:
            entity.act("Leggi su di una targetta la lista delle mercanzie di $N.", TO.OTHERS, dealer)
            entity.act("$n legge su di una targetta la lista delle mercanzie di $N.", TO.OTHERS, dealer)
            entity.act("$n legge la tua targetta con la lista delle mercanzie.", TO.TARGET, dealer)
    else:
        entity.act("Chiedi la lista delle mercanzie di $N.", TO.OTHERS, dealer)
        entity.act("$n chiede la lista delle mercanzie di $N.", TO.OTHERS, dealer)
        entity.act("$n ti chiede la lista delle mercanzie.", TO.TARGET, dealer)

    discount_exist = False
    for buyable in dealer.shop.buyables:
        if buyable.has_discount():
            discount_exist = True

    buy_translation = translate_input(entity, "buy", "en")
    rows = []
    rows.append('''<table class="mud">''')
    discount_cell = ""
    if SHOP.DISPENSER in dealer.shop.types:
        name_cell = "Prodotti"
    else:
        name_cell = "Mercanzia"
    if discount_exist:
        discount_cell = '''<th>Sconto</th>'''
    rows.append('''<tr><th></th><th>%s</th><th colspan="4">Prezzo</th><th>Livello</th><th></th><th></th>%s</tr>''' % (
        name_cell, discount_cell))
    for en in storage.get_list_of_entities(entity):
        en = en[INSTANCE]
        for buyable in dealer.shop.buyables:
            if en.prototype != buyable.proto_entity:
                continue

            # Purtroppo però il sistema di mucchio visivo non permetterà di
            # visualizzare quantità superiori ad 1 per oggetti di long uguali
            # tra loro, la quantità si deve per forza basare sul mucchio fisico
            quantity = 10
            if buyable.has_discount():
                quantity = buyable.discount_quantity
            if en.quantity < quantity:
                quantity = en.quantity

            name = en.get_name(looker=entity)
            single_price, dummy_discount = buyable.get_price(en, quantity=1)
            block_price, dummy_discount = buyable.get_price(en, quantity=quantity)
            mithril, gold, silver, copper = pretty_money_icons(single_price)
            rows.append('''<tr><td>%s</td>''' % create_icon(en.get_icon(), add_span=False))
            rows.append('''<td>%s </td>''' % create_tooltip(entity.get_conn(), en.get_descr(looker=entity), name))
            rows.append('''<td align="right">%s</td>''' % mithril)
            rows.append('''<td align="right">%s</td>''' % gold)
            rows.append('''<td align="right">%s</td>''' % silver)
            rows.append('''<td align="right">%s</td>''' % copper)
            rows.append('''<td align="center">%d</td>''' % en.level)
            rows.append('''<td><input type="submit" value="%s" onclick="sendInput('%s 1 %s')" title="Comprerai %s per un prezzo di %s"/></td>''' % (
                buy_translation.capitalize(),
                buy_translation,
                en.get_numbered_keyword(looker=entity),
                remove_colors(name),
                remove_colors(pretty_money_value(single_price))))
            rows.append('''<td><input type="submit" value="%s x %d" onclick="sendInput('%s %d %s')" title="Comprerai %d unità di %s per un prezzo di %s"/></td>''' % (
                buy_translation.capitalize(),
                quantity,
                buy_translation,
                quantity,
                en.get_numbered_keyword(looker=entity),
                quantity,
                remove_colors(name),
                remove_colors(pretty_money_value(block_price))))
            if discount_exist:
                if buyable.has_discount():
                    rows.append('''<td align="center">%d%% per quantità maggiori di %d</td>''' % (buyable.discount_percent, buyable.discount_quantity))
                else:
                    rows.append('''<td align="center">Nessuno</td>''')
            rows.append('''</tr>''')
    rows.append('''</table>''')
    entity.send_output("".join(rows), break_line=False)

    force_return = check_trigger(entity, "after_list", entity, dealer, behavioured)
    if force_return:
        return True
    force_return = check_trigger(dealer, "after_listed", entity, dealer, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax  = "list\n"
    syntax += "list <commerciante se più di uno nella stanza>\n"

    return syntax
#- Fine Funzione -
