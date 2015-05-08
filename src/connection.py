# -*- coding: utf-8 -*-

"""
Modulo per la gestione generica di una connessione al sito.
"""


#= IMPORT ======================================================================

import datetime

from twisted.internet import protocol

from src.config import config
from src.enums  import LOG, OPTION, TRUST
from src.log    import log


#= VARIABILI ===================================================================

# (TD) al posto di utilizzare le connessioni usare le sessions,
# attributi ereditato in questa classe, forse così risolto il problema
# delle connessioni
connections = {}  # Connessioni al sito


#= CLASSI ======================================================================

# (TD) Sbagliato! Devo inserire questi attributi nella Twisted Session al sito
class Connection(protocol.Protocol):
    """
    Questa classe serve a gestire le connessioni, e le relative sessioni, dei
    differenti Client al Mud.
    """
    def __init__(self):
        self.account              = None   # Account utilizzato
        self.new_player           = None   # Personaggio che si sta creando
        self.player               = None   # Personaggio in gioco
        self.session              = None   # Twisted Session
        self.request              = None   # Twisted Request
        self.ip                   = "None" # Ip del Client
        self.buffer               = ""     # Buffer con tutti l'output del gioco da inviare al client ad ogni richiesta ajax
        self.stop_buffering       = False  # Se impostato a valore di verità terminerà l'invio del buffer con una chiusura della sessione
        self.already_closed       = False  # Indica se è già stata chiusa la connessione
        self.defer_exit_from_game = None   # Deferred che si attiva quando il giocatore esce dal gioco
        self.logged_on            = datetime.datetime.now()  # Data e ora del login
    #- Fine Inizializzazione -

    def reinit(self):
        self.stop_buffering = False
        self.buffer         = ""
    #- Fine Metodo -

    def get_id(self, conn_looker=None):
        """
        Ritorna una o tutte tra le seguenti informazioni: l'ip della
        connessione, il nome dell'account e il nome del personaggio.
        Molto utile da utilizzare nei messaggi di log.
        Questo metodo fa a coppia con quello nella classe Account.
        """
        account_name = "None"
        player_name = "None"

        if self.account:
            account_name = self.account.name
        if self.player:
            player_name = self.player.code

        # Fa visualizzare l'IP completo solo a coloro che hanno abbastanza TRUST
        if not conn_looker or (conn_looker and conn_looker.account and conn_looker.account.trust >= TRUST.IMPLEMENTOR):
            return "%s %s.%s" % (self.ip, account_name, player_name)
        else:
            ip_number, port = self.ip.split(":")
            return "*.*.*.%s:%s %s.%s" % (ip_number.split(".")[3], port, account_name, player_name)
    #- Fine Metodo -

    # (TD) magari pensare di convertire queste stringhe identificative in
    # elementi di un'enumerazione
    def get_browser(self):
        """
        Ritorna un codice identificato del browser che il client sta utilizzando.
        Utile quando bisogna creare del codice xhtml ad uopo per un browser.
        """
        if (not self.request or not self.request.received_headers
        or not "user-agent" in self.request.received_headers):
            return ""

        user_agent = self.request.received_headers["user-agent"]
        if not user_agent:
            return ""

        browser = get_browser_from_ua(user_agent)
        if browser == "???":
            log.user_agent(self.request)

        return browser
    #- Fine Metodo -

    def get_os(self):
        """
        Ritorna un codice identificato del sistema operativo che il client
        sta utilizzando.
        """
        if (not self.request or not self.request.received_headers
        or not "user-agent" in self.request.received_headers):
            return ""

        user_agent = self.request.received_headers["user-agent"]
        if not user_agent:
            return ""

        operating_system = get_os_from_ua(user_agent)
        # Non vengono loggati solamente gli user agent sconosciuti ma anche
        # quelli generici, per veder se si riesce a carpire migliori
        # informazioni oppure semplicemente per curiosità
        if operating_system in ("???", "WINDOWS", "LINUX", "MAC", "MOBILE"):
            log.user_agent(self.request)

        return operating_system
    #- Fine Metodo -

    def get_user_agent(self):
        if not self.request:
            return ""
        if not self.request.received_headers:
            return ""
        if not "user-agent" in self.request.received_headers:
            return ""
        if not self.request.received_headers["user-agent"]:
            return ""

        return self.request.received_headers["user-agent"]
    #- Fine Metodo -

    def close_game_request(self):
        """
        Callback che serve a chiudere un'eventuale connessione alla pagina di
        gioco ancora aperta quando la sessione web relativa all'account scade.
        """
        if not self.player:
            return

        if not self.account or OPTION.COMET not in self.account.options:
            self.player.exit_from_game(True)

        if not self.player or not self.player.game_request:
            return

        log.conn("Chiusura della connessione al gioco: %s" % self.get_id())
        try:
            self.player.game_request.finish()
        except UserWarning:
            pass
        if self.player:
            self.player.game_request = None

        self.player = None
    #- Fine Metodo -


