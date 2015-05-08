# -*- coding: utf-8 -*-

"""
Modulo per la gestione del database e della persistenza tramite semplici file
testuali.
Tutti i file gestiti con il database si trovano nelle cartelle data/ oppure
persistence/, questi vengono caricati dal metodo db.load(), ogni singolo file
è caricato con la funzione fread() e salvato con la funzione fwrite().
"""


#= IMPORT ======================================================================

import datetime
import os
import sys
import tarfile
import time
import traceback
import types

from src.affect  import apply_all_affects, remove_all_affects
from src.color   import colors, close_color, check_colors, remove_colors
from src.element import EnumElement, fread_enum_element
from src.engine  import engine
from src.enums   import DOOR, ENTITYPE, FLAG, LOG, RACE
from src.log     import log
from src.utility import (is_same, to_capitalized_words, get_index_of_shortest_string, 
                         iter_files, is_number, create_folders)


#= COSTANTI ====================================================================

# Lista delle unità di misura relative alla lunghezza
UM_LENGTHS = ["cm", "m", "km"]

# Lista delle unità di misura relative al peso
UM_WEIGHTS = ["g", "kg", "q", "t"]


MODULE_NAME = 0
CLASS_NAME  = 1
FOLDER      = 2  # Nome della directory in cui vengono salvati sotto quella /data/
SUBFOLDER   = 3  # I dati di quel tipo verranno suddivisi creando delle sottocartelle relative all'attributo in questo campo
IMPORT      = 4  # Indica come importare la lista delle subfolder

# Lista dei caratteri invisibili che non devono esistere nelle stringhe; tutti
# tranne l'orizontal tab, il line feed e il carriage return
UNALLOWED_CHARS = []
ordinals = range(32)
ordinals.remove(9)
ordinals.remove(10)
ordinals.remove(13)
for ordinal in ordinals:
    UNALLOWED_CHARS.append(chr(ordinal))


#= CLASSI ======================================================================

