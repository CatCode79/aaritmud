# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.enums import TO
from src.item  import Item

from src.commands.command_get import command_get


#= COSTANTI ====================================================================

PROTO_ITEM_CODES = [ "flora_item_moneta-00-seme",
                     "ikea_item_calze-ratto",
                     "ikea_item_biscotto"]


#= FUNZIONI ====================================================================

def before_buying(client, dealer, purchase, quantity, behavioured):
    # si vieta la vendita multipla anche se non si riesce ad inibire completamente
    # resta il pulsante e il messaggio quando mancano i danari.
    if quantity > 1:
        client.act("Non puoi acquistare più di $N alla volta..", TO.ENTITY, purchase)
        client.act("Tenta di saccheggiarti ma invano.", TO.TARGET, purchase)
        return True
    client.act("Giri la manovella poi ti chini per raccogliere la pallina erogata.", TO.ENTITY, purchase)
    client.act("Ti senti un po' più vuoto", TO.TARGET, purchase)
    client.act("$n si piega per raccogliere la pallina appena acquistata.", TO.OTHERS, purchase)
    return

def after_buying(client, dealer, purchase, quantity, behavioured):
    item = Item(random.choice(PROTO_ITEM_CODES))
    item.inject(purchase)
    purchase.value = 0
