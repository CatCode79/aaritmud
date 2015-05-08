# -*- coding: utf-8 -*-

"""
Modulo contenente tutti le funzioni che servono alla ricerca di entity tramite
il passaggio di un argomento.
Tali funzioni verranno legate alla classe Entity e non sono da importare e
utilizzare come funzioni.
"""

#= IMPORT ======================================================================

from src.config    import config
from src.database  import database
from src.enums     import DIR, DOOR, ENTITYPE, FLAG, PART, TRUST
from src.exit      import get_direction
from src.interpret import translate_input
from src.log       import log
from src.utility   import (is_same, is_infix, is_prefix, is_suffix, one_argument,
                           number_argument, multiple_arguments, put_final_dot)


#= COSTANTI ====================================================================

INSTANCE     = 0
ICON         = 1
LONG         = 2
COUNTER      = 3
NO_LOOK_LIST = 4
BURIED       = 5
INGESTED     = 6
INCOGNITO    = 7
ENTITIES     = 8


#= CLASSI ======================================================================

# (TD) c'è da pensare se in realtà non sarebbe meglio se fa estendere quella
# classe alla sola Entity, ovvero passare la location al posto del looker se ne
# guadagnerebbe in semplicità di intrecci di import
class RelativePointSuperclass(object):
    """
    Classe che contiene i metodi necessari a creare e formattare liste d'entità,
    relative ad una determinata locazione, come vengono viste da un'altra
    entità, il looker.
    Tale lista deve essere utilizzata sia nella visualizzazione ma anche nella
    ricerca, così da mantenere una corrispondenza corretta nel qual caso il
    looker esegua comandi con il contatore (get 3.pomodoro) essendo le entità
    già ordinate secondo il suo punto di vista.
    Questa classe estende le classi Room e Entity.
    """
    def get_list_of_entities(self, looker, entity_tables=None, include_looker=False, avoid_inventory=False, avoid_equipment=True, avoid_doors=False, admin_descrs=False, use_number_argument=True):
        """
        Ritorna una stringa con tutte le entità relative ad una stanza.
        Il parametro no_number_argument serve ad evitare ricorsioni della
        get_long.
        """
        if not looker:
            log.bug("looker non è un parametro valido: %r" % looker)
            return

        # ---------------------------------------------------------------------

        from src.web_resource import create_icon

        look_translation = translate_input(looker, "look", "en")
        if not look_translation:
            log.bug("look_translation non è valida: %r" % look_translation)
            look_translation = "guarda"

        is_admin = looker.trust >= TRUST.MASTER

        # Ricava la lista di entità da visualizzare
        entities = []
        for entity in list(self.iter_contains(entity_tables=entity_tables)) + list(self.iter_only_interactable_entities(entity_tables=entity_tables, use_can_see=True)):
            if not include_looker and entity == looker:
                continue
            if avoid_inventory and len(entity.wear_mode) == 0:
                continue
            if avoid_equipment and len(entity.wear_mode) != 0:
                continue
            if avoid_doors and entity.door_type and entity.is_hinged():
                continue
            if entity in [en[INSTANCE] for en in entities]:
                continue

            if not is_admin:
                if FLAG.BURIED in entity.flags:
                    continue
                if FLAG.INGESTED in entity.flags:
                    continue
                if entity.incognito:
                    continue

            long_descr = put_final_dot(entity.get_long(looker, look_translation, use_number_argument))
            # (TD) magari in futuro creare addirittura una classe apposita
            # per tutta questa lista appendata
            entities.append([entity, create_icon(entity.get_icon()), long_descr, entity.quantity, "", "", "", "", []])

        # Raggruppa eventuali entità che si visualizzerebbero in maniera identica
        if config.use_visual_grouping:
            for entity1 in entities:
                for entity2 in entities:
                    if entity1[COUNTER] <= 0 or entity2[COUNTER] <= 0:
                        continue
                    if entity1[INSTANCE] == entity2[INSTANCE]:
                        continue
                    if entity1[ICON] != entity2[ICON]:
                        continue
                    if entity1[LONG] == entity2[LONG]:
                        if entity1[COUNTER] > 1:
                            entity1[COUNTER] += entity2[INSTANCE].quantity
                            entity2[COUNTER] -= entity2[INSTANCE].quantity
                            entity1[ENTITIES].append(entity2[INSTANCE])
                        else:
                            entity1[COUNTER] -= entity1[INSTANCE].quantity
                            entity2[COUNTER] += entity1[INSTANCE].quantity
                            entity2[ENTITIES].append(entity1[INSTANCE])

        # Ripulisce le entità che hanno ora counter minore o uguale a zero
        for entity in reversed(entities):
            if entity[COUNTER] <= 0:
                entities.remove(entity)

        # Inserisce per ultimi nella lista relativa a ENTITIES le entità che
        # possiedono la flag NO_LOOK_LIST, in maniera da mantenere l'ordinamento
        # della visualizzazione con quello della ricerca nel qual caso alcune
        # entità visualizzabili abbiano lo stesso nome di quelle con tale flag
        # In pratica tutto questo per evitare che qualcuno tramite, ad esempio,
        # get 2.pomodoro non raccolga per sbaglio l'entità NO_LOOK_LIST invece
        # di quella visualizzata, come invece sarebbe voluto
        for entity in entities:
            no_look_list_entities = []
            for en in reversed(entity[ENTITIES]):
                if FLAG.NO_LOOK_LIST in en.flags:
                    entity[ENTITIES].remove(en)
                    no_look_list_entities.append(en)
            entity[ENTITIES].extend(reversed(no_look_list_entities))

        # Ai soli admin crea le informazioni relative alle flags
        if is_admin and admin_descrs:
            for entity in entities:
                no_look_list_counter = 0
                buried_counter       = 0
                ingested_counter     = 0
                incognito_counter    = 0

                for en in [entity[INSTANCE]] + entity[ENTITIES]:
                    if FLAG.NO_LOOK_LIST in en.flags:
                        no_look_list_counter += en.quantity
                    if FLAG.BURIED in en.flags:
                        buried_counter += en.quantity
                    if FLAG.INGESTED in en.flags:
                        ingested_counter += en.quantity
                    if en.incognito:
                        incognito_counter += en.quantity

                no_look_list_descr = ""
                if no_look_list_counter == 1 and entity[COUNTER] == 1:
                    no_look_list_descr = " no_look_list"
                elif no_look_list_counter > 0:
                    no_look_list_descr = " no_look_list(%d)" % no_look_list_counter
                entity[NO_LOOK_LIST] = no_look_list_descr

                buried_descr = ""
                if buried_counter == 1 and entity[COUNTER] == 1:
                    buried_descr = " buried"
                elif buried_counter > 0:
                    buried_descr = " buried(%d)" % buried_counter
                entity[BURIED] = buried_descr

                ingested_descr = ""
                if ingested_counter == 1 and entity[COUNTER] == 1:
                    ingested_descr = " ingested"
                elif ingested_counter > 0:
                    ingested_descr = " ingested(%d)" % ingested_counter
                entity[INGESTED] = ingested_descr

                incognito_descr = ""
                if incognito_counter == 1 and entity[COUNTER] == 1:
                    incognito_descr = " incognito"
                elif incognito_counter > 0:
                    incognito_descr = " incognito(%d)" % incognito_counter
                entity[INCOGNITO] = incognito_descr

        return entities
    #- Fine Metodo -


