# -*- coding: utf-8 -*-

"""
MUD Internal Markup Language.
L'idea si basa su un sistema molto simile visto nel codice del Mud DODT,
uno smaug-based.
"""


#= IMPORT ======================================================================

from src.calendar import calendar
from src.database import database
from src.element  import Element
from src.enums    import DIR, FLAG
from src.log      import log
from src.utility  import is_number


# Lazy import
get_direction = None


#= COSTANTI ====================================================================

MIML_SEPARATOR = "#"


#= FUNZIONI ====================================================================

class MIMLParserSuperclass(object):
    def parse_miml(self, descr, looker=None):
        if not descr:
            log.bug("descr non è un parametro valido: " % descr)
            return ""

        # ---------------------------------------------------------------------

        if MIML_SEPARATOR not in descr:
            return descr

        parts = descr.split(MIML_SEPARATOR)

        # Rimuove la prima e l'ultima parte formata da soli spazi
        if parts[0].strip() == "":
            parts = parts[1 : ]
        if parts[-1].strip() == "":
            parts = parts[ : -1]

        if descr[0] == "#":
            result = []
        else:
            result = [parts.pop(0)]

        while len(parts) >= 3:
            original_check = parts.pop(0)
            check = original_check.strip()

            use_if_branch = False
            entity_found = None
            # Concettualmente sarebbe errato cercare la previous_location di
            # self visto che magari si vorrebbe quella di looker o della location
            # stessa ma va bene lo stesso, visto che esisterà il sistema alternativo
            # dei miml come script python inline
            if check[0 : 4] == "self" or check[0 : 8] == "location" or check[0 : 17] == "previous_location" or check[0 : 6] == "looker":
                use_if_branch = self.parse_miml_check(check, looker)
            # Questo è il caso in cui la condizione check è un codice di entità
            # o un codice di un giocatore
            elif ("_" in check and check.split("_")[1] in ("mob", "item")) or check in database["players"]:
                for entity in self.iter_contains():
                    if ((hasattr(entity, "prototype") and entity.prototype.code == check)
                    or  entity.code == check):
                        if not self.IS_ROOM and (len(entity.wear_mode) > 0 or FLAG.INGESTED in entity.flags):
                            continue
                        entity_found = entity
                        break
            # Questo è in tutti gli altri casi, ovvero quando il carattere #
            # non è un separatore di miml e quindi l'output deve essere ripristinato
            else:
                result.append("#" + original_check)
                continue

            if use_if_branch:
                result.append(parts.pop(0))
                parts.pop(0)
            elif entity_found:
                if_branch = parts.pop(0)  # if branch
                if "@" in if_branch:
                    result.append(if_branch.replace("@", entity_found.get_name(looker)))
                else:
                    result.append(if_branch)
                parts.pop(0)  # else branch
            else:
                parts.pop(0)  # if branch
                result.append(parts.pop(0))  # else branch

        if len(parts) <= 1:
            return "".join(result + parts)
        else:
            return "".join(result) + "#" + "#".join(parts)
    #- Fine Funzione -

    def parse_miml_check(self, check, looker=None):
        if not check:
            log.bug("check non è un parametro valido: %r" % check)
            return False

        # ---------------------------------------------------------------------

        check_parts = check.split()

        if check_parts[0][0 : 4] == "self":
            check_entity = self
        elif check_parts[0][0 : 8] == "location":
            if self.IS_ROOM:
                check_entity = self
            else:
                check_entity = self.location
        elif check_parts[0][0 : 17] == "previous_location":
            if self.IS_ROOM:
                check_entity = self
            else:
                check_entity = self.previous_location
        elif check_parts[0][0 : 6] == "looker":
            if not looker:
                log.bug("looker non valido (%r) anche se il check lo necessita: %s" % (looker, check))
                return False
            check_entity = looker
        elif check_parts[0][0 : 6] == "season":
            if check_parts[1] == "is":
                if calendar.season == Element(check_parts[2]):
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if calendar.season != Element(check_parts[2]):
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        else:
            log.bug("entità da utilizzare per i check è sconosciuta: %s" % check_parts[0])
            return False

        # (TD) no, dovrò splittare con or o and ed utilizzare le builtin any o all
        #for element_code in check_parts[2].split("|"):
        #    pass

        # Miml relativo alla razza dell'entità controllata
        if check_parts[2][0 : 5] == "RACE.":
            if check_entity.IS_ROOM:
                return False

            if check_parts[1] == "is":
                if check_entity.race == Element(check_parts[2]):
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if check_entity.race != Element(check_parts[2]):
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        # Miml relativo alla sessualità dell'entità controllata
        elif check_parts[2][0 : 4] == "SEX.":
            if check_entity.IS_ROOM:
                return False

            if check_parts[1] == "is":
                if check_entity.sex == Element(check_parts[2]):
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if check_entity.sex != Element(check_parts[2]):
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        # Miml relativo ai contenitori
        elif check_parts[2][0 : 10] == "CONTAINER.":
            if check_entity.IS_ROOM or not check_entity.container_type:
                return False

            if check_parts[1] == "is":
                if Element(check_parts[2]) in check_entity.container_type.flags:
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if Element(check_parts[2]) not in check_entity.container_type.flags:
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        # Miml relativo al settore di una stanza
        elif check_parts[2][0 : 7] == "SECTOR.":
            if not check_entity.IS_ROOM:
                return False

            if check_parts[1] == "is":
                if check_entity.sector == Element(check_parts[2]):
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if check_entity.sector != Element(check_parts[2]):
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        # Miml relativo alle flags di una stanza
        elif check_parts[2][0 : 5] == "ROOM.":
            if not check_entity.IS_ROOM:
                return False

            if check_parts[1] == "is":
                if Element(check_parts[2]) in check_entity.flags:
                    return True
                else:
                    return False
            elif check_parts[1] == "is not":
                if Element(check_parts[2]) not in check_entity.flags:
                    return True
                else:
                    return False
            else:
                log.bug("Operatore di check sconosciuto: %s per l'elemento con codice %s" % (check_parts[1], check_parts[2]))
                return False
        # Miml relativo all'inventario portato
        elif check_parts[0][-14 : ] == ".inventory_qty":
            check_qty = 0
            if is_number(check_parts[2]):
                check_qty = int(check_parts[2])
            else:
                log.bug("la parte destra dell'opeartore del check miml %s non è un numbero valido" % (check))

            qty = 0
            for content in check_entity.iter_contains():
                if len(content.wear_mode) == 0 and FLAG.INGESTED not in content.flags:
                    qty += 1

            if check_parts[1] == "==" and qty == check_qty:
                return True
            elif check_parts[1] == "!=" and qty != check_qty:
                return True
            elif check_parts[1] == ">" and qty > check_qty:
                return True
            elif check_parts[1] == ">=" and qty >= check_qty:
                return True
            elif check_parts[1] == "<" and qty < check_qty:
                return True
            elif check_parts[1] == "<=" and qty <= check_qty:
                return True
            else:
                return False
        # Miml relativo all'equipaggiamento portato
        elif check_parts[0][-14 : ] == ".equipment_qty":
            check_qty = 0
            if is_number(check_parts[2]):
                check_qty = int(check_parts[2])
            else:
                log.bug("la parte destra dell'opeartore del check miml %s non è un numbero valido" % check)

            qty = 0
            for content in check_entity.iter_contains():
                if len(content.wear_mode) != 0 and FLAG.INGESTED not in content.flags:
                    qty += 1

            if check_parts[1] == "==" and qty == check_qty:
                return True
            elif check_parts[1] == "!=" and qty != check_qty:
                return True
            elif check_parts[1] == ">" and qty > check_qty:
                return True
            elif check_parts[1] == ">=" and qty >= check_qty:
                return True
            elif check_parts[1] == "<" and qty < check_qty:
                return True
            elif check_parts[1] == "<=" and qty <= check_qty:
                return True
            else:
                return False
        # Miml relativo alle exits, wall e direzioni
        elif get_direction_miml(check_parts[0]) != DIR.NONE:
            if not check_entity.IS_ROOM:
                return False

            direction = get_direction_miml(check_parts[0])
            if direction in check_entity.exits:
                if check_parts[1] == "is":
                    if check_parts[2] == "Exit":
                        return True
                    elif check_parts[2] == "Wall":
                        # Il check qui ci vuole comunque perché una direzione può
                        # avere sia uscita che muro, idem per il ramo 'is not'
                        if direction in check_entity.walls:
                            return True
                        else:
                            return False
                    elif check_parts[2] == "Door":
                        if check_entity.exits[direction].door and check_entity.exits[direction].door.door_type:
                            return True
                        else:
                            return False
                    elif check_parts[2][ : 5] == "EXIT.":
                        if Element(check_parts[2]) in check_entity.exits[direction].flags:
                            return True
                        else:
                            return False
                    elif check_parts[2][ : 5] == "DOOR.":
                        if check_entity.exits[direction].door and check_entity.exits[direction].door.door_type and Element(check_parts[2]) in check_entity.exits[direction].door.door_type.flags:
                            return True
                        else:
                            return False
                elif check_parts[1] == "is not":
                    if check_parts[2] == "Exit":
                        return False
                    elif check_parts[2] == "Wall":
                        if direction in check_entity.walls:
                            return False
                        else:
                            return True
                    elif check_parts[2] == "Door":
                        if check_entity.exits[direction].door and check_entity.exits[direction].door.door_type:
                            return False
                        else:
                            return True
                    elif check_parts[2][ : 5] == "EXIT.":
                        if Element(check_parts[2]) in check_entity.exits[direction].flags:
                            return False
                        else:
                            return True
                    elif check_parts[2][ : 5] == "DOOR.":
                        if check_entity.exits[direction].door and check_entity.exits[direction].door.door_type and Element(check_parts[2]) in check_entity.exits[direction].door.door_type.flags:
                            return False
                        else:
                            return True
                else:
                    log.bug("Operatore di check sconosciuto: %s per il check %s" % (check_parts[1], check))
                    return False

            if direction in check_entity.walls:
                if check_parts[1] == "is":
                    if check_parts[2] == "Wall":
                        if direction in check_entity.walls:
                            return True
                        else:
                            return False
                elif check_parts[1] == "is not":
                    if check_parts[2] == "Wall":
                        if direction in check_entity.walls:
                            return False
                        else:
                            return True

            return False

        # Tutti gli altri casi vengono gestiti come errore di sintassi
        log.bug("check del miml dalla sintassi errata: %s" % check)
        return False
    #- Fine Metodo -


def get_direction_miml(check):
    global get_direction
    if not get_direction:
        from src.exit import get_direction as get_direction_function
        get_direction = get_direction_function

    open_bracket  = check.find("[")
    if open_bracket == -1:
        log.bug("miml errato su direzione, era attesa la parentesi quadra aperta: %s" % check)
        return False

    close_bracket = check.find("]")
    if close_bracket == -1:
        log.bug("miml errato su direzione, era attesa la parentesi quadra chiusa: %s" % check)
        return False

    return get_direction(check[open_bracket+1 : close_bracket], True)
#- Fine Funzione -
