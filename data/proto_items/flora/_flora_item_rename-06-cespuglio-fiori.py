# -*- coding: utf-8 -*-

#= COMMENT =====================================================================

# L'idea è quella di implementare una componente genetica per l'espressione di
# alcuni caratteri di una rosa.

# L'espressione delle caratteristiche è volta alla riproduzione di una rosa
# in ascii

# @>}-`-,---
# gli elementi variabili sono per ora:
# - la testa - '@', 'Þ', ...
# - calice -   '}', '{', ''
# - sepali -   ')', '(', ''

# Ogni allele è indicato con le lettere alfabetiche minuscole: 'a', 'b', ...
# Ogni allele è una lista a due valori binari
# L'espressione di un carattere dipende da quanti sono in totale i numeri 1
# su tutto un gene
# Esempio:
#   il gene della testa di una rosa è un dizionario e potrebbe contenere i seguenti:
#   generico fiore.fiore_2g = {'a':[0,1], 'b':[1,1], 'c':[1,0], 'd':[0,0], 'e':[1,0], 'f':[0,0]}
#   il numero totale di 1 presenti è pari a 5.
#   la sua testa sarà quindi la sesta: '×'

# A causa del calcolo combinatorio e di altri aspetti minori che non discuto,
# ecco una statistica sulla generazione di 10.000 fiori:

# n° relativo di teste

#     0.8 »»
#    10.2 @
#    42.1 §
#   116.7 ø
#   197.0 ××
#   250.5 ×
#   206.1 XX
#   122.9 X
#    42.5 þ
#    10.0 Þ
#     1.1 #

# calcolo combinatorio:
# n!/((n-k)!*k!)
# n=10 (ovvero il numero delle posizione che possono assumere il valore di 1 o di 0)
# k= 0..10 (ovvero quanti numeri 1 voglio nelle combinazioni finali)
# k = 0 ->   1
# k = 1 ->  10
# k = 2 ->  45
# k = 3 -> 120 
# k = 4 -> 210
# k = 5 -> 252
# k = 6 -> 210
# k = 7 -> 120
# k = 8 ->  45
# k = 9 ->  10
# k =10 ->   1


#= IMPORT ======================================================================

import random
import math

from src.item import Item


#= VARIABILI ===================================================================

heads     = {0:"»»", 1:"@", 2:"§", 3:"ø", 4:"××", 5:"×", 6:"XX", 7:"X", 8:"þ", 9:"Þ", 10:"#"}
calices   = {0:">", 1:"»", 2:"", 3:"", 4:")"}
sepalis   = {0:"}", 1:"B", 2:"", 3:"", 4:"{"}

# Colore per i petali
colors    = {0:'mediumblue', 1:'aquamarine', 2:'red', 3:'purple', 4:'yellowgreen', 5:'darkgreen', 6:'lightpink', 7:'lightsalmon', 8:'darkorange', 9:'mediumvioletred', 10:'gold', 11:'white', 12:'deepskyblue'}

# Colore per i sepali e calice
colors2   = {0:"white", 1:"yellow", 2:"olivedrab", 3:"darkgreen", 4:"lime", 5:"firebrick", 6:"cornflowerblue"}

PROTO_ROSA_CODE = "flora_item_rename-10-rosa"
PRICE_MULTIPLIER = 1.0


#= CLASSI ======================================================================

class Genotipo:

    def __init__(self):
        self.fiore_2g    = {'a':[0,0], 'b':[0,0], 'c':[0,0], 'd':[0,0], 'e':[0,0]}
        self.calice_2g   = {'a':[0,0], 'b':[0,0]}
        self.sepali_2g   = {'a':[0,0], 'b':[0,0]}
        self.head_color  = {'a':[0,0], 'b':[0,0], 'c':[0,0], 'd':[0,0], 'e':[0,0], 'f':[0,0]}
        self.color2_2g   = {'a':[0,0], 'b':[0,0], 'c':[0,0]}
        self.color3_2g   = {'a':[0,0], 'b':[0,0], 'c':[0,0]}

        self.color2 = ''
        self.color3 = ''
        self.head   = ''
        self.color  = ''
        self.sepal  = ''
        self.calice = ''
        self.stalk  = '[green]-`-,---[close]'
        self.flower = ''

        self.fiore_prob   = 1.0
        self.calice_prob  = 1.0
        self.sepali_prob  = 1.0
        self.colore_prob  = 1.0
        self.colore2_prob = 1.0
        self.colore3_prob = 1.0
        self.prob = 1.0
        self.price = 0.0