class Database(dict):
    """
    Classe per la gestione del database.
    """
    reference_error_found  = False  # Indica se è stato trovato un errore relativo ai riferimenti
    avoid_backup_on_shutdown = False
    avoid_save_on_shutdown   = False
    only_player_persistence  = False

    # (bb) Le tabelle sarebbero elencate in ordine del caricamento voluto,
    # ovviamente però l'ordine viene gestito poi visto che non è un ordered dict
    TABLES = {
        #                MODULE_NAME,     CLASS_NAME    FOLDER                  SUBFOLDER  IMPORT
        "areas"       : ("src.area",      "Area",       "data/areas",           "",        ""),
        "proto_rooms" : ("src.room",      "ProtoRoom",  "data/proto_rooms",     "area",    "primary-key-piece"),
        "proto_mobs"  : ("src.mob",       "ProtoMob",   "data/proto_mobs",      "area",    "primary-key-piece"),
        "proto_items" : ("src.item",      "ProtoItem",  "data/proto_items",     "area",    "primary-key-piece"),
        "accounts"    : ("src.account",   "Account",    "persistence/accounts", "",        ""),
        "bugs"        : ("src.note",      "Bug",        "persistence/bugs",     "",        ""),
        "commands"    : ("src.command",   "Command",    "data/commands",        "",        ""),
        "comments"    : ("src.note",      "Comment",    "persistence/comments", "",        ""),
        "fights"      : ("src.fight",     "Fight",      "persistence/fights",   "",        ""),
        #"groups"      : ("src.group",     "Group",      "persistence/groups",  "",        ""),
        "ideas"       : ("src.note",      "Idea",       "persistence/ideas",    "",        ""),
        "items"       : ("src.item",      "Item",       "persistence/items",    "area",    "code"),
        "helps"       : ("src.help",      "Help",       "data/helps",           "type",    "src.enums.HELP"),
        "mobs"        : ("src.mob",       "Mob",        "persistence/mobs",     "area",    "code"),
        "news"        : ("src.new",       "New",        "persistence/news",     "",        ""),
        "players"     : ("src.player",    "Player",     "persistence/players",  "account", "code"),
        #"quests"      : ("src.quest",     "Quest",      "data/quests",         "",        ""),
        #"recipes"     : ("src.recipe",    "Recipe",     "data/recipes",        "",        ""),
        "rooms"       : ("src.room",      "Room",       "persistence/rooms",    "area",    "code"),
        "socials"     : ("src.social",    "Social",     "data/socials",         "",        ""),
        "typos"       : ("src.note",      "Typo",       "persistence/typos",    "",        "")
        }

    def __init__(self):
        self.reading_data_code   = ""  # Indica il codice dell'ultimo dato letto, serve in casi particolari di caricamento dei dati
        self.spelling_dictionary = {}  # Dizionario contenente tutte le parole italiane da utilizzare per il controllore ortografico
        self.randomizable_codes  = []  # Lista delle entità inseribili in gioco in maniera casuale, come per le entità trovate tramite lo scavare (TD) bisognerà aggiungere dinamicamente eventuali entità randomizable create online
        self.race_money_codes    = []  # Lista delle monete delle varie razze utilizzate principalmente in gioco
        self.seed_codes          = []  # Lista di tutti i semi del database, così da poterli inserire casualmente in gioco (TD) bisognerà aggiungere dinamicamente eventuali entità randomizable create online

        # Inizializza le varie tabelle con dei dizionari
        for table_name in self.TABLES:
            self[table_name] = {}
    #- Fine Inizializzazione -

    def load(self, use_spelling=False):
        log.booting("Carica tutti i dati del Database")
        self.load_datas()

        log.booting("Converte alcune stringhe in riferimenti ad istanze di dato")
        self.convert_string_to_references()

        log.booting("Aggiunge il riferimento del prototipo ai dati che ne abbisognano")
        self.add_proto_references()

        log.booting("Aggiunge ad ogni dato di gioco il riferimento della loro entità che li contiene")
        self.add_location_references()

        log.booting("Aggiunge i riferimenti globali alle porte caricate dalla persistenza")
        self.add_door_references()

        log.booting("Controlla tutti i riferimenti delle entità del gioco")
        self.check_all_references()

        log.booting("Aggiorna i current_global_quantity della persistenza già nelle aree")
        self.refresh_global_quantities()

        from src.account import add_players_to_accounts
        log.booting("Inserisce i personaggi nei rispettivi account")
        add_players_to_accounts()

        from src.command import import_modules_and_functions
        log.booting("Importa le funzioni e i moduli dei comando nei rispettivi dati di comando.")
        import_modules_and_functions()

        if use_spelling:
            log.booting("Esegue lo spelling delle stringhe di tutto il database")
            database.spelling()

        log.booting("Procede ad un'eventuale conversione di alcuni dati.")
        self.convert()

        log.booting("Controlla tutti i dati del database.")
        self.check_for_error_messages()

        log.booting("Controlla le funzioni di comando duplicate o inesistenti negli input.")
        from command import check_commands_fun_name
        check_commands_fun_name()

        log.booting("Rimozione dei dati zombie senza alcun tipo di locazione valida")
        self.remove_datas_without_location()

        log.booting("Controlla che eventuali valori di MaxGlobalQuantity non siano stati superati.")
        self.check_max_global_quantities()

        log.booting("Controlla l'esistenza sul disco delle icone definite nelle varie entità.")
        self.check_for_all_icon_files()

        # (TD) Disattivato perché troppo cpu-intensive
        #log.booting("Controlla tutte le stringhe del database.")
        #for table_name, data_code, data in self.walk_datas():
        #    _check_all_strings(table_name, data_code, data)

        log.booting("Inizializza la lista delle entità randomizzabili")
        self.create_randomizable_list()

        log.booting("Inizializza la lista delle monete principalmente utilizzate dalle varie razze")
        self.create_race_money_list()

        log.booting("Inizializza la lista dei semi di tutto il database")
        self.create_seed_list()

        log.booting("È stato eseguito con successo il caricamento ed il controllo del database")

        # Questa parte di codice serve semplicemente per sapere quanto occupano
        # in bytes le stringhe di gioco, giusto così, per curiosità
        #total = 0
        #for table_name in ("proto_rooms", "proto_items", "proto_mobs"):
        #    for data in self[table_name].itervalues():
        #        for attr_name in data.__dict__:
        #            if attr_name in data.MULTILINES:
        #                total += len(getattr(data, attr_name))
        #print total
        #import sys
        #sys.exit(0)
    #- Fine Metodo -

    def load_datas(self):
        # Prepara la lista dei dati da caricare mettendo in testa i prototipi
        tables = sorted(self.TABLES.keys())
        tables.remove("areas")
        tables.remove("proto_rooms")
        tables.remove("proto_mobs")
        tables.remove("proto_items")

        # Esegue quindi il caricamento dei dati
        for table_name in ["areas", "proto_rooms", "proto_mobs", "proto_items"] + tables:
            if engine.options.restart_from_proto and table_name in ["rooms", "mobs", "items"]:
                continue
            log.booting("-> %s" % table_name)
            folder = self.TABLES[table_name][FOLDER]
            if not create_folders(folder):
                log.bug("Non è possibile creare la cartella %s" % folder)
                continue

            data_counter = 0
            for root, dirs, files in os.walk(folder):
                # Se c'è qualcosa nel campo di SUBFOLDER allora salta i dati
                # nella folder per leggere invece quelli delle sottocartelle
                # Al contrario se SUBFOLDER è una stringa vuota salta la
                # lettura di tutti gli eventuali dati nelle sottocartelle
                if self.TABLES[table_name][SUBFOLDER]:
                    if folder == root:
                        continue
                else:
                    if folder != root:
                        continue

                # Salta le cartelle sperimentali o commentate
                head, tail = os.path.split(root)
                if tail[0] == "_":
                    continue

                # Legge tutti i file che trova nelle cartelle volute saltando
                # quelli che iniziano con underscore o che non possiedono
                # l'estensione *.dat
                for filename in files:
                    if filename[0] == "_" or not filename.lower().endswith(".dat"):
                        continue
                    path = "%s/%s" % (root, filename)
                    try:
                        data_file = open(path, "r")
                    except IOError:
                        log.bug("Impossibile aprire il file %s/%s in lettura" % (root, filename))
                        continue
                    filename = os.path.splitext(filename)[0]
                    if not filename:
                        log.bug("Il nome del file %s del dato non è valido: %r" % (path, filename))
                        data_file.close()
                        continue
                    self.reading_data_code = filename

                    # Controlla che non stia caricando un dato persistente
                    # relativo a stanze, oggetti e mob che non abbia il
                    # carattere '#' nel nome
                    if table_name in ("rooms", "items", "mobs", "bugs", "ideas", "typos", "comments"):
                        if not "#" in filename:
                            log.bug("filename %s con carattere # mancante per la tabella %s alla cartella %s" % (
                                filename, table_name, root))
                            continue
                    else:
                        if "#" in filename:
                            log.bug("filename %s con carattere inatteso # per la tabella %s alla cartella %s" % (
                                filename, table_name, root))
                            continue

                    # Importa modulo e classe base del dato da leggere, ne crea
                    # uno nuovo e procede alla lettura del file con i valori
                    module_name = self.TABLES[table_name][MODULE_NAME]
                    class_name  = self.TABLES[table_name][CLASS_NAME]
                    data = fread(data_file, module_name, class_name)
                    self.add_data(data, table_name, filename, tail)
                    data_file.close()
                    data_counter += 1
            log.booting("   Caricati: %d" % data_counter)
        self.reading_data_code = ""
    #- Fine Metodo -

    def add_data(self, data, table_name, filename, area_code):
        if not data:
            log.bug("data non è un parametro valido: %r" % data)
            return

        if not table_name:
            log.bug("table_name non è un parametro valido: %r" % table_name)
            return

        if not filename:
            log.bug("filename non è un parametro valido: %r" % filename)
            return

        if not area_code:
            log.bug("area_code non è un parametro valido: %r" % area_code)
            return

        # ---------------------------------------------------------------------

        # Aggiunge il dato al database
        self[table_name][filename] = data

        if table_name in ("proto_rooms", "proto_mobs", "proto_items", "rooms", "mobs", "items"):
            if not area_code in self["areas"]:
                log.booting("Non è stata caricata o non esiste l'area %s" % area_code)
                return
            area = self["areas"][area_code]
            if table_name in ("proto_rooms", "proto_mobs", "proto_items"):
                # Letti i prototipi li inserisce ognuno nell'area di
                # riferimento
                getattr(area, table_name)[filename] = data
            elif table_name == "rooms":
                # Inserisce le istanze delle stanze nelle rispettive aree
                getattr(area, "rooms")["%d %d %d" % (data.x, data.y, data.z)] = data
            elif table_name in ("mobs", "items"):
                # Inserisce le istanze delle entità nelle rispettive aree
                getattr(area, table_name).append(data)
                if not data.area:
                    log.bug("Viene forzata l'assegnazione dell'area %s al dato %r in quanto mancante per qualche baco." % (area.code, data))
                    data.area = area
    #- Fine Metodo -

    def convert_string_to_references(self):
        from src.data import link_the_references
        from src.interpret import yield_inputs_items

        for table_name, data_code, data in self.walk_datas():
            link_the_references(data, "%s[%s]" % (table_name, data_code))

        for inputs_name, inputs in yield_inputs_items():
            for num, input in enumerate(inputs):
                link_the_references(input, "%s[%d]" % (inputs_name, num))

        # (TD) per ora il sistema è inutilizzato
        #for num, entry_word in enumerate(vocabulary):
        #    link_the_references(entry_word, "%s[%d]" % (vocabulary, num))
    #- Fine Metodo -

    def add_proto_references(self):
        """
        Aggiunge ai dati che ne abbisognano il riferimento al prototipo ricavandolo
        dal proprio codice.
        """
        for table_name in ("rooms", "items", "mobs"):
            for data in self[table_name].itervalues():
                data.add_proto_reference()
    #- Fine Metodo -

    def add_location_references(self):
        for table_name in ("rooms", "items", "mobs", "players"):
            for data in self[table_name].itervalues():
                data.add_location_reference()
    #- Fine Metodo -

    def add_door_references(self):
        for room in self["rooms"].itervalues():
            room.add_door_reference()
    #- Fine Metodo -

    def check_all_references(self):
        for table_name in ("items", "mobs"):
            for data in self[table_name].itervalues():
                error_founded = data.check_references()
                if error_founded:
                    self.reference_error_found = True
    #- Fine Metodo -

    def refresh_global_quantities(self):
        for table_name in ("items", "mobs"):
            for data in self[table_name].itervalues():
                data.refresh_global_quantity()
    #- Fine Metodo -

    def load_spelling_dictionary(self):
        self.spelling_dictionary = {}

        for file in iter_files("dicts", "dict"):
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line in self.spelling_dictionary:
                    log.bug("Parola %s nel dizionario %s già trovata in un'altro." % (line, file.name))
                else:
                    self.spelling_dictionary[line] = ""

        return self.spelling_dictionary
    #- Fine Metodo -

    def load_typos_file(self):
        typos_path = "dicts/typos.result"
        try:
            typos_file = open(typos_path, "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura." % typos_path)
            return None

        return typos_file
    #- Fine Metodo -

    def spelling(self):
        dictionary = self.load_spelling_dictionary()
        typos_file = self.load_typos_file()

        for table_name in ("proto_rooms", "proto_items", "proto_mobs"):
            for data in self[table_name].itervalues():
                data.spelling(dictionary=dictionary, typos_file=typos_file)
    #- Fine Metodo -

    def convert(self):
        """
        Questo metodo serve quando bisogna convertire uno o più tipologie di
        dato secondo un nuovo formato o azioni simili.
        """
        # (TD) fino a che non si risolve il problema del danno delle armi
        # questo pezzo di codice è meglio che rimanga
        log.convert("Converte tutti i valori di damage erronei nelle armi")
        for table_name in ("items", "mobs"):
            for data in self[table_name].itervalues():
                if not data.weapon_type:
                    continue
                if data.weapon_type.damage == 0 or data.weapon_type.damage == "0":
                    log.bug("Damage dell'arma %s non è valido: %r (viene convertito automaticamente)" % (data.code, data.weapon_type.damage))
                    if data.prototype.weapon_type:
                        data.weapon_type.damage = data.prototype.weapon_type.damage
                    else:
                        from src.fight import DAMAGES
                        data.weapon_type.damage = DAMAGES[data.weapon_type.level]
    #- Fine Metodo -

    def check_for_error_messages(self):
        """
        Controlla tutti dati del database.
        """
        # Chiama la funzione get_error_message che ogni classe di dato
        # deve possedere
        for table_name, data_code, data in self.walk_datas():
            if hasattr(data, "get_error_message"):
                data.get_error_message()
            else:
                log.booting("Il dato con classe %s non ha il metodo get_error_message" % type(data))
    #- Fine Metodo -

    def remove_datas_without_location(self):
        for table_name in ("mobs", "items"):
            for data in reversed(self[table_name].values()):
                if not data.location and not data.previous_location:
                    log.bug("-> %s" % data.code)
                    data.extract(data.quantity, use_repop=True)
    #- Fine Metodo -

    def check_max_global_quantities(self):
        for table_name in ("proto_mobs", "proto_items"):
            for data in self[table_name].itervalues():
                data.check_max_global_quantity()
    #- Fine Metodo -

    def check_for_all_icon_files(self):
        for table_name in ("proto_mobs", "proto_items", "proto_rooms", "mobs", "items", "rooms", "players"):
            for data in self[table_name].itervalues():
                data.check_for_icon_files()
    #- Fine Metodo -

    def create_randomizable_list(self):
        for table_name in ("proto_mobs", "proto_items"):
            for data in self[table_name].itervalues():
                if FLAG.RANDOMIZABLE in data.flags:
                    self.randomizable_codes.append(data.code)
    #- Fine Metodo -

    def create_race_money_list(self):
        for race in RACE.elements:
            if not race.copper_coin in self.race_money_codes:
                self.race_money_codes.append(race.copper_coin)
            if not race.silver_coin in self.race_money_codes:
                self.race_money_codes.append(race.silver_coin)
            if not race.gold_coin in self.race_money_codes:
                self.race_money_codes.append(race.gold_coin)
            if not race.mithril_coin in self.race_money_codes:
                self.race_money_codes.append(race.mithril_coin)
    #- Fine Metodo -

    def create_seed_list(self):
        for table_name in ("proto_mobs", "proto_items"):
            for data in self[table_name].itervalues():
                if data.entitype == ENTITYPE.SEED:
                    self.seed_codes.append(data.code)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def save(self):
        """
        Salva i dati relativi alla persistenza del mondo su file testuali.
        """
        log.shutdown("Crea eventuali cartelle di persistenza mancanti")
        self.create_persistence_folders()

        # Cancella quindi tutti i file relativi ai dati che si stanno per sovrascrivere
        self.remove_area_persistence(["rooms", "items", "mobs"])

        # (TD) Questa parte di codice verrà rimosso una volta creato il ciclo persistente
        log.shutdown("Rimuove le entità in purificazione")
        self.extract_purificable_entities()

        log.shutdown("Controlla ed eventualmente salva dati wrong in una cartella a parte.")
        self.check_all_wrong_datas()

        if self.avoid_save_on_shutdown:
            log.shutdown("È stato scelto di evitare il salvataggio durante lo shutdown.")
            return

        log.shutdown("Salva tutti i dati relativi alla persistenza delle aree:")
        self.save_persistent_datas()

        log.shutdown("Salva i dati relativi agli account:")
        self.save_account_datas()

        log.shutdown("Salva i dati relativi ai giocatori:")
        self.save_player_datas()

        log.shutdown("Salva i dati relativi alle news:")
        self.save_news_datas()

        log.shutdown("È stato eseguito con successo il salvataggio di persistenze, news, account e giocatori")
    #- Fine Metodo -

    def create_persistence_folders(self):
        """
        Se non esistono alcune cartelle, che alla partenza del Mud vengono
        create se mancanti, allora non prosegue con la persistenza, supponendo
        che l'admin le abbia rimosse a mano per qualche motivo, in questa
        maniera non vengono salvate solo alcune tipologie di dati
        """
        paths = ["persistence/rooms", "persistence/items", "persistence/mobs", "persistence/loops", "persistence/accounts", "persistence/players"]
        for path in paths:
            if not os.path.exists(path):
                log.bug("Non è stata trovata la cartella %s. È stata rimossa a mano durante l'esecuzione del gioco?" % path)
                return
    #- Fine Metodo -

    def remove_area_persistence(self, folders=None, message=""):
        from src.gamescript import check_trigger

        if not folders:
            folders = ["rooms", "items", "mobs"]

        log.save("Rimozione di tutti i dati relativi alla persistenza: %s" % message)
        for table_name in folders:
            log.save("-> %s" % table_name)
            for root, dirs, files in os.walk("persistence/%s" % table_name):
                for filename in files:
                    only_name, ext = os.path.splitext(filename)
                    if only_name in self[table_name]:
                        data = self[table_name][only_name]
                        check_trigger(data, "remove_persistence", data)
                    if only_name[0] == "_" or ext.lower() != ".dat":
                        continue
                    path = "%s/%s" % (root, filename)
                    try:
                        os.remove(path)
                    except:
                        log.bug("%s %s" % (sys.exc_info()[0], sys.exc_info()[1]))
                        continue
    #- Fine Metodo -

    def extract_purificable_entities(self):
        """
        Prima di salvare tutti i dati rimuove gli oggetti con purificazione
        in atto non essendo troppo utili e potenzialmente danneggiando il
        cumulo di ram utilizza e il limite di MaxGlobalQuantity.
        """
        for table_name in ("items", "mobs"):
            for data_code, data in reversed(self[table_name].items()):
                if data.deferred_purification:
                    data.stop_purification()
                    data.extract(data.quantity, use_repop=False)
    #- Fine Metodo -

    def check_all_wrong_datas(self):
        """
        Serve a salvare in una cartella a parte eventuali dati che hanno perso
        i loro riferimenti fondamentali.
        Tali dati erronei vengono rimossi dal database in maniera tale che
        nelle persistenze non vengano salvati.
        """
        already_checked_wrongs = []

        now = datetime.datetime.now()
        now = "%dy%dm%dd_%dh%dm%ds" % (now.year, now.month, now.day, now.hour, now.minute, now.second)

        # Controlla prima di tutto tra i dati del database
        for table_name in ("rooms", "items", "mobs"):
            for data_code, data in reversed(self[table_name].items()):
                self.check_wrong_data(table_name, data_code, data, now, already_checked_wrongs, "A")
                for table_name2 in ("items", "mobs"):
                    for en in data.iter_all_entities(entity_tables=[table_name2]):
                        self.check_wrong_data(table_name2, en.code, en, now, already_checked_wrongs, "B")

        # Ora esegue il controllo dal punto di vista delle aree, perché
        # potrebbe essere che alcuni dati si trovino nelle liste delle aree
        # ma non nel database
        for area in self["areas"].itervalues():
            for table_name in ("rooms", "items", "mobs"):
                if table_name == "rooms":
                    datas = area.rooms.values()
                else:
                    datas = getattr(area, table_name)
                # Qui non c'è bisogno di rimuovere i dati dalle rispettive liste
                # perché la persistenza viene salvata ciclando i dati nel database
                # e non ciclando tra le aree
                for data in datas:
                    self.check_wrong_data(table_name, data.code, data, now, already_checked_wrongs, "C")
                    for table_name2 in ("items", "mobs"):
                        for en in data.iter_all_entities(entity_tables=[table_name2]):
                            self.check_wrong_data(table_name2, en.code, en, now, already_checked_wrongs, "D")

        if already_checked_wrongs:
            log.save("    Sono stati salvati %d dati erronei nella cartella 'wrong' alla data di shutdown attuale" % len(already_checked_wrongs))
    #- Fine Metodo -

    def check_wrong_data(self, table_name, data_code, data, now, already_checked_wrongs, entry_code):
        if not table_name:
            log.bug("table_name non è un parametro valido: %r" % table_name)
            return

        if not data_code:
            log.bug("data_code non è parametro valido: %r" % data_code)
            return

        if not data:
            log.bug("data non è parametro valido: %r" % data)
            return

        if not entry_code:
            log.bug("entry_code non è un parametro valido: %r" % entry_code)
            return

        # ---------------------------------------------------------------------

        error = ""

        # Questo test vale solo per il controllo sui dati direttamente carpiti
        # dal database, altrimenti data_code e data.code sono per passaggio
        # di argomento uguali per forza
        if data_code != data.code:
            if not error:
                error = "Dato %s di tipo %s che ha il codice diverso da quello nel database: %s." % (data.code, table_name, data_code)

        if not hasattr(data, "area"):
            if not error:
                error = "Dato %s di tipo %s senza l'attributo area." % (data_code, table_name)

        if isinstance(data.area, basestring):
            if not error:
                error = "Dato %s di tipo %s con l'attributo area come stringa: %r" % (data_code, table_name, self.area)

        if data.area and not isinstance(data.area, basestring):
            # Questo test serve solo ai dati controllati nelle aree, quelli
            # del database è ovvio che si trovino lì vista l'iterazione per
            # passarli tutti
            if data_code not in self[table_name]:
                if not error:
                    error = "Il dato %s, che si trova nell'area %s, non si trova nel database['%s'] (quantity %d) (%s %s) (entry_code %s)" % (
                        data_code, data.area.code if data.area else "None", table_name, data.quantity,
                        FLAG.EXTRACTED in data.flags, FLAG.WEAKLY_EXTRACTED in data.flags, entry_code)

            if table_name == "rooms":
                datas = data.area.rooms.values()
            else:
                datas = getattr(data.area, table_name)
            if data not in datas:
                if not error:
                    location = ""
                    if not data.IS_ROOM:
                        location = " (location=%s)" % data.location.code
                    error = "Il dato %s non si trova nella lista %s dell'area %s%s" % (data_code, table_name, data.area.code, location)
        else:
            if not error:
                error = "Dato %s di tipo %s senza area valida: %r" % (data_code, table_name, data.area)
        
        # I dati senza location sono errati, a meno che non siano
        # di qualche pg, cosa normale perché in questa fase tutti i pg
        # sono offline e le entità in loro possesso non hanno
        # location valido
        if not data.IS_ROOM and not data.location and (not data.owner or not data.owner() or not data.owner().IS_PLAYER):
            if not error:
                error = "Il dato %s non ha un location valido: %r" % (data_code, data.location)

        if error and data_code not in already_checked_wrongs:
            log.save(error)
            self.save_wrong_data(table_name, data, error, now, area=data.area)
            already_checked_wrongs.append(data_code)
    #- Fine Metodo -

    def save_wrong_data(self, table_name, data, error, now, area=None):
        if not data:
            log.bug("data non è un parametro valido: %r" % data)
            return

        # ---------------------------------------------------------------------

        folders_path = "wrong/%s/" % now
        if area:
            area_code = area.code
        else:
            area_code = data.code.split("_")[0]
        folders_path += "%s/%s" % (table_name, area_code)
        try:
            os.makedirs(folders_path)
        except OSError:
            # Se passa di qui significa che precedentemente ha già creato tale cartella
            pass

        # Salva nella path attualmente inizializzata l'errore in un file di log
        wrong_file_path = "wrong/%s/errors.log" % now
        try:
            wrong_file = open(wrong_file_path, "a")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % wrong_file_path)
            # Viene comunque cercato di salvare il dato e continua
        else:
            wrong_file.write(error + "\n")
            wrong_file.close()

        # ---------------------------------------------------------------------

        filename = "%s.dat" % getattr(data, data.PRIMARY_KEY)
        try:
            data_file = open("%s/%s" % (folders_path, filename), "w")
        except IOError:
            log.bug("Impossibile aprire il file %s in scrittura" % folders_path)
            return

        remove_all_affects(data)
        fwrite(data_file, data)
        data_file.close()
    #- Fine Metodo -

    def save_persistent_datas(self):
        counter = 0

        for table_name in ("rooms", "items", "mobs"):
            log.save("-> %s" % table_name)
            data_counter = 0
            for data_code, data in self[table_name].iteritems():
                # Se si è deciso di eseguire uno shutdown salvando solo le
                # persistenze relative ai giocatori allora esegue il controllo
                if self.only_player_persistence and table_name != "rooms":
                    if (not data.owner or not data.owner() or not data.owner().IS_PLAYER) and not data.get_player_carrier():
                        continue

                # Per gli errori di questo tipo ci pensa il sistema di wrong
                if not data.area:
                    continue

                # Se non c'è la path relativa all'area allora la crea
                areapath = "persistence/%s/%s" % (table_name, data.area.code)
                if not os.path.exists(areapath):
                    os.mkdir(areapath)
                filename = "%s.dat" % getattr(data, data.PRIMARY_KEY)
                try:
                    data_file = open("%s/%s" % (areapath, filename), "w")
                except IOError:
                    log.bug("Impossibile aprire il file %s in scrittura" % areapath)
                    continue

                remove_all_affects(data)
                fwrite(data_file, data)
                data_file.close()
                data_counter += 1
                counter += 1
            log.save("   Salvati: %d" % data_counter)

        log.save("Sono stati salvati in totale %d dati persistenti" % counter)
    #- Fine Metodo -

    def save_account_datas(self):
        counter = 0

        for account_code, account in sorted(self["accounts"].iteritems()):
            log.save("-> %s: %d personaggi%s" % (
                account_code, len(account.players), "" if len(account.players) != 1 else "o"))
            account_path = "persistence/accounts/%s.dat" % account_code
            try:
                account_file = open(account_path, "w")
            except IOError:
                log.bug("Impossibile aprire il file %s in scrittura" % account_path)
                continue
            fwrite(account_file, account)
            account_file.close()
            counter += 1

        log.save("Sono stati salvati %d account" % counter)
    #- Fine Metodo -

    def save_player_datas(self):
        counter = 0

        for player_code, player in sorted(self["players"].iteritems()):
            if not player.account:
                log.bug("player.account non è valido: %r" % player.account)
                continue
            log.save("-> %s" % player_code)
            folder = "persistence/players/%s" % player.account.name
            if not os.path.exists(folder):
                os.mkdir(folder)
            player_path = "%s/%s.dat" % (folder, player_code)
            try:
                player_file = open(player_path, "w")
            except IOError:
                log.bug("Impossibile aprire il file %s in scrittura" % player_path)
                continue
            remove_all_affects(player)
            fwrite(player_file, player)
            player_file.close()
            counter += 1

        log.save("Sono stati salvati %d personaggi" % counter)
    #- Fine Metodo -

    def save_news_datas(self):
        counter = 0

        for new_code, new in sorted(self["news"].iteritems()):
            new_path = "persistence/news/%s.dat" % new_code
            try:
                new_file = open(new_path, "w")
            except IOError:
                log.bug("Impossibile aprire il file %s in scrittura" % new_path)
                continue
            fwrite(new_file, new)
            new_file.close()
            counter += 1

        log.save("Sono state salvate %d news" % counter)
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def backup(self, backup_descr):
        """
        Esegue un archivio di tutta la cartella /data salvandolo nella cartella
        /backup.
        Il parametro backup_descr è il suffisso al nome del file archivio
        per indicarne la tipologia.
        """
        if not backup_descr:
            log.bug("backup_descr non è un parametro valido: %r" % backup_descr)
            return

        # ---------------------------------------------------------------------

        if not os.path.exists("backup"):
            os.mkdir("backup")

        if self.avoid_backup_on_shutdown:
            log.backup("È stato scelto di evitare il backup durante lo shutdown.")
            return

        ext = "tar"
        mode = "w:"
        from src.config import config
        if config.compression_mode in ("gz", "bz2"):
            ext += ".%s" % config.compression_mode
            mode += config.compression_mode

        now = datetime.datetime.now()
        filename = "%d-%02d-%02d_%02d-%02d-%02d_%s.%s" % (
            now.year, now.month, now.day, now.hour, now.minute, now.second, backup_descr, ext)

        backup_tar = tarfile.open("backup/%s" % filename, mode)
        backup_tar.add("data", exclude=_exclude_compiled_files)
        backup_tar.add("persistence", exclude=_exclude_compiled_files)
        backup_tar.close()

        log.backup("Backup del database al file %s eseguito con successo" % filename)
    #- Fine Metodo -

    def walk_datas(self, table_names=None, use_reversed=False):
        """
        Itera tutti i dati del database ritornando una tupla di tre valori:
        (nome tabella, codice del dato, dato).
        """
        if not table_names:
            table_names = []

        for table_name, table in self.items():
            if table_names and table_name not in table_names:
                continue
            if use_reversed:
                for data_code in reversed(sorted(table.keys())):
                    yield table_name, data_code, table[data_code]
            else:
                for data_code in sorted(table.keys()):
                    yield table_name, data_code, table[data_code]
    #- Fine Metodo -

    def get_subfolder_related_datas(self, table_name, subfolder_code):
        datas = []

        subfolder = self.TABLES[table_name][SUBFOLDER]
        if subfolder == "area":
            for data_code in sorted(self[table_name].keys()):
                #print data_code, subfolder_code
                if subfolder_code == data_code.split("_")[0]:
                    datas.append((data_code, self[table_name][data_code]))
        else:
            for data_code in sorted(self[table_name].keys()):
                data = self[table_name][data_code]
                if getattr(data, subfolder).code == subfolder_code:
                    datas.append((data_code, data))

        return datas
    #- Fine Metodo -

    def get_proto_entity(self, proto_code):
        if not proto_code:
            log.bug("proto_code non è un parametro valido: %r" % proto_code)
            return None

        # ---------------------------------------------------------------------

        table = "proto_%ss" % proto_code.split("_")[1]
        if proto_code not in self[table]:
            log.bug("proto_code %s non si trova nella tabella %s" % (proto_code, table))
            return None

        return self[table][proto_code]
    #- Fine Metodo -

    def get_subfolder_names(self, table):
        """
        Ritorna le sottocartelle relative una tabella proprio come sono salvati
        i dati nell'alberatura di cartelle sul disco.
        Non viene utilizzata la semplice os.filelist perché in futuro le aree
        ed altre tipologie di dati saranno creabili online.
        """
        if not table:
            log.bug("table non è un parametro valido: %r" % table)
            return []

        # ---------------------------------------------------------------------

        subfolder_value = self.TABLES[table][SUBFOLDER]
        import_value    = self.TABLES[table][IMPORT]

        subfolder_names = []
        if import_value in ("code", "primary-key-piece"):
            subfolder_names = sorted(self[subfolder_value + "s"].keys())
        elif import_value.startswith("src.enums."):
            enums_module = __import__(import_value, globals(), locals(), [""])
            for element in enums_module.elements:
                subfolder_names.append(element.get_mini_code())
        else:
            log.bug("Impossibile ricavare la lista delle subfolder per la tabella %s" % table)
            return []

        return subfolder_names
    #- Fine Metodo -

    def iter_subfolder_related_datas(self, table, subtable):
        """
        Ritorna vero se la tabella passata possibile dei dati relativi alla
        sottotabella passata.
        """
        if not table:
            log.bug("table non è un parametro valido: %r" % table)
            yield None, None

        if not subtable:
            log.bug("table non è un parametro valido: %r" % subtable)
            yield None, None

        # ---------------------------------------------------------------------

        subfolder_value = self.TABLES[table][SUBFOLDER]
        import_value    = self.TABLES[table][IMPORT]

        for data_code, data_value in sorted(self[table].items()):
            if import_value == "code":
                subfolder_data = getattr(data_value, subfolder_value)
                if getattr(subfolder_data, subfolder_data.PRIMARY_KEY) == subtable:
                    yield data_code, data_value
            elif import_value == "primary-key-piece":
                if getattr(data_value, data_value.PRIMARY_KEY).split("_")[1] == subtable:
                    yield data_code, data_value
            else:
                subfolder_data = getattr(data_value, subfolder_value)
                if subfolder_data.get_mini_code() == subtable:
                    yield data_code, data_value

        yield None
    #- Fine Metodo -


