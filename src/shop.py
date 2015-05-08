# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei negozianti.
"""

#= IMPORT ======================================================================

import math

from src.color    import color_first_upper
from src.database import fread_number, fread_percent
from src.element  import Element, Flags
from src.enums    import ENTITYPE, RACE, SHOP, TO
from src.log      import log
from src.utility  import (copy_existing_attributes, is_same, is_prefix,
                          number_argument, multiple_arguments)


#= CLASSI ======================================================================

class Shop(object):
    """
    Classe che gestisce tutte le informazioni di un negoziante.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {"buyables"  : ("src.shop", "Buyable"),
                   "sellables" : ("src.shop", "Sellable")}
    REFERENCES  = {"proto_locations" : ["proto_rooms", "proto_mobs", "proto_items"],
                   "proto_storages"  : ["proto_rooms", "proto_mobs", "proto_items"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment                      = ""  # Commento relativo la struttura
        self.types                        = Flags(SHOP.NONE)  # Tipologia/e di shop, se non impostata viene considerato un negozio qualsiasi
        self.proto_locations              = []  # Prototipo delle locazioni in cui l'entità negozierà, se non ne viene indicata nessuna il negoziante è un venditore ambulante
        self.proto_storages               = []  # Prototipo delle locazioni da cui l'entità prenderà la mercanzia da vendere
        self.buyables                     = []  # Entità comprabili da parte di un giocatore e relative informazioni di magazzino
        self.sellables                    = []  # Tipologie di entità vendibili da parte del giocatore, se non viene impostata allora si potrà vendere qualsiasi cosa
        self.entity_buy_message           = ""  # Messaggi di act relativi al comando buy avvenuto, sono messaggi facoltativi
        self.others_buy_message           = ""
        self.target_buy_message           = ""
        self.dealer_buy_message           = ""
        self.entity_cannot_afford_message = ""  # Messaggi di act relativi al comando buy se non si hanno i soldi necessari, sono messaggi facoltativi
        self.others_cannot_afford_message = ""
        self.target_cannot_afford_message = ""
        self.dealer_cannot_afford_message = ""
        self.entity_sell_message          = ""  # Messaggi di act relativi al comando sell avvenuto, sono messaggi facoltativi
        self.others_sell_message          = ""
        self.target_sell_message          = ""
        self.dealer_sell_message          = ""
        self.entity_offer_message         = ""  # Messaggi di act relativi al comando offer avvenuto, sono messaggi facoltativi
        self.others_offer_message         = ""
        self.target_offer_message         = ""
        self.dealer_offer_message         = ""
        self.entity_uninterested_message  = ""  # Messaggi di act relativi al disinteresse del mercante per un determinata entità offerta o venduta, sono messaggi facoltativi
        self.others_uninterested_message  = ""
        self.target_uninterested_message  = ""
        self.dealer_uninterested_message  = ""
    #- Fine Inizializzazione -

    def get_error_message(self):
        if self.types.get_error_message(SHOP, "types") != "":
            return self.types.get_error_message(SHOP, "types")
        elif self.get_error_message_buyables() != "":
            return self.get_error_message_buyables()
        elif self.get_error_message_sellables() != "":
            return self.get_error_message_sellables()

        return ""
    #- Fine Metodo -

    def get_error_message_buyables(self):
        if not self.buyables:
            return "buyables non è stata impostata"

        for buyable in self.buyables:
            if buyable.get_error_message() != "":
                return buyable.get_error_message()

        return ""
    #- Fine Metodo -

    def get_error_message_sellables(self):
        for sellable in self.sellables:
            if sellable.entitype == ENTITYPE.NONE:
                if len(self.sellables) > 1:
                    return "Quando si esplicita il valore di ENTITYPE.NONE in un sellable deve essere il solo e unico."

        for sellable in self.sellables:
            if sellable.get_error_message() != "":
                return sellable.get_error_message()

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Shop()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, shop2):
        if not shop2:
            return False

        if self.comment != shop2.comment:
            return False
        if self.types != shop2.types:
            return False

        for location in self.proto_locations:
            for location2 in shop2.proto_locations:
                if location == location2:
                    break
            else:
                return False

        for storage in self.proto_storages:
            for storage2 in shop2.proto_storages:
                if storage == storage2:
                    break
            else:
                return False

        if len(self.buyables) != len(shop2.buyables):
            return False
        for buyable in self.buyables:
            for buyable2 in shop2.buyables:
                if buyable.equals(buyable2):
                    break
            else:
                return False

        if len(self.sellables) != len(shop2.sellables):
            return False
        for sellable in self.sellables:
            for sellable2 in shop2.sellables:
                if sellable.equals(sellable2):
                    break
            else:
                return False

        if self.entity_buy_message           != shop2.entity_buy_message:           return False
        if self.others_buy_message           != shop2.others_buy_message:           return False
        if self.target_buy_message           != shop2.target_buy_message:           return False
        if self.dealer_buy_message           != shop2.dealer_buy_message:           return False
        if self.entity_cannot_afford_message != shop2.entity_cannot_afford_message: return False
        if self.others_cannot_afford_message != shop2.others_cannot_afford_message: return False
        if self.target_cannot_afford_message != shop2.target_cannot_afford_message: return False
        if self.dealer_cannot_afford_message != shop2.dealer_cannot_afford_message: return False
        if self.entity_sell_message          != shop2.entity_sell_message:          return False
        if self.others_sell_message          != shop2.others_sell_message:          return False
        if self.target_sell_message          != shop2.target_sell_message:          return False
        if self.dealer_sell_message          != shop2.dealer_sell_message:          return False
        if self.entity_offer_message         != shop2.entity_offer_message:         return False
        if self.others_offer_message         != shop2.others_offer_message:         return False
        if self.target_offer_message         != shop2.target_offer_message:         return False
        if self.dealer_offer_message         != shop2.dealer_offer_message:         return False
        if self.entity_uninterested_message  != shop2.entity_uninterested_message:  return False
        if self.others_uninterested_message  != shop2.others_uninterested_message:  return False
        if self.target_uninterested_message  != shop2.target_uninterested_message:  return False
        if self.dealer_uninterested_message  != shop2.dealer_uninterested_message:  return False

        return True
    #- Fine Metodo -

    def in_location(self, dealer):
        """
        Controlla se possa interagire nel luogo in cui si trova.
        """
        if not dealer:
            log.bug("dealer non è un parametro valido: %s" % dealer)
            return 0

        # ---------------------------------------------------------------------

        if not self.proto_locations:
            return True

        if dealer.location.prototype in self.proto_locations:
            return True

        return False
    #- Fine Metodo -

    def get_storage(self, dealer):
        """
        Ritorna il luogo in cui vengono inserite le cose da vendere, il magazzino.
        """
        if not dealer:
            log.bug("dealer non è un parametro valido: %s" % dealer)
            return 0

        # ---------------------------------------------------------------------

        if not self.proto_storages:
            return dealer

        # Da priorità al dealer e alla locazione nel qual caso vi siano
        # più storages tutti nella stessa stanza
        if dealer.prototype in self.proto_storages:
            return dealer
        if dealer.location.prototype in self.proto_storages:
            return dealer.location

        for en in dealer.iter_contains():
            if en.IS_PLAYER:
                continue
            if en.prototype in self.proto_storages:
                return en

        for en in dealer.location.iter_contains():
            if en.IS_PLAYER:
                continue
            if en.prototype in self.proto_storages:
                return en

        # Adesso invece cerca tra le stanze dell'area
        for room in dealer.location.area.rooms.values():
            if room.prototype in self.proto_storages:
                return room

        return None
    #- Fine Metodo -

    def get_buyable(self, purchase):
        """
        Ritorna la struttura di buyable relativa alla mercanzia passata.
        """
        if not purchase:
            log.bug("purchase non è un parametro valido: %s" % purchase)
            return None

        # ---------------------------------------------------------------------

        for buyable in self.buyables:
            if purchase.prototype == buyable.proto_entity:
                return buyable

        return None
    #- Fine Metodo -

    def get_sellable(self, target):
        """
        Ritorna il sellable del negoziante relativo all'entità passata, se
        possibile.
        """
        if not self.sellables:
            return None

        # Se viene impostato esplicitamente ENTITYPE.NONE allora accetta di
        # far vendere qualsiasi cosa al negoziante
        for sellable in self.sellables:
            if sellable.entitype == ENTITYPE.NONE:
                return sellable

        for sellable in self.sellables:
            if sellable.entitype == target.entitype:
                return sellable

        return None
    #- Fine Metodo -

    def storage_is_empty(self, storage):
        """
        Ritorna verso se il magazzino passato non ha mercanzia da vendere.
        """
        if not storage:
            log.bug("storage non è un parametro valido: %r" % storage)
            return False

        # ---------------------------------------------------------------------

        for en in storage.iter_contains():
            for buyable in self.buyables:
                if en.prototype == buyable.proto_entity:
                    return False

        return True
    #- Fine Metodo -

    def add_buyable(self, dealer, target, sellable, quantity):
        """
        Aggiunge una nuova entità comprabile al negoziante ma senza che questa
        abbia futura possibilità di aggiornare il proprio magazzino.
        """
        if not dealer:
            log.bug("dealer non è un parametro valido: %s" % dealer)
            return

        if not target:
            log.bug("target non è un parametro valido: %s" % target)
            return

        if not sellable:
            log.bug("sellable non è un parametro valido: %s" % sellable)
            return

        if quantity <= 0:
            log.bug("quantity non può essere minore o uguale a 0: %d" % quantity)
            return

        # ---------------------------------------------------------------------

        # Se non c'è nessun magazzino in cui inserire l'entità allora esce
        storage = self.get_storage(dealer)
        if not storage:
            target.extract()
            return

        if not storage.IS_ROOM and not storage.can_carry_target(target, quantity=quantity):
            target.extract()
            return

        # Crea un buyable e lo aggiunge alla lista delle mercanzie del negozio
        buyable              = Buyable()
        buyable.proto_entity = target.prototype
        buyable.percent      = sellable.buyback_percent

        self.buyables.append(buyable)
    #- Fine Metodo -

    def send_buy_messages(self, entity, purchase, dealer, verbs, quantity, pretty_price, discount):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not purchase:
            log.bug("purchase non è un parametro valido: %r" % purchase)
            return

        if not dealer:
            log.bug("dealer non è un parametro valido: %r" % dealer)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        if not pretty_price:
            log.bug("pretty_price non è un parametro valido: %r" % pretty_price)
            return

        if discount < 0:
            log.bug("discount non è un parametro valido: %d" % discount)
            return

        # ---------------------------------------------------------------------

        is_dispenser = SHOP.DISPENSER in dealer.shop.types

        discount_descr = ""
        if discount > 0:
            discount_descr = " scontato"

        quantity_descr = ""
        if quantity > 1:
            quantity_descr = "%d " % quantity

        if self.entity_buy_message:
            message = self.entity_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["you"]))
                else:
                    message = message.replace("%verb", verbs["you"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            if is_dispenser:
                message = "%s %s$N da $a inserendovi %s." % (color_first_upper(verbs["you"]), quantity_descr, pretty_price)
            else:
                message = "%s %s$N da $a pagandol$O %s%s." % (color_first_upper(verbs["you"]), quantity_descr, pretty_price, discount_descr)
        entity.act(message, TO.ENTITY, purchase, dealer)

        if self.others_buy_message:
            message = self.others_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            if is_dispenser:
                message = "$n %s %s$N da $a inserendovi %s." % (verbs["it"], quantity_descr, pretty_price)
            else:
                message = "$n %s %s$N da $a pagandol$O %s%s." % (verbs["it"], quantity_descr, pretty_price, discount_descr)
        entity.act(message, TO.OTHERS, purchase, dealer)

        if self.target_buy_message:
            message = self.target_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            if is_dispenser:
                message = "$n ti %s da $a inserendovi %s." % (verbs["it"], pretty_price)
            else:
                message = "$n ti %s da $a pagandoti %s%s." % (verbs["it"], pretty_price, discount_descr)
        entity.act(message, TO.TARGET, purchase, dealer)

        if self.dealer_buy_message:
            message = self.dealer_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            if is_dispenser:
                message = "$n ti %s %s$N inserendoti %s." % (verbs["it"], quantity_descr, pretty_price)
            else:
                message = "$n ti %s %s$N pagandol$O %s%s." % (verbs["it"], quantity_descr, pretty_price, discount_descr)
        entity.act(message, TO.TARGET, dealer, purchase)
    #- Fine Metodo -

    def send_cannot_afford_messages(self, entity, purchase, dealer, verbs, quantity, pretty_price):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        if not purchase:
            log.bug("purchase non è un parametro valido: %r" % purchase)
            return

        if not dealer:
            log.bug("dealer non è un parametro valido: %r" % dealer)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r" % verbs)
            return

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        if not pretty_price:
            log.bug("pretty_price non è un parametro valido: %r" % pretty_price)
            return

        # ---------------------------------------------------------------------

        quantity_descr = ""
        if quantity > 1:
            quantity_descr = "%d " % quantity

        if self.entity_cannot_afford_message:
            message = self.entity_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["infinitive"]))
                else:
                    message = message.replace("%verb", verbs["infinitive"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            message = "Non hai abbastanza soldi per poter %s %s$N da $a: costa %s." % (verbs["infinitive"], quantity_descr, pretty_price)
        entity.act(message, TO.ENTITY, purchase, dealer)

        if self.others_cannot_afford_message:
            message = self.others_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["infinitive"]))
                else:
                    message = message.replace("%verb", verbs["infinitive"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            message = "$n non sembra avere abbastanza soldi per poter %s %s$N." % (verbs["infinitive"], quantity_descr)
        entity.act(message, TO.OTHERS, purchase, dealer)

        if self.target_cannot_afford_message:
            message = self.target_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["infinitive"]))
                else:
                    message = message.replace("%verb", verbs["infinitive"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            message = "$n non ha abbastanza soldi per poterti %s da $a." % verbs["infinitive"]
        entity.act(message, TO.TARGET, purchase, dealer)

        if self.dealer_cannot_afford_message:
            message = self.dealer_buy_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["infinitive"]))
                else:
                    message = message.replace("%verb", verbs["infinitive"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        else:
            message = "$n non ha abbastanza soldi per poter %s %s$a da te." % (verbs["infinitive"], quantity_descr)
        entity.act(message, TO.TARGET, dealer, purchase)
    #- Fine Metodo -

    def send_sell_messages(self, entity, target, dealer, verbs, quantity, pretty_price):
        if not entity:
            log.bug("entity non è un parametro valido: %r", entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r", target)
            return

        if not dealer:
            log.bug("dealer non è un parametro valido: %r", dealer)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r", verbs)
            return

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        if not pretty_price:
            log.bug("pretty_price non è un parametro valido: %r", pretty_price)
            return

        # ---------------------------------------------------------------------

        quantity_descr = ""
        if quantity > 1:
            quantity_descr = "%d " % quantity

        if self.entity_sell_message:
            message = self.entity_sell_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["you"]))
                else:
                    message = message.replace("%verb", verbs["you"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        elif quantity <= 1:
            message = "%s $a a $N per %s." % (color_first_upper(verbs["you"]), pretty_price)
        else:
            message = "%s $N, in %d unità, a $a per %s." % (color_first_upper(verbs["you"]))
        entity.act(message, TO.ENTITY, target, dealer)

        if self.others_sell_message:
            message = self.entity_sell_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        elif quantity <= 1:
            message = "$n %s $N a $a per %s." % (verbs["it"], pretty_price)
        else:
            message = "$n %s $N, in %d unità, a $a per %s." % (verbs["it"], quantity, pretty_price)
        entity.act(message, TO.OTHERS, target, dealer)

        if target != entity:
            if self.target_sell_message:
                message = self.entity_sell_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message.replace("%verb", color_first_upper(verbs["it"]))
                    else:
                        message = message.replace("%verb", verbs["it"].lower())
                if "%quantity" in message:
                    message = message.replace("%quantity", quantity_descr)
                if "%price" in message:
                    message = message.replace("%price", pretty_price)
            elif quantity <= 1:
                message = "$n ti %s $N per %s." % (verbs["it"], pretty_price)
            else:
                message = "$n ti %s $N, in %d unità, per %s." % (verbs["it"], quantity, pretty_price)
            entity.act(message, TO.TARGET, target, dealer)

        if dealer != entity:
            if self.dealer_sell_message:
                message = self.entity_sell_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message.replace("%verb", color_first_upper(verbs["it"]))
                    else:
                        message = message.replace("%verb", verbs["it"].lower())
                if "%quantity" in message:
                    message = message.replace("%quantity", quantity_descr)
                if "%price" in message:
                    message = message.replace("%price", pretty_price)
            elif quantity <= 1:
                message = "$n ti %s a $N per %s." % (verbs["it"], pretty_price)
            else:
                message = "$n ti %s a $N, in %d unità, per %s." % (verbs["it"], quantity, pretty_price)
            entity.act(message, TO.TARGET, dealer, target)
    #- Fine Metodo -

    def send_offer_messages(self, entity, target, dealer, verbs, quantity, pretty_price):
        if not entity:
            log.bug("entity non è un parametro valido: %r", entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r", target)
            return

        if not dealer:
            log.bug("dealer non è un parametro valido: %r", dealer)
            return

        if not verbs:
            log.bug("verbs non è un parametro valido: %r", verbs)
            return

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        if not pretty_price:
            log.bug("pretty_price non è un parametro valido: %r", pretty_price)
            return

        # ---------------------------------------------------------------------

        quantity_descr = ""
        if quantity > 1:
            quantity_descr = "%d " % quantity

        if self.entity_offer_message:
            message = self.entity_offer_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        elif quantity <= 1:
            message = "$N ti %s %s per $N." % (verbs["it"], pretty_price)
        else:
            message = "$N ti %s %s per %d unità di $N." % (verbs["it"], pretty_price, quantity)
        entity.act(message, TO.ENTITY, target, dealer)

        if self.others_offer_message:
            message = self.entity_offer_message
            if "%verb" in message:
                if message.startswith("%verb"):
                    message = message.replace("%verb", color_first_upper(verbs["it"]))
                else:
                    message = message.replace("%verb", verbs["it"].lower())
            if "%quantity" in message:
                message = message.replace("%quantity", quantity_descr)
            if "%price" in message:
                message = message.replace("%price", pretty_price)
        elif quantity <= 1:
            message = "$N %s %s a $n per $N." % (verbs["it"], pretty_price)
        else:
            message = "$N %s %s a $n per %d unità di $N." % (verbs["it"], pretty_price, quantity)
        entity.act(message, TO.OTHERS, target, dealer)

        if target != entity:
            if self.target_offer_message:
                message = self.entity_offer_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message.replace("%verb", color_first_upper(verbs["you"]))
                    else:
                        message = message.replace("%verb", verbs["you"].lower())
                if "%quantity" in message:
                    message = message.replace("%quantity", quantity_descr)
                if "%price" in message:
                    message = message.replace("%price", pretty_price)
            elif quantity <= 1:
                message = "%s a $n %s per $N." % (color_first_upper(verbs["you"]), pretty_price)
            else:
                message = "%s a $n %s per %d unità di $N." % (color_first_upper(verbs["you"], quantity), pretty_price)
            entity.act(message, TO.TARGET, target, dealer)

        if dealer != entity:
            if self.dealer_offer_message:
                message = self.entity_offer_message
                if "%verb" in message:
                    if message.startswith("%verb"):
                        message = message.replace("%verb", color_first_upper(verbs["it"]))
                    else:
                        message = message.replace("%verb", verbs["it"].lower())
                if "%quantity" in message:
                    message = message.replace("%quantity", quantity_descr)
                if "%price" in message:
                    message = message.replace("%price", pretty_price)
            elif quantity <= 1:
                message = "$a %s a $n %s per te." % (verbs["it"], pretty_price)
            else:
                message = "$a %s a $n %s per %d unità di te." % (verbs["it"], pretty_price, quantity)
            entity.act(message, TO.TARGET, dealer, target)
    #- Fine Metodo -

    def send_uninterested_messages(self, entity, target, dealer):
        if not entity:
            log.bug("entity non è un parametro valido: %r", entity)
            return

        if not target:
            log.bug("target non è un parametro valido: %r", target)
            return

        if not dealer:
            log.bug("dealer non è un parametro valido: %r", dealer)
            return

        # ---------------------------------------------------------------------

        if self.entity_uninterested_message:
            entity.act(self.entity_uninterested_message, TO.ENTITY, target, dealer)
        else:
            entity.act("$N non è una tipologia che a $a possa interessare.", TO.ENTITY, target, dealer)

        if self.others_uninterested_message:
            entity.act(self.others_uninterested_message, TO.OTHERS, target, dealer)
        else:
            entity.act("$N di $n non è una tipologia che a $a possa interessare.", TO.OTHERS, target, dealer)

        if self.target_uninterested_message:
            entity.act(self.target_uninterested_message, TO.TARGET, target, dealer)
        else:
            entity.act("Non sei una tipologia che a $a possa interessare.", TO.TARGET, target, dealer)

        if self.dealer_uninterested_message:
            entity.act(self.dealer_uninterested_message, TO.TARGET, dealer, target)
        else:
            entity.act("Non sei interessato a $a di $n, non è simile alla tua mercanzia.", TO.TARGET, dealer, target)
    #- Fine Metodo -


class Buyable(object):
    """
    Classe che gestisce tutte le entità vendute da parte di un negoziante,
    le relative quantità in magazzino e il tempo di rifornimento delle stesse.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"percent" : ("", "percent")}
    REFERENCES  = {"proto_entity" : ["proto_items", "proto_mobs"]}
    WEAKREFS    = {}

    def __init__(self):
        self.proto_entity      = ""  # Codice prototipo dell'entità messa in commercio
        self.percent           = 100 # 
        self.supply_minutes    = 0   # Minuti reali prima di rinnovare il magazzino, se 0 non rifornisce il proprio magazzino, se -1 imposta come valore il repop_time dell'area
        self.discount_percent  = 0   # Sconto eventualmente applicato (opzionale)
        self.discount_quantity = 0   # Se l'entità compra almeno questo quantitativo verrà applicato uno sconto (opzionale)
    #- Fine Metodo -

    def get_error_message(self):
        if not self.proto_entity:
            return "proto_entity non è un valore valido: %r" % self.proto_entity
        elif self.percent < 10 and self.percent > 1000:
            return "percent dev'essere un valore tra 10 e 1000 compresi: %d" % self.percent
        elif self.supply_minutes < -1:
            return "supply_minutes non può essere un valore minore di -1: %d" % self.supply_minutes
        elif self.discount_percent != 0 and (self.discount_percent < 1 or self.discount_percent > 100):
            return "discount_percent dev'essere un valore tra 1 e 100 compresi e non %d" % self.discount_percent
        elif self.discount_quantity != 0 and self.discount_quantity < 2:
            return "discount_quantity non può essere un valore minore di 2: %d" % self.discount_quantity

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Buyable()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, buyable2):
        if not buyable2:
            return False

        if self.proto_entity != buyable2.proto_entity:
            return False
        if self.percent != buyable2.percent:
            return False
        if self.supply_minutes != buyable2.supply_minutes:
            return False
        if self.discount_percent != buyable2.discount_percent:
            return False
        if self.discount_quantity != buyable2.discount_quantity:
            return False

        return True
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        try:
            proto_code, percent, supply_minutes, discount_percent, discount_quantity = line.split(None, 4)
        except ValueError:
            try:
                proto_code, percent, supply_minutes = line.split(None, 2)
            except ValueError:
                log.bug("Errore nella lettura di un Buyable nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                    file.name, line, attr))
                return
            else:
                discount_percent  = "0%"
                discount_quantity = "0"
        else:
            discount_percent  = discount_percent.lstrip("(")
            discount_quantity = discount_quantity.rstrip(")")

        self.proto_entity      = proto_code
        self.percent           = fread_percent(file, percent, attr)
        self.supply_minutes    = fread_number(file, supply_minutes, attr)
        self.discount_percent  = fread_percent(file, discount_percent, attr)
        self.discount_quantity = fread_number(file, discount_quantity, attr)
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        discount = ""
        if self.has_discount():
            discount = " (%d%% %d)" % (self.discount_percent, self.discount_quantity)

        file.write("%s%s %s %s%% %d %s\n" % (indentation, label, self.proto_entity.code, self.percent, self.supply_minutes, discount))
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def has_discount(self):
        if self.discount_percent != 0 and self.discount_quantity != 0:
            return True
        else:
            return False
    #- Fine Metodo -

    def get_price(self, purchase, quantity=1):
        if not purchase:
            log.bug("purchase non è un parametro valido: %r" % purchase)
            return 0, 0

        if quantity < 1:
            log.bug("quantity passato non è un parametro valido: %d" % quantity)
            return 0, 0

        # ---------------------------------------------------------------------

        total = purchase.value
        # Un'entità costa anche per un totale di tutte quelle che contiene
        for en in purchase.iter_all_entities():
            total += en.value * en.quantity

        if total == 0:
            return 0, 0

        single_price = (total * self.percent) / 100
        single_discount = 0
        if self.has_discount() and quantity >= self.discount_quantity:
            single_discount = (single_price * self.discount_percent) / 100

        price = math.trunc(single_price) * quantity
        discount = math.trunc(single_discount) * quantity

        return price - discount, discount
    #- Fine Metodo -


class Sellable(object):
    """
    Classe che gestisce le differenti tipologie di entità vendute e comprate
    dal negoziante.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"percent"         : ("", "percent"),
                   "buyback_percent" : ("", "percent")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.entitype        = Element(ENTITYPE.NONE)  # Tipologia di entità che possono essere venduta al negoziante
        self.percent         =  50 # Percentuale sul costo per le entità vendute al negoziante
        self.buyback_percent = 100 # Percentuale sul costo per le entità comprate dal negoziante e precedentemente vendutegli
    #- Fine Metodo -

    def get_error_message(self):
        if self.entitype.get_error_message(ENTITYPE, "entitype") != "":
            return self.entitypes.get_error_message(ENTITYPE, "entitype")
        elif self.buyback_percent < 10 and self.buyback_percent > 1000:
            return "buyback_percent dev'essere un valore tra 10 e 1000: %d" % self.buyback_percent
        elif self.percent < 10 and self.percent > 1000:
            return "percent dev'essere un valore tra 10 e 1000: %d" % self.percent

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Sellable()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, sellable2):
        if not sellable2:
            return False

        if self.entitype != sellable2.entitype:
            return False
        if self.percent != sellable2.percent:
            return False
        if self.buyback_percent != sellable2.buyback_percent:
            return False

        return True
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        try:
            entitype, percent, buyback_percent = line.split(None, 2)
        except ValueError:
            log.bug("Errore nella lettura di un Sellable nel file <%s> per la linea <%s> e l'attributo <%s>" % (
                file.name, line, attr))
            return

        self.entitype        = Element(entitype)
        self.percent         = fread_percent(file, percent, attr)
        self.buyback_percent = fread_percent(file, buyback_percent, attr)
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        file.write("%s%s %r %d%% %d%%\n" % (indentation, label, self.entitype, self.percent, self.buyback_percent))
    #- Fine Metodo -
