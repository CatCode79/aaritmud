# -*- coding: utf-8 -*-

"""
Modulo riguardante la gestisce fisica dei liquidi e la loro espansione nelle
stanze e tra le uscite.
"""

#= IMPORT ======================================================================

from src.loop import UnstoppableLoop


#= CLASSI ======================================================================

class BlobLoop(UnstoppableLoop):
    def __init__(self):
        super(BlobLoop, self).__init__()
    #- Fine Inizializzazione -

    def cycle(self):
        """
        Aggiorna tutti i file dei dati di prototipo, i file di modulo python e
        i file di view relative alle pagine web modificati dopo che il gioco è
        stato avviato (cioè dopo che è stato lanciato questo loop, quindi le
        modifiche inserite tra la lettura del dato e l'esecuzione di questo
        loop non verrebbero carpite).
        """
        # (TD) aspettare l'inserimento dei materiali prima di procedere
        return
        if self.paused:
            return
    #- Fine Metodo -


#= SINGLETON ===================================================================

blob_loop = BlobLoop()