#= Funzioni di lettura dei dati ================================================

def _search_correct_attribute(label, attributes_list):
    """
    Ritorna l'attributo corretto a cui l'etichetta si riferisce, se trovato.
    Difatti la funzione from_capitalized_words() nel modulo utility non basta, poiché
    se per esempio qualcuno sbaglia a scrivere la label Race e la scrive RACE
    la from_capitalized_words() la converte in r_a_c_e.
    C'è bisogno quindi di questa funzione in maniera tale da effettuare una
    ricerca più intelligente.
    Dà per scontato che non vi siano attributi simili in una singola classe
    di dato (per esempio: room_entities e roomentities)
    """
    if not label:
        log.bug("label non è un parametro valido: %r (attributes_list %r)" % (label, attributes_list))
        return ""

    if not attributes_list:
        log.bug("attributes_list non è un parametro valido: %s" % attributes_list)
        return ""

    # -------------------------------------------------------------------------

    label = label.lower()
    for attr in attributes_list:
        if label == (attr.replace("_", "") if "_" in attr else attr):
            return attr

    return ""
#- Fine Funzione -


def fread(file, module_name, class_name, indent=0, parent_line="", parent_attr="", parent_data=None):
    """
    Legge da un file i dati riguardo ad una classe di dato qualsiasi seguendo
    le relative regole della sua struttura contenute nei seguenti attributi:
    SCHEMA, PRIMARY_KEY, REFERENCES e WEAKREFS.
    La funzione può apparire confusionaria perché esegue delle cose un po'
    'magiche' per supportare la lettura delle multilinea senza dover per forza
    utilizzare un terminatore di stringa (come la tilde nei Diku-like).
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return None

    if not module_name:
        log.bug("module_name non è un parametro valido: %s" % module_name)
        return None

    if not class_name:
        log.bug("class_name non è un parametro valido: %s" % class_name)
        return None

    if indent < 0 or indent > 10:
        log.bug("indent passato non è un parametro valido: %d" % indent)
        return None

    # -------------------------------------------------------------------------

    # Importa la classe e ne crea una nuova istanza ricavandone gli attributi
    module = __import__(module_name, globals(), locals(), [""])
    try:
        data = getattr(module, class_name)()
    except AttributeError as (errno, strerror):
        log.bug("Errore numero %d: %s (tentando di creare un dato con modulo %s e classe %s)" % (
            errno, strerror, module_name, class_name))
        sys.exit(1)

    # Prepara la lista degli attributi che potrebbe incontrare durante la
    # lettura delle etichette del file
    data_attributes = []
    for key in data.__dict__:
        if key[0] == "_" or key in data.VOLATILES:
            continue
        data_attributes.append(key)

    # Prepara anche una lista vuota per segnarsi gli attributi già letti una
    # volta per indicare così se vi siano file con doppie label
    attributes_already_readed = []

    # reading_a_string uguale a True indica che nell'ultimo ciclo è stata
    # letta una stringa, è importante, assieme a original_line e
    # last_attr_founded, per la corretta lettura di stringhe multilinea
    reading_a_string = False
    last_attr_founded = ""
    while 1:
        line = file.readline()
        # Esce dal ciclo se ha incontrato un EOF
        if not line:
            if reading_a_string and last_attr_founded in data.MULTILINES:
                value = getattr(data, last_attr_founded)
                if isinstance(value, list):
                    value[-1] += "\n"
                else:
                    setattr(data, last_attr_founded, value.rstrip() + "\n")
            if indent > 0:
                log.bug("Non è stata trovata nessun'etichetta di End a fine file %s" % file.name)
            break

        original_line = line = line.replace("\r", "")

        # Rimuove caratteri spazio alle estremità della linea
        line = line.strip()
        # Salta le righe vuote, se però stava leggendo una stringa
        # aggiunge un a capo
        if not line:
            if reading_a_string and last_attr_founded in data.MULTILINES:
                value = getattr(data, last_attr_founded)
                if isinstance(value, list):
                    value[-1] += "\n"
                else:
                    setattr(data, last_attr_founded, value.rstrip() + "\n")
            continue

        # Se incontra End e c'è un'indentazione allora smette di leggere
        # il sottoriferimento del dato
        if indent > 0 and line.capitalize() == "End":
            if reading_a_string and last_attr_founded in data.MULTILINES:
                value = getattr(data, last_attr_founded)
                if isinstance(value, list):
                    value[-1] += "\n"
                else:
                    setattr(data, last_attr_founded, value.rstrip() + "\n")
            return data

        values = line.split(None, 1)

        # Visto che alcuni scrivono le label in maniera errata, dimenticando
        # i due punti oppure utilizzando l'uguale al loro posto qui c'è un
        # controllo che permette loro di 'fargliela passare liscia'
        label = values[0]
        if label[-1] == ":" or label[-1] == "=":
            label = label[ : -1]

        # Che non vi sia una label valida capita quando vi sono ascii art che
        # iniziano per : o = e poi con uno spazio
        if not label:
            attr = ""
            remaining_line = line 
        else:
            if len(values) == 2:
                remaining_line = values[1]
            else:
                remaining_line = ""
            attr = _search_correct_attribute(label, data_attributes + attributes_already_readed)

        # Per ogni etichetta, corrispondente ad un attributo del dato, ricava
        # il valore a seconda del tipo dell'attributo
        if attr in data_attributes:
            # Se fino al ciclo precedente stava leggendo una stringa la ricava
            # chiudendone eventuali stili css aperti
            if reading_a_string:
                value = getattr(data, last_attr_founded)
                if isinstance(value, list):
                    value[-1] = value[-1].rstrip().lstrip("\t")
                    if value[-1]:
                        value[-1] = close_color(value[-1])
                    else:
                        log.bug("Etichetta %s trovata vuota nel file %s" % (label, file.name))
                else:
                    value = value.rstrip().lstrip("\t")
                    if value:
                        setattr(data, last_attr_founded, close_color(value))
                    else:
                        log.bug("Etichetta %s trovata vuota nel file %s" % (label, file.name))
            reading_a_string = False
            last_attr_founded = ""

            if not attr in data.__dict__:
                log.bug("Attributo %s non trovato per il dato al file %s" % (attr, file.name))
                return None

            var = getattr(data, attr)

            # Rimuove ogni attributo trovato dalla lista degli attributi del
            # dato a meno che non sia una lista o un dizionario
            if type(var) not in (list, dict) and not isinstance(var, (list, dict)):
                data_attributes.remove(attr)

            # Aggiunge alla lista degli attributi letti l'attributo, a meno che
            # già non esista come può capitare con attributi dizionario o lista
            if attr not in attributes_already_readed:
                attributes_already_readed.append(attr)

            # Grazie a self.SCHEMA di ogni dato si possono leggere
            # correttamente dati come altre istanze di classe, dizionari,
            # liste e alcuni valori con unità di misura
            if attr in data.SCHEMA:
                sub_module_name = data.SCHEMA[attr][MODULE_NAME]
                sub_class_name  = data.SCHEMA[attr][CLASS_NAME]
                if sub_module_name:
                    if isinstance(var, list):
                        sub_module = __import__(sub_module_name, globals(), locals(), [""])
                        sub_class = getattr(sub_module, sub_class_name)
                        if sub_class_name == "Flags":
                            from element import Flags
                            var.append(Flags(remaining_line))
                        elif hasattr(sub_class(), "fread_the_line"):
                            sub_var = sub_class()
                            sub_var.fread_the_line(file, remaining_line, attr)
                            var.append(sub_var)
                        else:
                            var.append(fread(file, sub_module_name, sub_class_name, indent+1, remaining_line, attr, data))
                    elif isinstance(var, dict):
                        sub_data = fread(file, sub_module_name, sub_class_name, indent+1, remaining_line, attr, data)
                        key = getattr(sub_data, sub_data.PRIMARY_KEY)
                        var[key] = sub_data
                    elif isinstance(var, types.InstanceType):
                        var = fread(file, sub_module_name, sub_class_name, indent+1, remaining_line, attr, data)
                    else:
                        var_was_none = False
                        if var is None:
                            var_was_none = True
                        # Altrimenti si crea un'istanza del sotto dato e prova
                        # a leggerne i valori tramite il metodo fread che
                        # dovrebbe possedere
                        sub_module = __import__(sub_module_name, globals(), locals(), [""])
                        sub_class = getattr(sub_module, sub_class_name)
                        var = sub_class()
                        if hasattr(var, "fread_the_line"):
                            var.fread_the_line(file, remaining_line, attr)
                        else:
                            var = fread(file, sub_module_name, sub_class_name, indent+1, remaining_line, attr, data)
                    setattr(data, attr, var)
                # Alcuni valori nello schema non hanno sub_module_name e stanno
                # ad indicare delle specifiche modalità di lettura dei dati,
                # come ad esempio delle unità di misura facoltative
                else:
                    if isinstance(var, list):
                        if sub_class_name == "str":
                            reading_a_string = True
                            last_attr_founded = attr
                            var.append(remaining_line)
                        else:
                            log.bug("Tipo di sub_class_name per una lista errata: %s" % sub_class_name)
                            continue
                    # Supporto ai dizionari formati da valori stringa di
                    # default oppure da interi
                    elif isinstance(var, dict):
                        try:
                            key, value = remaining_line.split(None, 1)
                        except ValueError:
                            # Significa che la chiave del dizionario contiene
                            # un valore di stringa vuoto o con la seconda parte
                            # mancante, nel primo caso capita normalmente tra
                            # le specials
                            if label == "Specials":
                                key = remaining_line
                                value = ""
                            else:
                                log.bug("Contenuto di dizionario non valido: %r per la label %s e il file %s (ricordo che tali etichette sono formati da coppie di valori)" % (
                                    remaining_line, label, file.name))
                                continue
                        if sub_class_name == "int":
                            try:
                                var[key] = int(value)
                            except ValueError:
                                log.fread("il valore di dizionario %s per la chiave %s non è un numero valido per il file %s e la label %s" % (
                                    value, key, file.name, label))
                                continue
                        else:
                            # Per il solo dizionario delle specials, che può avere
                            # una qualsiasi tipologia tra le principali, esegue una
                            # lettura semi-intelligente dei valori
                            if label == "Specials":
                                try:
                                    var[key] = int(value)
                                except ValueError:
                                    if value in ("True", "False"):
                                        var[key] = bool(value)
                                    else:
                                        var[key] = value
                            else:
                                var[key] = value
                        setattr(data, attr, var)
                    else:
                        if sub_class_name == "percent":
                            value = fread_percent(file, remaining_line, attr)
                        elif sub_class_name == "temperature":
                            value = fread_temperature(file, remaining_line, attr)
                        elif sub_class_name == "measure":
                            value = fread_measure(file, remaining_line, attr)
                        elif sub_class_name == "weight":
                            value = fread_weight(file, remaining_line, attr)
                        elif sub_class_name == "css_measure":
                            value = fread_css_measure(file, remaining_line, attr)
                        elif sub_class_name == "css_border":
                            value = fread_css_border(file, remaining_line, attr)
                        elif sub_class_name == "date":
                            tm = time.strptime(remaining_line, "%Y-%m-%d")
                            value = datetime.date(tm.tm_year, tm.tm_mon, tm.tm_mday)
                        elif sub_class_name == "datetime":
                            tm = time.strptime(remaining_line, "%Y-%m-%d %H:%M:%S")
                            value = datetime.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
                        else:
                            log.bug("Tipo di sub_class_name generica per l'attributo %s errata: %s" % (attr, sub_class_name))
                            continue
                        setattr(data, attr, value)
            # Se l'attributo non si trova nello schema ma tra i riferimenti
            # significa che è un riferimento ad una chiave primaria di un altro
            # dato che potrebbe essere caricato solo in seguito, quindi per ora
            # legge il codice e lo salva come stringa
            elif attr in data.REFERENCES or attr in data.WEAKREFS:
                if not remaining_line:
                    log.bug("Il Contenuto dell'etichetta %s è vuoto nel file %s, era atteso un riferimento" % (label, file.name))
                    continue
                first_word = remaining_line.split()[0]
                if isinstance(var, list):
                    var.append(first_word)
                elif var is None:
                    var = first_word
                elif var == first_word:
                    pass
                else:
                    log.bug("Tipologia di var %s con valore %s inattesa nella lettura dei riferimenti per la label %s al file %s" % (
                        type(var), var, label, file.name))
                    continue
                setattr(data, attr, var)
            # Se la variabile è una stringa ne salva la linea trovata
            # impostando la variabile reading_a_string a True
            elif isinstance(var, basestring):
                reading_a_string = True
                # Salva l'attributo letto riguardante la stringa per poi,
                # eventualmente, aggiungerci altre linee lette
                last_attr_founded = attr
                if not remaining_line:
                    remaining_line = file.readline()
                    if not remaining_line:  # EOF
                        if indent > 0:
                            log.bug("Non è stata trovata nessun'etichetta di End a fine file %s" % file.name)
                        break
                    remaining_line = remaining_line.replace("\r", "")
                # Se la stringa inizia con un punto questo viene tolto, serve
                # ad evitare che gli spazi inseriti in alcune ascii art vengano
                # mangiati dalla normale lettura della stringa; se si vuole
                # visualizzare un punto a inizio stringa bisognerà quindi
                # inserirne due
                if remaining_line[0] == ".":
                    setattr(data, attr, remaining_line[1:].rstrip(" ").lstrip("\t"))
                else:
                    setattr(data, attr, remaining_line.strip(" ").lstrip("\t"))
            elif type(var) in (int, long):
                if not remaining_line:
                    log.bug("Il Contenuto dell'etichetta %s è vuoto nel file %s, era atteso un numero" % (label, file.name))
                    continue
                word = remaining_line.split()[0]
                value = fread_number(file, word, attr)
                setattr(data, attr, value)
            elif type(var) == bool:
                if not remaining_line:
                    log.bug("Il Contenuto dell'etichetta %s è vuoto nel file %s, era atteso un booleano" % (label, file.name))
                    continue
                word = remaining_line.split()[0]
                value = fread_bool(file, word, attr)
                setattr(data, attr, value)
            elif isinstance(var, EnumElement):
                if not remaining_line:
                    log.bug("Il Contenuto dell'etichetta %s è vuoto nel file %s, era atteso un EnumElement" % (label, file.name))
                    continue
                var = fread_enum_element(file, remaining_line, attr)
                setattr(data, attr, var)
            # Di seguito ci sono le letture di strutture personalizzate di
            # dato contenute in una sola riga e che non seguono le regole
            # delle etichette (Element e Flags)
            elif hasattr(var, "fread_the_line"):
                if not remaining_line:
                    log.bug("Il Contenuto dell'etichetta %s è vuoto nel file %s, era atteso una linea con dei valori" % (label, file.name))
                    continue
                var.fread_the_line(file, remaining_line, attr)
                setattr(data, attr, var)
            # C'è il caso particolare delle uscite che serve a recuperare il
            # codice in lettura anche se non ha la relativa reference
            elif class_name == "Exit" and attr == "door":
                setattr(data, attr, remaining_line)
            else:
                log.bug("Attributo %s.%s di tipo %r non caricabile nel file %s dalla fread" % (class_name, attr, type(var), file.name))
        else:
            # Se non ha trovato una label adatta e se precedentemente stava
            # leggendo una stringa dà per scontato che sia una stringa
            # multilinea e continua a leggerla, a meno che la rimanente riga
            # non sia formata da una sola parola e che questa parola sia simile
            # al nome della classe che si sta inizializzando, in tutti gli
            # altri casi lo gestisce come un errore
            if attr == "" and (is_same(label + "s", class_name) or is_same(class_name + "s", label)):
                log.bug("Trovata una label (%s) dal nome simile della classe da inizializzare (%s), forse manca una label End prima di una nuova struttura %s per il dato %s?" % (
                    label, class_name, label, getattr(parent_data, parent_data.PRIMARY_KEY)))
            elif reading_a_string:
                if original_line[0] == ".":
                    line_to_add = original_line[1:].rstrip(" ").lstrip("\t")
                else:
                    line_to_add = original_line.strip(" ").lstrip("\t")
                # Controllo alla buona ed empirico che permette di scovare in
                # alcuni casi l'utilizzo di etichette sintatticamente errate
                # che vengono altrimenti caricate come testo multilinea
                # (TD) sistema disattivato in attesa delle funzioni di soundex
                # altrimenti vengono generati troppi falsi positivi
                #if line_to_add[0].isupper() and line_to_add.split(" ", 1)[0][-1] == ":":
                #    log.bug("Potenziale etichetta errata per la linea %s letto nel file %s con la label %s" % (line_to_add, file.name, label))
                value = getattr(data, last_attr_founded)
                if isinstance(value, list):
                    if value[-1] and value[-1][-1] != "\n":
                        value[-1] += "\n"
                    value[-1] += line_to_add.rstrip()
                else:
                    if value[-1] != "\n":
                        value += "\n"
                    setattr(data, last_attr_founded, value + line_to_add.rstrip())
            else:
                if attr in attributes_already_readed:
                    log.bug("L'attributo %s è già stato letto nel file %s con la label %s per il dato %s" % (attr, file.name, label, type(data)))
                else:
                    log.bug("Non è stato trovato nessun attributo %r valido per la label %s al file %s per il dato %s" % (attr, label, file.name, type(data)))

    # Avendo creato alcune sottostrutture, nel ciclo di fread, con valori di
    # default bisogna reinizializzare alcune di esse per riottenere ancora
    # dei valori cachati corretti
    if class_name in ("Room", "Item", "Mob"):
        data.after_copy_existing_attributes()

    # Crea automaticamente le parole chiave se queste già non esistono
    if class_name in ("ProtoItem", "ProtoMob", "Item", "Mob"):
        create_all_couples_of_keywords(data)

    # Controlla se il nome del file sia uguale a quello della chiave primaria
    if data.PRIMARY_KEY:
        file_name_without_ext = os.path.split(file.name)[1].replace(".dat", "")
        if file_name_without_ext != getattr(data, data.PRIMARY_KEY):
            log.bug("Il nome del file %s non è uguale al codice identificatore della label %s: %r" % (
                file_name_without_ext, to_capitalized_words(data.PRIMARY_KEY), getattr(data, data.PRIMARY_KEY)))

    # Ritorna il dato appena letto
    return data
#- Fine Funzione -


def create_all_couples_of_keywords(data):
    if not data:
        log.bug("data non è un parametro valido: %r" % data)
        return

    # -------------------------------------------------------------------------

    from entity import create_keywords

    if data.IS_ROOM or data.IS_PLAYER:
        log.bug("Le stanze e i giocatori non hanno le keywords: %r" % data)
        return

    for labels in (("keywords_name", "name"), ("keywords_short", "short"), ("keywords_short_night", "short_night")):
        if not getattr(data, labels[0]) and getattr(data, labels[1]):
            keywords = create_keywords(getattr(data, labels[1]), data)
            if keywords:
                setattr(data, labels[0], keywords)
            else:
                log.bug("keywords create non valide con le label %s %s per il dato %s" % (
                    labels[0], labels[1], getattr(data, data.PRIMARY_KEY)))
                continue
#- Fine Funzione -


def fread_list(file_path, data_class, attr):
    """
    Legge una serie di dati da un file e ne ritorna una lista.
    """
    if not file_path:
        log.bug("file_path non è un parametro valido: %s" % file_path)
        return []

    if not data_class:
        log.bug("data_class non è un parametro valido: %s" % data_class)
        return []

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return []

    # -------------------------------------------------------------------------

    try:
        list_file = open(file_path, "r")
    except IOError:
        log.bug("Impossibile aprire il file %s in lettura" % file_path)
        return

    result = []
    counter = 0
    for line in list_file:
        if not line:  # trovato EOF
            return result
        line = line.strip()
        if not line:  # linea vuota
            continue
        if line[0] == "#":  # trovato commento
            continue

        data = data_class()
        data.fread_the_line(list_file, line, attr % counter)
        result.append(data)
        counter += 1
    list_file.close()

    return result
#- Fine Funzione -


def fread_number(file, word, attr, typology="un numero valido"):
    """
    Legge dal file una parola e la converte in numero intero ritornandolo.
    L'argomento attr indica l'attributo in cui verrà salvato il valore, viene
    utilizzato per debuggare.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    number = 0
    try:
        number = int(word)
    except ValueError:
        try:
            number = long(word)
        except ValueError:
            log.bug("La parola %s letta dal file %s, relativa all'attributo %s, non è %s" % (
                word, file.name, attr, typology))
    return number
