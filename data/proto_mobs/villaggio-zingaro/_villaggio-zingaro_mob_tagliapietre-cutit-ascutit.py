# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random
import string
from src.database              import database
from src.enums                 import TO
from src.commands.command_say  import command_say


#= COSTANTI ====================================================================

GEMMA_PROTO_CODE = "miniere-kezaf_item_gemma-lavorata-script"

GEMME_DATA = {"brillante ovale":[
             
            "brillantovale",

            "La superficie ovaleggiante dell$O splendid$O $ColoredName è arricchita da meravigliose sfaccettature e da luminescenze ponderate; la sua forza evocativa è così impetuosa da confondere la vista, complice lo scintillio che emerge dalla superficie della gemma quando viene mossa." 

            "La superficie ovaleggiante di quest$O $ColordeName è arricchita da sfaccettature e luminescenze, la sua superficie è ben lavorata e lo scintillio che emana ne rende piena evidenza.", 

            "L'imprecisa superficie ovaleggiante di quest$O $ColoredName è corredata da sfaccettature e da luminescenze che paiono un buon tentativo di nascondere alcuni errori nel taglio. Nel complesso la sua superficie è stata corretta con sufficiente fortuna.",

            "La superficie di quest$O $CloredName voleva essere ovaleggiante ma ci si è arresi davanti ad una piccola crepa evitando il disastro. Nel tentativo di mascherare l'imperfezione è stata leggermente sfaccettata ma le luminescenze che si originano paiono enfatizzare il problema. In alcune posizioni è meno evidente anche se mai assente."
           ],

       "brillante goccia":[
             
            "brillantgoccia",

            "Quest$O splendid$O $ColoredName, lavorat$O con indicibile maestria, ha un taglio peculiare e la forma ricorda quella di una goccia d’acqua. Nella parte sottostante la brillantezza è eccezionalmente amplificata, mentre la riflessione della luce sulla punta è volutamente limitata grazie alle smussature delle faccette inferiori",

            "Quest$O $ColoredName, lavorat$O con maestria, ha un taglio singolare poiché la sua forma ricorda quella di una goccia d’acqua. Nella parte sottostante la brillantezza è maggiormente percettibile, mentre la riflessione della luce sulla punta avviene con difficoltà a causa delle smussature delle faccette inferiori",

            "Quest$O $ColoredName, lavorat$O in modo impreciso, ha un taglio singolare poiché la sua forma ricorda quella di una goccia d’acqua. Nella parte sottostante la brillantezza è maggiormente percettibile, mentre la riflessione della luce sulla punta avviene con difficoltà a causa delle smussature delle faccette inferiori",

            "Quest$O $ColoredName più che lavorat$O è stat$O profanat$O con malagrazia; ha un taglio singolare e la sua forma vorrebbe ricordare quella di una goccia d’acqua. Nella parte sottostante la brillantezza è appena percettibile, mentre la riflessione della luce sulla punta avviene è inibita a causa delle smussature delle faccette inferiori"
           ],

       "brillante navetta":[
             
            "brillantavetta",

            "Un$O splendid$O $ColoredName dalla forma allungata che termina con delle punte simmetriche alle estremità. Questo taglio conferisce alla pietra una fulgida luminosità nella zona centrale con una progressiva sapiente riduzione dello scintillio sulle punte.",

            "Quest$O $ColoredName dalla forma allungata, termina con delle punte alle estremità. Con questo taglio la pietra assume una forte luminosità nella zona centrale ma una diminuzione dello scintillio sulle punte.",

            "Mediocre lavorazione per quest$O $ColoredName dalla forma allungata che termina con delle punte diseguali sulle estremità. Con questo taglio la pietra assume una discreta luminosità nella zona centrale ma una diminuzione dello scintillio sulle punte.",

            "Un$O svilit$O $ColoredName di qualità inferiore tagliato in forma oblunga; termina con delle punte sulle estremità di cui una monca. Con questo taglio la pietra assume una certa luminosità nella zona centrale a discapito delle punte nel tentativo di nascondere il danno."
           ],

       "gradini rettangolare":[
             
            "gradinangolare",

            "Un$O stupend$O $ColoredName a taglio rettangolare di fattura eccelsa. Le sfaccettature oblunghe che percorrono la pietra, sono disposte fittamente l'una sull'altra a guisa di scala e l'avvolgono sui quattro lati. L'effetto finale in termini percettivi è un morbido sentore d'avvolgente e diafana luminosità.",

            "Pregevole quest$O $ColoredName a taglio rettangolare e di buona qualità. Le sfaccettature oblunghe che percorrono la pietra, sono disposte l'una sull'altra a guisa di scala e l'avvolgono sui quattro lati. L'effetto finale in termini percettivi è un avvolgente luminosità.",

            "Il taglio di quest$O $ColoredName presenta una forma rettangolare con sfaccettature di fattura modesta, poste una sopra l'altra ricordano una scalinata che discende sui quattro lati. Tale forma produce una percezione di semitrasparenza unita ad una buffa luminosit.",

            "Impreciso il taglio rettangolare di quest$O $ColoredName. Le sfaccettature oblunghe che percorrono la pietra, sono disposte in modo diseguale sui quattro lati per tamponare il taglio approssimativo. L'effetto finale in termini percettivi è uno sgradevole senso d'incompiuto."
           ],

       "cabochon emisferico":[
             
            "cabosferico",

            "La luce scivola sulla superficie straordinariamente levigata e perfettamente sferica di un$O splendid$O $ColoredName. Infinite sfumature danzano instancabili sulla superficie in vampe multicolori.",

            "La luce si perde sulla superficie sferica di quest$O $ColoredName. Molteplici le sfumture che la luce gioca sulla superficie.",

            "Quest$O $ColoredName lavorat$O in forma sferica risulta a tratti satinat$O interrompendo i giochi di luce che danzano sulla superficie nelle parti in cui la lavorazione è migliore.",

            "Quest$O $ColoredName lavorat$O in forma sferica ha subito un eccessivo appiattimento su un lato con un risultato poco gradevole; Nel complesso la superficie zigrinata imprigiona la maggior parte della luce incupendone il disegno."
           ],

       "cabochon ellissoidale":[
             
            "cabollissoidale",

            "Quest$O $ColoredName di forma ellissoidale è levigat$O con tale precisione da non sembrare opera di un mortale. La luce dell'ambiente è catturata tutta e rifratta con tanta efficienza da farl$a brillare come di luce propria.",

            "Quest$O $ColoredName è levigat$O a forma ellissoidale e con la superficie liscia. La luce esterna è catturata dalla pietra che la riemette in un effetto luminoso importante.",

            "Quest$O $ColoredName è levigata a forma ellissoidale ma ad alcune angolazioni risulta più ovoidale. I tratti levigati con maggiore precisione enfatizzano le zone in cui tale precisione è leggermente in difetto.",

            "Quest$O $ColoredName levigat$O a forma ellissoidale somiglia più che altro al risultato di una frattura su una sfera unica. I giochi di luce sulla parte piatta rendono conto dell'irregolarità della base. Uno sfortunato taglio malamente ritoccato si staglia sulla parte a cupola a memoria delle male parole pronunciate dal suo autore."
           ]
}

