# -*- coding: utf-8 -*-

"""
Modulo per la gestione di un dato, cioè di una classe generica di informazioni
caricate da file testuale caricato e gestita dal database.
"""

#= IMPORT ======================================================================

import os
import weakref

from src.color      import remove_colors
from src.engine     import engine
from src.gamescript import check_trigger
from src.log        import log


#= CLASSI ======================================================================

# (TD) pensare se spostare anche la fread ef fwrite dal modulo di database
class Data(object):
    def add_proto_reference(self):
        if not hasattr(self, "prototype"):
            return

        from src.database import database

        if not self.PRIMARY_KEY in self.__dict__:
            log.bug("Non è stato potuto ricavare la chiave primaria %r del dato %r." % (
                self.PRIMARY_KEY, self))

        primary_key = self.__dict__[self.PRIMARY_KEY]
        if not primary_key:
            log.bug("primary_key %r non valida per il dato %r" % (primary_key, self))
            return

        sharp_position = primary_key.rfind("#")
        if sharp_position <= -1:
            log.bug("sharp_position non è valido: %r per il dato %r con primary_key %r" % (
                sharp_position, self, primary_key))
            return

        proto_code = primary_key[0 : sharp_position]
        if not proto_code:
            log.bug("proto_code non è valido: %r" % proto_code)
            return

        table_name = "proto_%ss" % self.__class__.__name__.lower()
        if not table_name in database:
            log.bug("Impossibile trovare la tabella %r nel database." % table_name)
            return

        if not proto_code in database[table_name]:
            log.bug("Impossibile trovare il codice %r nella tabella %s del database" % (
                proto_code, table_name))
            return

        proto_data = database[table_name][proto_code]
        if not proto_data:
            log.bug("proto_data non è valido: %r con il codice %r" % (proto_data, proto_code))
            return

        setattr(self, "prototype", proto_data)
    #- Fine Metodo -

    def add_location_reference(self):
        for entity in self.iter_contains():
            entity.location = self
    #- Fine Metodo -

    def add_door_reference(self):
        if not self.IS_ROOM:
            return

        for exit in self.exits.itervalues():
            if not exit.door:
                continue
            # Caso particolare per l'inserimento on the fly di porte non
            # prototipo, cioè quelle già resettate
            door_code = exit.door
            exit.door = _search_the_reference("exits[%s]" % exit.direction, exit.door, ["items", "mobs", "players"], "exit.door")
            if not exit.door:
                log.bug("Non è stato possibile trovare il riferimento alla porta %s per la stanza %s all'uscita %s" % (door_code, self.code, exit.direction))
                continue
            exit.door.area = self.area
            getattr(self.area, exit.door.ACCESS_ATTR).append(exit.door)
    #- Fine Metodo -

    def check_references(self):
        if not self.IS_ACTOR:
            return True

        if self.location and self not in getattr(self.location, self.ACCESS_ATTR):
            log.bug("(%s) ERRORE DI RIFERIMENTO LOCATION %s MA %s NON SI TROVA LÌ DENTRO (ultimo comando inviato da %s: %s)" % (
                self.ACCESS_ATTR, self.location.code, self.code, engine.last_input_sender.code, engine.last_input_sended))
            return True

        return False
    #- Fine Metodo -

    def refresh_global_quantity(self):
        if not self.prototype:
            log.bug("Il dato %s non possiede un prototipo valido: %r" % (self.code, self.prototype))
            return

        self.prototype.current_global_quantity += self.quantity
    #- Fine Metodo -

    # (TD) invece di utilizzare questa lista in place degli attributi magari
    # utilizzare una variabile di schema apposita oppure
    def spelling(self, dictionary=None, typos_file=None):
        if dictionary is None or typos_file is None:
            from src.database import database
            if not dictionary:
                dictionary = database.spelling_dictionary
            if not typos_file:
                typos_file = database.load_typos_file()

        for attr_name in ("descr", "descr_night", "descr_hearing", "descr_hearing_night", "descr_smell", "descr_smell_night", "descr_touch", "descr_touch_night", "descr_taste", "descr_taste_night", "descr_sixth", "descr_sixth_night"):
            text = getattr(self, attr_name)
            if not text:
                continue
            text = remove_colors(text)
            if not text:
                log.bug("testo dell'attributo %s del dato %s con solo il colore" % (attr_name, self.code))
                continue
            if "$o" in text:
                text = text.replace("$o", "o")
            if "$O" in text:
                text = text.replace("$O", "o")

            words = text.split()
            for word in reversed(words):
                if "'" in word and word[0] != "'" and word[-1] != "'":
                    if word.lower() != "po'":
                        words.remove(word)
                        words += word.split("'")

            for word in words:
                word = word.rstrip(",;.!?")
                if not word:
                    log.bug("Punteggiatura isolata per l'attributo %s al dato %s" % (attr_name, self.code))
                    continue
                if not word.isalpha():
                    continue
                if word not in dictionary:
                    word = word.lower()
                    if word not in dictionary:
                        typos_file.write("%s (%s)\n" % (word, self.code))
    #- Fine Metodo -

    def check_max_global_quantity(self):
        from src.database import database

        if self.max_global_quantity <= 0:
            return

        code = self.code + "#"
        counter = 0
        for en in database[self.ACCESS_ATTR.replace("proto_", "")].itervalues():
            if en.code.startswith(code):
                counter += en.quantity

        if counter > self.max_global_quantity:
            log.booting("Il prototipo %s si trova istanziato %d volte ma il suo massimo sarebbe %d" % (
                self.code, counter, self.max_global_quantity))
    #- Fine Metodo -

    def check_for_icon_files(self):
        for attr_name in ("icon", "icon_night"):
            path = getattr(self, attr_name)
            if path and not os.path.isfile("www/" + path):
                log.booting("File d'immagine inesistente per l'%s: %s" % (
                    attr_name, "www/" + path))
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def link_the_references(obj, path):
    """
    Converte alcune stringhe in riferimenti ad istanze di dati.
    Si avvale degli attributi SCHEMA, REFERENCES e WEAKREFS di ogni dato per
    ricavare i riferimenti ad altri dati in maniera corretta.
    """
    if not obj:
        log.bug("obj non è un parametro valido: %s" % obj)
        return

    if not path:
        log.bug("path non è un parametro valido: %s" % path)
        return

    # -------------------------------------------------------------------------

    for attr_name, attr_value in obj.__dict__.iteritems():
        if attr_name[0] == "_" or attr_name in obj.VOLATILES:
            continue

        # Cerca eventuali riferimenti da collegare alle istanze nei dati che
        # si rifanno a delle classi con altri attributi (che quindi hanno un
        # modulo da dove reperirle)
        if attr_name in obj.SCHEMA and obj.SCHEMA[attr_name][0]:
            if isinstance(attr_value, list):
                for i, sub_value in enumerate(attr_value):
                    sub_path = "%s.%s[%s]" % (path, attr_name, i)
                    link_the_references(sub_value, sub_path)
            elif isinstance(attr_value, dict):
                for key, sub_value in attr_value.iteritems():
                    sub_path = "%s.%s[%s]" % (path, attr_name, repr(key))
                    link_the_references(sub_value, sub_path)
            elif attr_value:
                link_the_references(attr_value, "%s.%s" % (path, attr_name))

        # Se la variabile si trova nel dizionario REFERENCES della classe
        # allora probabilmente è un dato precedentemente acquisito come
        # stringa ma che deve essere convertito al riferimento di dato
        elif attr_name in obj.REFERENCES or attr_name in obj.WEAKREFS:
            # La variabile di riferimento può benissimo essere None, già di
            # default è così, significa che non ha trovato nessuna etichetta
            # relativa nel file del dato, questo è normale per etichette
            # facoltative
            if attr_value is None:
                continue

            # Se la variabile si trova nel dizionario WEAKREFS della classe
            # si comporta come una variabile relativa alle REFERENCES
            # tuttavia se questa viene rimossa dal gioco il riferimento
            # debole va a mancare automaticamente
            if attr_name in obj.WEAKREFS:
                table_names = obj.WEAKREFS[attr_name]
            else:
                # Le tabelle per la ricerca del riferimento possono essere più
                # d'una, ognuna delle quali però deve possere delle chiavi
                # differenti tra loro (come per esempio il database dei mob
                # e quello degli oggetti)
                table_names = obj.REFERENCES[attr_name]

            # Se var è una stringa allora cerca il riferimento tra le tabelle
            if isinstance(attr_value, basestring):
                var = _search_the_reference(attr_name, attr_value, table_names, path)
                if var and attr_name in obj.WEAKREFS:
                    setattr(obj, attr_name, weakref.ref(var or None))
                else:
                    setattr(obj, attr_name, var or None)
            # Se var è una lista allora deve trovare tutti i riferimenti di
            # ogni elemento che sono identificati da un codice-stringa
            elif type(attr_value) == list:
                new_list = []
                for v in attr_value:
                    value = _search_the_reference(attr_name, v, table_names, path)
                    if value:
                        if attr_name in obj.WEAKREFS:
                            new_list.append(weakref.ref(value))
                        else:
                            new_list.append(value)
                setattr(obj, attr_name, new_list)
            elif type(attr_value) == dict:
                # (TD)
                raise NotImplementedError
