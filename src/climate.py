# -*- coding: utf-8 -*-

"""
Gestione delle condizioni meteo del Mud.
"""

# Ogni area ha la sua tipologia di climate suddivisa in 4 stagioni
# Viene fatta una media-random tra clima generale della wild (calcolato a
# seconda della fascia climatica e dell'altitudine) e clima dell'area
# Alcune cose le prenderò dal sistema meteo di Xandra


#= IMPORT ======================================================================

from src.element import Element
from src.enums   import DIR, COLOR, SEASON
from src.log     import log


#= CLASSI ======================================================================

class Climate(object):
    """
    Gestisce le informazioni climatiche di un'area.
    """
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {"temperature" : ("", "temperature"),
                    "cloud"      : ("", "percent"),
                    "humidity"   : ("", "percent"),
                    "fog"        : ("", "percent"),
                    "rain"       : ("", "percent"),
                    "hail"       : ("", "percent"),
                    "snow"       : ("", "percent"),
                    "lightning"  : ("", "percent")}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self, season=SEASON.NONE):
        self.season         = Element(season)
        self.temperature    = 17  # In gradi centigradi
        self.wind_direction = Element(DIR.NONE)  # Direzione del vento
        self.cloud_color    = Element(COLOR.NONE)  # Colore delle nuvole
        self.cloud          = 25  # Densità delle nuvole del cielo: 0 è limpido, 100 è completamente coperto
        self.humidity       = 20  # Umidità nell'aria: 0 deserto secco, 100 foresta pluviale
        self.fog            = 10  # Probabilità che vi sia la nebbia, da 0 a 100
        self.rain           = 15  # Probabilità che piova, da 0 a 100 (se la temperatura è bassa si tramuta in neve)
        self.hail           = 2   # Probabilità che grandini, da 0 a 100
        self.snow           = 3   # Probabilità che nevichi
        self.lightning      = 5   # Probabilità che tuoni e fulmini, da 0 a 100
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s: %s" % (super(Climate, self).__repr__, self.climate)
    #- Fine Metodo -

    def get_error_message(self):
        """
        Controlla l'integrità degli attributi della istanza.
        """
        if self.season.get_error_message(SEASON, "season") != "":
            msg = self.season.get_error_message(SEASON, "season")
        elif self.temperature < -273 or self.temperature > 10000:
            msg = "temperatura del clima errata: %d" % self.temperature
        elif self.wind_direction.get_error_message(DIR, "wind_direction") != "":
            msg = self.wind_direction.get_error_message(DIR, "wind_direction")
        elif self.cloud_color.get_error_message(COLOR, "cloud_color") != "":
            msg = self.cloud_color.get_error_message(COLOR, "cloud_color")
        elif self.cloud < 0 or self.cloud > 100:
            msg = "probabilità di nuvolosità errata: %d" % self.cloud
        elif self.humidity < 0 or self.humidity > 100:
            msg = "probabilità di umidità errata: %d" % self.humidity
        elif self.fog < 0 or self.fog > 100:
            msg = "probabilità di nebbia errata: %d" % self.fog
        elif self.rain < 0 or self.rain > 100:
            msg = "probabilità di pioggia errata: %d" % self.rain
        elif self.hail < 0 or self.hail > 100:
            msg = "probabilità di grandine errata: %d" % self.hail
        elif self.snow < 0 or self.snow > 100:
            msg = "probabilità di nevicate errata: %d" % self.snow
        elif self.lightning < 0 or self.lightning > 100:
            msg = "probabilità dei tempeste con fulmini errata: %d" % self.lightning
        else:
            return ""

        log.error("(Meteo: repr %s) %s" % (repr(self), msg))
        return msg
    #- Fine Metodo -


class Meteo(object):
    """
    Gestisce le informazioni meteo attuali in un'area.
    """

    def __init__(self):
        pass
    #- Fine Inizializzazione -

    def __repr__(self):
        # (TD)
        return "%s: " % (super(Meteo, self).__repr__)
    #- Fine Metodo -

    def is_raining_or_worse(self):
        # (TD)
        return False
    #- Fine Metodo -

    def get_error_message(self):
        # (TD)
        return ""
    #- Fine Metodo -