#    def mutazione(self, allele):
#        casual = random.randint(0,1)
#        gene = self.fiore_2g[allele].pop(casual)
#        if gene == 1:
#            gene = 0
#        else: gene = 1
#        self.fiore_2g[allele].insert(casual, gene) 

class fenotipo:

    def dominance_amount(self):
        dom = 0
        for allele in self.fiore_1g.keys():
            dom = dom + self.fiore_1g[allele].count(1)
        return dom

    def __init__(self):
        self.fiore_1g  = {'a':[0], 'b':[0], 'c':[0], 'd':[0], 'e':[0]}

#= FUNZIONI ====================================================================

def dominance_level(dictionary):
    dom = 0
    for allele in dictionary.keys():
        dom = dom + dictionary[allele].count(1)
    return dom

def dict_len(dictionary):
    length = 0
    for allele in dictionary.keys():
        length = length + len(dictionary[allele])
    return length

def cb(n,k):
    # Coefficinete binomiale
    f = math.factorial
    return f(n)/(f(n-k)*f(k))

def init_element(gen_alleli, char_dict,  rarity=False):
    # inizializza un genotipo esistente, mette random i valori nel dizionario,
    # aggiorna il char relativo allo stato del dizionario,
    # calcola la probabilità dei dizionaro per come popolato.
    for key in gen_alleli.keys():
        gen_alleli[key][0] = random.randint(0,1)
        gen_alleli[key][1] = random.randint(0,1)
    # Per rendere rare alcun espressioni del genoma uno degli alleli viene
    # posto 'a' al valore [0,0] 
    # si potrà mutare per altre vie
    if rarity:
        gen_alleli['a'] = [0,0]
    K = dominance_level(gen_alleli)
    element_char = char_dict[K] 

    N = dict_len(gen_alleli)
    stat_weigth = cb(N,K)
    total_combination = pow(2,N)   
    prob = (stat_weigth + 0.0) / total_combination
    return element_char, prob

def genera_genotipo(rarity=True):
    # genera un genotipo e ne inizializza tutte le parti,
    # crea la forma del fiore
    genoma = Genotipo()

    genoma.head, genoma.fiore_prob = init_element(genoma.fiore_2g, heads, rarity=True)
    genoma.color, genoma.colore_prob = init_element(genoma.head_color, colors, rarity=False)
    colored_head = '[' +  genoma.color + ']' + genoma.head + '[close]'

    genoma.calice, genoma.calice_prob = init_element(genoma.calice_2g, calices, rarity=False)
    # Solo se esce un fiore con calice ne genero il colore
    # Qui occhio che se faccio operazioni sul genoma 
    # devo ricordarmi di farle sul colore solo se c'è calice
    if genoma.calice:
        genoma.color2, genoma.colore2_prob = init_element(genoma.color2_2g, colors2, rarity=False)
        colored_calice = '[' + genoma.color2 + ']' + genoma.calice + '[close]'
    else:
        colored_calice = genoma.calice

    genoma.sepal, genoma.sepali_prob = init_element(genoma.sepali_2g, sepalis, rarity=False)
    # Solo se esce un fiore con sepali ne genero il colore
    if genoma.sepal  != '':
        genoma.color3, genoma.colore3_prob = init_element(genoma.color3_2g, colors2, rarity=False)
        colored_sepali = '[' + genoma.color3 + ']' + genoma.sepal + '[close]' 
    else:
        colored_sepali = genoma.sepal  

    genoma.flower = colored_head + colored_calice + colored_sepali + genoma.stalk

    genoma.prob = genoma.fiore_prob * genoma.colore_prob * genoma.calice_prob * genoma.colore2_prob * genoma.sepali_prob * genoma.colore3_prob
    genoma.price = (1/genoma.prob) * PRICE_MULTIPLIER * global_cheapest_prob(genoma)

    return genoma

