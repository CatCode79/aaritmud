# -*- coding: utf-8 -*-

"""
Enumerazione della lista dei colori.
"""

#= IMPORT ======================================================================

from src.element import EnumElement, finalize_enumeration
from src.log     import log


#= VARIABILI ===================================================================

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = True


#= CLASSI ======================================================================

class ColorElement(EnumElement):
    def __init__(self, name, hex_code=""):
        super(ColorElement, self).__init__(name)
        if "[" in name:
            self.web_name = name[1 : name.find("]")]
        else:
            self.web_name = ""
        self.hex_code    = hex_code
        self.hair_color  = ""
        self.alternative = False
    #- Fine Inizializzazione -

    def get_error_messages(self):
        # controllare che il nome del colore sia conposto da caratteri alfa
        # controllare che il primo carattere dell'hexcode sia la # mentre il resto numerico
        pass
    #- Fine Metodo -

    def _sum_hex_numbers(self):
        if len(self.hex_code) == 7:
            first_hex  = int(self.hex_code[1 : 3], 16)
            second_hex = int(self.hex_code[3 : 5], 16)
            third_hex  = int(self.hex_code[5 : 7], 16)
        elif len(self.hex_code) == 4:
            first_hex  = int(self.hex_code[1 : 2] * 2, 16)
            second_hex = int(self.hex_code[2 : 3] * 2, 16)
            third_hex  = int(self.hex_code[3 : 4] * 2, 16)
        else:
            log.bug("hex_code non è un codice esadecimale di colore valido: %r per il colore %s" % (self.hex_code, self))
            return 0

        return first_hex + second_hex + third_hex
    #- Fine Metodo -

    def get_bg_style(self):
        """
        Ritorna lo stile css per i colori sullo sfondo, per quelli scuri
        utilizza il carattere bianco, mentre per quelli quelli chiari utilizza
        il carattere nero
        """
        if self._sum_hex_numbers() < 320:
            return "background-color:%s;color:white" % self.hex_code
        else:
            return "background-color:%s;color:black" % self.hex_code
    #- Fine Metodo -

    def _get_color_row(self):
        # Rimuove i codici css dal nome del colore (non viene utilizzata la
        # remove_colors per evitare import circolari)
        # (TD) da rivedere la cosa
        bracket_close = self.name.find("]")
        bracket_open  = self.name.rfind("[")
        color_name = self.name[bracket_close+1 : bracket_open]

        return '''  <tr><td align="center" style="%s">%s</td></tr>\n''' % (
            self.get_bg_style(), self.get_mini_code())
    #- Fine Metodo -


#= ELEMENTI ====================================================================

# Il nero invia il codice esadecimale del grigio scuro perché altrimenti
# conflitterebbe con lo sfondo del sito

