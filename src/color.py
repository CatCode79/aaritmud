# -*- coding: utf-8 -*-

"""
Modulo per la gestione degli attributi di formattazione testuali, simili al CSS,
all'interno delle stringhe inviate dal Mud.
La differenza maggiore è che queste regole di stile sono incluse tra le
parentesi quadre.

Esempio:
[red]S[yellow]pada
Verrà convertito in:
<span style="color:red">S</span><span style="color:yellow">pada</span>

Si possono anche inserire delle regole di stile con l'attributo class
Esempio:
[class=mystyle]Magia
Verrà convertito in:
<span class:mystyle>Magia</span>
Laddove mystyle è definita in un foglio di stile css o nel file html inviato
al browser client.

Se capitasse un caso in cui si voglia chiudere il tag delle regole di stile
prima della fine della stringa, bisogna inserire [close]
Esempio:
Una [white]luce soffusa[close] illumina la tua spada
Risulterà:
Una <span style='color:white'>luce soffusa</span> illumina la tua spada

La lista degli attributi supportati è nel dizionario supported_attributes.
Ogni attributo ha delle limitazioni per non dare la possibilità di abusarne
l'utilizzo creando degli output troppo caotici.
"""


#= IMPORT ======================================================================

import re

from src.enums import COLOR
from src.log   import log


#= VARIABILI ===================================================================

# Lista dei colori inizializzata a runtime partendo dall'enumerazione dei colori
colors = []
for element in COLOR.elements:
    color = element.code.lower()
    colors.append(color.split(".")[1])

# Attributi e valori d'attributo supportati per le regole di
# stile inseribili tra le parentesi quadre
supported_attributes = {
    # Relativamente al colore del testo
    "color"            : colors,
    "background-color" : colors + ["trasparent"],
    # Non sono attributi validi del CSS ma servono nella funzione convert_colors:
    "close"            : (""),
    "class"            : ("")}


#= REGEX =======================================================================

colors_expression = r"\[close\]|"
colors_no_close_expression = r""
#colors_reverse_expression = r".*\[close\]|"  # (bb)
#colors_no_close_reverse_expression = r".*"  # (bb)

for color in colors:
    colors_expression += r"\[%s\]|" % color
    colors_no_close_expression += r"\[%s\]|" % color
    #colors_reverse_expression += r"\[%s\]|" % color
    #colors_no_close_reverse_expression += r"\[%s\]|" % color

COLORS_PATTERN                   = re.compile(colors_expression.rstrip("|"))
COLORS_NO_CLOSE_PATTERN          = re.compile(colors_no_close_expression.rstrip("|"))
#COLORS_REVERSE_PATTERN          = re.compile(colors_reverse_expression.rstrip("|"))
#COLORS_NO_CLOSE_REVERSE_PATTERN = re.compile(colors_no_close_reverse_expression.rstrip("|"))


#= FUNZIONI ====================================================================

def _find_color(argument, position):
    """
    Cerca nell'argomento una regola di stile tra parentesi quadre.
    Ritorna una tupla con la posizione della quadra aperta, poi la posizione
    di quella chiusa e infine il testo con la regola di stile senza le
    parentesi quadre.
    Si può eseguire una ricerca da fine stringa passando reverse a True, ciò
    è utile quando bisogna controllare che l'ultimo stile di una stringa sia
    stato chiuso o meno con [close].
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return (-1, -1, "")

    if position < 0 or position > len(argument):
        log.bug("position non è un parametro valido: %r" % position)
        return (-1, -1, "")

    # -------------------------------------------------------------------------

    # Cerca la posizione della quadra di apertura stile
    bracket_open = -1
    if "[" in argument:
        bracket_open = argument.find("[", position)
    if bracket_open == -1:
        return (-1, -1, "")

    # Cerca la posizione della quadra di chiusura stile
    bracket_close = -1
    if "]" in argument:
        bracket_close = argument.find("]", bracket_open)
    if bracket_close == -1:
        return (-1, -1, "")

    # Ricava un'eventuale stile e controlla che inizi correttamente
    style = argument[bracket_open+1 : bracket_close].strip().lower()
    if not style:
        return (bracket_open, bracket_close, "")

    if style == "close":
        return (bracket_open, bracket_close, style)
    if style in colors:
        return (bracket_open, bracket_close, style)

    # Se non ha trovato nessun colore valido allora cerca tra gli attributi
    for attribute in supported_attributes:
        if style.startswith("%s:" % attribute):
            return (bracket_open, bracket_close, style)

    return (bracket_open, bracket_close, "")
#- Fine Funzione -


def _rfind_color(argument, position):
    """
    Cerca nell'argomento una regola di stile tra parentesi quadre.
    Ritorna una tupla con la posizione della quadra aperta, poi la posizione
    di quella chiusa e infine il testo con la regola di stile senza le
    parentesi quadre.
    Si può eseguire una ricerca da fine stringa passando reverse a True, ciò
    è utile quando bisogna controllare che l'ultimo stile di una stringa sia
    stato chiuso o meno con [close].
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return (-1, -1, "")

    if position < 0 or position > len(argument):
        log.bug("position passato non un parametro è valido: %r" % position)
        return (-1, -1, "")

    # -------------------------------------------------------------------------

    # Cerca la posizione della quadra di apertura stile
    bracket_open = -1
    if "[" in argument:
        bracket_open = argument.rfind("[", position)
    if bracket_open == -1:
        return (-1, -1, "")

    # Cerca la posizione della quadra di chiusura stile
    bracket_close = -1
    if "]" in argument:
        bracket_close = argument.rfind("]", bracket_open)
    if bracket_close == -1:
        return (-1, -1, "")

    # Ricava un'eventuale stile e controlla che inizi correttamente
    style = argument[bracket_open+1 : bracket_close].strip().lower()
    if not style:
        return (bracket_open, bracket_close, "")

    if style == "close":
        return (bracket_open, bracket_close, style)
    if style in colors:
        return (bracket_open, bracket_close, style)

    # Se non ha trovato nessun colore valido allora cerca tra gli attributi
    for attribute in supported_attributes:
        if style.startswith("%s:" % attribute):
            return (bracket_open, bracket_close, style)

    return (bracket_open, bracket_close, "")