#- Fine Funzione -

def _search_the_reference(attr_name, attr_value, table_names, path):
    if not attr_name:
        log.bug("attr_name non è un parametro valido: %r" % attr_name)
        return None

    if not attr_value:
        log.bug("attr_value non è un parametro valido: %r" % attr_value)
        return None

    if not table_names:
        log.bug("table_names non è un parametro valido: %r" % table_names)
        return None

    if not path:
        log.bug("path non è un parametro valido: %r" % path)
        return None

    # -------------------------------------------------------------------------

    from src.database import database

    if not isinstance(table_names, list):
        log.bug("table_names, con attr_name %s, attr_value %r e path %s, dev'essere una lista ed invece è: %r" % (
            attr_name, attr_value, path, table_names))
        return None

    for table_name in table_names:
        if attr_value in database[table_name]:
            return database[table_name][attr_value]

    # (bb) qui, nella lettura dei riferimenti per le liste e le tuple,
    # vengono passati a volte delle entità già referenziate e non delle
    # stringhe.. E' come se il link_the_references al tal dato venga
    # effettuato due volte tuttavia non ho ancora trovato come e dove..
    # quindi per ora vengono effettuati dei controlli aggiuntivi per
    # ritornare il riferimento stesso
    for table_name in table_names:
        if attr_value in database[table_name].values():
            return attr_value

    if isinstance(attr_value, basestring):
        primary_key = attr_value
    else:
        primary_key = getattr(attr_value, attr_value.PRIMARY_KEY)

    log.bug("Non è stato trovato nessun riferimento a %r per l'attributo %s, con primary_key %r, %s database %r alla path %r. *ERRORE CRITICO*" % (
        attr_value, attr_name, primary_key, "nel" if len(table_names) == 1 else "nei", table_names, path))
    engine.critical_errors += 1
    return None
#- Fine Funzione -
