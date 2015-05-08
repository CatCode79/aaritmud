# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

from src.command    import get_command_syntax
from src.database   import database
from src.enums      import OPTION
from src.skill      import check_skill
from src.gamescript import check_trigger
from src.log        import log

# Da rifare bene, ora non ho voglia.. gh :P
# for attrs in rune.__dict__:
#     if attrs.startswith("runes_"):
#         import(attrs)


#= VARIABILI ===================================================================

RUNE_NAME  = 0
RUNE_COUNT = 1
RUNE_POWER = 2


#= FUNZIONI ====================================================================

#(TD) aggiungere il check_trigger
def command_cast(entity, argument="", behavioured=False):
    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che rune vorresti recitare?")
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_cast")
            entity.send_output(syntax, break_line=False)
        return

    runes = []  # lista di liste [RUNE_NAME, RUNE_COUNT, RUNE_POWER]
    last_rune = ""
    target = entity.location
    while 1:
        arg, argument = one_argument(argument)
        if not arg:
            break
        # Per ora le rune sono una per lettera dell'alfabeto quindi non le
        # ordina prima di effettuare la ricerca.
        # (TD) devo aggiungere un sistema di supporto per scrivere le rune tipo: 6 an 3 tym 2nox (sì, anche attaccate)
        for rune_name in database["runes"]:
            if is_prefix(arg, rune_name):
                if rune_name == last_rune:
                    runes[-1][RUNE_COUNT] += 1
                else:
                    runes.append([rune_name, 1, 0])
                last_rune = rune_name
                break
        else:
            # Se non ha trovato la runa corrispondente o è un errore oppure
            # cerca il bersaglio
            if not runes:
                entity.send_output("Non esiste nessuna runa chiamata %s.", capitalize(arg))
                return
            else:
                # (TD) Sarà da potenziare questa parte così da inserire rune in
                # parti del corpo o negli oggetti del bersaglio e anche per la direzione
                target = entity.find_entity_extensively(arg)
                if not target:
                    entity.act("Non esiste nessun %s qui attorno." % arg, TO.ENTITY)
                    entity.act("$n cerca qualcuno che non si trova nei paraggi", TO.OTHERS)
                    return
    # Ricava il potere della runa opzionale iniziale Tym
    rune_tym_power = 0
    if runes[0] == "Tym":
        while runes[0][RUNE_COUNT] > 0:
            rune_tym_power += check_rune(entity, target, runes[0][RUNE_NAME])
            runes[0][RUNE_COUNT] -= 1
        runes = runes[1 : ]
    # Ricava il potere della runa opzionale finale An
    rune_an_power = 0
    if runes[-1] == "An":
        negative = False
        if runes[-1][RUNE_COUNT] % 2 == 0:
            negative = True
        while runes[-1][RUNE_COUNT] > 0:
            if negative:
                rune_tym_power -= check_rune(entity, target, runes[-1][RUNE_NAME])
            else:
                rune_tym_power += check_rune(entity, target, runes[-1][RUNE_NAME])
            runes[-1][RUNE_COUNT] -= 1
        runes = runes[ : -1]
    # Ricava il potere delle rune a seconda del numero di quelle pronunciate
    negative = False
    for position in xrange(len(runes)):
        # Salta il calcolo del potere delle rune An che servono per invertire il
        # potere della o delle rune sucessive, più rune An
        if rune[position][RUNE_NAME] == "An":
            rune[position+1][RUNE_COUNT] += rune[position][RUNE_COUNT] - 1
            rune[position][RUNE_COUNT] = 1
            negative = True
            continue
        count = rune[RUNE_COUNT]
        while count > 0:
            if negative:
                rune[RUNE_POWER] -= check_rune(entity, target, rune[RUNE_NAME])
            else:
                rune[RUNE_POWER] += check_rune(entity, target, rune[RUNE_NAME])
            count -= 1
        negative = False
#- Fine Funzione -


def check_rune(entity, target, rune):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return 0

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return 0

    # -------------------------------------------------------------------------

    # (TD) per semplicità per ora utilizzo la check_skill()
    return check_skill(entity, target, rune)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "cast <sequenza di rune>\n"
    syntax += "cast <sequenza di rune> <bersaglio>\n"
    syntax += "cast <sequenza di rune> <direzione>\n"
    syntax += "cast <sequenza di rune> <direzione> <bersaglio>\n"

    return syntax
#- Fine Funzione -
