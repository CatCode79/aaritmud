# -*- coding: utf-8 -*-

"""
Modulo riguardante la composizione di materiale e percentuale delle entità e
delle stanze.
"""

#= IMPORT ======================================================================

import copy
import pprint

from src.element  import Element
from src.enums    import MATERIAL
from src.database import fread_percent
from src.log      import log
from src.utility  import pretty_list, copy_existing_attributes


#= CLASSI ======================================================================

class MaterialPercentages(list):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __repr__(self):
        material_percentages = sorted(self, key=lambda material: material.percent, reverse=True)
        return pprint.pformat(material_percentages, indent=0)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = MaterialPercentages()

        for value in self:
            try:
                copied_value = value.copy()
            except:
                copied_value = copy.copy(value)
            to_obj.append(copied_value)

        return to_obj
    #- Fine Metodo -

    def equals(self, material_percentages2):
        if not self and material_percentages2:
            return False
        if self and not material_percentages2:
            return False

        if len(self) != len(material_percentages2):
            return False
        for value in self:
            for value2 in material_percentages2:
                if value.equals(value2):
                    break
            else:
                return False

        return True
    #- Fine Metodo -

    def get_error_message(self, entity):
        total = 0
        for material_percentage in self:
            msg = material_percentage.get_error_message()
            if msg:
                return "(material_percentages) %s" % msg
            total += material_percentage.percent

        if entity.IS_ITEM and total == 0:
            return "(material_percentages) gli oggetti devono obbligatoriamente avere definita l'etichetta MaterialPercentages almeno per un materiale."

        if len(self) > 0:
            if total != 100:
                return "(material_percentages) Totale in percentuale differente da 100: %d" % total

        return ""
    #- Fine Metodo -

    # -------------------------------------------------------------------------

    def get_descr(self):
        material_percentages = []
        for material_percentage in sorted(self, key=lambda material_percentage: material_percentage.percent, reverse=True):
            material_percentages.append(material_percentage.material)
        return pretty_list(material_percentages)
    #- Fine Metodo -

    def get_major_material(self):
        material_percentages = sorted(self, key=lambda material_percentage: material_percentage.percent, reverse=True)
        if material_percentages:
            return material_percentages[0].material
        else:
            return None
    #- Fine Metodo -


class MaterialPercentage(object):
    PRIMARY_KEY = ""
    VOLATILES   = []
    MULTILINES  = []
    SCHEMA      = {}
    REFERENCES  = {}
    WEAKREFS    = {}

    def __init__(self):
        self.material = Element(MATERIAL.NONE)
        self.percent  = 0
    #- Fine Inizializzazione -

    def __repr__(self):
        return "%s %s %s%%" % (super(MaterialPercentage, self).__repr__(), self.material, self.percent)
    #- Fine Metodo -

    def copy(self, to_obj=None, avoid_volatiles=False):
        if not to_obj:
            to_obj = MaterialPercentage()
        copy_existing_attributes(self, to_obj, avoid_volatiles=avoid_volatiles)
        return to_obj
    #- Fine Funzione -

    def equals(self, material2):
        if not material2:
            return False

        if self.material != material2.material:
            return False

        if self.percent != material2.percent:
            return False

        return True
    #- Fine Metodo -

    def get_error_message(self):
        if self.material.get_error_message(MATERIAL, "material", allow_none=False) != "":
            return self.material.get_error_message(MATERIAL, "material", allow_none=False)
        elif self.percent < 1 or self.percent > 100:
            return "percent dev'essere tra 1 e 100 e non %d" % self.percent

        return ""
    #- Fine Metodo -

    def fread_the_line(self, file, line, attr):
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not line:
            log.bug("line non è un parametro valido: %r" % line)
            return

        if not attr:
            log.bug("attr non è un parametro valido: %r" % attr)
            return

        # ---------------------------------------------------------------------

        if "," in line:
            material, percent = line.split(",", 1)
        else:
            material, percent = line.split(None, 1)

        material = material.strip()
        percent = percent.strip()

        self.material = Element(material)
        self.percent = fread_percent(file, percent, attr)
    #- Fine Metodo -

    def fwrite_the_line(self, file, label, indentation=""):
        """
        Scrive su file un elemento sinonimo.
        """
        if not file:
            log.bug("file non è un parametro valido: %r" % file)
            return

        if not label:
            log.bug("label non è un parametro valido: %r" % label)
            return

        # -------------------------------------------------------------------------

        file.write("%s%s%s %s%%\n" % (indentation, label, self.material.code, self.percent))
    #- Fine Metodo -