def max_prob(dictionary):
    # Calcolo del valore di probabilità più alta del dizonario dato
    N = dict_len(dictionary)
    # Tutti i dict sono ad un numero pari di alleli (diploidismo)
    stat_weigth = cb(N,N/2)
    total_combination = pow(2,N)
    sup_prob = (stat_weigth + 0.0) / total_combination
    return sup_prob

def min_prob(dictionary):
    # Calcolo del valore di probabilità più bassa del dizonario dato
    N = dict_len(dictionary)
    # Tutti i dict sono ad un numero pari di alleli (diploidismo)
    stat_weigth = 1 #c'è una possibilità sola che tutti sia 1 o tutto sia 0
    total_combination = pow(2,N)
    inf_prob = (stat_weigth + 0.0) / total_combination
    return inf_prob

def global_cheapest_prob(genotipo):
    max_p = max_prob(genotipo.fiore_2g) * max_prob(genotipo.calice_2g) * max_prob(genotipo.sepali_2g) * max_prob(genotipo.head_color)
    # I colori sepali e tepali non si usano nel caso di fiori sprovvisti di
    # calice e sepali.
    #max_prob(genotipo.color2_2g)
    #max_prob(genotipo.color3_2g)
    return max_p

def global_highest_prob(genotipo):
    min_p = min_prob(genotipo.fiore_2g) * min_prob(genotipo.calice_2g) * min_prob(genotipo.sepali_2g) * min_prob(genotipo.head_color) * min_prob(genotipo.color2_2g) * min_prob(genotipo.color3_2g)

    return min_p

def split_geni(flower):
    fuffa = fenotipo()
    for alleli in fuffa.fiore_1g.keys():
       fuffa.fiore_1g[alleli][0] = random.choice(flower.fiore_2g[alleli])
    return fuffa

def fecondazione(feno_1, feno_2, mutazione=False, allele='vuoto'):
    fuffa = Genotipo()
    for alleli in fuffa.fiore_2g.keys():
        fuffa.fiore_2g[alleli][0] = feno_1.fiore_1g[alleli][0]
        fuffa.fiore_2g[alleli][1] = feno_2.fiore_1g[alleli][0]
    if mutazione and random.randint(1,MUTAZIONE) == 1:
        allele = random.choice(fiore_2g.keys())
        fuffa.mutazione(allele)
    return fuffa

# == AARITIZZIAMOLO ===========================================================

def after_inject(entity, room):
    print ">>> inserimento fiori via inject"
    if not entity.specials or not 'ancestors' in entity.specials or entity.specials['ancestors'] == False:

        # Qui genero un genotipo solo per fare dei contacci e passare il valore ai successivi genotipi
        # sistema da migliorare...


        entity.specials['ancestors']       = True

    numero_rose = random.randint(4,10)
    for i in range(0,numero_rose):
        genotipo = genera_genotipo()

        rosa = Item(PROTO_ROSA_CODE)
        rosa.inject(entity)
        rosa.specials['fiore']             = str(genotipo.fiore_2g)
        rosa.specials['calice']            = str(genotipo.calice_2g)
        rosa.specials['sepali']            = str(genotipo.sepali_2g)

        rosa.specials['colore']            = str(genotipo.head_color)
        rosa.specials['colore_calice']     = str(genotipo.color2_2g)
        rosa.specials['colore_sepali']     = str(genotipo.color3_2g)

        rosa.specials['fiore_prob']    = genotipo.fiore_prob
        rosa.specials['calice_prob']   = genotipo.calice_prob
        rosa.specials['sepali_prob']   = genotipo.sepali_prob

        rosa.specials['colore_prob']   = genotipo.colore_prob
        rosa.specials['colore2_prob']  = genotipo.colore2_prob
        rosa.specials['colore3_prob']  = genotipo.colore3_prob

        rosa.specials['prob']          = genotipo.prob
        rosa.specials['price']         = genotipo.price

        rosa.specials['ancestors']     = True

        rosa.short = genotipo.flower
        rosa.name  = genotipo.flower
        rosa.value = int(max(1, round(genotipo.price)))

    # Temporneo: alcuni dati dell'ultima rosa li metto sul cespuglio per verificare che
    # siano trasferiti sul next stage
    entity.descr += '\n' + genotipo.flower
    entity.specials['fiore']           = str(genotipo.fiore_2g)
    entity.specials['colore']          = str(genotipo.head_color)
    entity.specials['calice']          = str(genotipo.calice_2g)
    entity.specials['sepali']          = str(genotipo.sepali_2g)
    entity.specials['fiore_prob'] = genotipo.fiore_prob
    entity.specials['colore_prob']  = genotipo.colore_prob
    return False