NONE                 = ColorElement("Nessuno")
WHITE                = ColorElement("[white]bianco[close]",                                      "#FFF")
SNOW                 = ColorElement("[snow]neve[close]",                                         "#FFFAFA")
GHOSTWHITE           = ColorElement("[ghostwhite]bianco fantasma[close]",                        "#F8F8FF")
AZURE                = ColorElement("[azure]celeste[close]",                                     "#F0FFFF")
IVORY                = ColorElement("[ivory]avorio[close]",                                      "#FFFFF0")
MINTCREAM            = ColorElement("[mintcream]crema di menta[close]",                          "#F5FFFA")
FLORALWHITE          = ColorElement("[floralwhite]fiore bianco[close]",                          "#FFFAF0")
ALICEBLUE            = ColorElement("[aliceblue]blu alice[close]",                               "#F0F8FF")
LAVENDERBLUSH        = ColorElement("[lavenderblush]lavanda arrossita[close]",                   "#FFF0F5")
SEASHELL             = ColorElement("[seashell]conchiglia[close]",                               "#FFF5EE")
HONEYDEW             = ColorElement("[honeydew]goccia di miele[close]",                          "#F0FFF0")
WHITESMOKE           = ColorElement("[whitesmoke]bianco sporco[close]",                          "#F5F5F5")
LIGHTCYAN            = ColorElement("[lightcyan]ciano chiaro[close]",                            "#E0FFFF")
LIGHTYELLOW          = ColorElement("[lightyellow]giallo chiaro[close]",                         "#FFFFE0")
OLDLACE              = ColorElement("[oldlace]pizzo antico[close]",                              "#FDF5E6")
CORNSILK             = ColorElement("[cornsilk]setola di mais[close]",                           "#FFF8DC")
LINEN                = ColorElement("[linen]lino[close]",                                        "#FAF0E6")
LEMONCHIFFON         = ColorElement("[lemonchiffon]limone[close]",                               "#FFFACD")
LIGHTGOLDENRODYELLOW = ColorElement("[lightgoldenrodyellow]legno dorato giallo chiaro[close]",   "#FAFAD2")  # 250 250 210
BEIGE                = ColorElement("[beige]beige[close]",                                       "#F5F5DC")
LAVENDER             = ColorElement("[lavender]lavanda[close]",                                  "#E6E6FA")
MISTYROSE            = ColorElement("[mistyrose]rosa nebbioso[close]",                           "#FFE4E1")
PAPAYAWHIP           = ColorElement("[papayawhip]pesca pallido[close]",                          "#FFEFD5")
ANTIQUEWHITE         = ColorElement("[antiquewhite]bianco antico[close]",                        "#FAEBD7")
BLANCHEDALMOND       = ColorElement("[blanchedalmond]blanche dalmond[close]",                    "#FFEBCD")
BISQUE               = ColorElement("[bisque]biscotto[close]",                                   "#FFE4C4")
QUARTZ               = ColorElement("[quartz]quarzo[close]",                                     "#D9D9F3")
MOCASSIN             = ColorElement("[mocassin]mocassino[close]",                                "#FFE4B5")
GAINSBORO            = ColorElement("[gainsboro]gainsboro[close]",                               "#DCDCDC")
PEACHPUFF            = ColorElement("[peachpuff]pesca scuro[close]",                             "#FFDAB9")
PALETURQUOISE        = ColorElement("[paleturquoise]turchese pallido[close]",                    "#AFEEEE")
NAVAJOWHITE          = ColorElement("[navajowhite]bianco navajo[close]",                         "#FFDEAD")
PINK                 = ColorElement("[pink]rosa[close]",                                         "#FFC0CB")
WHEAT                = ColorElement("[wheat]grano[close]",                                       "#F5DEB3")
MEDIUMGOLDENROD      = ColorElement("[mediumgoldenrod]legno dorato medio[close]",                "#EAEAAE")
PALEGOLDENROD        = ColorElement("[palegoldenrod]legno dorato pallido[close]",                "#EEE8AA")
LIGHTGRAY            = ColorElement("[lightgray]grigio chiaro[close]",                           "#D3D3D3")
LIGHTGREY            = ColorElement("[lightgrey]grigio chiaro[close]",                           "#D3D3D3")
POWDERBLUE           = ColorElement("[powderblue]blu polvere[close]",                            "#B0E0E6")
LIGHTPINK            = ColorElement("[lightpink]rosa chiaro[close]",                             "#FFB6C1")
FADEDBROWN           = ColorElement("[fadedbrown]marrone sbiadito[close]",                       "#F5CCB0")
THISTLE              = ColorElement("[thistle]cardo[close]",                                     "#D8BFD8")
LIGHTBLUE            = ColorElement("[lightblue]blu chiaro[close]",                              "#ADD8E6")  # 173 216 230
VERYLIGHTGRAY        = ColorElement("[verylightgray]grigio molto chiaro[close]",                 "#CDCDCD")
VERYLIGHTGREY        = ColorElement("[verylightgrey]grigio molto chiaro[close]",                 "#CDCDCD")
KHAKI                = ColorElement("[khaki]khaki[close]",                                       "#F0E68C")
VIOLET               = ColorElement("[violet]violetto[close]",                                   "#EE82EE")
PLUM                 = ColorElement("[plum]prugno[close]",                                       "#DDA0DD")
LIGHTSTEELBLUE       = ColorElement("[lightsteelblue]blu acciaio chiaro[close]",                 "#B0C4DE")
AQUAMARINE           = ColorElement("[aquamarine]acquamarina[close]",                            "#7FFFD4")
LIGHTWOOD            = ColorElement("[lightwood]legno chiaro[close]",                            "#E9C2A6")
NEWTAN               = ColorElement("[newtan]fresca di abbronzatura[close]",                     "#EBC79E")
LIGHTSKYBLUE         = ColorElement("[lightskyblue]blu cielo chiaro[close]",                     "#87CEFA")
SILVER               = ColorElement("[silver]argento[close]",                                    "#C0C0C0")
SKYBLUE              = ColorElement("[skyblue]blu cielo[close]",                                 "#87CEEB")
BRIGHTPINK           = ColorElement("[brightpink]rosa brillante[close]",                         "#FF6EC7")
PALEGREEN            = ColorElement("[palegreen]verde pallido[close]",                           "#98FB98")
ORCHID               = ColorElement("[orchid]orchidea[close]",                                   "#DA70D6")
BURLYWOOD            = ColorElement("[burlywood]burly wood[close]",                              "#DEB887")
HOTPINK              = ColorElement("[hotpink]rosso acceso[close]",                              "#FF69B4")
LIGHTSALMON          = ColorElement("[lightsalmon]salmone chiaro[close]",                        "#FFA07A")
TAN                  = ColorElement("[tan]abbronzatura[close]",                                  "#D2B48C")
LIGHTGREEN           = ColorElement("[lightgreen]verde chiaro[close]",                           "#90EE90")  # 90 238 90
CYAN                 = ColorElement("[cyan]ciano[close]",                                        "#0FF")
MAGENTA              = ColorElement("[magenta]magenta[close]",                                   "#F0F")
YELLOW               = ColorElement("[yellow]giallo[close]",                                     "#FF0")
AQUA                 = ColorElement("[aqua]acqua[close]",                                        "#0FF")
FUCHSIA              = ColorElement("[fuchsia]fucsia[close]",                                    "#F0F")
DARKGREY             = ColorElement("[darkgrey]grigio scuro[close]",                             "#A9A9A9")
DARKGRAY             = ColorElement("[darkgray]grigio scuro[close]",                             "#A9A9A9")
DARKSALMON           = ColorElement("[darksalmon]salmone scuro[close]",                          "#E9967A")
SANDYBROWN           = ColorElement("[sandybrown]marrone sabbia[close]",                         "#F4A460")
LIGHTCORAL           = ColorElement("[lightcoral]corallo chiaro[close]",                         "#F08080")
TURQUOISE            = ColorElement("[turquoise]turchese[close]",                                "#40E0D0")
SALMON               = ColorElement("[salmon]salmone[close]",                                    "#FA8072")
CORNFLOWERBLUE       = ColorElement("[cornflowerblue]fiordaliso[close]",                         "#6495ED")
MEDIUMTURQUOISE      = ColorElement("[mediumturquoise]turchese medio[close]",                    "#48D1CC")
MEDIUMORCHID         = ColorElement("[mediumorchid]orchidea medio[close]",                       "#BA55D3")
DARKKHAKI            = ColorElement("[darkkhaki]khaki scuro[close]",                             "#BDB76B")
PALEVIOLETRED        = ColorElement("[palevioletred]rosso violetto pallido[close]",              "#DB7093")
MEDIUMPURPLE         = ColorElement("[mediumpurple]porpora medio[close]",                        "#9370DB")
MEDIUMAQUAMARINE     = ColorElement("[mediumaquamarine]acquamarina medio[close]",                "#66CDAA")
GREENYELLOW          = ColorElement("[greenyellow]giallo-verde[close]",                          "#ADFF2F")
DARKSEAGREEN         = ColorElement("[darkseagreen]verde mare scuro[close]",                     "#8FBC8F")
ROSYBROWN            = ColorElement("[rosybrown]marrone roseo[close]",                           "#BC8F8F")
FELDSPAR             = ColorElement("[feldspar]feldspato[close]",                                "#D19275")
GOLD                 = ColorElement("[gold]oro[close]",                                          "#FFD700")
MEDIUMSLATEBLUE      = ColorElement("[mediumslateblue]ardesia blu medio[close]",                 "#7B68EE")
CORAL                = ColorElement("[coral]corallo[close]",                                     "#FF7F50")
BRIGHTGOLD           = ColorElement("[brightgold]oro brillante[close]",                          "#D9D919")
SPICYPINK            = ColorElement("[spicypink]rosa piccante[close]",                           "#FF1CAE")
SUMMERSKY            = ColorElement("[summersky]cieclo estivo[close]",                           "#38B0DE")
OLDGOLD              = ColorElement("[oldgold]oro antico[close]",                                "#CFB53B")
DEEPSKYBLUE          = ColorElement("[deepskyblue]blu cielo intenso[close]",                     "#00BFFF")
DODGERBLUE           = ColorElement("[dodgerblue]blu furbo[close]",                              "#1E90FF")
TOMATO               = ColorElement("[tomato]rosso pomodoro[close]",                             "#FF6347")
DEEPPINK             = ColorElement("[deeppink]rosa intenso[close]",                             "#FF1493")
ORANGE               = ColorElement("[orange]arancio[close]",                                    "#FFA500")
DARKTURQUOISE        = ColorElement("[darkturquoise]turchese scuro[close]",                      "#00CED1")
GOLDENROD            = ColorElement("[goldenrod]legno dorato[close]",                            "#DAA520")
CADETBLUE            = ColorElement("[cadetblue]blu cadetto[close]",                             "#5F9EA0")
BRASS                = ColorElement("[brass]ottone[close]",                                      "#B5A642")
YELLOWGREEN          = ColorElement("[yellowgreen]verde-giallo[close]",                          "#9ACD32")
MANABLUE             = ColorElement("[manablue]blu mana[close]",                                 "#4D4DFF")
LIGHTSLATEGREY       = ColorElement("[lightslategrey]ardesia grigio chiaro[close]",              "#778899")
LIGHTSLATEGRAY       = ColorElement("[lightslategray]ardesia grigio chiaro[close]",              "#778899")
DARKORCHID           = ColorElement("[darkorchid]orchidea scuro[close]",                         "#9932CC")
BLUEVIOLET           = ColorElement("[blueviolet]blu-violetto[close]",                           "#8A2BE2")
VIOLETRED            = ColorElement("[violetred]rosso violetto[close]",                          "#CC3299")
MEDIUMSPRINGGREEN    = ColorElement("[mediumspringgreen]verde primavera medio[close]",           "#00FA9A")
SLATEBLUE            = ColorElement("[slateblue]blu ardesia[close]",                             "#6A5ACD")
PERU                 = ColorElement("[peru]peru[close]",                                         "#CD853F")
MANDARIANORANGE      = ColorElement("[mandarianorange]arancione medio[close]",                   "#E47833")
ROYALBLUE            = ColorElement("[royalblue]blu reale[close]",                               "#4169E1")
DARKORANGE           = ColorElement("[darkorange]arancio scuro[close]",                          "#FF8C00")
MEDIUMWOOD           = ColorElement("[mediumwood]legno medio[close]",                            "#A68064")
INDIANRED            = ColorElement("[indianred]rosso indiano[close]",                           "#CD5C5C")
GRAY                 = ColorElement("[gray]grigio[close]",                                       "#808080")
SLATEGREY            = ColorElement("[slategrey]grigio ardesia[close]",                          "#708090")
GREY                 = ColorElement("[grey]grigio[close]",                                       "#808080")
SLATEGRAY            = ColorElement("[slategray]grigio ardesia[close]",                          "#708090")
CHARTREUSE           = ColorElement("[chartreuse]chartreuse[close]",                             "#7FFF00")
SPRINGGREEN          = ColorElement("[springgreen]verde primavera[close]",                       "#00FF7F")
STEELBLUE            = ColorElement("[steelblue]blu acciaio[close]",                             "#4682B4")
LIGHTSEAGREEN        = ColorElement("[lightseagreen]verde mare chiaro[close]",                   "#20B2AA")
COOLCOPPER           = ColorElement("[coolcopper]rame freddo[close]",                            "#D98719")
LAWNGREEN            = ColorElement("[lawngreen]prato verde[close]",                             "#7CFC00")
DARKVIOLET           = ColorElement("[darkviolet]violetto scuro[close]",                         "#9400D3")
MEDIUMVIOLETRED      = ColorElement("[mediumvioletred]rosso violetto medio[close]",              "#C71585")
LIGHTBRONZE          = ColorElement("[lightbronze]bronzo chiaro[close]",                         "#A67D3D")
MEDIUMSEAGREEN       = ColorElement("[mediumseagreen]verde mare medio[close]",                   "#3CB371")
COPPER               = ColorElement("[copper]rame[close]",                                       "#B87333")
RICHBLUE             = ColorElement("[richblue]blu ricco[close]",                                "#5959AB")
CHOCOLATE            = ColorElement("[chocolate]cioccolato[close]",                              "#D2691E")
BRONZE               = ColorElement("[bronze]bronzo[close]",                                     "#8C7853")
DARKTAN              = ColorElement("[darktan]abbronzatura scura[close]",                        "#97694F")
DUSTYROSE            = ColorElement("[dustyrose]rosa polveroso[close]",                          "#856363")
DARKGOLDENROD        = ColorElement("[darkgoldenrod]legno d'orato scuro[close]",                 "#B8860B")
GREENCOPPER          = ColorElement("[greencopper]verde rame[close]",                            "#527F76")
ORANGERED            = ColorElement("[orangered]rosso arancio[close]",                           "#FF4500")
DIMGRAY              = ColorElement("[dimgray]grigio pallido[close]",                            "#696969")
DIMGREY              = ColorElement("[dimgrey]grigio pallido[close]",                            "#696969")
LIMEGREEN            = ColorElement("[limegreen]tiglio verde[close]",                            "#32CD32")
DARKGREENCOPPER      = ColorElement("[darkgreencopper]verde rame scuro[close]",                  "#4A766E")
CRIMSON              = ColorElement("[crimson]cremisi[close]",                                   "#DC143C")
DARKWOOD             = ColorElement("[darkwood]legno scuro[close]",                              "#855E42")
SIENNA               = ColorElement("[sienna]terra di siena[close]",                             "#A0522D")
DARKPURPLE           = ColorElement("[darkpurple]viola scuro[close]",                            "#871F78")
OLIVEDRAB            = ColorElement("[olivedrab]oliva incolore[close]",                          "#6B8E23")
MEDIUMFORESTGREEN    = ColorElement("[mediumforestgreen]verde foresta medio[close]",             "#6B8E23")
DARKMAGENTA          = ColorElement("[darkmagenta]magenta scuro[close]",                         "#8B008B")
DARKCYAN             = ColorElement("[darkcyan]ciano scuro[close]",                              "#008B8B")  # 0 139 139
SEAGREEN             = ColorElement("[seagreen]verde mare[close]",                               "#2E8B57")
DARKSLATEBLUE        = ColorElement("[darkslateblue]ardesia blu scuro[close]",                   "#483D8B")
OLIVE                = ColorElement("[olive]oliva[close]",                                       "#808000")
TEAL                 = ColorElement("[teal]tè blu[close]",                                       "#008080")
PURPLE               = ColorElement("[purple]porpora[close]",                                    "#800080")
LIME                 = ColorElement("[lime]tiglio[close]",                                       "#0F0")
BLUE                 = ColorElement("[blue]blu[close]",                                          "#00F")
RED                  = ColorElement("[red]rosso[close]",                                         "#FF0000")
BROWN                = ColorElement("[brown]marrone[close]",                                     "#A52A2A")  # 165 42 42
FIREBRICK            = ColorElement("[firebrick]rosso mattone[close]",                           "#B22222")
DARKOLIVEGREEN       = ColorElement("[darkolivegreen]verde oliva scuro[close]",                  "#556B2F")
SADDLEBROWN          = ColorElement("[saddlebrown]marrone cuoio[close]",                         "#8B4513")
SWEETCHOCOLATE       = ColorElement("[sweetchocolate]cioccolato dolce[close]",                   "#6B4226")
VERYDARKBROWN        = ColorElement("[verydarkbrown]marrone molto scuro[close]",                 "#5C4033")
FORESTGREEN          = ColorElement("[forestgreen]verde foresta[close]",                         "#228B22")
DARKBROWN            = ColorElement("[darkbrown]marrone scuro[close]",                           "#5C4033")
MEDIUMBLUE           = ColorElement("[mediumblue]blu medio[close]",                              "#0000CD")
DARKSLATEGRAY        = ColorElement("[darkslategray]ardesia grigio scuro[close]",                "#2F4F4F")
DARKSLATEGREY        = ColorElement("[darkslategrey]ardesia grigio scuro[close]",                "#2F4F4F")
INDIGO               = ColorElement("[indigo]indigo[close]",                                     "#4B0082")
SCARLET              = ColorElement("[scarlet]scarlatto[close]",                                 "#8C1717")
MIDNIGHTBLUE         = ColorElement("[midnightblue]blu di mezzanotte[close]",                    "#191970")
HUNTERGREEN          = ColorElement("[huntergreen]verde cacciatore[close]",                      "#215E21")
NEWMIDNIGHTBLUE      = ColorElement("[newmidnightblue]blu di mezzanotte appena scoccata[close]", "#00009C")
DARKBLUE             = ColorElement("[darkblue]blu scuro[close]",                                "#00008B")
DARKRED              = ColorElement("[darkred]rosso scuro[close]",                               "#8B0000")
GREEN                = ColorElement("[green]verde[close]",                                       "#008000")
MAROON               = ColorElement("[maroon]marrone[close]",                                    "#800000")
NAVY                 = ColorElement("[navy]blu marina[close]",                                   "#000080")
DARKGREEN            = ColorElement("[darkgreen]verde scuro[close]",                             "#006400")
BLACK                = ColorElement("[black]nero[close]",                                        "#2F2F2F")


# Lista dei nomi alternativi per i colori descriventi i capelli
BROWN.hair_color       = "[brown]castano[close]"
LIGHTYELLOW.hair_color = "[yellow]biondo chiaro[close]"
YELLOW.hair_color      = "[yellow]biondo[close]"

# Lista dei nomi che sono per comodità sinonimi di altri e che non hanno
# valenza nell'esser mostrati nella lista dei colori
DARKGREY.alternative       = True
DARKSLATEGREY.alternative  = True
DIMGREY.alternative        = True
GREY.alternative           = True
LIGHTGREY.alternative      = True
LIGHTSLATEGREY.alternative = True
SLATEGREY.alternative      = True
VERYLIGHTGREY.alternative  = True


#= FUNZIONI ====================================================================

def create_html_table_of_colors():
    # (TD) Crea la tabella html in maniera dinamica
    pass
#- Fine Funzione -


#= FINALIZZAZIONE ==============================================================

finalize_enumeration(__name__)
create_html_table_of_colors()
