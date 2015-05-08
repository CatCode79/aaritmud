# -*- coding: utf-8 -*-

# Se le rose vengono prese dal cespuglio si spezza lo stelo
# poi nello script delle sementi si fa in modo che le rose spezzate
# non diano semente fertile

PROTO_CESPUGLIO_CODE = 'flora_item_romil-06-cespuglio-fiori'
FIORE_DESCR = '\nLo stelo è stato spezzato alla base.'


def before_getted(entity, fiore, location, behavioured):
    print "rosa gettata"
    if fiore.specials and 'chopped' in fiore.specials and fiore.specials['chopped']:
        return

    if fiore.location.IS_ITEM and fiore.location.prototype.code == PROTO_CESPUGLIO_CODE:
        print 'rosa gettata dal cespuglio'
        fiore.specials['chopped'] = True
        fiore.descr += FIORE_DESCR
        return