#- Fine Funzione -


def fread_percent(file, word, attr):
    """
    Legge un numero che potrebbe avere un simbolo di percentuale alla fine
    della parola passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    if word[-1] == "%":
        word = word[ : -1]
    return fread_number(file, word.strip(), attr, typology="una percentuale valida")
#- Fine Funzione -


def fread_measure(file, word, attr):
    """
    Legge dal file un numero che potrebbe avere opzionalmente anche un'unità
    di misura differente da quella passata, quindi converte il valore ricavato
    a seconda dell'unità voluta.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    word = word.lower()

    multiplier = 1
    if word.endswith("cm"):
        word = word[ : -2]
    elif word.endswith("km"):
        multiplier = 100000
        word = word[ : -2]
    # Deve esserci per ultimo il controllo dei metri rispetto alle altre
    # misure visto che finisce in m come tutte le altre
    elif word.endswith("m"):
        multiplier = 100
        word = word[ : -1]
    else:
        log.bug("Distanza %s senza unità di misura al file %s: %s (verrà considerato di default in cm)" % (
            attr, file.name, word))

    number = fread_number(file, word.rstrip(), attr, typology="una misura valida")
    return number * multiplier
#- Fine Funzione -


def fread_weight(file, word, attr):
    """
    Come la fread_measure ma qui riguarda le unità di misura dei grammi,
    chilogrammi e tonnellate.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    word = word.lower()

    multiplier = 1
    # Deve esserci prima il controllo di chilogrammi rispetto ai grammi visto
    # che tutte e due le unità di misura finiscono in g
    if word.endswith("kg"):
        multiplier = 1000
        word = word[ : -2]
    elif word.endswith("g"):
        word = word[ : -1]
    elif word.endswith("q"):
        multiplier = 100000
        word = word[ : -1]
    elif word.endswith("t"):
        multiplier = 1000000
        word = word[ : -1]
    else:
        log.bug("Peso %s senza unità di misura al file %s: %s (verrà considerato di default in g)" % (
            attr, file.name, word))

    number = fread_number(file, word.strip(), attr, typology="un peso valido")
    return number * multiplier
#- Fine Funzione -


def fread_temperature(file, word, attr):
    """
    Come la fread_measure questa funzione serve a leggere dei valori con
    l'unità di misura con il grado.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    if word.endswith("°"):
        word = word.rstrip("°")
    return fread_number(file, word, attr, typology="una temperatura valida")
