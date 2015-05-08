# -*- coding: utf-8 -*-

#= IMPORT ======================================================================

import random

from src.enums import TO


#= COSTANTI ====================================================================

provacolore = ["un [red]dado[close] da gioco",
               "un [yellow]dado[close] da gioco",
               "un [orange]dado[close] da gioco",
               "un [green]dado[close] da gioco",
               "un [blue]dado[close] da gioco",
               "un [violet]dado[close] da gioco"]


#= FUNZIONI ====================================================================

def after_inject(coin, location):
    print " novizi2_item_dado >>>>>>inject<<<<<<"
    item.short = random.choice(provacolore)
#- Fine Funzione -


def on_booting(item):
    print " novizi2_item_dado >>>>>>booting<<<<<<"
    item.short = random.choice(provacolore)
#- Fine Funzione -


def on_reset(item):
    print " novizi2_item_dado >>>>>>reset<<<<<<"
    item.short = random.choice(provacolore)
#- Fine Funzione -


def before_dropped(entity, dice, room, behavioured):
    # Rimuovo un'occorrenza di dice prima del roll, altrimenti nel qual caso vi
    # siano più dadi ammucchiati tra di loro tutti avrebbero la stessa long
    dice = dice.from_location(1)
    dice.to_location(room)
    roll(dice)

    entity.act("Fai rotolare $N.", TO.ENTITY, dice)
    entity.act("$n fa rotolare te povero $N.", TO.TARGET, dice)
    entity.act("$n fa rotolare $N.", TO.OTHERS, dice)
    return True
#- Fine Funzione -


def after_inject(dice, room):
    dice.long = "C'è qui nuovo di zecca $N ancora nel suo cellophane"
#- Fine Funzione -


def on_reset(dice):
    roll(dice)
#- Fine Funzione -


def roll(dice):
    dice_launch_events = ["ha segnato un misero [red]UNO[close]...",
                          "segna [red]UNO[close].",
                          "indica il numero [red]1[close]!",
                          "ha fatto [orange]DUE[close].",
                          "non s'è sforzato molto, segna [orange]DUE[close].",
                          "indica il numero [orange]2[close]!",
                          "segna [yellow]TRE[close].",
                          "segna [yellow]TRE[close].",
                          "indica il numero [yellow]3[close]!",
                          "segna un dignitoso [green]Quattro[close].",
                          "segna un [green]Quattro[close].",
                          "indica il numero [green]4[close]!",
                          "ha fatto [blue]CINQUE[close].",
                          "ha quasi fatto il suo dovere... [blue]CINQUE[close].",
                          "indica il numero [blue]5[close]!",
                          "ha fatto [violet]SEI[close]!",
                          "ha fatto il suo bravo dovere: [violet]SEI[close]!",
                          "indica il numero [violet]6[close]!",
                          None]

    unbalance_dice_events = ["è in bilico tra l'[red]uno[close] e il [orange]due[close].. tocca ritirarlo.",
                             "è in bilico tra l'[red]uno[close] e il [yellow]tre[close].. tocca ritirarlo.",
                             "è in bilico tra l'[red]uno[close] e il [green]quattro[close].. tocca ritirarlo.",
                             "è in bilico tra l'[red]uno[close] e il [blue]cinque[close].. tocca ritirarlo.",
                             "è in bilico tra il [violet]sei[close] e il [orange]due[close].. tocca ritirarlo.",
                             "è in bilico tra il [violet]sei[close] e il [yellow]tre[close].. tocca ritirarlo.",
                             "è in bilico tra il [violet]sei[close] e il [green]quattro[close].. tocca ritirarlo.",
                             "è in bilico tra il [violet]sei[close] e il [blue]cinque[close].. tocca ritirarlo.",
                             "è in bilico tra il [orange]due[close] e il [yellow]tre[close].. tocca ritirarlo.",
                             "è in bilico tra il [yellow]tre[close] e il [blue]cinque[close].. tocca ritirarlo.",
                             "è in bilico tra il [blue]cinque[close] e il [green]quattro[close].. tocca ritirarlo.",
                             "è in bilico tra il [green]quattro[close] e il due[close].. tocca ritirarlo."]

    dice_event = random.choice(dice_launch_events)
    if not dice_event:
        dice_event = random.choice(unbalance_dice_events)

    dice.long = "$N " + dice_event
#- Fine Funzione -