class FindEntitySuperclass(object):
    """
    Questa classe estende la classe Entity.
    """
    ENTITY_TABLES = ["items", "mobs", "players"]

    def find_entity(self, argument, quantity=1, location=None, entity_tables=None, compare_functions=None, avoid_inventory=False, avoid_equipment=True, avoid_doors=True):
        """
        Cerca e ritorna una entità corrispondente con l'argomento passato alla
        locazione voluta.
        entity_tables è una lista di stringhe, tali stringhe possono essere al
        massimo tre: players, mobs e items, l'entità viene cercata tra le varie
        tipologie di entità a seconda dell'ordine passato in questa lista.
        Il parametro location è un'entità o room dove cercare oppure None per
        cercare in tutto il mondo del gioco.
        """
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return None

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        # -------------------------------------------------------------------------

        if not entity_tables:
            entity_tables = self.ENTITY_TABLES

        if not compare_functions:
            compare_functions = [is_same, is_prefix]

        # Permette la ricerca numerica di una entità. Per intenderci con
        # 3.spada verrebbe raccolta la terza spada trovata
        original_argument = argument
        number, argument = number_argument(argument)
        number_used = True
        if not argument:
            number = 1
            argument = original_argument
            # Per evitare che vengano ricercati mob a caso anche nella stanza
            # ma solo su tutto il database ordinato viene aggiunta questa flag
            number_used = False

        if self.trust > TRUST.PLAYER:
            find_entity_handler_function = _find_entity_handler_for_admin
        else:
            find_entity_handler_function = _find_entity_handler

        # Esegue la ricerca tramite le funzioni di compare volute
        for compare_function in compare_functions:
            # Se la locazione è una stanza, area o mud cerca prima di tutto
            # nella stanza in cui si trova l'entità e poi nell'eventuale resto
            if (not location and not number_used) or (location and location.IS_AREA and self.location.area == location):
                entities = []
                for en in self.location.get_list_of_entities(self, entity_tables, include_looker=True, avoid_inventory=avoid_inventory, avoid_equipment=avoid_equipment, avoid_doors=avoid_doors):
                    entities.append(en[INSTANCE])
                    entities.extend(en[ENTITIES])
                discovered = find_entity_handler_function(self, argument, entities, number, compare_function, avoid_inventory, avoid_equipment, avoid_doors=avoid_doors)
                if discovered:
                    if quantity == 0:
                        return discovered
                    else:
                        return discovered.split_entity(quantity)

            if location:
                entities = []
                for en in location.get_list_of_entities(self, entity_tables, include_looker=True, avoid_inventory=avoid_inventory, avoid_equipment=avoid_equipment, avoid_doors=avoid_doors):
                    entities.append(en[INSTANCE])
                    entities.extend(en[ENTITIES])
            else:
                # Cerca tutte le tipologie di entità nell'ordine passato
                for entity_table in entity_tables:
                    # Vengono ordinate per rendere più friendly il goto, che
                    # altrimenti riceve risultati differenti ogni volta che
                    # si riavvia il gioco
                    entities = sorted(database[entity_table].values(), key=lambda en: en.code)

            discovered = find_entity_handler_function(self, argument, entities, number, compare_function, avoid_inventory, avoid_equipment, avoid_doors=avoid_doors)
            if discovered:
                if quantity == 0:
                    return discovered
                else:
                    return discovered.split_entity(quantity)

        # Se non ha trovato nulla arriva fin qui
        return None
    #- Fine Funzione -

    def find_entity_extensively(self, argument, quantity=1, entity_tables=None, inventory_pos="", direct_search=True, reverse_search=True, avoid_inventory=False, avoid_equipment=False, avoid_doors=False):
        """
        Esegue una ricerca standard, di una entità corrispondente all'argomento
        passato, il più estensivamente possibile.
        reverse_search serve a indicare se cercare anche le porte dall'altra
        parte o meno.
        """
        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        # ---------------------------------------------------------------------

        if not entity_tables:
            entity_tables = self.ENTITY_TABLES

        original_argument = argument

        if inventory_pos == "first":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_same, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        # Prima esegue una ricerca esatta di tutte le entità attorno
        target = self.find_entity(argument, quantity, self.location, entity_tables, [is_same, ], avoid_inventory, avoid_equipment, avoid_doors)
        if target:
            if quantity == 0:
                return target
            else:
                return target.split_entity(quantity)

        if inventory_pos == "":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_same, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        if self.trust >= TRUST.MASTER:
            find_entity_handler_function = _find_entity_handler_for_admin
        else:
            find_entity_handler_function = _find_entity_handler

        if not avoid_doors:
            doors = []
            if self.location.IS_ROOM:
                # (TD) se ci sarà il sistema di più uscite per stanza qui bisognerà
                # utilizzare una get_exit, per supportare i vari 1.nord 2.nord, al
                # posto della get_direction (idem per il codice simile sottostante)
                direction = get_direction(argument, exact=True)
                if direction != DIR.NONE:
                    door = self.location.get_door(direction, direct_search, reverse_search)
                    if door and DOOR.NO_USE_DIR not in door.door_type.flags:
                        return door

                for direction in self.location.exits:
                    door = self.location.get_door(direction, direct_search, reverse_search)
                    if door:
                        doors.append(door)

                if doors:
                    number, argument = number_argument(argument)
                    target = find_entity_handler_function(self, argument, doors, number, is_same, avoid_inventory, avoid_equipment, avoid_doors)
                    if target:
                        return target

        if inventory_pos == "last":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_same, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        # Poi esegue una ricerca prefissa delle entità attorno
        argument = original_argument

        if inventory_pos == "first":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_prefix, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        target = self.find_entity(argument, quantity, self.location, entity_tables, [is_prefix, ], avoid_inventory, avoid_equipment, avoid_doors)
        if target:
            if quantity == 0:
                return target
            else:
                return target.split_entity(quantity)

        if inventory_pos == "":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_prefix, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        if not avoid_doors:
            # find_entity_handler_function e doors le deve aver già ricavate
            # precedentemente
            if self.location.IS_ROOM:
                direction = get_direction(argument, exact=False)
                if direction != DIR.NONE:
                    door = self.location.get_door(direction, direct_search, reverse_search)
                    if door and DOOR.NO_USE_DIR not in door.door_type.flags:
                        return door

                if doors:
                    number, argument = number_argument(argument)
                    target = find_entity_handler_function(self, argument, doors, number, is_prefix, avoid_inventory, avoid_equipment, avoid_doors)
                    if target:
                        return target

        if inventory_pos == "last":
            target = self.find_entity(argument, quantity, self, entity_tables, [is_prefix, ], avoid_inventory, avoid_equipment, avoid_doors)
            if target:
                if quantity == 0:
                    return target
                else:
                    return target.split_entity(quantity)

        return None
    #- Fine Funzione -

    def find_entity_from_args(self, arg, argument, quantity=1, location=None, entity_tables=None):
        """
        Serve a trovare un'entità nell'inventario di self a seconda degli
        argomenti passati.
        Se vi è un solo argomento allora prende quello (look target).
        Se ve ne sono due allora prende il secondo (look extra target).
        Se si passa il parametro location allora viene utilizzata la find_entity
        e non la find_entity_extensively.
        """
        if not arg:
            log.bug("arg non è un parametro valido: %r" % arg)
            return None, "", ""

        if not argument and argument != "":
            log.bug("argument non è un parametro valido: %r" % argument)
            return None, "", ""

        if quantity < 0:
            log.bug("quantity non è un parametro valido: %d" % quantity)
            return

        # -------------------------------------------------------------------------

        if not entity_tables:
            entity_tables = self.ENTITY_TABLES

        if not argument:
            target_argument = arg
            extra_argument = ""
        else:
            target_argument = argument
            extra_argument = arg

        if is_same(target_argument, ("me", "self")):
            target = self
        else:
            if location:
                target = self.find_entity(target_argument, quantity=quantity, location=location, entity_tables=entity_tables)
            else:
                target = self.find_entity_extensively(target_argument, quantity=quantity, entity_tables=entity_tables)

        #global get_direction
        #if not get_direction:
        #    from src.room import get_direction

        # Se il target è una porta aperta ricavata tramite una direzione allora
        # dà la precedenza all'uscita e non alla porta
        if (target and target.door_type and DOOR.CLOSED not in target.door_type.flags
        and get_direction(target_argument, exact=False) != DIR.NONE):
            return None, target_argument, extra_argument

        if quantity == 0:
            return target, target_argument, extra_argument
        else:
            return target.split_entity(quantity) if target else None, target_argument, extra_argument
    #- Fine Funzione -

    def find_equipped_entity(self, argument, location, entity_tables=None, compare_functions=None):
        """
        Cerca e ritorna una entità corrispondente con l'argomento passato al
        l'equipaggiamento della locazione voluta.
        """
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return None

        if not location:
            log.bug("location passato non è un parametro valido: %r (argument %r)" % (location, argument))
            return None

        # -------------------------------------------------------------------------

        if not entity_tables:
            entity_tables = self.ENTITY_TABLES

        if not compare_functions:
            compare_functions = [is_same, is_prefix]

        number, argument = number_argument(argument)

        if self.trust >= TRUST.MASTER:
            find_entities_handler_function = _find_entities_handler_for_admin
        else:
            find_entities_handler_function = _find_entities_handler

        for compare_function in compare_functions:
            for entity_type in entity_tables:
                founded_entities = find_entities_handler_function(self, argument, getattr(location, entity_type), compare_function, avoid_inventory=True, avoid_equipment=False, avoid_doors=True)
                if founded_entities:
                    break

        if not founded_entities:
            return None
        if number - 1 > len(founded_entities):
            return None

        # Una volta trovata la lista delle potenziali entità corrispondenti
        # le riordina in maniera tale da tenere in testa quelle relative
        # alle parti del corpo più utilizzate: le mani e le entità sopra ad altre
        ordered_entities = []
        for e in reversed(founded_entities):
            if PART.WIELD in e.wear_mode:
                ordered_entities.append(e)
                founded_entities.remove(e)
        for e in reversed(founded_entities):
            if PART.HOLD in e.wear_mode:
                ordered_entities.append(e)
                founded_entities.remove(e)
        for e in reversed(founded_entities):
            if e.under_weared and e.under_weared():
                ordered_entities.append(e)
                founded_entities.remove(e)
        ordered_entities += founded_entities

        # (TT) per ora invio il number al posto del counter che supporterò solo
        # se servirà realmente, e ne dubito visto che queste sono entità
        # equipaggiate e quindi la quantity è sempre 1
        return ordered_entities[number - 1]
    #- Fine Funzione -

    def find_room(self, argument):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return None

        # ---------------------------------------------------------------------

        number, argument = number_argument(argument)

        counter = 1
        if self.trust >= TRUST.MASTER:
            for room_code in database["rooms"]:
                if is_same(argument, room_code):
                    if counter == number:
                        return database["rooms"][room_code]
                    counter += 1

        counter = 1
        for room in database["rooms"].itervalues():
            if is_same(argument, room.get_name(looker=self)):
                if counter == number:
                    return room
                counter += 1

        # ---------------------------------------------------------------------

        counter = 1
        if self.trust >= TRUST.MASTER:
            for room_code in database["rooms"]:
                if is_prefix(argument, room_code):
                    if counter == number:
                        return database["rooms"][room_code]
                    counter += 1

        counter = 1
        for room in database["rooms"].itervalues():
            if is_prefix(argument, room.get_name(looker=self)):
                if counter == number:
                    return room
                counter += 1

        # ---------------------------------------------------------------------

        counter = 1
        if self.trust >= TRUST.MASTER:
            for room_code in database["rooms"]:
                if is_infix(argument, room_code):
                    if counter == number:
                        return database["rooms"][room_code]
                    counter += 1

        counter = 1
        for room in database["rooms"].itervalues():
            if is_infix(argument, room.get_name(looker=self)):
                if counter == number:
                    return room
                counter += 1

        return None
    #- Fine Metodo -

    def find_proto(self, argument, entity_tables=None, compare_functions=None):
        if not argument:
            log.bug("argument non è un parametro valido: %r" % argument)
            return None

        # -------------------------------------------------------------------------

        if not entity_tables:
            entity_tables = self.ENTITY_TABLES

        if self.trust < TRUST.MASTER:
            log.bug("I personaggi con trust normale non possono entrare in questa funzione.")
            return None

        for entity_type in entity_tables:
            if entity_type not in ("proto_mobs", "proto_items"): #, "proto_rooms"):
                log.bug("Impossibile cercare un prototipo nel database %s" % entity_type)
                return None

        if not compare_functions:
            compare_functions = [is_same, is_prefix, is_suffix, is_infix]

        # Permette la ricerca numerica di una entità. Per intenderci con
        # 3.spada verrebbe raccolta la terza spada trovata
        original_argument = argument
        number, argument = number_argument(argument)
        if not argument:
            number = 1
            argument = original_argument

        # Esegue la ricerca tramite le funzioni di compare volute
        for compare_function in compare_functions:
            counter = 1
            # Cerca tutte le tipologie di entità nell'ordine passato
            for entity_type in entity_tables:
                # Controlla se il dato è compatibile
                for data in database[entity_type].itervalues():
                    keywords = data.get_keywords(self)
                    if compare_function(argument, keywords) or compare_function(argument, data.code) or compare_function(argument, data.code.split("#")[0]):
                        if counter == number:
                            return data
                        counter += 1

        return None
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def _find_entity_handler(entity, argument, list_to_search, number, compare_function, avoid_inventory=False, avoid_equipment=True, avoid_doors=False):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return None

    if not list_to_search and list_to_search != []:
        log.bug("list_to_search non è valido: %r" % list_to_search)
        return None

    if number <= 0:
        log.bug("number non è un parametro valido: %r" % number)
        return None

    if not compare_function:
        log.bug("compare_function non è un parametro valido: %r" % compare_function)
        return None

    # -------------------------------------------------------------------------

    counter = 0
    for target in list_to_search:
        if avoid_inventory and len(target.wear_mode) == 0:
            continue
        if avoid_equipment and len(target.wear_mode) != 0:
            continue
        if avoid_doors and target.door_type and target.is_hinged():
            continue
        if not entity.can_see(target):
            continue

        keywords = target.get_keywords_attr(entity)
        if not keywords:
            log.bug("target %s senza keywords valide: %s" % (target.code, keywords))
            continue

        if compare_function(argument, multiple_arguments(keywords)):
            if counter + target.quantity >= number:
                return target
            counter += target.quantity

    return None
