# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

#from src.color     import color_first_upper
from src.enums     import ATTR, GRAMMAR, POINTS, TRUST
from src.grammar   import add_article
#from src.interpret import translate_input
from src.log       import log
from src.player    import experiences #, Player
from src.utility   import commafy #, get_weight_descr


#= FUNZIONI ====================================================================

def command_score(entity, argument="", behavioured=False):
    """
    Permette di visualizzare il proprio stato.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if argument and entity.trust >= TRUST.MASTER:
        target = entity.find_entity(argument, entity_tables=["players", "mobs"])
        if not target:
            entity.send_output("Non è stato trovato nessun giocatore o mob con argomento [white]%s[close]" % argument)
            return False
        target = target.split_entity(1)
    else:
        target = entity.split_entity(1)

    output = get_score_output(entity, target)
    if not output:
        log.bug("Inatteso output non valido con entity %s e target %s: %r" % (entity.code, target.code, output))
        return False
    entity.send_output(output)

    return True
#- Fine Funzione -


def get_score_output(entity, target):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    if not target:
        log.bug("target non è un parametro valido: %r" % target)
        return ""

    # -------------------------------------------------------------------------

    if entity.IS_ITEM:
        return "Gli oggetti non possono conoscere il proprio stato."

    output = []

    surname = ""
    if hasattr(target, surname) and target.surname:
        surname = " " + target.surname

    # (TD) se sei morto indicare che sei l'anima di un...
    race = str(target.race)
    race = add_article(race, GRAMMAR.INDETERMINATE)

    # (TD) se la razza ricavata da get_race è differente rispetto a a quella
    # normale allora indicare che si è trasformati

    output.append("%s%s, %s di livello %d\n" % (target.name, surname, race, target.level))

    # -------------------------------------------------------------------------

    output.append("La via in cui sei forte è quella del %s mentre quella in cui sei debole è quella del %s\n" % (
        target.get_strength_way(), target.get_weak_way()))

    # -------------------------------------------------------------------------

    if target.age == 1:
        age = " dell'anno scorso"
    elif target.age == 0:
        age = " di quest'anno"
    else:
        age = " di [white]%d[close] anni fa" % target.age

    affected_age = ""
    if target.get_age() != target.age:
        affected_age = ", anche se dimostri %s anni" % target.get_age()

    # (TD) Aggiungere il luogo di nascita

    output.append("Sei nat$o il [white]%d[close] del mese %s%s%s\n" % (
        target.birth_day, target.birth_month.description, age, affected_age))

    # -------------------------------------------------------------------------

    #constellation = add_article(str(target.constellation), GRAMMAR.INDETERMINATE)  # (bb) SEX.MALE

    # (TD) Il tuo carattere è prevalentemente %s, target.archetype

    output.append("Sei della costellazione %s\n" % (target.constellation))

    # -------------------------------------------------------------------------

    if hasattr(target, "title") and target.title:
        output.append("Sei conosciuto come: %s\n" % target.title)

    # -------------------------------------------------------------------------

    if hasattr(target, "target_descr") and target.target_descr:
        output.append("Il tuo obiettivo è: %s\n" % target.target_descr)

    # -------------------------------------------------------------------------

    output.append('''<table class="mud">''')

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.STRENGTH)
    output.append('''<td>%d<td>''' % target.strength)
    output.append('''<td>%s:</td>''' % POINTS.LIFE)
    output.append('''<td>%s </td>''' % target.get_actual_and_max_points(POINTS.LIFE))
    output.append('''<td>%s</td>''' % target.get_thirst_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.ENDURANCE)
    output.append('''<td>%d<td>''' % target.endurance)
    output.append('''<td>%s:</td>''' % POINTS.MANA)
    output.append('''<td>%s </td>''' % target.get_actual_and_max_points(POINTS.MANA))
    output.append('''<td>%s</td>''' % target.get_hunger_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.AGILITY)
    output.append('''<td>%d<td>''' % target.agility)
    output.append('''<td>%s:</td>''' % POINTS.VIGOUR)
    output.append('''<td>%s </td>''' % target.get_actual_and_max_points(POINTS.VIGOUR))
    output.append('''<td>%s</td>''' % target.get_sleep_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.SPEED)
    output.append('''<td>%d<td>''' % target.speed)
    output.append('''<td></td>''')
    output.append('''<td></td>''')
    output.append('''<td>%s</td>''' % target.get_drunkness_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.INTELLIGENCE)
    output.append('''<td>%d<td>''' % target.intelligence)
    output.append('''<td></td>''')
    output.append('''<td></td>''')
    output.append('''<td>%s</td>''' % target.get_adrenaline_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.WILLPOWER)
    output.append('''<td>%d<td>''' % target.willpower)
    output.append('''<td></td>''')
    output.append('''<td></td>''')
    output.append('''<td>%s</td>''' % target.get_mind_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.PERSONALITY)
    output.append('''<td>%d<td>''' % target.personality)
    output.append('''<td></td>''')
    output.append('''<td></td>''')
    output.append('''<td>%s</td>''' % target.get_emotion_condition())
    output.append('''</tr>''')

    # -------------------------------------------------------------------------

    output.append('''<tr>''')
    output.append('''<td>%s:<td>''' % ATTR.LUCK)
    output.append('''<td>%d<td>''' % target.luck)
    output.append('''<td></td>''')
    output.append('''<td></td>''')
    output.append('''<td>%s</td>''' % target.get_bloodthirst_condition())
    output.append('''</tr>''')

    output.append('''</table>''')

    output.append('''Hai %s punti di esperienza e te ne mancano %s per il prossimo livello''' % (
        commafy(target.experience), commafy(experiences[target.level] - target.experience)))
    if target.talents > 0:
        # (TD) qui aggiungere il link per aprire la tab di distribuzione talenti
        # (TD) fare l'opzione rpg e la frase differente, del tipo: hai ancora del talento da utilizzare per crescere
        output.append('''\nHai ancora %d punti di talento da <a href="#" onclick="sendInput('talents');">distribuire</a>''' % target.talents)

    # -------------------------------------------------------------------------

    return "".join(output)
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = "score\n"
    if entity.trust >= TRUST.MASTER:
        syntax += "score <nome o codice giocatore>"
        syntax += "score <nome o codice mob>"
    return syntax
#- Fine Funzione -