#- Fine Funzione -


def convert_colors(argument):
    """
    Converte tutte le regole di stile entro le quadre in linguaggio html.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if "[" not in argument:
        return argument

    # Per ogni quadra controlla che la prima parola sia un attributo supportato,
    # se sì procede alla conversione con il tag <mudcolor> inserendovi tutto
    # ciò che è stato trovato fino alla prossima parentesi quadra chiusa
    position = 0
    result = []
    tag_is_open = False
    while 1:
        bracket_open, bracket_close, style = _find_color(argument, position)
        if not style:
            if bracket_open == -1 and bracket_close == -1:
                result.append(argument[position : ])
                break
            else:
                result.append(argument[position : bracket_close+1])
                position = bracket_close + 1
                continue

        # Copia in result la parte fino alla parentesi quadra aperta
        result.append(argument[position : bracket_open])

        # La regola di stile close serve a forzare la chiusura del tag <mudcolor>
        if style == "close":
            if tag_is_open:
                result.append("</span>")
            else:
                # (TD) questo messaggio qui è spammoso, devo spostarlo
                # piuttosto nella check_colors
                pass
                #safe_colored_string = argument.replace("[", "{").replace("]", "}")
                #note1 = "(oppure possibile colore precedente a questo stile dimenticato o scorretto)"
                #note2 = "(attenzione qui converto le parentesi quadre con delle grafe per evitare ricorsioni di log)"
                #log.bug("regola di stile {close} dove non serve: %s %s %s" % (safe_colored_string, note1, note2))
            tag_is_open = False
        # Altrimenti procede alla conversione dell'attributo nel risultato
        else:
            if tag_is_open:
                result.append("</span>")
            if ":" not in style or style[ : 6] == "color:":
                if ":" not in style:
                    color_name = style
                else:
                    color_name = style[len("color:") : ].strip()
                enum_element = getattr(COLOR, color_name.upper())
                result.append("<span style='color:%s;'>" % (enum_element.hex_code))
            elif style[ : 6] == "class:":
                result.append("<span class='%s'>" % style.remove("class:").strip())
            else:
                result.append("<span style='%s'>" % style)
            tag_is_open = True
        # Imposta la nuova posizione da dove controllare
        position = bracket_close + 1

    # Ritorna il risultato chiudendo prima il tag di mudcolor se serve
    if tag_is_open:
        result.append("</span>")

    return "".join(result)
#- Fine Funzione -


# (TT) (TD) da finire, controllare e/o sostituire con le regex
def check_colors(argument):
    """
    Controlla la validità degli stili css in una stringa.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return False

    # -------------------------------------------------------------------------

    if "[" not in argument:
        return True

    last_style = ""  # ultimo stile controllato
    position = 0  # posizione di lettura corrente dell'argomento
    last_close_bracket = -2  # posizione della quadra di chiusura dell'ultimo stile [close] trovato
    while 1:
        bracket_open, bracket_close, style = _find_color(argument, position)
        if not style:
            if bracket_open == -1 and bracket_close == -1:
                break
            else:
                # (TD) qui ci vuole una funzione di soundex per trovare
                # eventuali colori scritti scorrettamente
                position = bracket_close
                continue
        last_style = style

        # Salta l'attributo close e class
        if (style == "close" or style[ : 6] == "class:"
        or  ":" in style and style[ : style.find(":")] not in supported_attributes):
            position = bracket_close
            continue

        # Se la prima parola dello stile non è un attributo supportato lo salta
        if (":" in style and style[ : style.find(":")] not in supported_attributes
        or  ":" not in style and style not in colors):
            position = bracket_close
            continue

        # Controlla che lo stile di chiusura [close] non si trovi subito prima
        # di un nuovo stile; anche se corretto, sarebbe uno spreco inutile
        if last_close_bracket == bracket_open - 1:
            log.bug("style [close] di troppo trovato poco prima un altro stile in: %s" % argument)
            return False
        if style == "close":
            last_close_bracket = bracket_close

        # (TD) Controlla, nel caso che vi siano due stili consecutivi, uno per il
        # colore del testo e l'altro per il background, che tali due colori
        # non siano uguali, altrimenti sarebbe impossibile leggere il testo.

        # (TD) Controlla che non vi siano attributi doppi nello stesso stile

        # Controlla tutti gli attributi del singolo stile
        for attr in style.split(";"):
            if ":" in attr:
                attr, value = attr.split(":")
                attr = attr.strip()
                value = value.strip()
            else:
                value = attr
                value = value.strip()
                attr = "color"

            if attr not in supported_attributes:
                log.bug("stile %s con attributo %s errato" % (style, attr))
                return False
            if value not in supported_attributes[attr]:
                log.bug("stile %s ha un attributo con valore errato: %s" % (style, value))
                return False

        # Finito di controllare questo stile imposta la posizione alla
        # parentesi chiusa
        position = bracket_close

    # Controlla che l'ultimo stile sia quello di chiusura
    #last_style = _rfind_color(argument, 0)[2]
    if last_style != "close" and get_first_color(argument):
        log.bug("stringa con uno stile non chiuso: %s (%s)" % (last_style, argument))
        return False

    # Se non ha trovato errori 'potrebbe' essere tutto a posto
    return True