#- Fine Funzione -


def fread_bool(file, word, attr):
    """
    Legge da file la parola True o False o simili e ritorna un booleano.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    if is_same(word, ("True", "Vero", "Si", "Yes")):
        return True
    elif is_same(word, ("False", "Falso", "No", "Non", "Not")):
        return False
    else:
        log.bug("La parola letta <%s> al file <%s> per l'attributo <%s> non è un booleano valido." % (
            word, file.name, attr))
        return None
#- Fine Funzione -

def fread_css_measure(file, word, attr):
    """
    Legge dal file un numero che potrebbe avere opzionalmente anche un'unità
    di misura css.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    word = word.lower()

    if is_number(word):
        log.bug("Misura css %s senza unità al file %s: %s (verrà considerata come px)" % (attr, file.name, word))
        return word + "px"

    if word[-1] == "%":
        number, unit = word[ : -1], word[-1]
    else:
        number, unit = word[ : -2], word[-2 : ]
    number = number.rstrip()

    if not is_number(number):
        log.bug("Misura css %s non numerica al file %s: %s" % (attr, file.name, word))

    if unit not in ("%", "in", "cm", "mm", "em", "ex", "pt", "pc", "px"):
        log.bug("Misura css %s senza unità di misura al file %s: %s" % (attr, file.name, word))

    return word
