# -*- coding: utf-8 -*-

"""
Elenca il totale delle le monete che si posseggono.
"""

#= IMPORT ======================================================================

from src.gamescript import check_trigger
from src.log        import log
from src.utility    import commafy

from src.entitypes.money import pretty_money_value


#= FUNZIONI ====================================================================

def command_money(entity, argument="", behavioured=False):
    # È possibile se questo comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    force_return = check_trigger(entity, "before_money", entity, behavioured)
    if force_return:
        return True

    all_moneys = []
    for en in entity.iter_all_entities():
        if en.money_type:
            all_moneys.append(en)

    moneys = []
    openable_entities = [entity] + list(entity.iter_through_openable_entities(use_can_see=True))
    for openable_entity in openable_entities:
        for en in openable_entity.iter_contains():
            if en.money_type:
                moneys.append(en)

    if moneys:
        output = []
        total = 0
        plural = "a" if len(moneys) == 1 else "e"
        output.append('''<table class="mud">''')
        output.append('''<tr><th>Qtà</th><th>Monet%s</th><th>in Rame</th><th> Accettat%s dalla razza</th><tr>''' % (plural, plural))
        for en in moneys:
            total += en.money_type.copper_value * en.quantity

            races = str(en.money_type.races)
            print races
            if "$o" in races:
                races = races.replace("$o", "a")
            if not races:
                races = "Tutte"

            output.append('''<tr><td style="text-align:center">%d</td>''' % en.quantity)
            output.append('''<td style="text-align:center">* %s =</td>''' % en.get_name(looker=entity))
            output.append('''<td style="text-align:center">%s</td>''' % commafy(en.money_type.copper_value * en.quantity))
            output.append('''<td style="text-align:center">%s</td><tr>''' % races)
        output.append('''</table>''')

        output.append("La tua ricchezza ammonta a un corrispettivo di %s." % pretty_money_value(total, extended=True))
        entity.send_output("".join(output))
    else:
        entity.send_output("Non possiedi nessuna [gold]moneta[close].")
    if len(all_moneys) != len(moneys):
        output.append("Non viene contata la ricchezza dentro eventuali contenitori chiusi, o invisibili, che possiedi.")

    force_return = check_trigger(entity, "after_money", entity, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    return "money <oggetto o creatura da comprare> (commerciante se più di uno nella stanza)\n"
#- Fine Funzione -
