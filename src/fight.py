# -*- coding: utf-8 -*-

"""
Modulo per la gestione dei combattimenti.
"""


#= IMPORT ======================================================================

import math
import random

from src.config   import config
from src.data     import Data
from src.database import database
from src.defer    import defer
from src.enums    import FLAG, OPTION, TO, TRUST
from src.grammar  import grammar_gender
from src.log      import log
from src.loop     import UnstoppableLoop
from src.utility  import multiple_arguments, random_marks, dice, format_for_admin, number_fuzzy

from src.skills.skill_counter import skill_counter


#= COSTANTI ====================================================================

DAM_MESSAGES = ((0,    0,   1, "Manchi",                                     "manca"),
                (5,    7,   1, "Sfiori",                                     "sfiora"),
                (10,   14,  1, "Graffi",                                     "graffia"),  # (TD) non è che sia molto friendly questo messaggio se uno utilizza i pugni, magari fare messaggi di danno differenti per ogni arma
                (20,   21,  1, "Colpisci di striscio",                       "colpisce di striscio"),
                (30,   28,  1, "Colpisci",                                   "colpisce"),
                (40,   35,  1, "Colpisci con forza",                         "colpisce con forza"),
                (60,   42,  1, "Ferisci",                                    "ferisce"),
                (70,   49,  1, "Ferisci gravemente",                         "ferisce gravemente"),
                (80,   56,  1, "Decimi",                                     "decima"),
                (100,  63,  1, "Devasti",                                    "devasta"),
                (120,  70,  1, "Laceri",                                     "lacera"),
                (140,  77,  1, "ScOnQuAsSi",                                 "ScOnQuAsSA"),
                (170,  84,  2, "DiStRuGgI",                                  "DiStRuGgE"),
                (200,  91,  2, "SqUiNtErNi",                                 "SqUiNtErNa"),
                (230,  98,  2, "DISASSEMBLI",                                "DISASSEMBLA"),
                (270,  105, 2, "SMEMBRI",                                    "SMEMBRA"),
                (310,  112, 2, "MASSACRI",                                   "MASSACRA"),
                (350,  119, 2, "- SFIGURI -",                                "- SFIGURA -"),
                (400,  126, 2, "-- FRACASSI --",                             "-- FRACASSA --"),
                (450,  133, 2, "--- DEMOLISCI ---",                          "--- DEMOLISCE ---"),
                (500,  140, 2, "== SBUDELLI ==",                             "== SBUDELLA =="),
                (560,  147, 2, "=== MACIULLI ===",                           "=== MACIULLA ==="),
                (620,  154, 2, "==== SQUARTI ====",                          "==== SQUARTA ===="),
                (680,  161, 2, "*** MUTILI ***",                             "*** MUTILA ***"),
                (750,  168, 3, "**** ANNIENTI ****",                         "**** ANNIENTA ****"),
                (820,  175, 3, "***** SMINUZZI *****",                       "***** SMINUZZA *****"),
                (890,  182, 3, "=*=*=* ATOMIZZI *=*=*=",                     "=*=*=* ATOMIZZA *=*=*="),
                (970,  189, 3, "<*> <*> ANNICHILISCI <*> <*>",               "<*> <*> ANNICHILISCE <*> <*>"),
                (1050, 196, 3, "<*>!<*> SRADICHI <*>!<*>",                   "<*>!<*> SRADICA <*>!<*>"),
                (1130, 203, 3, "<*><*><*> ELETTRONIZZI <*><*><*>",           "<*><*><*> ELETTRONIZZA <*><*><*>"),
                (1120, 210, 3, "<-*#*-> SCHELETRIZZI <-*#*->",               "<-*#*-> SCHELETRIZZA <-*#*->"),
                (1310, 217, 3, "(*)!(*)!(*) POLVERIZZI (*)!(*)!(*)",         "(*)!(*)!(*) POLVERIZZA (*)!(*)!(*)"),
                (1400, 224, 3, "(*)!<#*#>!(*) TERMINI (*)!<#*#>!(*)",        "(*)!<#*#>!(*) TERMINA (*)!<#*#>!(*)"),
                (1500, 231, 3, "<*>!(*)!<*>>> DILANI <<<*)!(*)!<*>",         "<*>!(*)!<*>>> DILANIA <<<*)!(*)!<*>"),
                (1750, 255, 3, "=<*)-!!!-(*>= ! SBRICIOLI ! =<*)-!!!- (*>=", "=<*)-!!!-(*>= ! SBRICIOLA ! =<*)-!!!- (*>="),
                (2000, 255, 3, "=<*)-!!!-(*>= ! SBRICIOLI ! =<*)-!!!- (*>=", "=<*)-!!!-(*>= ! SBRICIOLA ! =<*)-!!!- (*>="))


