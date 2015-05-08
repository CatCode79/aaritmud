# -*- coding: utf-8 -*-

"""
Serve a leggere dei libri o altri scritti.
"""

#= IMPORT ======================================================================

from src.color      import color_first_upper
from src.command    import get_command_syntax
from src.config     import config
from src.enums      import CONTAINER, DIR, EXTRA, OPTION, TO
from src.exit       import get_direction
from src.gamescript import check_trigger
from src.grammar    import add_article
from src.interpret  import multiple_search_on_inputs
from src.log        import log
from src.utility    import one_argument, is_number

if config.reload_commands:
    reload(__import__("src.commands.command_look", globals(), locals(), [""]))
    reload(__import__("src.commands.__senses__", globals(), locals(), [""]))
from src.commands.command_look import MESSAGES
from src.commands.__senses__ import sense_at_direction


#= COSTANTI ====================================================================

VERBS = {"infinitive" : "[sandybrown]leggere[close]",
         "you"        : "[sandybrown]leggi[close]",
         "it"         : "[sandybrown]legge[close]"}


#= FUNZIONI ====================================================================

def command_read(entity, argument="", verbs=VERBS, behavioured=False):
    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # -------------------------------------------------------------------------

    # È possibile se il comando è stato deferrato
    if not entity:
        return False

    entity = entity.split_entity(1)

    if not argument:
        entity.send_output("Che cosa vorresti %s?" % verbs["infinitive"])
        if entity.IS_PLAYER and OPTION.NEWBIE in entity.account.options:
            syntax = get_command_syntax(entity, "command_read")
            entity.send_output(syntax, break_line=False)
        return False

    arg1, argument = one_argument(argument)
    arg2, argument = one_argument(argument)
    location = None
    if not arg2:
        page_number = 0
    elif is_number(arg2):
        page_number = int(arg2)
    else:
        # Altrimenti cerca la locazione da cui leggere la extra o il readable
        page_number = 0
        if argument and is_number(argument):
            page_number = int(argument)
        location = entity.find_entity_extensively(arg2, inventory_pos="first")
        if not location:
            entity.act("Non riesci a trovare nessun [white]%s[close] da dove cercare di %s qualcosa." % (arg2, verbs["infinitive"]), TO.ENTITY)
            entity.act("$n sembra voler %s da qualcosa che non trova." % verbs["infinitive"], TO.OTHERS)
            return False

    if location:
        target = entity.find_entity(arg1, location=location)
    else:
        target = entity.find_entity_extensively(arg1, inventory_pos="first")
    if not target:
        result = read_extra_from_location(entity, location if location else entity.location, arg1, verbs, behavioured)
        # (TT) non dovrebbero servire queste righe perché ci pensa la fine
        # della read_extra_from_location, tuttavia ho un dubbio sulla
        # sense_at_direction e quindi mantengo le linee per un po' a vedere...
        #if not result:
        #    entity.act("Non riesci a trovare nessun [white]%s[close] da %s." % (arg1, verbs["infinitive"]), TO.ENTITY)
        #    entity.act("$n sembra voler %s qualcosa che non trova." % verbs["infinitive"], TO.OTHERS)
        return result

    if not target.readable_type:
        entity.act("Non trovi modo di poter %s $N" % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n non trova modo di poter %s $N" % verbs["infinitive"], TO.OTHERS, target)
        return False

    if page_number < 0:
        entity.act("Cerchi di %s pagine inesistenti di $N." % verbs["infinitive"], TO.ENTITY, target)
        entity.act("$n cerca di %s pagine inesistenti di $N" % verbs["infinitive"], TO.OTHERS, target)
        return False

    if page_number > len(target.readable_type.pages) - 1:
        entity.act("Puoi %s solo fino alla %d° pagina di $N." % (verbs["infinitive"], len(target.readable_type.pages)-1), TO.ENTITY, target)
        # E' voluto che qui il messaggio sia uguale a quello sopra, non è un copia e incolla selvaggio
        entity.act("$n cerca di %s pagine inesistenti di $N" % verbs["infinitive"], TO.OTHERS, target)
        return False

    output = target.readable_type.get_pages(entity, target, page_number, location)
    if not output:
        log.bug("Output ricavato dalle pagine per il comando read con entità %s e book %s non valido: %r" % (entity.code, target.code, output))
        return False

    force_return = check_trigger(entity, "before_read", entity, target, output, None, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "before_readed", entity, target, output, None, behavioured)
    if force_return:
        return True

    from_descr = ""
    if location:
        from_descr = " da %s" % location.get_name(looker=entity)

    # Invia un messaggio adeguato di azione
    previous_same_book  = False
    if entity.sended_inputs and len(entity.sended_inputs) > 2 and len(target.readable_type.pages) > 2 and page_number != 0 and page_number != len(target.readable_type.pages) - 1:
        last_input, last_argument = one_argument(entity.sended_inputs[-2])
        last_input, huh_input, language = multiple_search_on_inputs(entity, last_input)
        last_argument, last_page_argument = one_argument(last_argument)
        last_target = entity.find_entity(last_argument, location=entity)
        if last_input and last_input.command.function == command_read and last_target and last_target == target:
            previous_same_book = True
            if last_page_argument and is_number(last_page_argument):
                last_page_argument = int(last_page_argument)
                if page_number > last_page_argument:
                    entity.act("Sfogli $N%s in avanti." % from_descr, TO.ENTITY, target)
                    entity.act("$n sfoglia $N%s in avanti." % from_descr, TO.OTHERS, target)
                elif page_number < last_page_argument:
                    entity.act("Sfogli $N%s all'indietro." % from_descr, TO.ENTITY, target)
                    entity.act("$n sfoglia $N%s all'indietro." % from_descr, TO.OTHERS, target)
                else:
                    entity.act("Continui a %s $N%s." % (verbs["infinitive"], from_descr), TO.ENTITY, target)
                    entity.act("$n continua a %s $N%s." % (verbs["infinitive"], from_descr), TO.OTHERS, target)
            else:
                entity.act("Continui a %s $N%s." % (verbs["infinitive"], from_descr), TO.ENTITY, target)
                entity.act("$n continua a %s $N%s." % (verbs["infinitive"], from_descr), TO.OTHERS, target)

    # Se non ha trovato che sia stato inviato un comando uguale precedentemente
    # allora invia la messaggistica normale
    if not previous_same_book:
        if len(target.readable_type.pages) > 2:
            if page_number == 0:
                entity.act("%s la copertina di $N%s." % (color_first_upper(verbs["you"]), from_descr), TO.ENTITY, target)
                entity.act("$n %s la copertina di $N%s." % (verbs["it"], from_descr), TO.OTHERS, target)
            elif page_number == 1:
                entity.act("Cominci a %s $N%s." % (verbs["infinitive"], from_descr), TO.ENTITY, target)
                entity.act("$n comincia a %s $N%s." % (verbs["infinitive"], from_descr), TO.OTHERS, target)
            elif page_number == len(target.readable_type.pages) - 1:
                entity.act("%s la retrocopertina di $N%s." % (color_first_upper(verbs["you"]), from_descr), TO.ENTITY, target)
                entity.act("$n %s la retrocopertina di $N%s." % (verbs["it"], from_descr), TO.OTHERS, target)
            else:
                entity.act("%s $N%s." % (color_first_upper(verbs["you"]), from_descr), TO.ENTITY, target)
                entity.act("$n %s $N%s." % (verbs["it"], from_descr), TO.OTHERS, target)
        else:
            entity.act("%s $N%s." % (color_first_upper(verbs["you"]), from_descr), TO.ENTITY, target)
            entity.act("$n %s $N%s." % (verbs["it"], from_descr), TO.OTHERS, target)

    # Visualizza la o le pagine dell'entità leggibile al lettore
    entity.send_output(output)

    # Dona un po' di esperienza ai giocatori che leggono per la prima
    # volta il libro
    if entity.IS_PLAYER:
        if target.prototype.code in entity.readed_books:
            entity.readed_books[target.prototype.code] += 1
        else:
            entity.readed_books[target.prototype.code] = 1
            reason = "per aver letto per la prima volta %s" % target.get_name(looker=entity)
            entity.give_experience(target.level * 10, reason=reason)

    force_return = check_trigger(entity, "after_read", entity, target, output, None, behavioured)
    if force_return:
        return True
    force_return = check_trigger(target, "after_readed", entity, target, output, None, behavioured)
    if force_return:
        return True

    return True
#- Fine Funzione -


def read_extra_from_location(entity, location, extra_argument, verbs, behavioured):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return False

    if not location:
        log.bug("location non è un parametro valido: %r" % location)
        return False

    if not extra_argument:
        log.bug("extra_argument non è un parametro valido: %r" % extra_argument)
        return False

    if not verbs:
        log.bug("verbs non è un parametro valido: %r" % verbs)
        return False

    # behavioured ha valore di verità

    # -------------------------------------------------------------------------

    # Cerca un'eventuale extra leggibile nella locazione, prima in maniera esatta
    extra = location.extras.get_extra(extra_argument, exact=True)
    if extra and EXTRA.READABLE in extra.flags:
        if can_read(entity, location, verbs, extra):
            descr = extra.get_descr("", looker=entity, parent=entity)
            if descr:
                force_return = check_trigger(entity, "before_read", entity, entity.location, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_readed", entity, entity.location, descr, extra, behavioured)
                if force_return:
                    return True
                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if EXTRA.NO_LOOK_ACT not in extra.flags:
                    entity.act("$n legge %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS)
                force_return = check_trigger(entity.location, "after_read", entity, entity.location, descr, extra, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_readed", entity, entity.location, descr, extra, behavioured)
                if force_return:
                    return True
                return True

    # Gestisce il read in una direzione, prima in maniera esatta
    if extra_argument:
        direction = get_direction(extra_argument, True)
        if direction != DIR.NONE:
            return sense_at_direction(entity, direction, extra_argument, True, "read", "readed", "", MESSAGES, behavioured, "to_dir", readable=True)

    # Cerca un'eventuale extra leggibile nella locazione, ora in maniera prefissa
    extra = entity.location.extras.get_extra(extra_argument, exact=False)
    if extra and EXTRA.READABLE in extra.flags:
        if can_read(entity, location, verbs, extra):
            descr = extra.get_descr("", looker=entity, parent=entity)
            if descr:
                force_return = check_trigger(entity, "before_read", entity, entity.location, extra, descr, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "before_readed", entity, entity.location, extra, descr, behavioured)
                if force_return:
                    return True
                entity.send_output('''<div style="width:66%%">%s</div>''' % descr, break_line=False)
                if EXTRA.NO_LOOK_ACT not in extra.flags:
                    entity.act("$n legge %s." % add_article(extra.keywords.split()[0], GRAMMAR.INDETERMINATE), TO.OTHERS)
                force_return = check_trigger(entity.location, "after_read", entity, entity.location, extra, descr, behavioured)
                if force_return:
                    return True
                force_return = check_trigger(entity.location, "after_readed", entity, entity.location, extra, descr, behavioured)
                if force_return:
                    return True
                return True

    # Gestisce il read in una direzione, ora in maniera prefissa
    if extra_argument:
        direction = get_direction(extra_argument, exact=False)
        if direction != DIR.NONE:
            return sense_at_direction(entity, direction, extra_argument, False, "read", "readed", "", MESSAGES, behavioured, "to_dir", readable=True)

    if extra:
        entity.act("Guardi [white]%s[close] ma non vedi nulla di speciale da %s." % (extra_argument, verbs["infinitive"]), TO.ENTITY)
    else:
        entity.act("Non vedi nessun [green]%s[close] qui attorno da %s" % (extra_argument, verbs["infinitive"]), TO.ENTITY)
    entity.act("$n si guarda attorno alla ricerca di qualcuno o qualcosa che non trova", TO.OTHERS)
    return False
#- Fine Funzione -


def can_read(entity, location, verbs, extra):
    # (TD) in futuro al posto di utilizzare il contenitore bisogna dare la
    # possibilità di leggere anche da libri appoggiati sui mobili
    if EXTRA.INSIDE_CONTAINER in extra.flags:
        if not location.container_type:
            entity.act("Non ti sarà possibile %s nulla da $N non potendo contenere nulla." % verbs["infinitive"], TO.ENTITY, location)
            entity.act("$n sembra voler %s da $N ma ciò non gli è possibile poiché che non è un contenitore." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("$n sembra voler %s da te ma ciò non gli è possibile poiché che non è un contenitore." % verbs["infinitive"], TO.TARGET, location)
            return False
        if CONTAINER.CLOSED in location.container_type.flags:
            entity.act("Non ti sarà possibile %s nulla da $N non essendo aperto." % verbs["infinitive"], TO.ENTITY, location)
            entity.act("$n sembra voler %s da $N ma ciò non gli è possibile poiché che non è aperto." % verbs["infinitive"], TO.OTHERS, location)
            entity.act("$n sembra voler %s da te ma ciò non gli è possibile poiché che non è aperto." % verbs["infinitive"], TO.TARGET, location)
            return False

    # Qui arriva anche nel caso che non vi sia la flag INSIDE_CONTAINER
    return True
#- Fine Funzione -


def get_syntax_template(entity):
    if not entity:
        log.bug("entity non è un parametro valido: %r" % entity)
        return ""

    # -------------------------------------------------------------------------

    syntax = ""

    syntax += "read\n"
    syntax += "read <qualcosa>\n"
    syntax += "read <qualcosa> <di qualcosa o qualcuno>\n"
    syntax += "read <un particolare> <di qualcosa o qualcuno>\n"
    syntax += "read <un particolare> <di una direzione>\n"

    return syntax
#- Fine Funzione -
