# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle monete.
"""


#= IMPORT ======================================================================

import math
import random

from src.config  import config
from src.element import Flags
from src.enums   import ENTITYPE, RACE
from src.log     import log
from src.utility import copy_existing_attributes, commafy


#= CLASSI ======================================================================

class Money(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, title=""):
        self.comment      = ""
        self.copper_value = 0
        self.races        = Flags(RACE.NONE)
    #- Fine Inizializzazione -

    def __str__(self):
        r = "<"
        if self.comment:
            r += "C "
        r += "%d" % self.copper_value
        if self.races:
            return " %s" % self.races
        r += ">"

        return r
    #- Fine Metodo -

    def get_error_message(self, entity):
        if self.copper_value <= 0:
            return "copper_value non è un valore valido: %d" % self.copper_value
        elif self.races.get_error_message(RACE, "races") != "":
            return self.races.get_error_message(RACE, "races")

        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Money()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, money2):
        if not money2:
            return False

        if self.comment != money2.comment:
            return False
        if self.copper_value != money2.copper_value:
            return False
        if self.races != money2.races:
            return False

        return True
    #- Fine Metodo -


#= Funzioni ====================================================================

def pretty_money_icons(value, race=RACE.HUMAN, entity=None):
    if value < 0:
        log.bug("Il parametro value non è una quantità valida: %r" % value)
        return "", "", "", ""

    # -------------------------------------------------------------------------

    # Se entity è stato passato allora fa vedere con che monete paga il negoziante
    if entity:
        # (TD)
        return "", "", "", ""

    mithril, gold, silver, copper = compute_currencies(value)

    mithril = '''%d<img src="%s" width="16" height="16" alt=" Mithril" title="Mithril" />''' % (mithril, race.get_money_icon("mithril"))
    gold    = '''%d<img src="%s" width="16" height="16" alt=" Oro" title="Oro" />'''         % (gold,    race.get_money_icon("gold"))
    silver  = '''%d<img src="%s" width="16" height="16" alt=" Argento" title="Argento" />''' % (silver,  race.get_money_icon("silver"))
    copper  = '''%d<img src="%s" width="16" height="16" alt=" Rame" title="Rame" />'''       % (copper,  race.get_money_icon("copper"))

    return mithril, gold, silver, copper
#- Fine Funzione -


def pretty_money_value(value, extended=False, entity=None):
    if value < 0:
        log.bug("Il parametro value non è una quantità valida: %r" % value)
        return ""

    # -------------------------------------------------------------------------

    # (TD) Se entity è stato passato allora fa vedere con che monete paga il negoziante
    if entity:
        return ""

    # Nel qual caso arrivi qui con un prezzo di 0
    if value == 0:
        if extended:
            return "0 monete di [copper]rame[close]"
        else:
            return "0 di [copper]rame[close]"

    mithril, gold, silver, copper = compute_currencies(value)

    if mithril > 0:
        if extended:
            mithril = "%d monet%s di [white]mithril[close]" % (mithril, "a" if mithril == 1 else "e")
        else:
            mithril = "%d di [white]mithril[close]" % mithril
    else:
        mithril = ""
    if gold > 0:
        if extended:
            gold = "%d monet%s d'[gold]oro[close]" % (gold, "a" if gold == 1 else "e")
        else:
            gold = "%d d'[gold]oro[close]" % gold
    else:
        gold = ""
    if silver > 0:
        if extended:
            silver = "%d monet%s d'[lightgray]argento[close]" % (silver, "a" if silver == 1 else "e")
        else:
            silver = "%d d'[lightgray]argento[close]" % silver
    else:
        silver = ""
    if copper > 0:
        if extended:
            copper = "%d monet%s di [copper]rame[close]" % (copper, "a" if copper == 1 else "e")
        else:
            copper = "%d di [copper]rame[close]" % copper
    else:
        copper = ""

    descr = ""
    for coin in (mithril, gold, silver, copper):
        if coin:
            descr += "%s, " % coin
    descr = descr.rstrip(", ")
    if "," in descr:
        descr = descr[::-1].replace(",", "e ", 1)[::-1]

    return descr
#- Fine Funzione -


# (TD) fare una lista di tuple (copper_value, entity) in maniera tale da
# riordinarle dalla minore alla maggiore così ritornando il minimo di monete
# possibili da dare per pagare senza avere un resto eccessivo
def can_afford(value, entity, race=RACE.NONE):
    if value < 0:
        log.bug("Il parametro value non è una quantità valida: %d" % value)
        return []

    if not entity:
        log.bug("Il parametro entity non è valido: %r" % entity)
        return []

    # -------------------------------------------------------------------------

    # C'è da notare che il ciclo controlla solo le entitype money e non anche
    # le strutture money_type che vengono lasciare ad altri check, per esempio
    # da parte di mob che effettuano conversioni di valuta o cose simili
    total = 0
    moneys = []
    openable_entities = [entity] + list(entity.iter_through_openable_entities(use_can_see=True))
    for openable_entity in openable_entities:
        for en in openable_entity.iter_contains():
            if en.entitype != ENTITYPE.MONEY and not en.money_type:
                continue

            if race != RACE.NONE:
                if en.money_type.races and race not in en.money_type.races:
                    continue

            total += en.quantity * en.money_type.copper_value
            moneys.append(en)
            if total >= value:
                break
        if total >= value:
            break
    else:
        return []

    return moneys
#- Fine Funzione -


def give_moneys(entity, target, value, race=RACE.NONE):
    if not entity:
        log.bug("Il parametro entity non è valido: %r" % entity)
        return

    if not target:
        log.bug("Il parametro target non è valido: %r" % target)
        return

    if value < 0:
        log.bug("Il parametro value non è una quantità valida: %d" % value)
        return

    # -------------------------------------------------------------------------

    moneys = can_afford(value, entity, race=RACE.NONE)
    if not moneys:
        log.bug("Inaspettato: non è stato eseguito un check can_afford in precedenza")
        return

    total = 0
    for money in moneys:
        # (TD) Cerca di evitare di dare il resto il più possibile
        #if money == moneys[-1]:
        #    diff = value - total
        total += money.quantity * money.money_type.copper_value
        money = money.from_location(money.quantity)
        money.to_location(target)

    if total <= value:
        if total < value:
            log.bug("Inaspettato: totale %d minore del valore di purchase %s: %d" % (total, purchase.code, value))
        return 0

    # Calcola quanto resto dare
    change = total - value
    mithril, gold, silver, copper = compute_currencies(change)

    # Da il resto in monete sonanti
    # Attenzione che il resto crea moneta dal nulla, non è come il sell che
    # da moneta solo se esistente, c'è da tenerne conto se si vuole creare
    # un'economia realistica
    if race == RACE.NONE:
        race = RACE.HUMAN
    for money_type, qty in (("mithril", mithril), ("gold", gold), ("silver", silver), ("copper", copper)):
        if qty > 0:
            instance = race.get_money_instance(money_type)
            instance.quantity = qty
            instance.inject(entity)

    return change
#- Fine Funzione -


def random_moneys(value, race=RACE.HUMAN):
    """
    Ritorna una lista casuale di entità moneta pari al valore passato.
    Parte sempre a creare quelle di valuta più grande, così da creare meno
    monete diminuendo così il peso totale delle monete.
    """
    if value < 0:
        log.bug("value non è un parametro valido: %d" % value)
        return []

    if not race:
        log.bug("race non è un parametro valido: %r" % race)
        return []

    # -------------------------------------------------------------------------

    # Esegue una copia per eventuale debug successivo
    original_value = value

    moneys = []
    for limit, currency, get_percent in ((1000 * config.currency_jump, "mithril", random.randint),
                                         ( 100 * config.currency_jump, "gold",    random.randint),
                                         (  10 * config.currency_jump, "silver",  random.randint),
                                         (   1,                        "copper",  max)):
        if value >= limit:
            quantity = (value / limit) * get_percent(0, 100) / 100
            if quantity > 0:
                money = _create_money(race, currency, quantity)
                if money:
                    moneys.append(money)
                else:
                    log.bug("La moneta di %s non è stata creata con successo con razza %r e quantità %d" % (currency, race, quantity))
                value -= quantity * limit

    if value != 0:
        log.bug("Inatteso, value non è 0 ma %d per original_value %d, race %r" % (
            value, original_value, race))
        return []

    return moneys
#- Fine Funzione -


def _create_money(race, currency, quantity):
    if not race:
        log.bug("race non è un parametro valido: %r" % race)
        return None

    if currency not in ("copper", "silver", "gold", "mithril"):
        log.bug("currency non è un parametro valido: %s" % currency)
        return None

    if not quantity:
        log.bug("quantity non è un parametro valido: %d" % quantity)
        return None

    # -------------------------------------------------------------------------

    from src.item import Item
    from src.mob  import Mob

    money_code = getattr(race, currency + "_coin")

    type = money_code.split("_", 2)[1]
    if type == "item":
        constructor = Item
    else:
        constructor = Mob

    money = constructor(money_code)
    money.quantity = quantity
    return money
#- Fine Funzione -


def compute_currencies(value):
    if value < 0:
        log.bug("value non è un parametro valido: %d" % value)
        return -1, -1, -1, -1

    # -------------------------------------------------------------------------

    mithril = math.trunc(value * config.currency_jump / 1000)
    gold    = math.trunc(value * config.currency_jump /  100) % 10
    silver  = math.trunc(value * config.currency_jump /   10) % 10
    copper  =           (value                        /    1) % 10

    return mithril, gold, silver, copper
#- Fine Funzione -