DAMAGES = {1   : "1D4+0",
           2   : "1D5+0",
           3   : "1D6+0",
           4   : "1D5+1",
           5   : "1D6+1",
           6   : "1D7+1",
           7   : "1D8+1",
           8   : "1D7+2",
           9   : "1D8+2",
           10  : "2D4+2",
           11  : "1D10+2",
           12  : "1D10+3",
           13  : "2D5+3",
           14  : "1D12+3",
           15  : "2D6+3",
           16  : "2D6+4",
           17  : "3D4+4",
           18  : "2D7+4",
           19  : "2D7+5",
           20  : "2D8+5",
           21  : "4D4+5",
           22  : "4D4+6",
           23  : "3D6+6",
           24  : "2D10+6",
           25  : "2D10+7",
           26  : "3D7+7",
           27  : "5D4+7",
           28  : "2D12+8",
           29  : "2D12+8",
           30  : "4D6+8",
           31  : "4D6+9",
           32  : "6D4+9",
           33  : "6D4+10",
           34  : "4D7+10",
           35  : "4D7+11",
           36  : "3D10+11",
           37  : "3D10+12",
           38  : "5D6+12",
           39  : "5D6+13",
           40  : "4D8+13",
           41  : "4D8+14",
           42  : "3D12+14",
           43  : "3D12+15",
           44  : "8D4+15",
           45  : "8D4+16",
           46  : "6D6+16",
           47  : "6D6+17",
           48  : "6D6+18",
           49  : "4D10+18",
           50  : "5D8+19",
           51  : "5D8+20",
           52  : "6D7+20",
           53  : "6D7+21",
           54  : "7D6+22",
           55  : "10D4+23",
           56  : "10D4+24",
           57  : "6D8+24",
           58  : "5D10+25",
           59  : "8D6+26",
           60  : "8D6+28",
           61  : "8D6+30",
           62  : "8D6+30",
           63  : "8D7+30",
           64  : "8D8+30",
           65  : "10D8+32",
           66  : "10D8+34",
           67  : "10D8+36",
           68  : "10D9+36",
           69  : "10D10+36",
           70  : "12D10+36",
           71  : "12D10+38",
           72  : "12D10+40",
           73  : "12D11+40",
           74  : "12D11+40",
           75  : "12D12+40",
           76  : "14D10+40",
           77  : "14D10+42",
           78  : "14D10+44",
           79  : "14D11+44",
           80  : "14D12+44",
           81  : "14D13+44",
           82  : "14D14+44",
           83  : "14D15+45",
           84  : "14D16+45",
           85  : "14D17+45",
           86  : "14D18+45",
           87  : "14D19+46",
           88  : "14D20+46",
           89  : "14D21+46",
           90  : "14D22+46",
           91  : "14D23+47"}
           #(TD) mancano tutti gli altri


#= CLASSI ======================================================================

