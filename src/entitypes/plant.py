# -*- coding: utf-8 -*-

"""
Modulo riguardante la tipologia di entità piana assieme a tutto ciò che serve
per la crescita e la cura delle piante, fiorescenza e raccolta dei relativi
frutti.
"""


#= IMPORT ======================================================================

import math
import random

from src.color      import color_first_upper
from src.config     import config
from src.database   import database
from src.defer      import defer
from src.element    import Flags
from src.enums      import CONTAINER, ENTITYPE, FLAG, LOG, SECTOR
from src.gamescript import check_trigger
from src.log        import log
from src.loop       import UnstoppableLoop
from src.utility    import copy_existing_attributes, get_percent

from src.entitypes.container import Container


#= CLASSI ======================================================================

class Plant(object):
    PRIMARY_KEY = ""
    VOLATILES   = ["deferred_stage"]
    MULTILINES  = ["comment"]
    SCHEMA      = {"temperature"    : ("",            "temperature"),
                   "humidity"       : ("",            "percent"),
                   "contents"       : ("",            "int"),
                   "worse_affects"  : ("src.affect",  "Affect"),
                   "better_affects" : ("src.affect",  "Affect")}
    REFERENCES  = {"worse_entity"   : ["proto_items", "proto_mobs"],
                   "normal_entity"  : ["proto_items", "proto_mobs"],
                   "better_entity"  : ["proto_items", "proto_mobs"],
                   "dead_entity"    : ["proto_items", "proto_mobs"]}
    WEAKREFS    = {}

    def __init__(self):
        self.comment        = ""
        self.sectors        = Flags(SECTOR.NONE)  # Settori in cui può essere seminato
        self.rpg_hours      = 1    # Durata in ore rpg prima che questo stadio si attivi
        self.temperature    = 20   # Temperatura media ideale
        self.humidity       = 50   # Percentuale dell'umidità ideale
        self.contents       = {}   # Dizionario con valori di codice_entità/quantità per popolare il contenuto dell'entità di questo stadio
        self.worse_entity   = None # Entità peggiore del prossimo stadio di crescita, se in questo stadio non viene curata o curata male
        self.normal_entity  = None # Entità normale del prossimo stadio di crescita, se in questo stadio viene curata normalmente
        self.better_entity  = None # Entità migliore del prossimo stadio di crescita, se in questo stadio viene curata molto bene
        self.dead_entity    = None # Entità morta relativa al prossimo stadio
        self.worse_affects  = []   # Affect che danneggiano la pianta
        self.better_affects = []   # Affect che migliorano la pianta
        self.decomposition_rpg_hours = config.purification_rpg_hours  # Ore Rpg prima che il contenuto venga decomposto dopo essere caduta dalla pianta
        self.remaining_life = -1   # Cicli di vita rimanenti alla pianta prima di morire
        self.worse_counter  = 0    # Contatore degli stadi di crescita andati male
        self.normal_counter = 0    # Contatore degli stadi di crescita andati normalmente
        self.better_counter = 0    # Contatore degli stadi di crescita andati ottimamente

        # Volatili
        self.deferred_stage = None
    #- Fine Inizializzazione -

    def get_error_message(self, entity):
        if self.remaining_life <= 0 and self.remaining_life != -1:
            return "remaining_life non è un'aspettativa di vita valida, deve essere maggiore di 0 oppure diverso da -1: %d" % self.remaining_life
        elif self.sectors.get_error_message(SECTOR, "sectors") != "":
            return self.sectors.get_error_message(SECTOR, "sectors")
        if self.rpg_hours <= 0:
            return "rpg_hours non è una durata in ore rpg valida: %d" % self.rpg_hours
        elif self.get_contents_error_message() != "":
            return self.get_contents_error_message()
        elif self.get_affects_error_message("worse_affects") != "":
            return self.get_affects_error_message("worse_affects")
        elif self.get_affects_error_message("better_affects") != "":
            return self.get_affects_error_message("better_affects")

        return ""
    #- Fine Metodo -

    def get_contents_error_message(self):
        for key, value in self.contents.iteritems():
            if not key:
                return "contents con chiave non valida (%r) per il valore %s" % (key, value)
            if int(value) <= 0:
                return "contents con valore non valido (%d) per la chiave %s" % (int(value), key)

        return ""
    #- Fine Metodo -

    def get_affects_error_message(self, attr_name):
        if attr_name not in ("worse_affects", "better_affects"):
            log.bug("attr_name non è un parametro valido: %s" % attr_name)
            return ""

        # ---------------------------------------------------------------------

        for affect in getattr(self, attr_name):
            error_message = affect.get_error_message()
            if error_message != "":
                return error_message
        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Plant()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, plant2):
        if not plant2:
            return False

        if self.deferred_stage or plant2.deferred_stage:
            return False

        if self.comment != plant2.comment:
            return False
        if self.sectors != plant2.sectors:
            return False
        if self.rpg_hours != plant2.rpg_hours:
            return False
        if self.temperature != plant2.temperature:
            return False
        if self.humidity != plant2.humidity:
            return False
        if self.worse_entity != plant2.worse_entity:
            return False
        if self.normal_entity != plant2.normal_entity:
            return False
        if self.better_entity != plant2.better_entity:
            return False
        if self.dead_entity != plant2.dead_entity:
            return False
        if self.decomposition_rpg_hours != plant2.decomposition_rpg_hours:
            return False
        if self.remaining_life != plant2.remaining_life:
            return False
        if self.worse_counter != plant2.worse_counter:
            return False
        if self.normal_counter != plant2.normal_counter:
            return False
        if self.better_counter != plant2.better_counter:
            return False

        if len(self.contents) != len(plant2.contents):
            return False
        for key, value in self.contents.iteritems():
            if key not in plant2.contents:
                return False
            if value != plant2.contents[key]:
                return False

        if len(self.worse_affects) != len(plant2.worse_affects):
            return False
        for affect in self.worse_affects:
            for affect2 in plant2.worse_affects:
                if affect == affect2:
                    break
            else:
                return False

        if len(self.better_affects) != len(plant2.better_affects):
            return False
        for affect in self.better_affects:
            for affect2 in plant2.better_affects:
                if affect == affect2:
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    #---------------------------------------------------------------------------

    def start_growth(self, entity, type_attr_name):
        if not entity:
            log.bug("entity non è parametro valido: %r" % entity)
            return

        if type_attr_name not in ("plant_type", "seed_type"):
            log.bug("type_attr_name non è parametro valido: %r" % type_attr_name)
            return

        # ---------------------------------------------------------------------

        seconds = self.rpg_hours * (config.seconds_in_minute * config.minutes_in_hour)
        self.deferred_stage = defer(seconds, self.next_stage, entity, type_attr_name)
    #- Fine Metodo -

    def stop_growth(self):
        if self.deferred_stage:
            self.deferred_stage.pause()
            self.deferred_stage = None
    #- Fine Metodo -

    def next_stage(self, old_entity, type_attr_name):
        if not old_entity:
            log.bug("old_entity non è parametro valido: %r" % old_entity)
            return

        if type_attr_name not in ("plant_type", "seed_type"):
            log.bug("type_attr_name non è parametro valido: %r" % type_attr_name)
            return

        # ---------------------------------------------------------------------

        # Pulisce la deferred relativa a questo metodo in qualsiasi caso
        self.deferred_stage = None

        entitype = getattr(old_entity, type_attr_name)
        if not entitype:
            log.bug("%s dell'entità precedente non valido: %r" % (type_attr_name, entitype))
            return

        # (TD) deve scegliere quale delle tre entità worse, normal o better
        # in maniera non casuale ma basandosi su effettivi fattori ambientali
        entitypes = []
        for entitype_name in ("worse_entity", "normal_entity", "better_entity"):
            if getattr(entitype, entitype_name):
                entitypes.append(entitype_name)
        if not entitypes:
            log.bug("Nessuna tipologia d'entità da utilizzare come prossimo stadio: %r" % entitypes)
            return
        choised_attr = random.choice(entitypes)

        # Se la vita della pianta è terminata e finalmente si trova un'entità
        # di pianta morta, allora la utilizza
        if entitype.remaining_life == 0 and entitype.dead_entity:
            choised_attr = "dead_entity"

        # ---------------------------------------------------------------------

        # Crea la nuova pianta a seconda delle scelte di cui sopra
        choised_entity = getattr(entitype, choised_attr)
        if not choised_entity:
            log.bug("Impossibile continuare con la crescita della pianta da %s per la scelta %s" % (
                old_entity.code, choised_attr))
            return

        if choised_entity.max_global_quantity > 0 and choised_entity.current_global_quantity >= choised_entity.max_global_quantity:
            return

        new_entity = choised_entity.CONSTRUCTOR(choised_entity.code)

        # Passa alcune caratteristiche della vecchia entità nella nuova
        # prima di distruggerla
        if new_entity.plant_type:
            new_entity.flags += FLAG.GROWING
            new_entity.plant_type.remaining_life = entitype.remaining_life
            new_entity.plant_type.worse_counter  = entitype.worse_counter
            new_entity.plant_type.normal_counter = entitype.normal_counter
            new_entity.plant_type.better_counter = entitype.better_counter
            quality_attr = choised_attr.split("_")[0] + "_counter"
            setattr(new_entity.plant_type, quality_attr, getattr(new_entity.plant_type, quality_attr) + 1)

        # Inserisce la nuova entità in gioco
        new_entity.inject(old_entity.location)

        # ---------------------------------------------------------------------

        # Lista delle entità che cambieranno locazione nel ciclo sottostante
        # e che vengono passate nel trigger on_next_stage per comodità, vengono
        # salvati solo le entità frutta, seme e cibo
        entities = []

        # Controlla come deve comportarsi con il contenuto della vecchia entità:
        # se passarlo alla nuova, oppure distruggerlo, oppure ancora farlo
        # cadere a terra
        flower_counter = 0
        for content in old_entity.iter_contains(use_reversed=True):
            if content.entitype == ENTITYPE.FLOWER:
                flower_counter += 1
                continue
            elif content.entitype in (ENTITYPE.FRUIT, ENTITYPE.SEED, ENTITYPE.FOOD):
                content = content.from_location(content.quantity, use_repop=False)
                in_room = content.get_in_room()
                container_carrier = content.get_container_carrier()
                # Più la pianta è grande e maggiore è la probabilità che il suo
                # contenuto cada nella stanza invece che nel vaso
                if in_room and container_carrier and random.randint(0, max(1, math.log(new_entity.get_weight()) - math.log(container_carrier.get_weight()))) == 0:
                    content.to_location(in_room)
                    entities.append(content)
                elif in_room and random.randint(0, max(1, math.log(new_entity.get_weight()))) == 0:
                    content.to_location(in_room)
                    entities.append(content)
                elif container_carrier:
                    content.to_location(container_carrier)
                    entities.append(content)
                else:
                    content.to_location(old_entity.location)
                    entities.append(content)
                # Tutte le entità inserite a terra attivano un timer per
                # rimuoverle e non creare inutili mucchi di semi
                content.start_purification(entitype.decomposition_rpg_hours, decomposition=True)
            else:
                # (BB) qui se passavano delle entità di tipo food invece di
                # ENTITYPE.FRUIT bacava i riferimenti, probabilmente il
                # problema c'è ancora, per questo l'elif sopra accetta
                # anche food
                content = content.from_location(content.quantity, use_repop=False)
                content.to_location(new_entity)

        # ---------------------------------------------------------------------

        # Si salva tutti i semi per sapere se entità da inserire nella pianta
        # sia solo di tipo seme oppure se eventuali semi sono mischiati ad
        # altre tipo di entità, ciò serve perché in tal caso i semi vengono
        # inseriti nelle altre tipologie di entità (frutti o fiori chessia)
        seeds = []
        for proto_code, quantity in entitype.contents.iteritems():
            prototype = database.get_proto_entity(proto_code)
            if not prototype:
                continue
            if prototype.entitype == ENTITYPE.SEED:
                seeds.append([prototype, quantity])
        if len(seeds) == len(entitype.contents):
            seeds = []

        # Ogni volta che la pianta produce dei semi diminuisce le proprie
        # risorse vitali
        if seeds and new_entity.plant_type.remaining_life > 0:
            new_entity.plant_type.remaining_life -= 1

        # Crea l'eventuale contenuto voluto per la nuova entità
        for proto_code, quantity in entitype.contents.iteritems():
            prototype = database.get_proto_entity(proto_code)
            if not prototype:
                continue
            # Se il prototipo è un seme da inserire in un frutto o simile allora lo salta
            for seed in seeds:
                if prototype == seed[0]:
                    break
            else:
                add_content(prototype, quantity, choised_attr, flower_counter, new_entity, seeds)

        # Crea, se è il caso, una tipologia di contenitore alla nuova entità
        # per permettere ai giocatori ad interagire con la pianta
        if not new_entity.container_type and new_entity.entitype == ENTITYPE.PLANT:
            container = Container()
            container.max_weight = new_entity.get_carried_weight() * 2
            new_entity.container_type = container

        # Avvisa dell'avvenuta crescita della pianta
        if new_entity.plant_type:
            message = "%s cresce: %s"
        else:
            message = "%s finisce di crescere: %s"
        log.plant(message % (old_entity.prototype.code, new_entity.prototype.code))

        # Supporto gamescript, se viene forzato il ritorno non esegue
        # l'eventuale stadio successivo
        force_return = check_trigger(old_entity, "on_next_stage", old_entity, new_entity, choised_attr, entities)
        if force_return:
            return True

        # Ora si può rimuovere la vecchia pianta
        # (la si può estrarre completamente perché se possiede del contenuto non
        # viene raggruppata fisicamente, altrimenti si può rimuovere il gruppetto
        # senza problemi perché senza contenuto)
        old_entity.extract(old_entity.quantity, use_repop=False)

        # Prepara il lancio per il prossimo stage
        if choised_attr != "dead_entity" and new_entity.plant_type:
            new_entity.plant_type.start_growth(new_entity, "plant_type")
    #- Fine Metodo -