#- Fine Funzione -


def _find_entity_handler_for_admin(entity, argument, list_to_search, number, compare_function, avoid_inventory=False, avoid_equipment=True, avoid_doors=False):
    """
    Per velocizzare la find_entity, che con parametro location passato a Null
    può arrivare a rallentamenti notevoli, è stata creata questa copia dalla
    _find_entity_handler con un check aggiuntivo che riguarda solo gli admin.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return None

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)  # (TT) questo test potrebbe non servire
        return None

    if not list_to_search and list_to_search != []:
        log.bug("list_to_search non è valido: %r" % list_to_search)
        return None

    if number <= 0:
        log.bug("number non è un parametro valido: %r" % number)
        return None

    if not compare_function:
        log.bug("compare_function non è un parametro valido: %r" % compare_function)
        return None

    # -------------------------------------------------------------------------

    counter = 0
    for target in list_to_search:
        if avoid_inventory and len(target.wear_mode) == 0:
            continue
        if avoid_equipment and len(target.wear_mode) != 0:
            continue
        if avoid_doors and target.door_type and target.is_hinged():
            continue
        if not entity.can_see(target):
            continue

        keywords = target.get_keywords_attr(entity)
        if not keywords:
            log.bug("target %s senza keywords valide: %s" % (target.code, keywords))
            continue

        if compare_function(argument, multiple_arguments(keywords)) or is_same(argument, target.code) or is_prefix(argument + "#", target.code):
            if counter + target.quantity >= number:
                return target
            counter += target.quantity

    return None
#- Fine Funzione -


def _find_entities_handler(entity, argument, list_to_search, compare_function, avoid_inventory, avoid_equipment, avoid_doors):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return []

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return []

    if not list_to_search and list_to_search != []:
        log.bug("list_to_search non è valido: %r" % list_to_search)
        return []

    if not compare_function:
        log.bug("compare_function non è un parametro valido: %r" % compare_function)
        return []

    # avoid_inventory e avoid_equipment e avoid_doors hanno valore di verità

    # -------------------------------------------------------------------------

    entities = []

    for target in list_to_search:
        if avoid_inventory and len(target.wear_mode) == 0:
            continue
        if avoid_equipment and len(target.wear_mode) != 0:
            continue
        if not avoid_equipment and target.under_weared and target.under_weared():
            continue
        if avoid_doors and target.door_type and target.is_hinged():
            continue
        if not entity.can_see(target):
            continue

        keywords = target.get_keywords_attr(entity)
        if not keywords:
            log.bug("target %s senza keywords valide: %s" % (target.code, keywords))
            continue

        if compare_function(argument, multiple_arguments(keywords)):
            entities.append(target)

    return entities
#- Fine Funzione -


def _find_entities_handler_for_admin(entity, argument, list_to_search, compare_function, avoid_inventory=False, avoid_equipment=True, avoid_doors=False):
    """
    Per velocizzare la find_entity, che con parametro location passato a Null
    può arrivare a rallentamenti notevoli, è stata creata questa copia dalla
    _find_entity_handler con un check aggiuntivo che riguarda solo gli admin.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return []

    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)  # (TT) questo test potrebbe non servire
        return []

    if not list_to_search and list_to_search != []:
        log.bug("list_to_search non è valido: %r" % list_to_search)
        return []

    if not compare_function:
        log.bug("compare_function non è un parametro valido: %r" % compare_function)
        return []

    # -------------------------------------------------------------------------

    entities = []

    for target in list_to_search:
        if avoid_inventory and len(target.wear_mode) == 0:
            continue
        if avoid_equipment and len(target.wear_mode) != 0:
            continue
        if avoid_doors and target.door_type and target.is_hinged():
            continue
        if not entity.can_see(target):
            continue

        keywords = target.get_keywords_attr(entity)
        if not keywords:
            log.bug("target %s senza keywords valide: %s" % (target.code, keywords))
            continue

        if compare_function(argument, multiple_arguments(keywords)) or is_same(argument, target.code):
            entities.append(target)

    return entities
#- Fine Funzione -