#- Fine Funzione -


def fread_css_border(file, word, attr):
    """
    Legge dal file un numero che potrebbe avere opzionalmente anche un'unità
    di misura css.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not word:
        log.bug("word non è un parametro valido: %s" % word)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %s" % attr)
        return

    # -------------------------------------------------------------------------

    word = word.lower()

    css_measure, border_style, color = word.split()

    # Chiamando questa funzione verranno eseguiti tutti i test sulla misura css
    fread_css_measure(file, css_measure, attr)

    if border_style not in ("dotted", "dashed", "solid", "double", "groove", "ridge", "inset", "outset"):
        log.bug("Bordo css %s senza uno stile valido al file %s: %s" % (attr, file.name, word))

    if color not in colors:
        log.bug("Bordo css %s senza un colore valido al file %s: %s" % (attr, file.name, word))

    return word
#- Fine Funzione -


#- Funzioni di scrittura dei dati ----------------------------------------------

# (TD) allineare indentation con la fread, non so se utilizzare gli spazi o
# il numero di spazi però, da pensare
def fwrite(file, data, data_label="", indentation=""):
    """
    Scrive su file testuale tutte le variabili di un qualsiasi dato del
    database.
    """
    if not file:
        log.bug("filepath non è un parametro valido: %s" % file)
        return

    if not data:
        log.bug("data non è un parametro valido: %s" % data)
        return

    # -------------------------------------------------------------------------

    # Prepara la lista di attributi da scrivere, nell'ordine voluto
    data_attributes = []
    if hasattr(data, "__dict__"):
        if "PRIMARY_KEY" in data.__dict__:
            data_attributes += [data.PRIMARY_KEY]
        for key in sorted(data.__dict__):
            if key[0] == "_" or key in data.VOLATILES:
                continue
            if key not in data_attributes:
                data_attributes.append(key)

    # La fwrite deve sempre avere una lista valida di attributi su cui ciclare
    if not data_attributes:
        log.bug("Caso inatteso per il dato %r al file %s con label %s" % (data, file.name, data_label))
        return

    # Scrive su file le informazioni degli attributi del dato passato
    for attr_name in data_attributes:
        label = "%-14s" % ("%s: " % to_capitalized_words(attr_name))
        attr = getattr(data, attr_name)

        if attr_name in data.REFERENCES or attr_name in data.WEAKREFS:
            if attr and attr_name in data.WEAKREFS:
                attr = attr()
            if isinstance(attr, list):
                for sub_data in attr:
                    if not hasattr(sub_data, "PRIMARY_KEY"):
                        log.bug("sub_data %r nella attr %r di attr_name %r non possiede la PRIMARY_KEY al file %s" % (
                            sub_data, attr, attr_name, file.name))
                        continue
                    file.write("%s%-14s" % (indentation, label))
                    file.write(indentation + getattr(sub_data, sub_data.PRIMARY_KEY))
                    file.write("\n")
            elif isinstance(attr, dict):
                raise NotImplementedError  # (TD)
            elif attr is None:
                continue
            elif hasattr(attr, "PRIMARY_KEY"):
                file.write(indentation + label)
                file.write(getattr(attr, attr.PRIMARY_KEY))
                file.write("\n")
            else:
                log.bug("Inaspettato raggiungimento del codice, attr %r per la label %s al dato %r" % (attr, label, data))
                continue
        elif attr_name == "door" and data.__class__.__name__ == "Exit":
            # Caso speciale delle porte
            if attr:
                file.write(indentation + label)
                file.write(attr.code)
                file.write("\n")
        elif hasattr(attr, "fwrite_the_line"):
            attr.fwrite_the_line(file, label, indentation)
        elif ((attr is None or attr == [] or attr == {} or attr == "") 
        and   attr.__class__.__name__ not in ("Flags", "EnumElementDict")):
            continue
        elif attr_name in data.SCHEMA:
            sub_module_name = data.SCHEMA[attr_name][MODULE_NAME]
            sub_class_name  = data.SCHEMA[attr_name][CLASS_NAME]
            if isinstance(attr, types.InstanceType):
                file.write("%s%s\n" % (indentation, label.strip()))
                fwrite(file, attr, label, "%s\t" % indentation)
                file.write("%sEnd\n" % indentation[1 : ])
            elif isinstance(attr, list):
                if sub_class_name == "str":
                    for sub_value in attr:
                        file.write("%s%s %s\n" % (indentation, label, sub_value))
                elif sub_class_name == "Flags":
                    for sub_value in attr:
                        file.write("%s%s %r\n" % (indentation, label.strip(), sub_value))
                else:
                    for sub_value in attr:
                        if hasattr(sub_value, "fwrite_the_line"):
                            sub_value.fwrite_the_line(file, label, indentation)
                        else:
                            file.write("%s%s\n" % (indentation, label.strip()))
                            fwrite(file, sub_value, label, "%s\t" % indentation)
                            file.write("%sEnd\n" % indentation[1 : ])
            elif isinstance(attr, dict):
                for sub_key, sub_value in attr.iteritems():
                    if sub_class_name == "str":
                        file.write("%s%s %s %s\n" % (indentation, label.strip(), sub_key, sub_value))
                    elif sub_class_name == "int":
                        file.write("%s%s %s %d\n" % (indentation, label.strip(), sub_key, int(sub_value)))
                    else:
                        if hasattr(sub_value, "fwrite_the_line"):
                            sub_value.fwrite_the_line(file, label, indentation)
                        else:
                            file.write("%s%s\n" % (indentation, label.strip()))
                            fwrite(file, sub_value, label, "%s\t" % indentation)
                            file.write("%sEnd\n" % indentation[1 : ])
            elif sub_class_name == "percent":
                fwrite_percent(file, attr, attr_name, label, indentation)
            elif sub_class_name == "temperature":
                fwrite_temperature(file, attr, attr_name, label, indentation)
            elif sub_class_name == "measure":
                fwrite_measure(file, attr, attr_name, label, indentation)
            elif sub_class_name == "weight":
                fwrite_weight(file, attr, attr_name, label, indentation)
            elif sub_class_name == "css_measure":
                fwrite_css_measure(file, attr, attr_name, label, indentation)
            elif sub_class_name == "css_border":
                fwrite_css_border(file, attr, attr_name, label, indentation)
            elif sub_class_name == "date":
                file.write(indentation + label)
                file.write(attr.strftime("%Y-%m-%d"))
                file.write("\n")
            elif sub_class_name == "datetime":
                file.write(indentation + label)
                file.write(attr.strftime("%Y-%m-%d %H:%M:%S"))
                file.write("\n")
            else:
                file.write("%s%s\n" % (indentation, label.strip()))
                fwrite(file, attr, label, "\t%s" % indentation)
                file.write("%sEnd\n" % indentation[1 : ])
        elif type(attr) in (int, long):
            fwrite_number(file, attr, attr_name, label, indentation)
        elif isinstance(attr, basestring):
            fwrite_string(file, attr, attr_name, label, indentation)
        elif type(attr) == bool:
            fwrite_bool(file, attr, attr_name, label, indentation)
        elif isinstance(attr, list):
            for sub_data in attr:
                sub_class_name = data.SCHEMA[attr_name][CLASS_NAME]
                if sub_class_name == "str":
                    fwrite_string(file, attr, attr_name, label, indentation)
                else:
                    file.write(indentation + getattr(sub_data, sub_data.PRIMARY_KEY))
                file.write("\n")
        # Supporto ai dizionari formati da sole stringhe
        elif isinstance(attr, dict):
            for key, value in attr.iteritems():
                file.write("%s%-14s %s %s\n" % (indentation, label, key, value))
        else:
            log.bug("Tipologia di variabile %s passata tramite l'attributo %s non gestibile dalla fwrite al file %s" % (
                type(attr), attr_name, file.name))

    if isinstance(data, (list, dict)):
        file.write("%sEnd\n" % indentation[1 : ])
#- Fine Funzione -


def fwrite_list(file_path, list_to_write):
    """
    E' la funzione corrispondente a fread_list in scrittura.
    """
    if not file_path:
        log.bug("file_path non è un parametro valido: %r" % file_path)
        return

    if not list_to_write:
        log.bug("list_to_write non è un parametro valido: %r" % list_to_write)
        return

    # -------------------------------------------------------------------------

    try:
        data_file = open(file_path, "w")
    except IOError:
        log.bug("Impossibile aprire il file %s in scrittura" % file_path)
        return

    for data in list_to_write:
        data.fwrite_the_line(data_file)
    data_file.close()
#- Fine Funzione -


def fwrite_number(file, var, attr, label, indentation=""):
    """
    Scrive su file il numero, intero o long, passato.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write("%d" % var)
    file.write("\n")
