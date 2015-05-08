# -*- coding: utf-8 -*-


#= DESCRIZIONE =================================================================

# prova dei behaviour


#= IMPORT ======================================================================

from src.enums      import TO


#= COSTANTI ====================================================================



#= FUNZIONI ====================================================================


def after_smelled(entity, target, detail, descr, behavioured):

    if detail == target:
        return False

    if behavioured:
        return False
    print "Behavioured parameter room: ", behavioured
    entity.act("Hai respirato cose qui che sarebbe meglio non aver respirato!", TO.ENTITY)
    entity.act("Prova Respiro!", TO.TARGET, target)
    entity.act("$n ha annusato $l e già boccheggia...", TO.OTHERS)
