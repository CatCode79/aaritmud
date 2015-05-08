# -*- coding: utf-8 -*-

"""
Gestisce gli effetti delle varie entità.
"""


#= IMPORT ======================================================================

from src.element import Flags
from src.enums   import AFFECT, APPLY, RACE
from src.log     import log
from src.utility import copy_existing_attributes, from_capitalized_words, is_number


#= CLASSI ======================================================================

class Affect(object):
    """
    Classe che gestisce un effetto.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = ["comment"]
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, type=AFFECT.NONE, apply=APPLY.NONE):
        if not type:
            log.bug("type non è un parametro valido: %r" % type)
            return

        if not apply:
            log.bug("apply non è un parametro valido: %r" % apply)
            return

        # ---------------------------------------------------------------------

        self.comment     = ""  # Eventuale commento riguardante l'affect
        self.type        = Element(type)  # Indica dove andare a inserire l'affect, in genere se sull'entità stessa o su quella che la contiene
        self.flags       = Flags(AFFECTFLAG.NONE)  # Flags di affect
        self.conditional = Flags(RACE.NONE)  # (TD) GenericFlags, può essere un qualsiasi elemento o flags, a seconda della flags o che cambia, bisognerà anche inserire un NOT iniziale, ma magari supportarlo anche per le Flags semplici
        self.apply       = ""  # Etichetta, o meglio attributo, da modificare
        self.modifier    = ""  # Modificatore (TD) sarà un GenericModifier, cioè prenderà il tipo dell'etichetta da modificare, +100 100 -100, il problema dei modifier senza segno li posso correggere aggiungendo una flags di affect che indichi che un affect dello stesso tipo edve spegnersi prima che quello nuovo venga messo in auge
        self.reason      = ""  # Descrizione della ragione dell'affect
        self.rpg_minutes = -1  # Durata dell'affect, -1 è per sempre

        self.skill_code  = ""  # Se l'affect deriva da una skill o simile, questo è il suo identificativo
        self.level       = 0   # Il livello viene utilizzato di solito per indicare il potere di un affect di skill, se l'affect è entrato con un masterly il livello è cmq sempre 100, altrimenti dipende dal lancio dei dadi
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %r" % (super(Affect, self).__repr__, self.type)
    #- Fine Metodo -

    def get_error_message(self):
        # (TD)
        return ""
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = Affect(self.type)
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Metodo -

    def equals(self, affect2):
        raise NotImplementedError
    #- Fine Metodo -

    def apply(self):
        # Ricava l'obiettivo in cui copiare l'self
        if self.type == AFFECT.SELF:
            target = obj
        elif self.type == AFFECT.CONTAINED_BY:
            target = obj.location
        elif self.type == AFFECT.ROOM and obj.location.IS_ROOM:
            target = obj.location
        elif self.type == AFFECT.ENTITY and not obj.location.IS_ROOM:
            target = obj.location
        elif self.type == AFFECT.ITEM and obj.location.IS_ITEM:
            target = obj.location
        elif self.type == AFFECT.ACTOR and obj.location.IS_ACTOR:
            target = obj.location
        elif self.type == AFFECT.MOB and obj.location.IS_MOB:
            target = obj.location
        elif self.type == AFFECT.PLAYER and obj.location.IS_PLAYER:
            target = obj.location
        else:
            return

        # Controlla se ci sono le condizioni per copiare l'self
        if self.conditional and target.race not in self.conditional:
            return

        # Cerca l'attributo da applicare relativo all'etichetta
        apply_attr = from_capitalized_words(self.apply)
        if not hasattr(target, apply_attr):
            log.bug("Non è stato trovato nessun attributo valido dall'etichetta %s per l'self su %s" % (self.apply, obj.code))
            return

        # Infine imposta il valore e si salva il riferimento dell'self
        attr = getattr(target, apply_attr)
        if isinstance(attr, basestring):
            setattr(target, apply_attr, self.modifier)
        else:
            if self.modifier[0] == "+":
                if not is_number(self.modifier[1 : ]):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, attr + int(self.modifier[1 : ]))
            elif self.modifier[0] == "-":
                if not is_number(self.modifier[1 : ]):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, attr - int(self.modifier[1 : ]))
            else:
                if not is_number(self.modifier):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, int(self.modifier))

        target.affect_infos.append((self, attr))
    #- Fine Metodo -

    # (TD) ogni remove deve andare alla ricerca posizionale dell'affect nel
    # relativo infos ed eseguire il ciclo di rimozione apposito
    def remove(self, target=None, affect_info=None):
        """
        Da notare che non esegue controlli condizionali e sulla duration.
        """
        if not target:
            # Ricava l'obiettivo in cui copiare l'self
            if self.type == AFFECT.SELF:
                target = obj
            elif self.type == AFFECT.CONTAINED_BY:
                target = obj.location
            elif self.type == AFFECT.ROOM and obj.location.IS_ROOM:
                target = obj.location
            elif self.type == AFFECT.ENTITY and not obj.location.IS_ROOM:
                target = obj.location
            elif self.type == AFFECT.ITEM and obj.location.IS_ITEM:
                target = obj.location
            elif self.type == AFFECT.ACTOR and obj.location.IS_ACTOR:
                target = obj.location
            elif self.type == AFFECT.MOB and obj.location.IS_MOB:
                target = obj.location
            elif self.type == AFFECT.PLAYER and obj.location.IS_PLAYER:
                target = obj.location
            else:
                return

        # Cerca l'self su target riguardante questo, se non lo trova
        # significa che l'entità per qualche motivo non lo ha più addosso
        if not affect_info:
            for affect_info in target.affect_infos:
                if affect_info[0] == self:
                    break
            else:
                log.bug("Per qualche motivo bacoso %s non ha il riferimento all'self con apply %s e modifier %s di %s" % (
                    target.code, self.apply, self.modifier, obj.code))
                return

        # Cerca l'attributo da applicare relativo all'etichetta
        apply_attr = from_capitalized_words(self.apply)
        if not hasattr(target, apply_attr):
            log.bug("Non è stato trovato nessun attributo valido dall'etichetta %s per l'self su %s" % (self.apply, obj.code))
            return

        # Infine rimuove il valore eventualmente dall'attributo salvato
        # precedentemente
        attr = getattr(target, apply_attr)
        if isinstance(attr, basestring):
            setattr(target, apply_attr, affect_info[1])
        else:
            if self.modifier[0] == "+":
                if not is_number(self.modifier[1 : ]):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, attr + int(self.modifier[1 : ]))
            elif self.modifier[0] == "-":
                if not is_number(self.modifier[1 : ]):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, attr - int(self.modifier[1 : ]))
            else:
                if not is_number(self.modifier):
                    log.bug("modifier per un self su di %s non è un numero: %s" % (obj.code, self.modifier))
                    return
                setattr(target, apply_attr, affect_info[1])

        target.affect_infos.remove(affect_info)
    #- Fine Metodo-


#= FUNZIONI ====================================================================

# (TD) Stesso lavoro eseguito per le extra, fare una classe come le Flags
def get_error_message_affects(affects):
    """
    Controlla l'integrità di tutti gli affect passati, se trova un errore ne
    ritorna il relativo messaggio.
    """
    if not affects and affects != []:
        log.bug("affects passato non è una lista valida: %s" % affects)
        return

    # -------------------------------------------------------------------------

    # (TD)
    return ""
#- Fine Funzione -


def is_affected(obj, affect_type):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return False

    if not affect_type:
        log.bug("affect_type non è un parametro valido: %r" % affect_type)
        return False

    # -------------------------------------------------------------------------

    for affect in obj.affect_infos:
        pass

    # (TD)
    return False
#- Fine Funzione -


def apply_all_affects(obj):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return False

    # -------------------------------------------------------------------------

    # (TD) aggiunge gli affect razziali
    pass

    # Aggiunge gli affect delle entità indossate
    for weared_entity in obj.iter_contains():
        print weared_entity
        if len(weared_entity.wear_mode) > 0:
            for affect in weared_entity.affects:
                affect.apply()

    # Aggiunte gli affect delle entità cibo o bevanda mangiate, se non
    # ancora digerite
    pass

    # (TD) Aggiunge gli affect speciali delle entità anche non indossate
    pass

    # Aggiunge gli affect della stanza
#- Fine Funzione -


def remove_all_affects(obj):
    if not obj:
        log.bug("obj non è un parametro valido: %r" % obj)
        return False

    # -------------------------------------------------------------------------

    # Esegue un ciclo a rovescio di come sono stati inseriti gli affect
    # per rimuoverli correttamente ed avere alla fine lo stato originale
    for affect_info in reversed(obj.affect_infos):
        affect_info[0].remove(obj, affect_info)
#- Fine Funzione -


# (TD) update degli affects duration
