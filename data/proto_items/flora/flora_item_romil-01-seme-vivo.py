# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

import random
import math

#= COSTANTI ====================================================================

HEADS     = {0:"»»", 1:"@", 2:"§", 3:"ø", 4:"××", 5:"×", 6:"XX", 7:"X", 8:"þ", 9:"Þ", 10:"#"}
CALICES   = {0:">", 1:"»", 2:"i", 3:"l", 4:")"}
SEPALIS   = {0:"}", 1:"B", 2:"p", 3:"m", 4:"{"}

# Colore per i petali
COLORS    = {0:'mediumblue', 1:'aquamarine', 2:'red', 3:'purple', 4:'yellowgreen', 5:'darkgreen', 6:'lightpink', 7:'lightsalmon', 8:'darkorange', 9:'mediumvioletred', 10:'gold', 11:'white', 12:'deepskyblue'}

# Colore per i sepali e calice
COLORS2   = {0:"white", 1:"yellow", 2:"olivedrab", 3:"darkgreen", 4:"lime", 5:"firebrick", 6:"cornflowerblue"}

PROTO_ROSA_CODE = "flora_item_romil-10-rosa"
PRICE_MULTIPLIER = 1.0

#= CLASSI ======================================================================

class Gameti:

    def __init__(self):
        self.fiore_2g    = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0}
        self.calice_2g   = {'a':0, 'b':0}
        self.sepali_2g   = {'a':0, 'b':0}
        self.head_color  = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0}
        self.color2_2g   = {'a':0, 'b':0, 'c':0}
        self.color3_2g   = {'a':0, 'b':0, 'c':0}

    def get_all_genoma(self):
        return [self.fiore_2g, self.calice_2g, self.sepali_2g, self.head_color, self.color2_2g, self.color3_2g]

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
        self.price = 0

        self.gameti_propri = []
        self.gameti_altrui = []

    def get_all_genoma(self):
        return [self.fiore_2g, self.calice_2g, self.sepali_2g, self.head_color, self.color2_2g, self.color3_2g]

    def new_get_all_genoma(self):
        return {'fiore':self.fiore_2g, 'calice':self.calice_2g, 'sepali':self.sepali_2g, 'fiore_color':self.head_color, 'calice_color':self.color2_2g, 'sepali_color':self.color3_2g}

    def get_gameti(self):
        sx = Gameti()
        lista_sx = sx.get_all_genoma()
        dx = Gameti()
        lista_dx = dx.get_all_genoma()
        lista_self = self.get_all_genoma()

        for x in xrange(len(lista_sx)):
            for key in lista_self[x]:
                lista_sx[x][key] = lista_self[x][key][0] 
                lista_dx[x][key] = lista_self[x][key][1]

        return [lista_sx, lista_dx]
  
    def fecondazione(self, lista_sx, lista_dx):
        lista_self  = self.get_all_genoma()
        for x in xrange(len(lista_self)):
            for key in lista_self[x]:
                lista_self[x][key][0] = lista_sx[x][key]
                lista_self[x][key][1] = lista_dx[x][key]
        return

    def mutazione(self, position=False, accidenti=False):
        choosed_dict = ''
        num = 0
        list_genoma = self.get_all_genoma()
        print ">>>> Genera mutazione, list_genoma", list_genoma
        for genomi in list_genoma:
            num += dict_len(genomi)
        dice = random.randint(1,num)
        for genomi in list_genoma:
            num -= dict_len(genomi)
            if num <= dice:
                choosed_dict = genomi
                break
    
        coppia = random.choice(choosed_dict.keys())
        pos = random.randint(0,1)
        if choosed_dict[coppia][pos] == 0:
            choosed_dict[coppia][pos] = 1
        else:
            choosed_dict[coppia][pos] = 0
        return


    def importa_specials(self, entity):
    # Importa le special dentro ad un entità della classe Genotipo
    
        # Nelle specials non salvo tutti i parametri,
        # questi gli orfani
        #self.color2 = ''
        #self.color3 = ''
        #self.head   = ''
        #self.color  = ''
        #self.sepal  = ''
        #self.calice = ''
    
        # dizionari
        self.fiore_2g   = eval(entity.specials['fiore'])
        self.calice_2g  = eval(entity.specials['calice'])
        self.sepali_2g  = eval(entity.specials['sepali'])
    
        self.head_color = eval(entity.specials['colore'])
        self.color2_2g  = eval(entity.specials['colore_calice'])
        self.color3_2g  = eval(entity.specials['colore_sepali'])
    
        # === Parametri Derivabili dai Precedenti ===
        # probabilità parziali
        self.fiore_prob   = entity.specials['fiore_prob']
        self.calice_prob  = entity.specials['calice_prob']
        self.sepali_prob  = entity.specials['sepali_prob']
    
        self.colore_prob  = entity.specials['colore_prob']
        self.colore2_prob = entity.specials['colore2_prob']
        self.colore3_prob = entity.specials['colore3_prob']
    
        self.flower = entity.specials['flower']
        self.prob   = entity.specials['prob']
        self.price  = entity.specials['price']

    def crea_specials(self, entity):
        entity.specials['fiore']             = str(self.fiore_2g)
        entity.specials['calice']            = str(self.calice_2g)
        entity.specials['sepali']            = str(self.sepali_2g)
    
        entity.specials['colore']            = str(self.head_color)
        entity.specials['colore_calice']     = str(self.color2_2g)
        entity.specials['colore_sepali']     = str(self.color3_2g)
    
        entity.specials['fiore_prob']    = self.fiore_prob
        entity.specials['calice_prob']   = self.calice_prob
        entity.specials['sepali_prob']   = self.sepali_prob
    
        entity.specials['colore_prob']   = self.colore_prob
        entity.specials['colore2_prob']  = self.colore2_prob
        entity.specials['colore3_prob']  = self.colore3_prob
    
        entity.specials['flower']        = self.flower
        entity.specials['prob']          = self.prob
        entity.specials['price']         = self.price
    
        entity.specials['ancestors']     = True
        return False