#= FUNZIONI ====================================================================

def before_giving(player, gemma_grezza, tagliapietre, direction, behavioured):
    if not player.IS_PLAYER:
        tagliapietre.act("$N cerca di darti robaccia ma tu non accetti.", TO.ENTITY, player)
        tagliapietre.act("$n non accetta che tu gli dia alcunché.", TO.TARGET, player)
        tagliapietre.act("$N cerca inutilmente di dare qualcosa a $n.", TO.OTHERS, player)
        return True

    if not tagliapietre.specials:
        tagliapietre.specials["work_with"] = None
    if not tagliapietre.specials["work_with"] == player.code:
        if tagliapietre.specials["work_with"]:
#    if "work_with" in tagliapietre.specials and player.code != tagliapietre.specials["work_with"] and not tagliapietre.specials["work_with"] :
            to_say = "a %s ... dammi tempo che son già occupato con, %s" % (player.code, tagliapietre.specials["work_with"])
            command_say(tagliapietre, to_say)
            return True
       
    id_generico = gemma_grezza.prototype.code.split("_")[2][:12]
    if id_generico != 'gemma-grezza':
        to_say = "a %s ... e cosa vuoi che ne faccia?" % player.code
        command_say(tagliapietre, to_say)
        return True
    else:
        id_gemma = gemma_grezza.prototype.code.split("_")[2][13:]
        to_say = "a %s è un buon inizio: %s." % (player.code, id_gemma)
        command_say(tagliapietre, to_say)
        room = tagliapietre.location
        crea_gemma(id_gemma, player, tagliapietre, gemma_grezza, room)
        return False

def crea_gemma(id_gemma, player, tagliapietre, gemma_grezza, room):
    tagliapietre.specials["work_with"] = player.code
    # OBJ CREATION
    proto_gemma_lavorata = database["proto_items"][GEMMA_PROTO_CODE]
    gemma_lavorata = proto_gemma_lavorata.CONSTRUCTOR(proto_gemma_lavorata.code)
    # ---- #
    gemma_lavorata.sex = gemma_grezza.sex
    colored_name = gemma_grezza.name
    # DELETE GREZZ$O
    num = string.rfind(colored_name, " ")
    colored_name = colored_name[:num]
    # ATTENZIONE MANCANO LE KEYWORDS!! (forse esiste un metodo per crearle automaticamanete)
    gemma_lavorata.name = colored_name + " con taglio a " + GEMME_DATA["brillante ovale"][0] 
    gemma_lavorata.short = string.lower(gemma_lavorata.name)
    if "'" in colored_name:
        num = string.find(colored_name, "'")
    else:
        num = string.find(colored_name, " ")
    colored_name = colored_name[num+1:]
    colored_name_lower = string.lower(colored_name)
     
    # OBJ INJECTION
    gemma_lavorata.inject(room)
    # ---- #
    descr = GEMME_DATA['brillante ovale'][1] 
    descr = string.replace(descr,'$ColoredName' , colored_name_lower)
    gemma_lavorata.descr = descr
    print ">>>>>>>>>>>>>>>>>>>>>>>>:+", colored_name   
    print ">>>>>>>>>>>>>>>>>>>>>>>>:+", descr
    print ">>>>>>>>>>>>>>>>>>>>>>>>:+", gemma_lavorata.sex
    print ">>>>>>>>>>>>>>>>>>>>>>>>:+", gemma_grezza.sex()
    return False

# Questo serve per debug, se si fa uno shake al mob si resetta la special
# senza dover rebottare tutte le sante volte
def after_shake(player, target, argument):
    del(target.specials["work_with"])
