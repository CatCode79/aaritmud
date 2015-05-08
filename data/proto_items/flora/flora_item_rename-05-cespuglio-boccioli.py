# -*- coding: utf-8 -*-

def on_next_stage(old_entity, new_entity, choised_attr, entities):
    if not old_entity.specials or 'ancestors' not in old_entity.specials or new_entity.specials or 'ancestors' not in new_entity.specials:
        new_entity.specials['ancestors']=False
    else:
        print ">>>>>>> passo di qui!"
        print old_entity.specials

        for special in old_entity.specials:

            new_entity.specials[special] = old_entity.specials[special]

    # questo consenti di caricare il prossimo stadio ma non il successivo
    #return True