#- Fine Funzione -


def fwrite_string(file, var, attr, label, indentation=""):
    """
    Scrive su file la stringa passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not var:
        log.bug("var non è un parametro valido: %s" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    # Per le stringhe multilinea va subito a capo, non è obbligatorio
    # sintatticamente ma è più leggibile e salta maggiormente all'occhio
    # che la stringa è multilinea
    if "\n" in var:
        file.write(indentation + label.strip() + "\n")
        for line in var.split("\n"):
            if line and line[0] == " ":
                file.write(".%s\n" % line)
            else:
                file.write("%s\n" % line)
    else:
        file.write(indentation + label)
        if var[0] == " ":
            file.write(".%s\n" % var)
        else:
            file.write(var + "\n")
#- Fine Funzione -


def fwrite_bool(file, var, attr, label, indentation=""):
    """
    Scrive su file un valore booleano come stringa.
    """
    if not file:
        log.bug("file non è un parametro valido: %s" % file)
        return

    if not var and var != False:
        log.bug("var non è un parametro valido: %s" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write(str(var))
    file.write("\n")
#- Fine Funzione -


def fwrite_percent(file, var, attr, label, indentation=""):
    """
    Scrive un valore con il simbolo di percentuale finale.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write("%s%%" % var)
    file.write("\n")