#class PlantLoop(UnstoppableLoop):
#    def __init__(self):
#        super(PlantLoop, self).__init__()
#        self.paused = False  # Indica se questo ciclo è stato messo in pausa dal comando loop
#    #- Fine Inizializzazione -
#
#    def start(self, seconds):
#        super(PlantLoop, self).start(seconds)
#    #- Fine Metodo -
#
#    def stop(self):
#        super(PlantLoop, self).stop()
#    #- Fine Metodo -
#
#    def cycle(self):
#        if self.paused:
#            return
#        
#    #- Fine Metodo -


#= FUNZIONI ====================================================================

def restart_all_planting():
    for obj in database["rooms"].values() + database["players"].values() + database["items"].values() + database["mobs"].values():
        for entity in obj.iter_contains():
            if FLAG.GROWING not in entity.flags:
                continue
            if entity.plant_type:
                entity.plant_type.start_growth(entity, "plant_type")
            elif entity.seed_type:
                entity.seed_type.start_growth(entity, "seed_type")
            else:
                log.bug("entità %s con flag di GROWING anche se non ha la struttura seed_type o plant_type valida" % entity.code)
#- Fine Funzione -


def add_content(prototype, quantity, choised_attr, flower_counter, location, seeds):
    quantity = random.randint(quantity - 1, quantity + 1)
    if choised_attr == "worse_entity":
        quantity /= 4
    elif choised_attr == "better_entity":
        quantity *= 2

    # I frutti possono nascere in un numero massimo pari agli eventuali
    # precedenti fiori
    if flower_counter != 0 and quantity > flower_counter and prototype.entitype == ENTITYPE.FRUIT:
        quantity = flower_counter

    while quantity > 0:
        content = prototype.CONSTRUCTOR(prototype.code)
        if content.prototype.max_global_quantity == 0 or content.prototype.current_global_quantity < content.prototype.max_global_quantity:
            if FLAG.INTERACTABLE_FROM_OUTSIDE in location.flags and location.entitype == ENTITYPE.GROUND:
                # Inserisce il contenuto nel vaso invece che nel terreno
                content.inject(location.location)
            else:
                content.inject(location)
            if seeds:
                content.container_type = Container()
                content.container_type.flags = Flags(CONTAINER.CLOSED, CONTAINER.CLOSABLE, CONTAINER.OPEN_ONE_TIME)
                content.container_type.max_weight = content.get_total_weight()
                seed = random.choice(seeds)
                add_content(seed[0], seed[1], choised_attr, 0, content, [])
        quantity -= 1