def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if not old_entity.specials or 'ancestors' not in old_entity.specials:
        new_entity.specials['ancestors']=False
    else:
        for key in old_entity.specials.keys():
            new_entity.specials[key] = old_entity.specials[key]
    return False

# == FUNZIONI DI TEST =========================================================

def test_funzioni(verbose=False):
    print "=== Primo Fiore ==="
    primo_fiore = genera_genotipo()
    print 'generazione genotipo:\t', primo_fiore.fiore_2g
    primo_fiore.update_head()
    print 'testa primo fiore:\t', primo_fiore.head
    print 'numero dominanti primo fiore:\t', primo_fiore.dominance_amount()
    primo_gamete = split_geni(primo_fiore)
    print 'primo gamerete:\t', primo_gamete.fiore_1g

    print "=== Secondo Fiore ==="
    secondo_fiore = genera_genotipo()
    print 'generazione genotipo:\t', secondo_fiore.fiore_2g
    secondo_fiore.update_head()
    print 'testa secondo fiore:\t', secondo_fiore.head
    print 'numero dominanti secondo fiore:\t', secondo_fiore.dominance_amount()
    secondo_gamete = split_geni(secondo_fiore)
    print 'secondo gamerete:\t', secondo_gamete.fiore_1g
   
    if verbose:
        print ">>>>>>>#####"
        print 'primo gamerete:\t', primo_gamete.fiore_1g
        print 'primo   genotipo:\t\t', primo_fiore.fiore_2g
        print 'secondo genotipo:\t\t', secondo_fiore.fiore_2g
        print ">>>>>>>#####"
   
   
    print "=== Fecondazione Fiore ==="
    figlio = fecondazione(primo_gamete, secondo_gamete)
    figlio.update_head()
    print 'genotipo figlio:\t', figlio.fiore_2g
    print 'testa figlio:\t', figlio.head

    print "=== Fecondazione con mutazione su A  ==="
    figlio = fecondazione(primo_gamete, secondo_gamete)
    figlio.mutazione('a')
    figlio.update_head()
    print 'genotipo figlio:\t', figlio.fiore_2g
    print 'testa figlio:\t', figlio.head
    return False

def test_a_nastro():
    for i in range(1,10000):
        sample = genera_genotipo(rarity=False)
        print sample.update_head()
   

def test_multi_funzione():
    print "=== Primo Fiore ==="
    primo_fiore = genera_genotipo()
    print 'generazione genotipo:\t', primo_fiore.fiore_2g, primo_fiore.calice_2g, primo_fiore.sepali_2g, primo_fiore.head_color
    print 'generazione genotipo:\t', primo_fiore.head
    print 'generazione genotipo:\t', primo_fiore.calice
    print 'generazione genotipo:\t', primo_fiore.sepal
    print 'generazione genotipo:\t', primo_fiore.color
    print 'generazione genotipo:\t', primo_fiore.flower


# == ESECUZIONE ===============================================================

#test_funzioni(verbose=True)
#test_a_nastro()
#test_multi_funzione()
