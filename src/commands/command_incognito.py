# -*- coding: utf-8 -*-


#= IMPORT ======================================================================

from src.command  import get_command_syntax
from src.database import database
from src.enums    import LOG, TRUST
from src.log      import log
from src.player   import search_online_player
from src.utility  import is_same


#= FUNZIONI ====================================================================

def command_incognito(entity, argument=""):
    """
    Forza l'esecuzione di un comando da parte di un'altra entità.
    """
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    # -------------------------------------------------------------------------

    if not argument:
        syntax = get_command_syntax(entity, "command_incognito")
        entity.send_output(syntax, break_line=False)

        players = []
        for player in database["players"].itervalues():
            if player.incognito:
                players.append(player)

        mobs = []
        for mob in database["mobs"].itervalues():
            if mob.incognito:
                mobs.append(mob)

        items = []
        for item in database["items"].itervalues():
            if item.incognito:
                items.append(item)

        if not players and not mobs and not items:
            entity.send_output("Nessuna entità in incognito.")

        if players:
            entity.send_output("Giocatori in incognito:")
            for player in players:
                entity.send_output("- %s" % player.name)
            if mobs or items:
                entity.send_output("\n")

        if mobs:
            entity.send_output("Mob in incognito:")
            for mob in mobs:
                entity.send_output("- %s" % mob.name)
            if items:
                entity.send_output("\n")

        if items:
            entity.send_output("Oggetti in incognito:")
            for item in items:
                entity.send_output("- %s" % item.name)

        return True

    # -------------------------------------------------------------------------

    if entity.trust < TRUST.MASTER:
        entity.send_output("Solo gli [yellow]amministratori[close] di livello superiore a %s possono rendere [darkslategray]incognito[close] un personaggio qualsiasi." % TRUST.MASTER)
        return False

    # Cerca prima tra i giocatori online
    target = search_online_player(argument)
    if not target:
        target = entity.find_entity(argument, entity_tables=["players", "mobs", "items"])
        if not target:
            entity.send_output("Non esiste nessun'entità con argomento [green]%s[close]" % argument)
            return False

    if target.incognito:
        target.incognito = False
        if target == entity:
            entity.send_output("Esci dalle [royalblue]pieghe dimensionali[close] [red]a[gold]ariatiane[close] dell'incognito.")
            # Questo e il messaggio di log sotto non dovrebbero servire visto
            # che l'incognito viene effettuato senza danni su se stessi (ovvero
            # volontariamente)
            #log.admin("%s esce dalle pieghe dimensionali aaritiane dell'incognito" % entity.name)
        else:
            entity.send_output("Fai uscire dalle [royalblue]pieghe dimensionali[close] [red]a[gold]ariatiane[close] dell'incognito %s." % target.get_name(entity))
            log.admin("%s fa uscire dalle pieghe dimensionali aaritiane dell'incognito %s" % (entity.name, target.name))
    else:
        target.incognito = True
        if target == entity:
            entity.send_output("Entri nelle [royalblue]pieghe dimensionali[close] [red]a[gold]ariatiane[close] dell'incognito.")
            #log.admin("%s entra nelle pieghe dimensionali aaritiane dell'incognito" % entity.name)
        else:
            entity.send_output("Fai entrare nalle [royalblue]pieghe dimensionali[close] [red]a[gold]ariatiane[close] dell'incognito %s." % target.get_name(entity))
            log.admin("%s fa entrare nelle pieghe dimensionali aaritiane dell'incognito %s" % (entity.name, target.name))

    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "incognito\n"
    syntax += "incognito <nome del giocatore>\n"

    return syntax
#- Fine Funzione -
