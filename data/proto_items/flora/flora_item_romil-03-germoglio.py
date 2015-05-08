# -*- coding: utf-8 -*-


def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if old_entity.specials and 'ancestors' in old_entity.specials and old_entity.specials['ancestors']:
        print "#### ROMIL - NEXT STAGE - *** copia pedigree ***"
        for key in old_entity.specials:
            new_entity.specials[key] = old_entity.specials[key]
    else:
        print "#### ROMIL - NEXT STAGE - *** nessuna copia ***"
    return False