#= FUNZIONI ====================================================================

def close_all_connections():
    for conn in reversed(connections.values()):
        conn.close_game_request()
#- Fine Metodo -


def get_browser_from_ua(user_agent):
    if not user_agent:
        log.bug("user_agent non è un parametro valido: r" % user_agent)
        return ""

    # -------------------------------------------------------------------------

    if "MSIE " in user_agent:
        version = user_agent.split("MSIE")[1].split(".")[0]
        return "IE_" + version.strip()
    elif "Firefox/" in user_agent:
        version = user_agent.split("Firefox/")[1].split(".")[0]
        return "FIREFOX_" + version.strip()
    elif "Chrome/" in user_agent:
        version = user_agent.split("Chrome/")[1].split(".")[0]
        return "CHROME_" + version.strip()
    elif "Safari/" in user_agent:
        version = user_agent.split("Version/")[1].split(".")[0]
        return "SAFARI_" + version.strip()
    elif "Opera/" in user_agent:
        version = user_agent.split("Version/")[1].split(".")[0]
        return "OPERA_" + version.strip()
    elif "Iceweasel/" in user_agent:
        version = user_agent.split("Iceweasel/")[1].split(".")[0]
        return "FIREFOX_" + version.strip()
    elif "Kindle" in user_agent:
        versione = user_agent.split("Kindle/")[1].split(".")[0]
        return "KINDLE_" + version.strip()
    elif "Links (2" in user_agent:
        return "LINKS_2"
    elif "ELinks/0" in user_agent:
        return "ELINKS_0"

    return "???"
#- Fine Funzione -


def get_os_from_ua(user_agent):
    if not user_agent:
        log.bug("user_agent non è un parametro valido: r" % user_agent)
        return ""

    # -------------------------------------------------------------------------

    if "Windows NT 6.1" in user_agent:
        return "WINDOWS_SEVEN"
    elif "Windows NT 6.0" in user_agent:
        return "WINDOWS_VISTA"
    elif "Windows NT 5.2" in user_agent:
        return "WINDOWS_2003"
    elif "Windows NT 5.1" in user_agent:
        return "WINDOWS_XP"
    elif "Windows NT 5.0" in user_agent:
        return "WINDOWS_2000"
    elif "Windows" in user_agent:
        return "WINDOWS"
    elif "Ubuntu" in user_agent:
        return "LINUX_UBUNTU"
    elif "Sabayon" in user_agent:
        return "LINUX_SABAYON"
    elif "CentOS" in user_agent:
        return "LINUX_CENTOS"
    elif "Linux" in user_agent:
        return "LINUX"
    elif "OS X" in user_agent:
        return "MAC_OSX"
    elif "Macintosh" in user_agent:
        return "MAC"
    elif "Mobile" in user_agent:
        if "Android" in user_agent:
            return "MOBILE_ANDROID"
        else:
            return "MOBILE"

    return "???"
#- Fine Funzione -