class FightLoop(UnstoppableLoop):
    def __init__(self):
        super(FightLoop, self).__init__()
        self.paused = False
    #- Fine Inizializzazione -

    def start(self, seconds=0):
        if seconds == 0:
            seconds = config.fight_loop_seconds
        super(FightLoop, self).start(seconds)
    #- Fine Metodo -

    def stop(self):
        if self.running:
            super(FightLoop, self).stop()
        else:
            log.bug("Il FightLoop non è stato trovato attivo.")
    #- Fine Metodo -

    # (TD) Ho diminuito la probabilità di effettuare parate, tuttavia poiché il check
    # della parata si basa sulle tempistiche di durata del turno dei due combattenti,
    # entità in lotta con valori di speed e livello simili o identici avranno quindi
    # durata di turno di combattimento simile o identico, propinando durante il
    # combattimento una listona semi-infinita di parate o tentativi delle stesse.
    # Ho diminuito la probabilità di questo problema, ma non so quanto la cosa mi
    # soddisfi, forse farla time-dipendente non è la cosa più corretta
    def cycle(self):
        if self.paused:
            return

        for fight in reversed(database["fights"].values()):
            force_stop = False
            if fight.defender.is_extracted() or fight.attacker.is_extracted():
                force_stop = True

            # Evita di attaccare se i due combattenti non si trovano nella
            # stessa locazione
            if fight.defender.location != fight.attacker.location:
                fight.away_seconds += 0.1
                # Tempo prima che il combattimento si fermi del tutto se i due
                # combattenti stanno lontani per un qualsiasi motivo
                # (TD) migliorare inserendo l'attributo hated per l'entità
                if fight.away_seconds > 60 * 5:
                    force_stop = True
                continue
            else:
                fight.away_seconds == 0.0

            if fight.defender.IS_ITEM:
                if fight.attacker_seconds <= 0.0:
                    force_stop = fight.hit_turn(fight.attacker, fight.defender, "attacker", "defender")
                    fight.attacker_seconds -= 0.2
            else:
                # Solo coloro che hanno un'arma possono deflettere i colpi
                wielded_entity = fight.defender.get_wielded_entity()
                if fight.attacker_seconds <= 0.15 and fight.defender_seconds <= 0.15:
                    force_stop = fight.parry_turn(fight.attacker, fight.defender, "attacker", "defender")
                    fight.attacker_seconds -= 0.15
                    fight.defender_seconds -= 0.15
                elif wielded_entity and (fight.attacker_seconds <= 0.15 and fight.defender_seconds <= 0.3):
                    force_stop = fight.deflects_turn(fight.attacker, fight.defender, "attacker", "defender")
                    fight.attacker_seconds -= 0.15
                    fight.defender_seconds -= 0.3
                elif wielded_entity and (fight.defender_seconds <= 0.15 and fight.attacker_seconds <= 0.3):
                    force_stop = fight.deflects_turn(fight.defender, fight.attacker, "defender", "attacker")
                    fight.defender_seconds -= 0.15
                    fight.attacker_seconds -= 0.3
                elif fight.attacker_seconds <= 0.0:
                    force_stop = fight.hit_turn(fight.attacker, fight.defender, "attacker", "defender")
                elif fight.defender_seconds <= 0.0:
                    force_stop = fight.hit_turn(fight.defender, fight.attacker, "defender", "attacker")

            if force_stop:
                fight.stop()
                continue

            if fight.attacker_seconds <= 0.0:
                fight.set_turn_time(fight.attacker, "attacker")
            else:
                fight.attacker_seconds -= 0.1

            if not fight.defender.IS_ITEM:
                if fight.defender_seconds <= 0.0:
                    fight.set_turn_time(fight.defender, "defender")
                else:
                    fight.defender_seconds -= 0.1
    #- Fine Metodo -


# (TD) Convertirlo forse in un loop persistente, togliendogli il code, e quindi
# anche togliendo il database["fights"]
# (TD) anche se ora è un data poi non lo sarà più
class Fight(Data):
    """
    Gestisce un combattimento tra due entità.
    """
    PRIMARY_KEY = "code"
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {"attacker" : ["players", "mobs", "items"],
                   "defender" : ["players", "mobs", "items"]}
    WEAKREFS    = {}

    def __init__(self, attacker=None, defender=None):
        if attacker and defender:
            code = "%s %s" % (attacker.code, defender.code)
        else:
            code = ""

        self.code             = code     # Codice identificativo
        self.attacker         = attacker # Colui che ha iniziato il combattimento
        self.defender         = defender # Colui che si difende
        self.attacker_seconds = 0.0      # Secondi al prossimo turno dell'aggressore
        self.defender_seconds = 0.0      # Secondi al prossimo turno della vittima
        self.attacker_damage  = 0        # Danni totali dati al difensore
        self.defender_damage  = 0        # Danni totali dati all'attaccante
        self.away_seconds     = 0.0      # Secondi totali che i due combattenti rimangono lontani
    #- Fine Inizializzazione -

    def get_error_message(self):
        # (TD)
        return ""
    #- Fine Metodo -

    #- Metodi relativi i turni di combattimento --------------------------------

    def start(self):
        # Non inizia il combattimento se questo c'è già nell'apposito database
        for fight in database["fights"].values():
            if fight.attacker == self.attacker and fight.defender == self.defender:
                log.bug("Combattimento tra %s e %s già attivato" % (self.attacker, self.defender))
                return

        database["fights"][self.code] = self
        self.attacker.fights.append(self)
        self.defender.fights.append(self)

        self.weapon_high_level_warning(self.attacker)
        self.weapon_high_level_warning(self.defender)

        # Opportunità da parte della vittima che eseguire un counter ad inizio combattimento
        if self.defender.IS_ITEM:
            counter_result = "failure"
        else:
            counter_result = skill_counter(self.defender, self.attacker)
        if counter_result == "success":
            self.defender_seconds = 0.2
            self.set_turn_time(self.attacker, "attacker")
        elif counter_result == "masterly":
            self.defender_seconds = 0.2
            self.set_turn_time(self.attacker, "attacker", modifier=2.0)
        elif counter_result == "clumsy":
            self.attacker_seconds = 0.2
            self.set_turn_time(self.defender, "defender", modifier=2.0)
        else:
            self.attacker_seconds = 0.2
            self.set_turn_time(self.defender, "defender")
    #- Fine Metodo -

    def stop(self):
        if self in self.attacker.fights:
            self.attacker.fights.remove(self)
        else:
            log.bug("Non è stato trovato nessun fight nella lista dei combattimenti di attacker %s " % self.attacker.code)
            
        if self in self.defender.fights:
            self.defender.fights.remove(self)
        else:
            log.bug("Non è stato trovato nessun fight nella lista dei combattimenti di defender %s " % self.defender.code)

        if self.code in database["fights"]:
            del(database["fights"][self.code])
        else:
            log.bug("Non è stato trovato nessun fight dal codice %s nel database dei combattimenti" % self.code)
    #- Fine Metodo -

    def weapon_high_level_warning(self, entity):
        if not entity:
            log.bug("entity non è un parametro valido: %r" % entity)
            return

        # ---------------------------------------------------------------------

        wielded_entity = self.defender.get_wielded_entity()
        if not wielded_entity or not wielded_entity.weapon_type:
            return

        if wielded_entity.level > entity.level:
            entity.send_output("Non ti trovi a tuo agio a combattere con %s perché il suo livello è troppo alto rispetto al tuo." % wielded_entity.get_name(looker=entity))
    #- Fine Metodo -

    def set_turn_time(self, active_entity, active, modifier=1.0):
        """
        Imposta il tempo di un turno di combattimento basandosi sul livello
        dell'entità, sulla sua velocità ed eventualmente applicando il
        modificatore.
        """
        # Il tempo varia tra i 5.3 secondi ed un minimo (modifier a parte) di 1 secondo
        turn_time = 5.3
        admin_log = "Prossimo Turno: %s" % turn_time

        # (TD) in futuro gli oggetti se armi potrebbero attaccare se animate,
        # nel caso di bacchette e simili invece potrebbero far scattare
        # incantesimi ad ogni colpo
        if active_entity.IS_ITEM:
            return 0.0

        # Ogni dieci livelli l'attacco diminuisce di un decimo di secondo, quindi al livello 200 vi sarà una diminuizione di 2 secondi
        subtracting_level = active_entity.level / 100
        turn_time -= subtracting_level
        admin_log += " - livello(%d)/100 = %s" % (active_entity.level, turn_time)

        # Se la speed è 100 c'è una diminuzione di 2.3 secondi, se la speed è 10 di 1.1 secondi
        if active_entity.speed > 0:
            subtracting_speed = math.log(active_entity.speed) / 2
            turn_time -= subtracting_speed
            admin_log += " - log_speed(%d)/2 = %s" % (active_entity.speed, turn_time)
        else:
            log.bug("La speed di %s è zero o meno: %d" % (active_entity.code, active_entity.speed))

        if modifier != 1.0:
            turn_time = max(0.0, turn_time * modifier)
            admin_log += " * modifier(%d) = %s" % (modifier, turn_time)

        # Il tempo viene reso casuale di un decimo in più o in meno per dare
        # la possibilità a entità che si scontrano con stessa durata di turno
        # di slittare un poco ed evitare, per esempio, troppe parate di fila
        turn_time = number_fuzzy(turn_time, fuzzy_value=0.1)

        if ((active_entity.IS_PLAYER and active_entity.trust >= TRUST.MASTER)
        or active_entity.IS_MOB or active_entity.IS_ITEM):
            active_entity.send_to_admin(admin_log, break_line=False)

        # Non v'è bisogno che il turn_time sia un valore intero
        setattr(self, active + "_seconds", turn_time)
        return turn_time
    #- Fine Metodo -

    # (TD) questa però diverrà la skill pugno senza armi, altrimenti l'arma adatta
    # (TD) c'è anche da fare l'evade, agilità
    def hit_turn(self, active_entity, passive_entity, active, passive, modifier=1.0):
        # Calcola il danno e controlla se chi lo subisce muore
        damage = self.give_damage(active_entity, passive_entity, active, passive, modifier=modifier)

        # Ricava il messaggio di danno:
        for dam_message in DAM_MESSAGES:
            if damage <= dam_message[0]:
                break

        dam_color = '''<span style="color:rgb(%d,%d,255)">''' % (255-dam_message[1], 255-dam_message[1])
        dam_punct = random_marks(0, dam_message[2])

        # Colpisce la vittima
        wielded_entity = active_entity.get_wielded_entity()
        if wielded_entity:
            active_entity.act("\n%s%s</span> $N con $a%s" % (dam_color, dam_message[3], dam_punct), TO.ENTITY, passive_entity, wielded_entity)
            active_entity.act("$n %s%s</span> $N con $a%s" % (dam_color, dam_message[4], dam_punct), TO.OTHERS, passive_entity, wielded_entity)
            active_entity.act("$n ti %s%s</span> con $a%s" % (dam_color, dam_message[4], dam_punct), TO.TARGET, passive_entity, wielded_entity)
        else:
            active_entity.act("\n%s%s</span> $N col %s%s" % (dam_color, dam_message[3], active_entity.skin_colorize("pugno"), dam_punct), TO.ENTITY, passive_entity)
            active_entity.act("$n %s%s</span> $N con un %s%s" % (dam_color, dam_message[4], active_entity.skin_colorize("pugno"), dam_punct), TO.OTHERS, passive_entity)
            active_entity.act("$n ti %s%s</span> con un %s%s" % (dam_color, dam_message[4], active_entity.skin_colorize("pugno"), dam_punct), TO.TARGET, passive_entity)
        active_entity.send_prompt()

        if passive_entity.life <= 0:
            # Poiché è possibile che il combattimento non si fermi in tempo
            # ci possono essere errori nel qual caso che la vittima muoia nella
            # stessa stanza in cui viene rigenerata, quindi viene inserita
            # una deferred per assicurarsi che il True, cioè il segnale di
            # fine combattimento, venga prima di tutto
            defer(0.001, self.defeat, active_entity, passive_entity, active, passive)
            return True

        return False
    #- Fine Metodo -

    # (TD) qui bisogna utilizzare la skill di deflect/devia  e spostarlo nel file apposito
    def deflects_turn(self, active_entity, passive_entity, active, passive):
        probability = random.randint(1, 4)

        # Non riesce a deviare il colpo
        if probability == 1:
            active_entity.act("\n$N cerca di [cyan]deviare[close] il tuo colpo senza riuscirvi.",  TO.ENTITY, passive_entity)
            active_entity.act("$N cerca di [cyan]deviare[close] il colpo di $n senza riuscirvi.", TO.OTHERS, passive_entity)
            active_entity.act("Cerchi di [cyan]deviare[close] il colpo di $n senza riuscirci.", TO.TARGET, passive_entity)
            self.hit_turn(active_entity, passive_entity, active, passive)
            if passive_entity.life > 0:
                active_entity.send_prompt()
            else:
                return True
        elif probability == 2:
            # Devia il colpo solo di un poco
            active_entity.act("\n$N ti [cyan]devia[close] in parte il colpo.",  TO.ENTITY, passive_entity)
            active_entity.act("$N [cyan]devia[close] in parte il colpo di $n.", TO.OTHERS, passive_entity)
            active_entity.act("[cyan]Defletti[close] in parte il colpo di $n.", TO.TARGET, passive_entity)
            self.hit_turn(active_entity, passive_entity, active, passive, modifier=0.5)
            if passive_entity.life > 0:
                active_entity.send_prompt()
            else:
                return True
        else:
            active_entity.act("\n$N ti [cyan]devia[close] il colpo.",  TO.ENTITY, passive_entity)
            active_entity.act("$N [cyan]devia[close] il colpo di $n.", TO.OTHERS, passive_entity)
            active_entity.act("[cyan]Defletti[close] il colpo di $n.", TO.TARGET, passive_entity)
            active_entity.send_prompt()

        return False
    #- Fine Metodo -

    # (TD) qui bisogna utilizzare la skill di parry/para e spostarlo nel file apposito
    def parry_turn(self, active_entity, passive_entity, active, passive):
        probability = random.randint(1, 4)

        if probability == 1:
            active_entity.act("\n$N cerca di [orange]parare[close] il tuo colpo senza riuscirvi.",  TO.ENTITY, passive_entity)
            active_entity.act("$N cerca di [orange]parare[close] il colpo di $n senza riuscirvi.", TO.OTHERS, passive_entity)
            active_entity.act("Cerchi di [orange]parare[close] il colpo di $n senza riuscirci.", TO.TARGET, passive_entity)
            self.hit_turn(active_entity, passive_entity, active, passive)
            if passive_entity.life > 0:
                active_entity.send_prompt()
            else:
                return True
        elif probability == 2:
            # Devia il colpo solo di un poco
            active_entity.act("\n$N ti [orange]para[close] in parte il colpo.",  TO.ENTITY, passive_entity)
            active_entity.act("$N [orange]para[close] in parte il colpo di $n.", TO.OTHERS, passive_entity)
            active_entity.act("[orange]Pari[close] in parte il colpo di $n.", TO.TARGET, passive_entity)
            self.hit_turn(active_entity, passive_entity, active, passive, modifier=0.5)
            if passive_entity.life > 0:
                active_entity.send_prompt()
            else:
                return True
        else:
            active_entity.act("\n$N ti [orange]para[close] il colpo.",  TO.ENTITY, passive_entity)
            active_entity.act("$N [orange]para[close] il colpo di $n.", TO.OTHERS, passive_entity)
            active_entity.act("[orange]Pari[close] il colpo di $n.", TO.TARGET, passive_entity)
            active_entity.send_prompt()

        return False
    #- Fine Metodo -

    # - Altri -----------------------------------------------------------------

    def get_damage(self, active_entity, passive_entity, active, passive, modifier=1.0):
        # (TD) Skill apposita del danno
        
        return damage
    #- Fine Metodo -

    def give_damage(self, active_entity, passive_entity, active, passive, modifier=1.0):
        """
        Metodo che serve a calcolare il danno inverto da un'entità ad un'altra.
        """
        admin_log = ""

        if active_entity.IS_ITEM:
            return 0

        wielded_entity = active_entity.get_wielded_entity()
        if wielded_entity:
            if wielded_entity.weapon_type:
                # Danno ricavato se l'attaccante ha un'arma in mano
                if wielded_entity.weapon_type.damage:
                    damage = dice(wielded_entity.weapon_type.damage, for_debug=wielded_entity)
                    admin_log += "Arma; danno_arma_definito(%s)=%d" % (wielded_entity.weapon_type.damage, damage)
                else:
                    if wielded_entity.level <= 0 or wielded_entity.level > len(DAMAGES):
                        log.bug("Livello dell'arma %s fuori dai range di livello dei danni: %d" % (wielded_entity.code, wielded_entity.level))
                        damage = 1
                    else:
                        damage = dice(DAMAGES[wielded_entity.level], for_debug=wielded_entity)
                    admin_log += "Arma; danno_arma_non_definito(%s)=%d" % (DAMAGES[wielded_entity.level], damage)
            else:
                # Danno ricavato se l'attaccante ha qualcosa in mano che non sia un'arma
                damage = math.log(wielded_entity.level * wielded_entity.level * wielded_entity.get_total_weight())
                admin_log += "Oggetto; danno_grezzo(peso_arma:%d)=%d" % (wielded_entity.get_total_weight(), damage)
                damage = random.randint(damage / 1.5, damage * 1.5)
                admin_log += " -> danno_casualizzato()=%d" % damage

            # Il danno viene ridimensionato a seconda che il livello dell'attaccante
            # sia minore di quello dell'entità impugnata
            if active_entity.level < wielded_entity.level:
                damage = damage/2 + ((damage / wielded_entity.level) * active_entity.level)/2
                #damage = (damage / wielded_entity.level) * active_entity.level
                admin_log += " -> danno_liv_maggiore(liv_arma:%d)=%d" % (wielded_entity.level, damage)

            # Il danno viene maggiorato a seconda della forza dell'attaccante
            damage = (damage * (100 + active_entity.strength)) / 100
            admin_log += " -> danno_bonus_forza(%d)=%d" % (active_entity.strength, damage)

            # Il danno viene maggiorato o diminuito a seconda delle differenza
            # di livello tra i due combattenti
            level_difference = active_entity.level - passive_entity.level
            if level_difference != 0:
                damage += ((damage * level_difference) / 100 ) / 2
                admin_log += " -> danno_diff_livello(%d)=%d" % (level_difference, damage)
        else:
            # Danno ricavato se l'attaccante è a mani nude
            damage = random.randint(active_entity.strength / 6, active_entity.strength / 3)
            admin_log += "Mani Nude: danno_casualizzato(forza_attaccante:%d)=%d" % (active_entity.strength, damage)

        if   active_entity.IS_PLAYER and passive_entity.IS_PLAYER: dam_vs = config.dam_plr_vs_plr
        elif active_entity.IS_PLAYER and passive_entity.IS_MOB:    dam_vs = config.dam_plr_vs_mob
        elif active_entity.IS_MOB and passive_entity.IS_PLAYER:    dam_vs = config.dam_mob_vs_plr
        elif active_entity.IS_MOB and passive_entity.IS_MOB:       dam_vs = config.dam_mob_vs_mob
        elif active_entity.IS_ITEM and passive_entity.IS_PLAYER:   dam_vs = config.dam_item_vs_plr
        elif active_entity.IS_ITEM and passive_entity.IS_MOB:      dam_vs = config.dam_item_vs_mob
        if dam_vs != 100:
            damage = (damage * dam_vs) / 100

        if modifier != 1.0:
            damage = damage * modifier
            admin_log += " -> danno_con_modificatore(modificatore:%f)=%d" % (modifier, damage)

        if ((active_entity.IS_PLAYER and active_entity.trust >= TRUST.MASTER)
        or active_entity.IS_MOB or active_entity.IS_ITEM):
            admin_log = "\n" + format_for_admin(admin_log)
            active_entity.send_output(admin_log, break_line=False)

        # (TD) Skill apposita della pelle dura (bonus razziali) e armatura
        damage = int(damage)
        passive_entity.life -= damage

        attr_name = active + "_damage"
        setattr(self, attr_name, getattr(self, attr_name) + damage)
        return damage
    #- Fine Metodo -

    def defeat(self, active_entity, passive_entity, active, passive):
        # Può accadere visto che il metodo è deferrato
        if not passive_entity:
            return

        if not passive_entity.IS_ITEM:
            if active_entity.IS_MOB:
                passive_entity.defeat_from_mob_counter += 1
            elif active_entity.IS_ITEM:
                passive_entity.defeat_from_item_counter += 1
            elif active_entity.IS_PLAYER:
                passive_entity.defeat_from_player_counter += 1

        if passive_entity.IS_ITEM:
            active_entity.item_defeated_counter += 1
        elif passive_entity.IS_PLAYER:
            active_entity.player_defeated_counter += 1
        else:
            active_entity.mob_defeated_counter += 1

        if passive_entity.IS_ITEM:
            if self.code.startswith("rip_item_broken-"):
                active_entity.act("\nDopo il colpo che gli hai inferto $N si polverizza.",  TO.ENTITY, passive_entity)
                active_entity.act("Dopo il colpo che $n gli ha inferto $N si polverizza.", TO.OTHERS, passive_entity)
                active_entity.act("Dopo il colpo che $n ti ha inferto ti polverizzi.",   TO.TARGET, passive_entity)
            else:
                active_entity.act("\nDopo il colpo che gli hai inferto $N si rompe.",  TO.ENTITY, passive_entity)
                active_entity.act("Dopo il colpo che $n gli ha inferto $N si rompe.", TO.OTHERS, passive_entity)
                active_entity.act("Dopo il colpo che $n ti ha inferto ti rompi.",   TO.TARGET, passive_entity)
            active_entity.send_prompt(show_opponent=False)
        else:
            active_entity.act("\nDopo il colpo che gli hai inferto $N stramazza al suolo.",  TO.ENTITY, passive_entity)
            active_entity.act("Dopo il colpo che $n gli ha inferto $N stramazza al suolo.", TO.OTHERS, passive_entity)
            active_entity.act("Dopo il colpo che $n ti ha inferto stramazzi al suolo.",   TO.TARGET, passive_entity)
            #passive_entity.send_output('''<script>$("#output").vibrate()</script>''')  # (bb)
            self.gain_xp(active_entity, passive_entity, active, passive)

            # A seconda del numero di morti il gap dei px persi è maggiore,
            # alle prime morti è zero
            died_counter = passive_entity.defeat_from_mob_counter + passive_entity.defeat_from_item_counter + passive_entity.death_from_player_counter
            malus = 1
            if died_counter > 0:
                malus = math.log(died_counter)
            self.loose_xp(active_entity, passive_entity, active, passive)

        # Se è un giocatore bisogna digitare il comando kill per finirlo
        if active_entity.IS_PLAYER and passive_entity.IS_PLAYER:
            from src.interpret import translate_input
            passive_entity.flags += FLAG.BEATEN
            kill_translation = translate_input(active_entity, "kill", "en")
            javascript_code = '''javascript:parent.sendInput('%s %s');''' % (
                kill_translation, passive_entity.get_numbered_keyword(looker=active_entity))
            active_entity.send_output('''\nHai vinto! Se vuoi finire %s <a href="%s">uccidil%s</a>.\n''' % (
                passive_entity.get_name(active_entity), javascript_code, grammar_gender(passive_entity)))
        else:
            # Altrimenti se è un'entità muore o di rompe in automatico
            if active_entity.IS_PLAYER and active_entity.account and OPTION.AUTO_LOOT in active_entity.account.options:
                passive_entity.dies(opponent=active_entity, auto_loot=True)
            else:
                passive_entity.dies(opponent=active_entity)
    #- Fine Metodo -

    # (TD) tutto da fare, una volta terminato creare una tooltip descrivende
    # i vari parziali o anche i valori donati agli altri giocatori
    def gain_xp(self, active_entity, passive_entity, active, passive, bonus=1.0):
        experience = passive_entity.level * random.randint(9, 11)
        experience = int(experience * bonus)
        if experience > 0 and active_entity.IS_PLAYER:
            active_entity.give_experience(experience)
            active_entity.send_output("Guadagni [white]%d[close] punti d'esperienza!" % experience)
            active_entity.send_prompt(show_opponent=False)

        return experience
    #- Fine Metodo -

    # (TD) tutto da fare
    def loose_xp(self, active_entity, passive_entity, active, passive, malus=1.0):
        experience = passive_entity.level * random.randint(9, 11)
        experience = int(experience * malus)
        if experience > 0:
            passive_entity.experience -= experience
            passive_entity.send_output("Perdi [black]%d[close] punti d'esperienza!" % experience)

        return experience
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def start_fight(attacker, defender):
    """
    Inizia un nuovo combattimento tra due entità.
    """
    if not attacker:
        log.bug("attacker non è un parametro valido: %r" % attacker)
        return

    if not defender:
        log.bug("defender non è un parametro valido: %r" % defender)
        return

    # -------------------------------------------------------------------------

    fight = Fight(attacker, defender)
    fight.start()