#- Fine Funzione -


# (TD) L'intuito alto farà ricordare d'annaffiare le piante

"""
Premesse:
- Visto che questo sistema non tiene conto delle stazioni e vista la velocità
con cui alcune piante crescerebbero ho pensato che potrei inserirlo come
skill-spell (coltivare o che) per il druido o l'erborista (meglio il primo che
ha più spell-skill a sostegno l'erboristeria la vedo più legata all'alchimista)
ma visto che le classi oltre le prime 4 (guerriero, mago, ranger e ladro)
avranno la loro comparsa solo tra secoli a venire potrei inserirla come
skill-meccanica globale o che..
- Da notare la percentuale per i valori di effect, perché visto che posso
cambiare il massimale delle varie statistiche in qualsiasi momento (causa
bilanciamenti progressivi) anche gli effect si modificheranno di conseguenza.
Ed è più facile pensare in termini di: "Il cinque per cento della vita di una
persona normale viene aumentata" invece che cercare di indovinare come sarà
il sistema aaritiano delle statistiche.
Si possono mettere qualsiasi effect che venga in mente, non avendoli ancora
creati non ho una lista precisa ma sicuramente più di un Mud normale (il
sistema di effect è legato alla creazione casuale degli oggetti alla Diablo).

--------------------------------------------------------------------------------

Partiamo dalle tipologie d'acqua: a parte l'acqua pura e semplice, che non
ha modificatori di effetti sul risultato, tutti gli altri tipi d'acqua sono
delle miscele o soluzioni con dei modificatori sugli oggetti che la
pianta darà.
Tutto questo ha a che fare un po' con l'alchimia, è vero che di solito l'acqua
si trova già così com'è (salata, con magnesio, con sodio tutto in minime
quantità) però volendo uno la si può creare da sé.
L'idea che va' per la maggiore, che poi è quella che potrebbe dare le basi ad
una "alchimia generica", è questa: bisogna associare ad ogni materiale un
particolare effetto (o affect che dir si voglia) per esempio a MATERIAL_IRON
ci potrebbe stare bene un +3% forza.
Quindi l'acqua ferrosa/rugginosa avrà come modificatore un +3% di forza sui
frutti.
Purtroppo questo sistema non è esattamente quello che avevi ideato tu, avevi
ideato acque di fonte, di pozzo etc etc, è più una cosa alchemica; l'idea
sarebbe quella di creare grazie ai materiali una miscela e legare questa miscela
ad un oggetto di tipo liquido che può essere trasportato
Ovvero per ogni materiale che vuoi che abbia effetto con l'acqua tu ci metti
un affect, fai una lista
MATERIAL_XXX  effect
e siano a posto per ora, gli effect te li inventi, un solo effect per materiale,
è meglio, a meno che non sia un materiale particolare o raro; possono essere
negativi, tutti i valori sono in percentuale, le ore di durata media dell'effect
vanno calcolati in ore rpg.

--------------------------------------------------------------------------------

L'etichetta Seed è un'etichetta per i soli oggetti che sono dei semi (o fanno
da seme, ovvero una spada anche se è ITEMTYPE_WEAPON può avere l'etichetta Seed
è quindi può essere piantata per creare così poi la pianta: "ombelico del mondo"
e far sbucare come frutti: "vari porcellini pi-chan con cartine stradali in mano")
Ma quello era un caso particolare.
Guardati la struttura prima, poi la spiego.

Seed:
  Stages:
    Duration: 12
    Result: garden_item_quercia_piccola
  End
  Stages:
    Duration: 8
    Result: garden_item_quercia_media
  End
  Stages:
    Duration: 6
    Result: garden_item_oak_quercia_frutti
    Give: garden_item_oak_fruit
    Quantity: 15
  End
  Stages:
    Duration: 2
    Result: garden_item_quercia_cadono_frutti
    Give: -1
  End
  Stages:
    Duration: 3
    Result: garden_item_quercia_morta
  End
End

Ad ogni stages corrisponde un'innaffiata, da quando uno inserisce questo
oggetto seed a quando il primo oggetto pianta dal codice
'garden_item_quercia_piccola'
si rivela passeranno 12 ore rpg (ho messo le ore a caso non prenderle come
traccia)
poi una volta sbucata fuori questa ci vorranno 8 ore perchè il prossimo oggetto
pianta sbuchi fuori, altrimenti dipende, per una volta che non la si annaffia
la pianta del prossimo stage sbuca fuori lo stesso, però vengono salvate delle
informazioni sulla innaffiata o meno e con che acqua (come hai detto tu vale il
primo tipo di acqua utilizata per fase)
Nel terzo stages, c'è la fruttificazione della pianta, con una media di 15
frutti (il valore cambia in più o in meno a seconda della innaffiata ottimale)
anche qui il valore è indicativo.. se ci metti tanti effect potenti o che durano
molto tempo meglio pochi frutti, altrimenti vedi tu.. .15 forse è un numero già
altuccio cmq.
Poi nella fase successiva grazie al Give a -1 si indica che i frutti che ha
addosso la pianta vanno per terra.
Nell'ultima fase si inserisce una pianta morente o morta.

Come vedi sono tutti oggetti, falli come ti vengono, buttali giù, sono abbastanza
convinto che queste siano le etichette che ti servano e non credo che le cambierò.
Mentre invece ho fatto una fatica boia a immaginarmi il sistema che sta sotto
alle tipologie d'acqua e mi sono scontrato con diversi problemi legati ai materiali.
Ho scritto un po' di fretta, spero si capisca, sennò fammi delle domande.
Bho, quindi ti ho dato da fare gli effect per materiale che male che vada si
possono utilizzare per l'alchimia. (cioè composizione di pozioni, unguenti,
bombe tramite alambicchi vari e varie regole per ottenere variegati risultati
partendo da quei materiali con certi effetti e bla bla bla)



(13.09.19) andrea.postal@gmail.com/ED2D7942: gli attributi di un seed type sono questi:
(13.09.20) andrea.postal@gmail.com/ED2D7942:         self.comment        = ""
        self.rpg_hours      = 60   # Durata in minuti rpg dell'attuale stadio di crescita
        self.content        = {}   # Dizionario con valori di codice_entità/quantità per popolare il contenuto dell'entità di questo stadio
        self.worse_entity   = None # Entità peggiore del prossimo stadio di crescita, se in questo stadio non viene curata o curata male
        self.normal_entity  = None # Entità normale del prossimo stadio di crescita, se in questo stadio viene curata normalmente
        self.better_entity  = None # Entità migliore del prossimo stadio di crescita, se in questo stadio viene curata molto bene
        self.worse_counter  = 0    # Contatore degli stadi di crescita andati male
        self.normal_counter = 0    # Contatore degli stadi di crescita andati normalmente
        self.better_counter = 0    # Contatore degli stadi di crescita andati ottimamente
        self.worse_affects  = []   # Affect che danneggiano la pianta
        self.better_affects = []   # Affect che migliorano la pianta

(13.09.40) andrea.postal@gmail.com/ED2D7942: rpg_hours è la durata di questo stadio di crescita
(13.09.58) andrea.postal@gmail.com/ED2D7942: metti caso che ad un seme metti un seedtype, con rpg_hours 120 tanto per
(13.10.18) Sulfrum: ecco io pensavo ad integrare la cosa nel calendario
(13.10.38) Sulfrum: ovvero che vi sia uno shift in modo che la pianta si sincronizzi con le stagioni
(13.10.43) Sulfrum: se pianto in inverno
(13.10.50) Sulfrum: alta possibilità magari di morte
(13.10.59) Sulfrum: lunga fase di crescita
(13.11.01) Sulfrum: etc etc
(13.11.17) andrea.postal@gmail.com/ED2D7942: sì vi piazzerò dei bonus o malus
(13.11.44) andrea.postal@gmail.com/ED2D7942: ma bisognerà considerare anche il freeze della crescita se il pg della pianta è offline.. questo se la crescita è lenta, ma non troppo
(13.11.50) Sulfrum: ottimo basterà che vi siano bonus e malus e la pianta potrà sincornizzarsi con le stagioni
(13.12.26) andrea.postal@gmail.com/ED2D7942: il problema di fondo è che se obblighiamo il pg ad entrare per annaffiare creiamo una dipendenza, a cui ormai sono concettualmente contrario
(13.12.51) andrea.postal@gmail.com/ED2D7942: preferisco un sistema per cui i giocatori entrano in gioco perchè si divertono veramente e non perchè sono obbligati
(13.12.58) andrea.postal@gmail.com/ED2D7942: cmq a parte questo
(13.13.02) Sulfrum: beh anche io
(13.13.17) Sulfrum: cmnq potrebbe bastare pagare o comperare un elementale
(13.13.59) andrea.postal@gmail.com/ED2D7942: non è una cattiva idea, ma è da pensare solo alla fine di tutto il ciclo
(13.14.03) andrea.postal@gmail.com/ED2D7942: content, che ora che ci penso sarà Contents, funziona come Specials dei gamescript
(13.14.06) andrea.postal@gmail.com/ED2D7942: sarà qualcosa tipo
(13.14.17) andrea.postal@gmail.com/ED2D7942: Contents codice_frutto 5
(13.14.43) andrea.postal@gmail.com/ED2D7942: ad indicare che in questo stadio di crescita potenzialmente ci sono 5 frutti, se la crescita è andata normalmente
(13.14.52) andrea.postal@gmail.com/ED2D7942: di più se è andata bene, di meno se è andata male
(13.15.01) andrea.postal@gmail.com/ED2D7942: poi il tutto si intreccia con le stagioni
(13.15.17) andrea.postal@gmail.com/ED2D7942: un attimo eh
(13.16.24) andrea.postal@gmail.com/ED2D7942: ecco, poi ci sono tre attributi
(13.16.35) andrea.postal@gmail.com/ED2D7942: worst_entity, normal_entity e better_entity
(13.17.27) andrea.postal@gmail.com/ED2D7942: sono le tre entità da utilizzare per iniziare il prossimo stadio di crescita a seconda che le cose siano andate bene o male
(13.17.36) andrea.postal@gmail.com/ED2D7942: o normali
(13.17.41) andrea.postal@gmail.com/ED2D7942: e qui è l'unico mio dubbio
(13.17.52) andrea.postal@gmail.com/ED2D7942: perchè forse servono 4 entità
(13.18.21) andrea.postal@gmail.com/ED2D7942: due per le cose andate a male: una per la secchezza e una per la troppa innaffiatura, ovvero la marcita
(13.18.57) andrea.postal@gmail.com/ED2D7942: devo dire che pensandoci.. viene fuori una bella struttura ad albero per tutte le fasi.. tutto dipende da come la si gioca
(13.19.06) Sulfrum: forse conviene nello stesso item
(13.19.16) Sulfrum: inserire descrizioni in una struttura specifica
(13.19.20) andrea.postal@gmail.com/ED2D7942: 3 stadi per tre entità ognuna sono già 9 seedtype da definire
(13.19.37) andrea.postal@gmail.com/ED2D7942: cioè?
(13.20.29) Sulfrum: tu intndi che devo avere 4 entità diverse ovvero scrivere 4 oggetti diversi?
(13.21.50) Sulfrum: cioè:
karpuram_item_papavero-04.dat
karpuram_item_papavero-04-secco.dat
karpuram_item_papavero-04-fradicio.dat
karpuram_item_papavero-04.morente.dat
(13.21.52) andrea.postal@gmail.com/ED2D7942: diciamo come vuoi... puoi utilizzare 3 entità invece di 4 e per le due fallite usare la stessa
(13.22.22) andrea.postal@gmail.com/ED2D7942: volendo per tutti gli stadi si potrebbe utilizzare sempre la stessa entità "fallita"
(13.22.36) andrea.postal@gmail.com/ED2D7942: mentre magari per l'entità normale e migliore crearle ad uopo
(13.23.01) Sulfrum: quel che dicevo io era un:
(13.23.50) Sulfrum: Name:
Name_marcia:
Name_secca:
(13.24.01) Sulfrum: all'interno dello stesso prototipo
(13.24.33) Sulfrum: in modo che quando si fa il prototipo ad es dello stadio 03 del Fiordaliso
(13.24.33) andrea.postal@gmail.com/ED2D7942: si ma poi vorrai personalizzare la descrizione... questo... quell'altro.. etc etc
(13.24.52) Sulfrum: di fatto dici che son davvero obj diversi
(13.25.13) Sulfrum: e che a parità di complicazioni tanto vale averli come item separati
(13.25.22) andrea.postal@gmail.com/ED2D7942: in realtà potrei creare il sistema in maniera tale che funzioni anche se abbia solo la normal_entity
(13.25.36) andrea.postal@gmail.com/ED2D7942: perchè tanto le info di fallimento o meno sono separate
(13.26.01) andrea.postal@gmail.com/ED2D7942: e che anche se uno stadio è fallito far apparire la normal entity
(13.26.05) Sulfrum: cioè a dire che è come se fosse immune al seccume e al marciume
(13.26.27) andrea.postal@gmail.com/ED2D7942: visivamente immune, in realtà lo ha subito
(13.26.40) Sulfrum: terrei però obbligatoriamente almeno 2 cose
(13.26.50) andrea.postal@gmail.com/ED2D7942: ma questo è giusto solo per alleggerire il lavoro dei builer, prima o poi i pg si lamenteranno :P
(13.26.52) Sulfrum: seme morto e pianta morta
(13.27.33) Sulfrum: beh tanto vale allora rendere obbligatorie le varie strutture item
(13.27.49) Sulfrum: alla peggio il builder va di copia incolla e poi modifica opportunamente
(13.32.52) andrea.postal@gmail.com/ED2D7942: sarà un po' un casino da avere tutte le strutture sotto il naso
(13.33.01) andrea.postal@gmail.com/ED2D7942: ma forse poi rivedo un po' le cose in tal senso
(13.33.16) andrea.postal@gmail.com/ED2D7942: poi ci sono questi tre:
(13.33.16) andrea.postal@gmail.com/ED2D7942:         self.worse_counter  = 0    # Contatore degli stadi di crescita andati male
        self.normal_counter = 0    # Contatore degli stadi di crescita andati normalmente
        self.better_counter = 0    # Contatore degli stadi di crescita andati ottimamente
(13.33.33) andrea.postal@gmail.com/ED2D7942: che mantiene il contatore dei vari stadi
(13.33.41) andrea.postal@gmail.com/ED2D7942: se uno ti va male aumenta di uno il worse_counter
(13.33.47) andrea.postal@gmail.com/ED2D7942: e così via
(13.34.23) andrea.postal@gmail.com/ED2D7942: quindi in realtà la pianta, o il seme della stessa, non ti muore fino alla fine degli stadi, in quel momento si va' a tirare il dado e si controlla se possa vivere o morire
(13.34.33) Sulfrum: questo nella globalità prevede che la pianta ad un certo punto finisca quindi ed arrivi allo stadio finale?
(13.35.04) andrea.postal@gmail.com/ED2D7942: sì, semplicemente non può morire durante gli stadi ma solo alla fine del ciclo degli stadi
(13.35.11) Sulfrum: ok
(13.35.23) andrea.postal@gmail.com/ED2D7942: non è molto realistico ma.. mi è venuto così
(13.36.03) Sulfrum: io mi riferivo ai miei mirtilli che possono fare semi anche 100 volte
(13.36.03) andrea.postal@gmail.com/ED2D7942: poi in realtà si potrebbe cambiare.. ma, per come sto pensando il sistema non mi sembra ok, perchè altrimenti il counter sul worse non ha senso
(13.36.17) andrea.postal@gmail.com/ED2D7942: 100 cicli vitali intendi?
(13.36.43) Sulfrum: 100 cicli a 3 stadi (pianta fiore frutti)
(13.37.16) andrea.postal@gmail.com/ED2D7942: per come la vedo io può anche andare all'infinito, basta che si annafi correttamente ad ogni generazione
(13.37.33) Sulfrum: ok uindi tu arli di generazioni
(13.37.40) Sulfrum: io mi riferisco alla stessa pianta
(13.38.03) andrea.postal@gmail.com/ED2D7942: ah ok, ma in realtà non ci ho pensato sai?
(13.38.06) Sulfrum: pianta di 100 anni e tu la nipote della nipote della nipote della pianta originale
(13.38.21) Sulfrum: sono 2 approcci diversi
(13.38.30) andrea.postal@gmail.com/ED2D7942: sì
(13.38.31) Sulfrum: una è una pianta annuale
(13.38.38) Sulfrum: seme pianta fiore frutto morta
(13.38.41) Sulfrum: get seme
(13.38.48) Sulfrum: una è un melo
(13.38.49) andrea.postal@gmail.com/ED2D7942: manca una attributo.. quello che indica quanti anni, o cicli di vita propri, può avere la pianta
(13.39.01) Sulfrum: seme piantina loop( pianta fiore frutti)
(13.39.41) andrea.postal@gmail.com/ED2D7942: qui, come nota per me, posso fare in modo che il ciclo proprio aumenti o diminuisca a seconda del worse counter o better counter
(13.40.19) andrea.postal@gmail.com/ED2D7942: cmq lascio questa cosa per dopo che non ci ho pensato
(13.40.35) andrea.postal@gmail.com/ED2D7942: dulcis in fundus, o come cappero si dice:
(13.40.36) andrea.postal@gmail.com/ED2D7942:         self.worse_affects  = []   # Affect che danneggiano la pianta
        self.better_affects = []   # Affect che migliorano la pianta
(13.41.03) andrea.postal@gmail.com/ED2D7942: la lista degli affect (che non esistono manco :P) che possono danneggiare o migliorare la pianta
(13.41.05) andrea.postal@gmail.com/ED2D7942: ovvero
(13.41.24) andrea.postal@gmail.com/ED2D7942: tutte le piante abbisogneranno di qualcosa per crescere.. di solito un liquido
(13.42.02) andrea.postal@gmail.com/ED2D7942: se si innafia con acqua liscia senza affect si passa al normale stadio e, a meno che non si esageri con l'acqua facendola marcire, prima o poi fruttificherà normalmente
(13.42.37) andrea.postal@gmail.com/ED2D7942: mettiamo caso che tu innafi con birra nanica che ha affect +5 umorismo (sparo)
(13.43.04) Sulfrum: yep
(13.43.10) andrea.postal@gmail.com/ED2D7942: se tale affect c'è tra quelli che possono peggiorare la pianta, tale annaffiata la peggiorerà e il prossimo stadio caricherà il worse_entity
(13.43.20) Sulfrum: devi riuscire ad innaffiare prima che scatti lo stadio successivo
(13.43.29) andrea.postal@gmail.com/ED2D7942: sì
(13.43.51) Sulfrum: quindi temporanemante nessun innaffio è considerato neutro
(13.44.00) andrea.postal@gmail.com/ED2D7942: viceversa se si trova nel better affects la pianta migliorerà ed avrà più contents, ovvero frutti di norma (anche se il contents si può fare con dei fiori o con degli uccelli per esempio)
(13.44.19) andrea.postal@gmail.com/ED2D7942: che intendi dire esattamente?
(13.45.12) andrea.postal@gmail.com/ED2D7942: mah secondo me qualsiasi liquido senza affect è da considerarsi neutro.. anche se forse è meglio pensare che solo l'acqua senza affects sia da considerarsi neutra, se è questo che intendi
(13.46.10) Sulfrum: mi riferivo al tuo desiderio di non implementare l'obbligo ad entrare in mud per accudire la pianta sennò muore
(13.47.20) andrea.postal@gmail.com/ED2D7942: sì, penso che l'idea dell'elementale d'acqua sia la migliore, anche se non migliora di molto le caratteristiche
(13.47.44) andrea.postal@gmail.com/ED2D7942: a meno, aggiungendo affects casuali ai vari elementali, non si dia la possibilità di scegliere quello con cui annaffiare
(13.48.21) Sulfrum: quella è una cosa che svilupperei cmnq dopo
(13.49.13) andrea.postal@gmail.com/ED2D7942: cmq l'idea è quella di aggiungere parte di tali affect al risultato, cioè ai frutt che se mangiati daranno tali affects; e al seme, che avrà come better affects quelli del frutto
(13.49.35) andrea.postal@gmail.com/ED2D7942: in questa maniera la generazione successiva deve essere bagnata con un'acqua dagli affect giusti, per avere il meglio
(13.50.07) andrea.postal@gmail.com/ED2D7942: probabilmente ora che vedo.. è meglio che gli affects vengano aggiunti al frutto e al seme solo se si ha avuto tutti gli stati better
(13.50.30) andrea.postal@gmail.com/ED2D7942: questo per evitare cicli successivi generazionali man mano troppo migliori e potenti
(13.50.40) andrea.postal@gmail.com/ED2D7942: capisci il giro?
(13.52.26) andrea.postal@gmail.com/ED2D7942: è come se il seme portasse le informazioni dna del frutto, e su come innaffiarlo correttamente per farlo crescere
(13.53.17) Sulfrum: basta avere cmn un Max settato
(13.53.29) Sulfrum: ovvero un massimo effetto possibile
(13.54.06) andrea.postal@gmail.com/ED2D7942: mah io non lo aggiungerei, piuttosto basta dare rara la possibilità di avere liquidi che possano annaffiare con certi affects e tutto torna
(13.54.15) andrea.postal@gmail.com/ED2D7942: poi vedremo un po' come gira
(13.54.33) andrea.postal@gmail.com/ED2D7942: cmq dovrò fare in modo che vengano creati anche dei worse_affect se lo stadio della pianta è andato a mal fine
(13.54.50) Sulfrum: se ti piace la matematica
(13.55.09) Sulfrum: gli affect da un cert punto in poi ad effetto logaritmico fanno in modo che cresca davvero di poco
(13.55.24) Sulfrum: le formule sono le stesse volendo della skill musicale
(13.55.25) andrea.postal@gmail.com/ED2D7942: ecco, questa è una buona idea
(13.55.52) andrea.postal@gmail.com/ED2D7942: ma vedremo, secondo me son cose da testare sul campo
(13.55.53) Sulfrum: usando solo quelle per l'incremento
(13.56.06) andrea.postal@gmail.com/ED2D7942: per il resto ci sono le finezze per cui tu puoi già impostare nel prototipo della pianta se uno stadio è andato bene o male, impostando appunto i counter
(13.56.46) andrea.postal@gmail.com/ED2D7942: praticamente ti ho già detto che i contents possono essere più di uno e puoi uppare anche mob volendo, vengono uppati nel contenuto, quindi la pianta funzionerà come container
(13.57.04) andrea.postal@gmail.com/ED2D7942: non ci sarà bisogno di impostare containertype farò funzionare il tutto
(13.57.09) andrea.postal@gmail.com/ED2D7942: automaticamente
(13.57.25) andrea.postal@gmail.com/ED2D7942: che altro? basta direi... a parte i comandi semina e innafia
(13.57.37) Sulfrum: fra le altre cose ti dico cosa m'ero segnato io
(13.57.39) andrea.postal@gmail.com/ED2D7942: volendo al posto del get sull'albero potrei fare il comando raccogli
(13.58.14) Sulfrum: piante longeve --> il numero medio di semi per raccolto è una funzione dell'età
(13.58.41) Sulfrum: i primi anni pochi semi e poi si arriva ad un massimo e poi scende più o meno lenta
(13.59.28) Sulfrum: differenza seme / frutto: alcune piante potrebbero avere l'esigenza di avere tale differenza
(13.59.44) Sulfrum: non è che pianto una Mela ma un seme di mela
(14.00.12) Sulfrum: poi c'è la questione più mastodontica e massiva
(14.00.39) Sulfrum: incorci e migliorie della pianta stessa
(14.00.48) Sulfrum: ovvero fecondazione eterotrofa
(14.00.59) Sulfrum: 2 piante diverse
(14.01.31) Sulfrum: detto meglio: 2 esemplari della stessa pianta quando sono in fiore possono dare modifiche al frutto
(14.02.05) Sulfrum: ma mi è parso di capire che questo finisca tutto dentro al calderone di quel che tu mi dicevi ieri
(14.02.12) Sulfrum: incorci fra razze
(14.02.18) Sulfrum: etcetera
(14.03.07) andrea.postal@gmail.com/ED2D7942: mah quello è solo concettualmente legato ai pg, non ho pensato ad un sistema generico
(14.05.34) Sulfrum: beh una volta approntato il sistema delle piante mi piacerebbe pensare di introdurre una cosa del genere
(14.05.41) Sulfrum: ma intando vediamo uno stadio per volta
(14.08.47) andrea.postal@gmail.com/ED2D7942: tanto poi mi sa che prima c'è l'innesto da fare
(14.09.05) andrea.postal@gmail.com/ED2D7942: e ancora prima... come si chiama l'azione di trasportare la pianta da un terreno ad un altro?
(14.09.30) andrea.postal@gmail.com/ED2D7942: in effetti non abbiamo pensato al terreno.. ovvero agli affect della room
(14.09.35) andrea.postal@gmail.com/ED2D7942: (che casino..)
(14.13.57) Sulfrum: non è un modo di procedere funzionale strutturare con il tempo la feature?
(14.14.44) Sulfrum: io non sapendo far molto in python contavo di svilupparlo a stadi quello script
(14.14.55) andrea.postal@gmail.com/ED2D7942: sì, in un modo o nell'altro si possono togliere alcune feature e farlo dopo
(14.14.57) Sulfrum: - terreno
- stadi della pianta
(14.15.13) andrea.postal@gmail.com/ED2D7942: ma debbo sapere prima di tutto un po', altrimenti poi ti tocca rifare da zero tutte le strutture di building
(14.15.14) Sulfrum: questi quelli che avevo pensato come più importanti
(14.15.26) Sulfrum: uhm.. già
(14.15.57) Sulfrum: beh non è un grosso problema lavorando su una pianta prototipo iniziale
(14.19.14) andrea.postal@gmail.com/ED2D7942: vabbe' cmq mi pare che abbian detto utte le cose principali
(14.24.46) andrea.postal@gmail.com/ED2D7942: vabbe' non esistendo ancora gli affects
(14.25.01) andrea.postal@gmail.com/ED2D7942:  all'inizio sarà solo un ciclo vitale visivo

temperatura media:
si intende quella primaverile, se la temperatura è troppo bassa rispetto la
media dipende dalla stagione, se non si è in inverno potrebbe rischiare la morte

umidità media: idem come sopra

far evitare di seminare troppe piante dello stesso tipo nella stessa locazione

Se si è passati sempre nel better stage c'è la possibilità che la remaining life
non diminuisca durante la prossima semenza, da non abusare visto il sistema di
affects delle piante, i frutti potrebber divenire troppo potenti?
Forse è meglio gestire la cosa con un limite sommario agli affects dei frutti
"""
