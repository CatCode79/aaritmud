# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina che serve a testare gli inputs.
"""


#= IMPORT ======================================================================

import random
import string
import sys
import time
import traceback

from twisted.internet import reactor

from src.color        import remove_colors
from src.config       import config
from src.database     import database
from src.engine       import engine
from src.enums        import TRUST
from src.interpret    import inputs_command_it, inputs_command_en
from src.web_resource import WebResource


#= COSTANTI ====================================================================

LETTERS = " qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMòàùèéìÒÀÙÈÉÌ"
ACCENTS = ""
NUMBERS = ("1", "2", "3", "4", "5", "6", "7", "8", "9")


#= CLASSI ======================================================================

class TestInputsPage(WebResource):
    """
    Link che serve a testare casualmente tutti gli inputs in un'area creata al
    momento casualmente.
    """
    TITLE = "Test Inputs"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE         = string.Template(open("src/views/test_inputs.view").read())
    #AFTER_SUBMIT_TEMPLATE = string.Template(open("src/views/test_inputs_submit.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        disabled = ""
        if engine.test_inputs_mode:
            disabled = ''' disabled="disabled"'''

        mapping = {"game_name"         : config.game_name,
                   "game_name_nocolor" : remove_colors(config.game_name),
                   "disabled"          : disabled}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if engine.options.mode == "official":
            return '''<span style="colors:royalblue">Per evitare utilizzi erronei di tale pagina è impossibile eseguire il test sugli inputs su una instanza di %s avviata come modalità official.</span>'''

        if engine.test_inputs_mode:
            return '''<span style="colors:royalblue">È già stato avviato un test degli inputs.</span>'''

        engine.test_inputs_mode = True
        #time_start = time.time()

        for area in database["areas"].itervalues():
            for entity in area.iter_contains():
                self.test_inputs(entity)

        for player in database["players"].itervalues():
            if not player.location and (not player.previous_location or not player.previous_location()):
                player.enter_in_game()
                self.test_inputs(player)

        # Una volta terminato tutto esce evitando di salvare le persistenze
        reactor.stop()
        sys.exit(0)
    #- Fine Metodo -

    def test_inputs(self, entity):
        # I social funzionano tutti allo stesso modo, quindi è inutile controllarli
        input = random.choice(inputs_command_en + inputs_command_it)
        if input.command.trust > TRUST.PLAYER and entity.trust <= TRUST.PLAYER:
            return
        input_word = random.choice(input.words.split())
        self.test_input(entity, input.command)
        for arg1 in self.create_test_arguments():
            self.test_input(entity, input.command, arg1)
            for arg2 in self.create_test_arguments():
                self.test_input(entity, input.command, "%s %s" % (arg1, arg2))
    #- Fine Metodo -

    def create_test_arguments(self):
        argument = "".join(random.sample(LETTERS, config.min_len_name+2))
        for len in xrange(1, config.min_len_name+2):
            arg = argument[ : len].strip()
            if not arg: 
                continue
            yield arg
        yield "%s.%s" % (random.choice(NUMBERS), argument.strip())
    #- Fine Metodo -

    def test_input(self, entity, command, argument=""):
        # Scrive su console da attivare in caso di test sugli argomenti
        #print command.fun_name.split("_")[1], argument

        # Viene utilizzata la command.function invece della send_input così
        # eventuali traceback sono più facili da decifrare
        try:
            command.function(entity, argument)
        except:
            return '''<span style="colors:red">%s</span>''' % traceback.format_exc()
    #- Fine Metodo -