#- Fine Funzione -


def is_fighting(entity, with_him=None):
    """
    Ritorna un valore di verità se si sta combattendo, di falsità altrimenti.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    for fight in entity.fights:
        for target in entity.location.iter_contains():
            if (with_him and target != with_him) or target == entity:
                continue
            if target == fight.defender or target == fight.attacker:
                return True

    return False
#- Fine Funzione -


def get_fight(entity, with_him=None):
    """
    Ritorna il combattimento in cui ci si è attualmente cimentati.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    if not with_him:
        with_him = entity.get_opponent()

    if not with_him:
        return None

    for fight in entity.fights:
        if fight.defender == with_him or fight.attacker == with_him:
            return fight

    return None
#- Fine Funzione -


def get_opponent(entity):
    """
    Ritorna l'entità contro cui si sta attualmente combattendo.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return

    # -------------------------------------------------------------------------

    # Dà la precedenza agli ultimi fight iniziati
    for fight in reversed(entity.fights):
        for target in entity.location.iter_contains():
            if target == entity:
                continue
            if target == fight.defender or target == fight.attacker:
                return target

    return None
#- Fine Funzione -


def get_damage_verbs(damage):
    if damage < 0:
        log.bug("damage non è un parametro valido: %d" % damage)
        return "", ""

    # -------------------------------------------------------------------------

    for index, dam_message in enumerate(DAM_MESSAGES):
        if damage <= dam_message[0]:
            return index, dam_message[3], dam_message[4]

    return -1, "", ""
#- Fine Funzione -


def create_damages_page():
    """
    Crea una pagina html statica con la lista di tutti i danni per livello
    di default per le armi.
    """
    lines = []

    lines.append('''<html>''')
    lines.append('''<head>''')
    lines.append('''<link rel="Shortcut Icon" type="image/x-icon" href="favicon.ico">''')
    lines.append('''<link rel="Stylesheet" type="text/css" href="../style.css">''')
    lines.append('''<link rel="Stylesheet" type="text/css" href="../style_doc.css">''')
    lines.append('''<title>Documentazione di Aarit, il Mud in Python</title>''')
    lines.append('''<meta http-equiv="content-type" content="text/html;" charset="utf-8" />''')
    lines.append('''</head>''')
    lines.append('''<body>''')
    lines.append('''<table class="mud">''')
    lines.append('''<tr><th>Livello</th><th>Danno</th></tr>''')

    for level, damage in DAMAGES.iteritems():
        lines.append('''<tr><td>%d</td><td>%s</td></tr>''' % (level, damage))

    lines.append('''</table>''')
    lines.append('''<body>''')
    lines.append('''</html>''')

    html_file = open("www/builder_pages/damages.htm", "w")
    html_file.write("\n".join(lines))
    html_file.close()
#- Fine Funzione -


#= SINGLETON ===================================================================

fight_loop = FightLoop()
