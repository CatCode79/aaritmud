# -*- coding: utf-8 -*-

"""
Modulo per tipologie d'entità utilizzabili per pescare o per attirare prede
in trappola.
"""


#= CLASSI ======================================================================

class BaitableGenericType(object):
    """
    Classe utilizzata per tutte le tipologie che richiedono di un'esca.
    """
    def __init__(self):
        self.minutes   = 1     # Minuti reali di attesa media per avere un pesce sull'esca
        self.quantity  = 1     # Quantità media di pesci pescata per volta, se il valore è 1 pescherà sempre 1 e non più
        self.two_hands = False # Indica se l'oggetto bisogna utilizzarlo ad una o due mani  # (TD) spostarlo come flag di oggetto?
        self.charged   = False # Indica se la trappola è stata caricata
        #self.bait      = None  # Esca inseribile per migliorarne tempo e quantità # (TD) farla tipo contenitore
        #self.catches   = []    # Prede catturate  # (TD) farli tipo contenitore
    #- Fine Inizializzazione -

    def equals(self, baitable2):
        if not baitable2:
            return False

        if self.minutes != baitable2.minutes:
            return False
        if self.quantity != baitable2.quantity:
            return False
        if self.two_hands != baitable2.two_hands:
            return False
        if self.charged != baitable2.charged:
            return False

        return True
    #- Fine Metodo -
