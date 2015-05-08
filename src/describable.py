# -*- coding: utf-8 -*-

"""
Modulo per la gestione delle stanze, uscite, mura e destinazioni.
"""


#= CLASSI ======================================================================

class Describable(object):
    ASCIIART_TAG_OPEN  = '''<pre class="asciiart">'''
    ASCIIART_TAG_CLOSE = '''</pre>'''

    # (OO) Questa parte la potrei farla all'istanzazione di una stanza
    # e di un mob invece che ad ogni esecuzione di un comando sensoriale
    def convert_asciiart_linefeeds(self, descr):
        if not descr:
            log.bug("descr non è un parametro valido: %r" % descr)
            return ""

        # ---------------------------------------------------------------------

        if self.ASCIIART_TAG_OPEN not in descr:
            log.bug("Non è bene chiamare tale funzione se non possiede il tag caratteristico delle asciiart.")
            return ""

        new_descr = ""
        tag_close_index = 0
        while self.ASCIIART_TAG_OPEN in descr:
            tag_open_index  = descr.find(self.ASCIIART_TAG_OPEN, tag_close_index)
            if tag_open_index == -1:
                break
            new_descr += descr[tag_close_index : tag_open_index]

            tag_close_index = descr.find(self.ASCIIART_TAG_CLOSE, tag_open_index)
            if tag_close_index == -1:
                log.bug("Era atteso un tag per chiudere la ascii art: %s" % descr)
                new_descr += descr[tag_open_index : ]
                return new_descr
            new_descr += descr[tag_open_index : tag_close_index].replace("\n", "<br>")

        new_descr += descr[tag_close_index : ]
        return new_descr
    #- Fine Metodo -
