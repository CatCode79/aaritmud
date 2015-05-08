# -*- coding: utf-8 -*-

"""
Serve a gestire il sito web del gioco.
"""


#= IMPORT ======================================================================

import os

from twisted.web import script, server, static

from src.utility import to_capitalized_words


#= CLASSI ======================================================================

class Site(server.Site):
    WWW_PATH = "www"
    CONTROLLERS_PATH = "src/controllers"
    INDEX_FILENAME = "index.html"
    RPY_EXTENSION = ".html"

    def __init__(self):
        root = static.File(self.WWW_PATH)
        root.indexNames = [self.INDEX_FILENAME, ]
        root.processors = {self.RPY_EXTENSION : script.ResourceScript}

        server.Site.__init__(self, root)

        #self.lost_password_requests = {}  # Richieste di password perduta  (TD) farle vedere anche nella pagina delle connessioni
        #self.contact_staff_requests = {}  # Richieste di contatto con lo staff  (TD) serve per evitare di inviare mail a iosa

        self.remove_rpy_files()
        self.generate_rpy_files()
        self.import_controllers()
    #- Fine Inizializzazione -

    def remove_rpy_files(self):
        """
        Rimuove tutti i file html-risorsa esistenti nella cartella web.
        I file html-risorsa si trovano tutti in questa cartella e non in altre
        sottocartelle.
        Per riconoscere i file di codice HTML statici questi hanno l'estenzione
        htm e si possono trovare nelle sottocartelle.
        """
        for filename in os.listdir(self.WWW_PATH):
            if filename[0] == "_" or not filename.lower().endswith(self.RPY_EXTENSION):
                continue
            filepath = "%s/%s" % (self.WWW_PATH, filename)
            try:
                os.remove(filepath)
            except EnvironmentError:
                log.bug("Impossibile rimuovere il file %s" % filepath)
                continue
    #- Fine Metodo -

    def generate_rpy_files(self):
        """
        Visto che tutte le pagine web sono uguali ed hanno la stessa funzione i
        resource scripts vengono generati automaticamente all'avvio del server.
        Convenzionalmente i resource script hanno come estenzione 'rpy' ma qui
        l'ho modificata in 'html' per far apparire l'url nella barra degli
        indirizzi del browser il meno aliena possibile.
        """
        for module_name in self.iter_controller_module_names():
            rpy_file = open(self.WWW_PATH + "/%s%s" % (module_name, self.RPY_EXTENSION), "w")
            rpy_file.write("from src.config import config as config_module\n")
            rpy_file.write("from %s import %s\n" % (self.CONTROLLERS_PATH.replace("/", "."), module_name))
            rpy_file.write("if config_module.reload_web_pages:\n")
            rpy_file.write("    reload(%s)\n" % module_name)
            rpy_file.write("resource = %s.%sPage()\n" % (module_name, to_capitalized_words(module_name)))
            rpy_file.close()
    #- Fine Metodo -

    def import_controllers(self):
        """
        Importa tutti i controller per assicurarsi che nessuno di loro abbia
        un errore di sintassi o qualche cosa del genere, in maniera tale da
        evitare che la cosa venga scoperta solo poi, durante la navigazione.
        """
        for module_name in self.iter_controller_module_names():
            module_path = "%s.%s" % (self.CONTROLLERS_PATH.replace("/", "."), module_name)
            __import__(module_path, globals(), locals(), [""])
    #- Fine Metodo -

    def iter_controller_module_names(self):
        """
        Ritorna tutti i nomi del moduli dei controller esistenti.
        """
        for filename in os.listdir(self.CONTROLLERS_PATH):
            filename = filename.lower()
            if filename[0] != "_" and  filename.endswith(".py"):
                yield filename.replace(".py", "")
    #- Fine Metodo -


#= SINGLETON ===================================================================

site = Site()
