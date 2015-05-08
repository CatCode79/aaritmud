# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle quest automatico, basato sullo schema di Propp:
http://it.wikipedia.org/wiki/Schema_di_Propp.
Lo schema generale di una fiaba, secondo Propp, è il seguente:
    Equilibrio iniziale (inizio);
    Rottura dell'equilibrio iniziale (movente o complicazione);
    Peripezie dell'eroe;
    Ristabilimento dell'equilibrio (conclusione).
"""


#= IMPORT ======================================================================

from src.data import Data
from src.log  import log


#= CLASS =======================================================================

class Quest(Data):
    PRIMARY_KEY = "code"
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"antagonist"        : ("src.quest", "QuestActant"),
                   "mandator"          : ("src.quest", "QuestActant"),
                   "helper"            : ("src.quest", "QuestActant"),
                   "award"             : ("src.quest", "QuestActant"),
                   "owner"             : ("src.quest", "QuestActant"),
                   "giver"             : ("src.quest", "QuestActant"),
                   "hero"              : ("src.quest", "QuestActant"),
                   "false_hero"        : ("src.quest", "QuestActant"),
                   "introduction"      : ("src.quest", "QuestFunction"),
                   "departure"         : ("src.quest", "QuestFunction"),
                   "prohibition"       : ("src.quest", "QuestFunction"),
                   "breach"            : ("src.quest", "QuestFunction"),
                   "recognition"       : ("src.quest", "QuestFunction"),
                   "delation"          : ("src.quest", "QuestFunction"),
                   "trap"              : ("src.quest", "QuestFunction"),
                   "connivance"        : ("src.quest", "QuestFunction"),
                   "damage"            : ("src.quest", "QuestFunction"),
                   "mediation"         : ("src.quest", "QuestFunction"),
                   "consensus"         : ("src.quest", "QuestFunction"),
                   "departure"         : ("src.quest", "QuestFunction"),
                   "donor_function"    : ("src.quest", "QuestFunction"),
                   "hero_reaction"     : ("src.quest", "QuestFunction"),
                   "supplying_magical" : ("src.quest", "QuestFunction"),
                   "transfer"          : ("src.quest", "QuestFunction"),
                   "fight"             : ("src.quest", "QuestFunction"),
                   "mark"              : ("src.quest", "QuestFunction"),
                   "victory"           : ("src.quest", "QuestFunction"),
                   "removal"           : ("src.quest", "QuestFunction"),
                   "return_home"       : ("src.quest", "QuestFunction"),
                   "persecution"       : ("src.quest", "QuestFunction"),
                   "rescue"            : ("src.quest", "QuestFunction"),
                   "incognito_arrival" : ("src.quest", "QuestFunction"),
                   "false_claims"      : ("src.quest", "QuestFunction"),
                   "trial"             : ("src.quest", "QuestFunction"),
                   "overcoming"        : ("src.quest", "QuestFunction"),
                   "identification"    : ("src.quest", "QuestFunction"),
                   "unmasking"         : ("src.quest", "QuestFunction"),
                   "transfiguration"   : ("src.quest", "QuestFunction"),
                   "punishment"        : ("src.quest", "QuestFunction"),
                   "final_reward"      : ("src.quest", "QuestFunction")}
    REFERENCES  = {}

    def __init__(self, code=""):
        self.code = code  # Codice identificativo della quest

        # Elenco dei possibili Attanti della quest:
        # Uno stesso ruolo può essere ricoperto da più personaggi (ad esempio,
        # l'eroe sconfigge il drago malefico e la sorella, altrettanto malvagia,
        # si incarica del ruolo antagonistico di inseguirlo per ucciderlo e
        # vendicarsi); oppure, per converso, uno dei personaggi potrebbe
        # ricoprire più ruoli (ad esempio, un padre potrebbe mandare suo figlio
        # alla ricerca dell'oggetto della mancanza e dargli una spada, agendo
        # quindi sia da mandante che da donatore).
        self.antagonist = []  # L'antagonista, colui che lotta contro l'eroe
        self.mandator   = []  # Il mandante: il personaggio che esplicita la mancanza e manda via l'eroe
        self.helper     = []  # L'aiutante (magico): la persona che aiuta l'eroe nella sua ricerca
        self.award      = []  # Il premio: l'eroe si rende degno del premio nel corso della storia, ma è impossibilitato a usufruirne per via di una serie di ingiustizie, generalmente causate dall'antagonista
        self.owner      = []  # Il proprietario del premio: colui che fornisce gli incarichi all'eroe, identifica il falso eroe e dona il premio a questi
        self.giver      = []  # Il donatore: il personaggio che prepara l'eroe o gli fornisce l'oggetto magico
        self.hero       = []  # L'eroe o la vittima/il ricercatore: colui che reagisce al donatore
        self.false_hero = []  # Il falso eroe: la persona che si prende il merito delle azioni dell'eroe

        # Elenco delle possibili Funzioni della quest:
        # Occasionalmente, alcune di queste funzioni possono essere invertite:
        # ad esempio, l'eroe potrebbe ricevere l'oggetto magico quando si trova
        # ancora a casa, anticipando quindi la funzione del donatore.
        # Più frequentemente, il donatore nega l'oggetto all'eroe per ben due
        # volte prima di consegnarglielo, secondo quelle che vengono chiamate
        # -Le tre regole della Cultura Occidentale:
        self.introduction      = []  # Situazione Iniziale
        self.departure         = []  # Allontanamento
        self.prohibition       = []  # Divieto
        self.breach            = []  # Infrazione
        self.recognition       = []  # Ricognizione
        self.delation          = []  # Delazione
        self.trap              = []  # Tranello
        self.connivance        = []  # Connivenza
        self.damage            = []  # Danneggiamento o Mancanza
        self.mediation         = []  # Mediation
        self.consensus         = []  # Concenso
        self.departure         = []  # Partenza
        self.donor_function    = []  # Funzione del Donatore
        self.hero_reaction     = []  # Reazione dell'Eroe
        self.supplying_magical = []  # Fornitura dell'Oggetto Magico
        self.transfer          = []  # Trasferimento
        self.fight             = []  # Lotta
        self.mark              = []  # Marchiatura
        self.victory           = []  # Vittoria
        self.removal           = []  # Rimozione
        self.return_home       = []  # Ritorno al luogo originale
        self.persecution       = []  # Persecuzione
        self.rescue            = []  # Salvataggio
        self.incognito_arrival = []  # Arrivo in Incognito
        self.false_claims      = []  # Pretese Infondate
        self.trial             = []  # Prova
        self.overcoming        = []  # Superamento della Prova
        self.identification    = []  # Identificazione
        self.unmasking         = []  # Smascheramento
        self.transfiguration   = []  # Trasfigurazione
        self.punishment        = []  # Punizione
        self.final_reward      = []  # Ricompensa Finale
    #- Fine Inizializzazione -


class QuestActant(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"entities" : ("proto_mobs", "proto_items"),
                   "areas"    : ("areas", )}

    def __init__(self):
        self.areas    = []
        self.entities = []
    #- Fine Inizializzazione -


class QuestFunction(object):
    def __init__(self):
        self.inputs = ""
        self.check  = ""
    #- Fine Inizializzazione -


#= FUNZIONI ====================================================================

