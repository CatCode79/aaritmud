# -*- coding: utf-8 -*-

"""
Modulo di gestione del forum.
"""

#http://docs.python.org/library/sqlite3.html
#http://www.vbulletin.it/forum.php?s=472ca7c8ddfd23457d7ff51b6cd06c32
#immagine avatar: 180 * 260 * 15kb direi che potrebbe andare bene


#= IMPORT ======================================================================

import sqlite3

from src.config import config


#= CLASSI ======================================================================

class Table(object):
    def __init__(self, code="", name="", descr=""):
        self.code  = code
        self.name  = name
        self.descr = descr
    #- Fine Inizializzazione -


class ForumDB(object):
    tables = [Table("player_help",      "Richieste di aiuto",            "Qui si può chiedere informazioni d'ogni tipo"),
              Table("player_mud",       "Riguardo Aarit e i Mud",        "Qui è possibile parlare di Aarit e dei Mud in generale"),
              Table("player_fantasy",   "Fantasy all'Opera",             "Qui i giocatori hanno la possibilità di narrare le loro avventure o raccontare il loro passato"),
              Table("player_quests",    "Quests",                        "Organizzazione, partecipazione e considerazioni a riguardo"),
              Table("player_idea",      "Idee, Proposte o Suggerimenti", "Qui è possibile suggerire alla Ciurma di Aarit modifiche utili"),
              Table("player_bug",       "Bug o Typo",                    "Qui è possibile segnalare errori riscontrati in Aarit"),
              Table("player_technical", "L'Angolo Tecnico",              "Discussioni aperte relative l'area building e il codice di Aarit"),
              Table("player_other",     "Parliamo d'Altro",              "Discussioni non inerenti Aarit e i Mud"),
             #Table("clan_",            "",                              ""),
              Table("admin_general",    "Gestione del Mud in generale",  "Discussioni su come gestire al meglio Aarit")]

    def __init__(self):
        self.conn   = None
        self.cursor = None
    #- Fine Inizializzazione -

    def load(self):
        """
        Apre ed eventualmente crea le tabelle del database del forum.
        """
        self.conn   = sqlite3.connect("persistence/forum.sqlite")
        self.cursor = self.conn.cursor()
        self.create()
    #- Fine Metodo -

    def save(self):
        """
        Dalva e chiude il database del forum.
        """
        self.conn.commit()
        self.cursor.close()
    #- Fine Metodo -

    def create(self):
        """
        Crea le tabelle dei forum non ancora esistenti nel database.
        """
        for forum_table in self.tables:
            # (bb) ma qui non bisognerebbe utilizzare forse l'operatore ? invece, oppure è giusto così?
            query = '''CREATE TABLE IF NOT EXISTS %s(subject TEXT, author TEXT, date TEXT, visits INTEGER, important INTEGER, closed INTEGER)''' % forum_table.code
            self.cursor.execute(query)
        self.conn.commit()
    #- Fine Metodo -

    def get_threads_qty(self, forum_code):
        return 0
    #- Fine Metodo -

    def get_visits_qty(self, forum_code):
        return 0
    #- Fine Metodo -

    def get_last_thread(self, forum_code):
        return None
    #- Fine Metodo -

    def iter_threads(self, forum_code):
        #query = ''''''
        #self.cursor.execute(query)
        #yield 
        return []
    #- Fine Metodo -


class Thread(object):
    def __init__(self, id="", subject="", author="", date="", visits=0, important=False, closed=False):
        self.id        = id
        self.subject   = subject
        self.author    = author
        self.date      = date  # (TT)
        self.visits    = visits
        self.important = important
        self.closed    = closed
    #- Fine Inizializzazione -

    def get_icon(self, account_conn):
        return ""
    #- Fine Metodo -

    def get_post_id(account_conn):
        if False:
            return "#post0"
        else:
            return ""
    #- Fine Metodo -


#= SINGLETON ===================================================================

forum_db = ForumDB()