#= FUNZIONI ====================================================================

def dominance_level(dictionary):
    dom = 0
    for allele in dictionary:
        dom = dom + dictionary[allele].count(1)
    return dom

def dict_len(dictionary):
    # nome brutto da cambiare
    length = 0
    for allele in dictionary:
        length = length + len(dictionary[allele])
    return length

def cb(n,k):
    # Coefficinete binomiale
    f = math.factorial
    return f(n)/(f(n-k)*f(k))

def init_element(gen_alleli, char_dict,  rarity=False, popola=True):
    # inizializza un genotipo esistente, mette random i valori nel dizionario,
    # aggiorna il char relativo allo stato del dizionario,
    # calcola la probabilità dei dizionaro per come popolato.
    if popola:
        for key in gen_alleli:
            gen_alleli[key][0] = random.randint(0,1)
            gen_alleli[key][1] = random.randint(0,1)
    # Per rendere rare alcun espressioni del genoma uno degli alleli viene
    # posto 'a' al valore [0,0] 
    # si potrà mutare per altre vie
    if rarity:
        keys = gen_alleli.keys()
        keys.sort
        first_key = keys[0]
        gen_alleli[first_key] = [0,0]

    K = dominance_level(gen_alleli)
    element_char = char_dict[K] 

    N = dict_len(gen_alleli)
    stat_weigth = cb(N,K)
    total_combination = pow(2,N)   
    prob = (stat_weigth + 0.0) / total_combination
    return element_char, prob

def ricalcola_genotipo(genoma, popola=False):
    # prende un genotipo inizializzato nei suoi dizionari e lo aggiorna,
    # crea la forma del fiore

    genoma.head, genoma.fiore_prob = init_element(genoma.fiore_2g, HEADS, rarity=True, popola=popola)
    genoma.color, genoma.colore_prob = init_element(genoma.head_color, COLORS, rarity=False, popola=popola)
    colored_head = '[' +  genoma.color + ']' + genoma.head + '[close]'

    genoma.calice, genoma.calice_prob = init_element(genoma.calice_2g, CALICES, rarity=False, popola=popola)
    # Solo se esce un fiore con calice ne genero il colore
    # Qui occhio che se faccio operazioni sul genoma 
    # devo ricordarmi di farle sul colore solo se c'è calice
    if genoma.calice:
        genoma.color2, genoma.colore2_prob = init_element(genoma.color2_2g, COLORS2, rarity=False, popola=popola)
        colored_calice = '[' + genoma.color2 + ']' + genoma.calice + '[close]'
    else:
        colored_calice = genoma.calice

    genoma.sepal, genoma.sepali_prob = init_element(genoma.sepali_2g, SEPALIS, rarity=False, popola=popola)
    # Solo se esce un fiore con sepali ne genero il colore
    if genoma.sepal  != '':
        genoma.color3, genoma.colore3_prob = init_element(genoma.color3_2g, COLORS2, rarity=False, popola=popola)
        colored_sepali = '[' + genoma.color3 + ']' + genoma.sepal + '[close]' 
    else:
        colored_sepali = genoma.sepal  

    genoma.flower = colored_head + colored_calice + colored_sepali + genoma.stalk

    genoma.prob = genoma.fiore_prob * genoma.colore_prob * genoma.calice_prob * genoma.colore2_prob * genoma.sepali_prob * genoma.colore3_prob
    genoma.price = int(round((1/genoma.prob) * PRICE_MULTIPLIER * global_cheapest_prob(genoma)))
    print "ricalcola_genotipo\t", genoma.flower
    return

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

def specials_to_entity(entity):
    entity.short = entity.specials['flower']
    entity.name  = entity.specials['flower']
    entity.value = entity.specials['price']
    return False

# == AARITIZZIAMOLO ===========================================================


def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if old_entity.specials and 'ancestors' in old_entity.specials and old_entity.specials['ancestors']:
        print "#### ROMIL - NEXT STAGE - *** copia pedigree ***"
        for key in old_entity.specials:
            new_entity.specials[key] = old_entity.specials[key]
    else:
        print "#### ROMIL - NEXT STAGE - *** nessuna copia ***"
    return False

def after_seeded(seminatore, seed, location, ground, behavioured):
    if seed.specials and 'ancestors' in seed.specials and seed.specials['ancestors']:
        print "#### ROMIL - SEME - *** Si Pedigree ***"
        return False

    genotipo = Genotipo()
    ricalcola_genotipo(genotipo, popola=True)
    #genotipo = genera_genotipo()

    # Temporaneo: alcuni dati dell'ultima rosa li metto sul cespuglio per verificare che
    # siano trasferiti sul next stage
    seed.descr += '\n' + genotipo.flower

    #crea_specials(genotipo, seed)
    genotipo.crea_specials(seed)
    print "#### ROMIL - SEME - *** No Pedigree, generato nuovo ***"
    return False
