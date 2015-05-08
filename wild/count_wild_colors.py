"""
Conta il numero di occorrenze per ogni tipo di colore per le immagini delle
wild e stampa a video i risultati.
"""

import pprint

import Image

if __name__ == "__main__":
    im  = Image.open("altitudes.png")
    im2 = Image.open("sectors.png")
    print("Elenco dei colori delle altitudini:")
    pprint.pprint(im.getcolors())
    print
    print("Elenco dei colori dei settori:")
    pprint.pprint(im2.getcolors())