#- Fine Funzione -


def fwrite_temperature(file, var, attr, label, indentation=""):
    """
    Scrive un valore con il simbolo dei gradi finale.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write("%s°" % var)
    file.write("\n")
#- Fine Funzione -


def fwrite_measure(file, var, attr, label, indentation=""):
    """
    Scrive un valore con l'unità di misura adatta alla lunghezza passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    if var > 0:
        cm_value_string = str(var)
        m_value_string  = str(var / 1000)
        km_value_string = str(var / 1000000)

        lengths = [cm_value_string, m_value_string, km_value_string]

        index = get_index_of_shortest_string(lengths)
        if index < 0 or index >= len(lengths):
            log.bug("index cercato è errato: %r per l'attributo %s" % (index, attr))
            index = 0
    else:
        if var < 0:
            log.bug("var è un valore negativo: %r" % var)
        index = 0
        lengths = ["0"]

    file.write(indentation + label)
    file.write(lengths[index] + UM_LENGTHS[index])
    file.write("\n")
#- Fine Funzione -


def fwrite_weight(file, var, attr, label, indentation=""):
    """
    Scrive un valore con l'unità di misura adatta alla larghezza passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    if var > 0:
        g_value_string  = str(var)
        kg_value_string = str(var / 1000)
        q_value_string  = str(var / 1000000)
        t_value_string  = str(var / 1000000000)

        weights = [g_value_string, kg_value_string, q_value_string, t_value_string]

        index = get_index_of_shortest_string(weights)
        if index < 0 or index >= len(weights):
            log.bug("index cercato è errato: %r per l'attributo %s" % (index, attr))
            index = 0
    else:
        if var < 0:
            log.bug("var è un valore negativo: %r" % var)
        index = 0
        weights = ["0"]

    file.write(indentation + label)
    file.write(weights[index] + UM_WEIGHTS[index])
    file.write("\n")
#- Fine Funzione -


def fwrite_css_measure(file, var, attr, label, indentation=""):
    """
    Scrive un valore con l'unità di misura adatta alla larghezza passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write(var)
    file.write("\n")
#- Fine Funzione -


def fwrite_css_border(file, var, attr, label, indentation=""):
    """
    Scrive un valore con l'unità di misura adatta alla larghezza passata.
    """
    if not file:
        log.bug("file non è un parametro valido: %r" % file)
        return

    if not var and var != 0:
        log.bug("var non è un parametro valido: %r" % var)
        return

    if not attr:
        log.bug("attr non è un parametro valido: %r" % attr)
        return

    if not label:
        log.bug("label non è un parametro valido: %r" % label)
        return

    # -------------------------------------------------------------------------

    file.write(indentation + label)
    file.write(var)
    file.write("\n")
#- Fine Funzione -


#- ALTRE FUNZIONI --------------------------------------------------------------

def _check_all_strings(table_name, data_code, data):
    """
    Controlla ricorsivamente che tutte le stringhe contenute nel dato che non
    abbiano nessun tra i primi 32 caratteri (esclusi gli a capo) e che gli
    eventuali stili css siano corretti.
    """
    if not table_name:
        log.bug("table_name non è un parametro valido: %r" % table_name)
        return

    if not data_code:
        log.bug("data_code non è un parametrova valido: %r" % data_code)
        return

    if not data:
        log.bug("data non è un parametro valido: %s" % data)
        return

    # -------------------------------------------------------------------------

    if isinstance(data, (list, tuple)):
        for var in data:
            if var:
                _check_all_strings(table_name, data_code, var)
    elif isinstance(data, dict):
        for key in data:
            if key:
                _check_all_strings(table_name, data_code, key)
            if data[key]:
                _check_all_strings(table_name, data_code, data[key])
    elif isinstance(data, basestring):
        # Cicla alla ricerca di caratteri speciali saltando \n e \r
        for c in data:
            if c in UNALLOWED_CHARS:
                log.bug("Carattere speciale numero %d nella stringa %s (%s/%s)" % (
                    ord(c), data, table_name, data_code))

        # Controlla che vi sia caratteri di spazio dopo la punteggiatura
        # (TD) oltre che spammoso da molti falsi positivi
        #if "asciiart" not in data and "\n" in data:
        #    for n, c in enumerate(remove_colors(data)[ : -1]):
        #        if c in (",", ";", ".", ":", "!", "?"):
        #            if data[n+1] in ("\n", "\r") or data[n+1] in (".", "!", "?"):
        #                continue
        #            if data[n+1] != " ":
        #                log.bug("Punteggiatura %s senza una spaziatura successiva alla stringa %s (%s/%s)" % (
        #                    c, data, table_name, data_code))

        # Controlla che la stringa con contenga degli erronei doppi spazi
        # (TT) per ora disattivato perché spammoso
        #if "asciiart" not in data  and "  " in data:
        #    log.bug("Doppi spazi trovati alla stringa %s (%s/%s)" % (
        #        data, table_name, data_code))

        # Controlla gli stili della stringa
        check_colors(data)
    elif type(data) == EnumElement:
        log.bug("Non dovrebbero esistere EnumElement tra i dati del database (%s/%s)" % (
            table_name, data_code))
    elif isinstance(data, types.InstanceType):
        references = []
        if hasattr(data, "REFERENCES"):
            references += data.REFERENCES.keys()
        if hasattr(data, "WEAKREFS"):
            references += data.WEAKREFS.keys()
        for key in data.__dict__:
            if key in references:
                continue
            if data.__dict__[key]:
                _check_all_strings(table_name, data_code, data.__dict__[key])
#- Fine Funzione -


def _exclude_compiled_files(filename):
    if not filename or filename.endswith((".pyc", ".pyo")):
        return True
    else:
        return False
#- Fine Funzione -


#= SINGLETON ===================================================================

database = Database()
