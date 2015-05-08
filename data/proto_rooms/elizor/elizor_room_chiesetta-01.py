# -*- coding: utf-8 -*-

#= COMMENT =====================================================================

# Script del mosaico
# usando una special stringa che separa i valori tramite virgola
# e poi li converti quando ti serve come una lista
# pieces = entity.specials["pieces"].split(",")
# viceversa quando ti serve salvarli, nell'on_shutdown per esempio
# entity.specials["pieces"] = ",".join(pieces)
# per il dizionario è un po' più complesso magari, o fai un doppio carattere di separazione, uno che separa la coppia key/value e l'altro che separa key e value
# oppure fai due liste distinte che poi unisci con...
# dictionary = dict(zip(keys, values))
# posso anche gestire le due liste in modo separato
# anche, dipende dai tuoi bisogni
# c'è un altro tipo oltre list e dict
# set
# funziona come una list, ma qualsiasi doppia, tripla, quadrupla etc etc occorrenza di elementi uguali viene rimossa e mantenuta una sola
# sostanzialmente i set sono gli insiemi in matematica
# se uno vuole una lista che abbia in sé una occorrenza di ogni elemento differente basta che faccia:
# lista_ripulita = list(set(lista_con_doppioni))


#= IMPORT ======================================================================

from src.web_resource import create_icon


#= COSTANTI ====================================================================

icona_testo_001 = "icon/elizor-mosaic/mosaic-text-001.png"
icona_testo_002 = "icon/elizor-mosaic/mosaic-text-002.png"

X = 4
Y = 3
lista_tessere = []


#= FUNZIONI ====================================================================

def before_looked(entity, target, descr, detail, use_examine, behavioured):
    if not detail:
        return False

    if not detail.IS_EXTRA:
        return False

    if "mosaico" not in detail.keywords:
        return False

    popola_mosaico_vuoto()
    show_mosaic(entity)
    return


def popola_mosaico_vuoto():
    for num in xrange(X*Y):
        lista_tessere.append(icona_testo_001)
        lista_tessere.append(icona_testo_002)
        if len(lista_tessere) >= X*Y:
            break
    print "lista delle tessere", lista_tessere


def show_mosaic(entity):
    result =  '''<br><div>'''
    for y in xrange(Y):
        for x in xrange(X):
            # cerca l'ennesimo elemento della lista tesserine
            ennesima = x + (y-1)*X -1
            result += '''<div style="float:left; position:relative">'''
            result += '''<img src=%s border="0" />''' % lista_tessere[ennesima]
            result += '''</div>'''
        result += '''<div style="clear:both"></div>'''
    result += '''</div>'''
    entity.send_output(result, break_line=True)
