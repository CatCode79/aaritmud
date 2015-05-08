# -*- coding: utf-8 -*-

"""
Modulo per la gestione della pagina web che testa i social.
"""


#= IMPORT ======================================================================

import operator
import string

from src.color        import convert_colors, remove_colors
from src.database     import database
from src.element      import get_element_from_name
from src.enums        import RACE, TRUST
from src.player       import create_random_player
from src.utility      import is_number
from src.web_resource import WebResource


#= CLASSI ======================================================================

class ShowSocialsPage(WebResource):
    """
    Serve ad eseguire un test sui sociali.
    """
    TITLE = "Show Socials"

    ACCOUNT_MUST_EXIST_IN_GET  = True
    ACCOUNT_MUST_EXIST_IN_POST = True

    MINIMUM_TRUST_ON_GET  = TRUST.MASTER
    MINIMUM_TRUST_ON_POST = TRUST.MASTER

    PAGE_TEMPLATE = string.Template(open("src/views/show_socials.view").read())

    NEW_PAGE = True

    def render_GET(self, request, conn):
        race_options = ""
        for race in RACE.sort_playable_first():
            name = remove_colors(race.name.replace("$o", "o"))
            race_options += '''\t<option value="%s">%s</option>\n''' % (name, name)

        social_options = ""
        for social in sorted(database["socials"].values()):
            social_name = social.fun_name[len("social_") : ]
            social_options += '''\t<option value="%s">%s</option>\n''' % (social_name, social_name)

        mapping = {"race_options"   : race_options,
                   "social_options" : social_options}
        return self.PAGE_TEMPLATE.safe_substitute(mapping)
    #- Fine Metodo -

    def render_POST(self, request, conn):
        if "race" in request.args:
            return self.get_output_race(request.args["race"][0])
        elif "social" in request.args:
            return self.get_output_social(request.args["social"][0])
        else:
            return '''L'esecuzione del post non è andato a buon fine con la richiesta %r''' % request.args
    #- Fine Metodo -

    def get_output_race(self, choised_option):
        if not choised_option:
            return '''Non è stata selezionata nessuna razza valida.'''

        entity_race = get_element_from_name(RACE, choised_option)
        if not entity_race:
            return '''Non è stata trovata nessuna razza valida con %s''' % choised_option

        entity = create_random_player(race=entity_race)
        if not entity:
            return '''Creazione di entity random fallita'''

        target = create_random_player()
        if not target:
            return '''Creazione di target random fallita'''

        other = create_random_player()
        if not other:
            return '''Creazione di other random fallita'''

        outputs = []
        for social in sorted(database["socials"].values()):
            social_name = social.fun_name[len("social_") : ].capitalize()
            outputs.append("<tr><td colspan='2'><br>[white]%s[close] eseguito dalla razza %s</td></tr>" % (social_name, entity_race))
            outputs.append(self.get_racial_message_output(social, entity, None, other, "entity_no_arg", "EntityNoArg"))
            outputs.append(self.get_racial_message_output(social, entity, None, other, "others_no_arg", "OthersNoArg"))
            outputs.append(self.get_racial_message_output(social, entity, target, other, "entity_found", "EntityFound", "mio"))
            outputs.append(self.get_racial_message_output(social, entity, target, other, "others_found", "OthersFound", "suo"))
            outputs.append(self.get_racial_message_output(social, entity, target, other, "target_found", "TargetFound"))
            outputs.append(self.get_racial_message_output(social, entity, target, other, "entity_auto", "EntityAuto"))
            outputs.append(self.get_racial_message_output(social, entity, target, other, "others_auto", "OthersAuto"))

        return "%s%s%s" % ("<table>", convert_colors("".join(outputs)), "</table>")
    #- Fine Metodo -

    def get_output_social(self, choised_option):
        if not choised_option:
            return '''Non è stato selezionato nessun social valido.'''

        choised_option = "social_" + choised_option
        selected_social = None
        for social_code in database["socials"]:
            if social_code == choised_option:
                selected_social = database["socials"][social_code]
                break

        if not selected_social:
            return '''Non è stato trovato nessun social valido con indice %s''' % choised_option

        target = create_random_player()
        if not target:
            return '''Creazione di target random fallita'''

        other = create_random_player()
        if not other:
            return '''Creazione di other random fallita'''

        outputs = []
        for race in RACE.sort_playable_first():
            entity = create_random_player(race=race)
            if not entity:
                return '''Creazione di entity random fallita per la razza %s''' % race
            social_name = selected_social.fun_name[len("social_") : ].capitalize()
            outputs.append("<tr><td colspan='2'><br>[white]%s[close] eseguito dalla razza %s</td></tr>" % (social_name, race))
            outputs.append(self.get_racial_message_output(selected_social, entity, None, other, "entity_no_arg", "EntityNoArg"))
            outputs.append(self.get_racial_message_output(selected_social, entity, None, other, "others_no_arg", "OthersNoArg"))
            outputs.append(self.get_racial_message_output(selected_social, entity, target, other, "entity_found", "EntityFound", "mio"))
            outputs.append(self.get_racial_message_output(selected_social, entity, target, other, "others_found", "OthersFound", "suo"))
            outputs.append(self.get_racial_message_output(selected_social, entity, target, other, "target_found", "TargetFound"))
            outputs.append(self.get_racial_message_output(selected_social, entity, target, other, "entity_auto", "EntityAuto"))
            outputs.append(self.get_racial_message_output(selected_social, entity, target, other, "others_auto", "OthersAuto"))

        return "%s%s%s" % ("<table>", convert_colors("".join(outputs)), "</table>")
    #- Fine Metodo -

    def get_racial_message_output(self, social, entity, target, other, attribute, label, possessive=""):
        message = social.get_racial_message(entity, attribute, target, possessive, use_human=False)
        if message and "$" in message:
            message = entity.replace_act_tags(message, target=target)
            message = entity.replace_act_tags_name(message, looker=other, target=target)
        return "<tr><td>%s:</td><td>%s</td></tr>" % (label, message)
    #- Fine Metodo -
