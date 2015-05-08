# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.config     import config
from src.enums      import SKILL, TO
from src.fight      import start_fight
from src.gamescript import check_trigger
from src.log        import log
from src.skill      import check_skill
from src.utility    import one_argument

if config.reload_commands:
    reload(__import__("src.commands.command_attack", globals(), locals(), [""]))
from src.commands.command_attack import command_attack


#= COSTANTI ====================================================================

VERBS = {}
VERBS["infinitive"] = "[orange]calciare[close]"
VERBS["you2"]     = "[orange]calciarti[close]"
VERBS["noun"]     = "[orange]calciarl$O[close]"

STATS = ("strength", "agility")

KICK_WAIT = 1.5


#= FUNZIONI ====================================================================

def skill_kick(entity, argument="", verbs=VERBS, silent=False):
    """
    Skill di combattimento, deve avere un target già prefissato.
    Dà un calcio alla vittima con cui si combatte.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return "failure"

    # -------------------------------------------------------------------------

    arg, argument = one_argument(argument)
    if arg:
        target = entity.find_entity_extensively(arg)
        if not target:
            entity.send_output("Chi vorresti %s?" % verbs["infinitive"])
            return "failure"
    else:
        target = opponent = entity.get_opponent()

    if not target:
        entity.send_output("Chi vorresti %s?" % verbs["infinitive"])
        return "failure"

    # (TD) gestire le posizioni

    if "kick" not in entity.skills:
        entity.skills["kick"] = 0

    skill_result = check_skill(entity, target, "kick")
    print ">>>>>>> skill kick: skill_result: ", skill_result

    # Ricava quale parte viene colpita
    #arg, argument = one_argument(argument)
    #if not arg:
    #    victim_part = None

    # Ricava se viene utilizzata la gamba destra o sinistra
    #right_leg = True
    #if not argument:
    #    right_leg = entity.hand
    #else:
    #    if is_same(argument, ("destro", "destra", "right")):
    #        right_leg = True
    #    elif is_same(argument, ("sinistro", "sinistra", "left")):
    #        right_leg = False
    #    else:
    #        entity.send_output("Vuoi calciare con la gamba destra o quella sinistra?")
    #        return False

    force_return = check_trigger(entity, "before_kick", entity, target, skill_result)
    if force_return:
        return "failure"
    force_return = check_trigger(target, "before_kicked", entity, target, skill_result)
    if force_return:
        return "failure"

    if not entity.is_fighting(with_him=target):
        start_fight(entity, target)

    if skill_result < config.clumsy_value:
        if not silent:
            entity.act("Tenti di %s il colpo di $N ma metti male la caviglia ed un dolore acuto ti trafigge." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n tenta di %s il colpo di $N ma inciampa facendosi del male." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n si fa del male mentre tenta di %s d'anticipo." % verbs["you2"], TO.TARGET, target)
        # (TD) l'attaccante cade
        kick_damage(entity, target, "clumsy", skill_result)
        execution_result = "clumsy"
        entity.wait(KICK_WAIT * 2)
    elif skill_result < config.failure_value:
        if not silent:
            entity.act("Tenti maldestramente di %s $N rischiando pure di cadere." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n tenta maldestramente di %s $N rischiando di cadere." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n tenta maldestramente di %s rischiando di cadere." % verbs["you2"], TO.TARGET, target)
        kick_damage(entity, target, "failure", skill_result)
        execution_result = "failure"
        entity.wait(KICK_WAIT * 2)
    elif skill_result < config.success_value:
        if not silent:
            entity.act("Riesci a prendere alla sprovvista $N e %s." % verbs["noun"], TO.ENTITY, target)
            entity.act("$n riesce a prendere alla sprovvista$N e %s." % verbs["noun"], TO.OTHERS, target)
            entity.act("$n ti prende alla alla sprovvista e riesce a %s."% verbs["you2"], TO.TARGET, target)
        damage = kick_damage(entity, target, "success", skill_result)
        execution_result = "success"
        entity.wait(KICK_WAIT)
    else:
        if not silent:
            entity.act("Riesci magistralmente a %s $N prendendol$O alla sprovvista." % verbs["infinitive"], TO.ENTITY, target)
            entity.act("$n riesce magistralmente a %s $N prendendol$O alla sprovvista." % verbs["infinitive"], TO.OTHERS, target)
            entity.act("$n riesce magistralmente a %s prendendoti alla sprovvista."% verbs["infinitive"], TO.TARGET, target)
        # (TD) il nemico cade
        kick_damage(entity, target, "masterly", skill_result)
        execution_result = "masterly"
        entity.wait(KICK_WAIT)

    force_return = check_trigger(entity, "after_kick", entity, target, skill_result)
    if force_return:
        return execution_result
    force_return = check_trigger(target, "after_kicked", entity, target, skill_result)
    if force_return:
        return execution_result

    return execution_result
#- Fine Funzione -


# (TD) si può calciare dalla montatura ma il danno è dimezzato
def kick_damage(entity, target, mode_name, skill_result, modifier=1):
    if not entity:
        log.bug("entity non è parametro valido: %r" % entity)
        return

    if not target:
        log.bug("target non è parametro valido: %r" % target)
        return

    if mode_name not in ("clumsy", "failure", "success", "magistral"):
        log.bug("mode_name non è parametro valido: %s" % mode_name)
        return

    if not skill_result:
        log.bug("skill_result non è parametro valido: %r" % skill_result)
        return

    # -------------------------------------------------------------------------

    if mode_name == "clumsy":
        modifier_target_damage = 0
        modifier_entity_damage = 1
    elif mode_name == "failure":
        modifier_target_damage = 0
        modifier_entity_damage = 0
    elif mode_name == "success":
        modifier_target_damage = 1
        modifier_entity_damage = 0
    else:
        modifier_target_damage = 1.5
        modifier_entity_damage = 0

    fight = entity.get_fight(with_him=target)
    if not fight:
        log.bug("non è stato trovato nessun fight tra %s e %s" % (entity.code, target.code))
        return

    if modifier_target_damage != 0:
        target_damage = int(modifier_target_damage * (random.randint(1, 5) + (entity.strength / 5) * (skill_result / 200 ) * modifier))
        target.life -= target_damage
        if target.life <= 0:
            fight.defeat(entity, target, "attacker", "defender")
            fight.stop()
    elif modifier_entity_damage != 0:
        entity_damage = int(modifier_entity_damage * (random.randint(1, 5) + (entity.strength / 5) * (skill_result / 200 ) * modifier))
        entity.life -= entity_damage
        if entity.life <= 0:
            entity.dies(opponent=target)
            fight.stop()

    return
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""
    syntax += "kick\n"
    syntax += "kick <vittima>\n"
    #syntax += "kick <parte della vittima> destro|sinistro\n"

    return syntax
#- Fine Funzione -
