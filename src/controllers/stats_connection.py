# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che visualizza le statistiche relative
alle connessioni al sito o al gioco stesso.
"""


#= IMPORT ======================================================================

import json
import string
import time

from src.config       import config
from src.enums        import TRUST
from src.log          import log
from src.web_resource import WebResource


#= CLASSI ======================================================================

class StatsConnectionPage(WebResource):
    """
    Pagina web per la visualizzazione delle stastistiche delle connessioni.
    """
    TITLE = "Statistiche Connessioni"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/stats_connection.view").read())

    def render_GET(self, request, conn):
        local_data  = []
        server_data = []

        connections_path = "log/connections.stat"
        try:
            connections_file = open(connections_path, "r")
        except IOError:
            mapping = {"local_data"  : "[0,0]",
                       "server_data" : "[0,0]"}
            return self.PAGE_TEMPLATE.safe_substitute(mapping)

        # (TD) in attesa di fare la pagina
        mapping = {"local_data"  : "[0,0]",
                   "server_data" : "[0,0]"}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)

        previous_seconds = 0
        for line in connections_file:
            line = line.strip()
            if not line:
                continue
            if line[0] == "#":
                continue

            # Ricava e pulisce le informazioni dalla linea del file
            version, pid, date, local_cpu, server_cpu = line.split(";")
            version    = version.strip()
            pid        = pid.strip()
            date       = date.strip()
            local_cpu  = local_cpu.strip()
            server_cpu = server_cpu.strip()

            # Controlla la validità dei valori ricavati
            tm = time.strptime(date, "%Y-%m-%d %H:%M:%S")
            if not tm:
                log.bug("date ricavata dalla linea %s del file %s non è valida: %s" % (line, connections_path, date))
                continue

            try:
                local_cpu = float(local_cpu)
            except ValueError:
                log.bug("local_cpu ricavato dalla linea %s del file %s non è valida: %s" % (line, connections_path, local_cpu))
                continue

            try:
                server_cpu = float(server_cpu)
            except ValueError:
                log.bug("server_cpu ricavato dalla linea %s del file %s non è valida: %s" % (line, connections_path, server_cpu))
                continue

            # (TD) inserire delle linee verticali che indicano nel grafico
            # quando vi sia stato un riavvio o un cambio di release tramite
            # le informazioni della version e del pid

            # Inserisce dei buchi di informazione delle ore non loggate
            seconds = int(time.mktime(tm)) * 1000
            if previous_seconds != 0:
                while seconds - previous_seconds > 3600000:
                    previous_seconds += 3600000
                    local_data.append([previous_seconds, None])
                    server_data.append([previous_seconds, None])
            previous_seconds = seconds

            # Aggiunge la data e i valori per creare i dati
            local_data.append([seconds, local_cpu])
            server_data.append([seconds, server_cpu])

        mapping = {"local_data"  : json.dumps(local_data,  separators=(',',':')),
                   "server_data" : json.dumps(server_data, separators=(',',':'))}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -
