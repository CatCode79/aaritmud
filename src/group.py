# -*- coding: utf-8 -*-

"""
Modulo per la gestione del gruppo di avventurieri e delle formazioni.
"""


#= IMPORT ======================================================================

#from src.enums import LOCATION
from src.data import Data
from src.log  import log


#= CLASS =======================================================================

class Group(Data):
    """
    Gestisce un gruppo di personaggi.
    """
    def __init__(self, leader=None):
        if not leader and leader is not None:
            log.bug("leader non è un parametro valido: %r" % leader)
            return

        # ---------------------------------------------------------------------

        self.name      = "di %s" % leader.codename  # Nome del gruppo, di default è: "di nome_capo_gruppo"
        self.leader    = leader  # Capo del gruppo
        self.members   = []  # Membri del gruppo
        self.formation = self.disband()  # Formazione del gruppo  # (TD) non son convinto del doppio array, forse meglio fare un dizionario ed accedervi con degli EnumElement ad uopo
    #- Fine Inizializzazione -

    def disband(self):
        """
        Utilizzato per inizializzare la formazione o per disperderne una.
        """
        self.formation = [[None for i in xrange(3)] for i in xrange(3)]
    #- Fine Metodo -

    def get_members_here(self, location):
        """
        Ritorna una lista con i membri del gruppo che si trovano nella stanza,
        o nell'entità, passata.
        """
        if not location:
            log.bug("location non è un parametro valido: %r" % location)
            return []

        # ---------------------------------------------------------------------

        members = []
        for member in self.members:
            if member.location == location:
                members.append(member)
        return members
    #- Fine Metodo -

    #def get_members_area(self, area):
    #    """
    #    Ritorna una lista con i membri del gruppo che si trovano nell'area
    #    passata.
    #    """
    #    if not area:
    #        log.bug("area non è un parametro valido: %r" % area)
    #        return []
    #
    #    # ---------------------------------------------------------------------
    #
    #    members = []
    #    for member in self.members:
    #        if member.location.area == area:
    #            members.append(member)
    #    return members
    #- Fine Metodo -


#= FUNZIONI ====================================================================