#- Fine Funzione -


def remove_colors(argument):
    """
    Rimuove tutti gli stili dall'argomento passato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if "[" not in argument:
        return argument

    return COLORS_PATTERN.sub("", argument)
#- Fine Funzione -


def close_color(argument):
    """
    Se nell'argomento passato trova uno stile CSS e questo non è chiuso alla
    fine della stringa, viene chiuso con l'attributo [close] e ritornato.
    Viene utilizzata soprattutto nell'editing online dei dati per chiudere
    automaticamente le stringhe con dello stile aperto.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if "[" not in argument:
        return argument

    matches = COLORS_PATTERN.findall(argument)
    if matches and matches[-1] != "[close]":
        return "".join((argument, "[close]"))

    return argument
#- Fine Funzione -


def get_first_color(argument):
    """
    Ricava e ritorna il primo codice di colore che trova nella stringa passata.
    Il colore viene ritornato con le parentesi quadre.
    Di solito questa funzione è utile da utilizzare sui nomi degli elementi
    delle enumerazioni.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if "[" not in argument:
        return ""

    match = COLORS_NO_CLOSE_PATTERN.search(argument)
    if match:
        return match.group()

    return ""
#- Fine Funzione -


def color_first_upper(argument):
    """
    Nel qual caso che la stringa contenga un colore all'inizio provvede a
    uppare il primo carattere che verrà realmente visualizzato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return ""

    # -------------------------------------------------------------------------

    if argument[0] != "[":
        return "".join((argument[0].upper(), argument[1 : ]))

    match = COLORS_PATTERN.match(argument)
    if match:
        try:
            return "".join((match.group(), argument[match.end()].upper(), argument[match.end()+1 : ]))
        except IndexError:
            log.bug("IndexError per l'argomento %s e match.end() a %d" % (argument, match.end()))
            return argument
    else:
        return "".join((argument[0].upper(), argument[1 : ]))
#- Fine Funzione -


def color_first_lower(argument):
    """
    Nel qual caso che la stringa contenga un colore all'inizio provvede a
    loware il primo carattere che verrà realmente visualizzato.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    if argument[0] != "[":
        return "".join((argument[0].lower(), argument[1 : ]))

    match = COLORS_PATTERN.match(argument)
    if match:
        return "".join((match.group(), argument[0].lower(), argument[1 : ]))
    else:
        return "".join((argument[0].lower(), argument[1 : ]))
#- Fine Funzione -


def count_colors(argument):
    """
    Ritorna il numero di colori trovati nella stringa passata come argomento.
    """
    if not argument:
        log.bug("argument non è un parametro valido: %r" % argument)
        return

    # -------------------------------------------------------------------------

    counter = 0
    position = 0
    while 1:
        bracket_open, bracket_close, style = _find_color(argument, position)
        print bracket_open, bracket_close, style
        if bracket_open == -1 and bracket_close == -1:
            break
        if style and style != "close":
            counter += 1
        position = position = bracket_close + 1

    return counter
#- Fine Funzione -


def colors_to_html(text):
    """
    Permette di rendere leggibili i css lato web senza convertirli in span.
    """
    if not text:
        log.bug("text non è un parametro valido: %r" % text)
        return ""

    # -------------------------------------------------------------------------

    if "[" in text:
        text = text.replace("[", "&#91;")
    if "]" in text:
        text = text.replace("]", "&#93;")

    return text
#- Fine Funzione -
