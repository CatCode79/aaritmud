# -*- coding: utf-8 -*-

"""
Enumerazione delle tipologie di canale, sia rpg che non.
"""

from src.element import EnumElement, finalize_enumeration
from src.enums   import TRUST

#-------------------------------------------------------------------------------

name = __name__[__name__.rfind(".")+1 : ]
elements = []
cycle_on_last = False


#------------------------------------------------------------------------------

class ChannelElement(EnumElement):
    def __init__(self, name, description=""):
        super(ChannelElement, self).__init__(name, description)
        self.verb_you = ""
        self.verb_it  = ""
        self.trust    = TRUST.PLAYER
        self.trigger  = ""
    #- Fine Inizializzazione -


#------------------------------------------------------------------------------

NONE       = ChannelElement("Nessuno")
WHISPER    = ChannelElement("[green]sussurrare[close]",      "Canale sussurrare, dal tono bassissimo")
MURMUR     = ChannelElement("[green]mormorare[close]",       "Canale per mormorare, dal tono basso")
HISSING    = ChannelElement("[dimgray]sibilare[close]",      "Canale per sibilare qualcosa a qualcuno e impaurirlo")
SAY        = ChannelElement("[white]dire[close]",            "Canale per parlare con tonalità di default")
THUNDERING = ChannelElement("[red]tuonare[close]",           "Canale per tuonare qualcosa a qualcuno e sorprenderlo")
SING       = ChannelElement("[lightgreen]cantare[close]",    "Canale per cantare, con tono abbastanza alto")
YELL       = ChannelElement("[yellow]urlare[close]",         "Canale per urlare con tono alto")
SHOUT      = ChannelElement("[yellow]gridare[close]",        "Canale per gridare con tono altissimo")
TELL       = ChannelElement("[teal]comunicare[close]",       "Canale per comunicare con i pg in maniera off-gdr")
GTELL      = ChannelElement("[orange]gcomunicare[close]",    "Canale per comunicare col gruppo in maniera off-gdr, alcuni gruppi lo utilizzano in maniera gdr")
CHAT       = ChannelElement("[crimson]chattare[close]",      "Canale per parlare con tutti i giocatori del Mud in maniera off-gdr")
THINK      = ChannelElement("[blueviolet]pensare[close]",    "Canale per comunicare pensieri agli amministratori, può essere usato come gdr o meno")
ADMTALK    = ChannelElement("[blueviolet]admtalkare[close]", "Canale per comunicare tra amministratori")

# Ai canali rpg non bisogna aggiungere i colori perché vengono gestiti nella
# funzione rpg_channel del modulo src.channel
WHISPER.verb_you    = "Sussurri"
MURMUR.verb_you     = "Mormori"
HISSING.verb_you    = "Sibili"
SAY.verb_you        = "Dici"
THUNDERING.verb_you = "Tuoni"
SING.verb_you       = "Canti"
YELL.verb_you       = "Urli"
SHOUT.verb_you      = "Gridi"
TELL.verb_you       = "[teal]Comunichi[close]"
GTELL.verb_you      = "[orange]GComunichi[close]"
CHAT.verb_you       = "[crimson]Chatti[close]"
THINK.verb_you      = "[blueviolet]Penso[close]"
ADMTALK.verb_you    = "[blueviolet]AdminTalk[close]"

WHISPER.verb_it    = " sussurra"
MURMUR.verb_it     = " mormora"
HISSING.verb_it    = " sibila"
SAY.verb_it        = " dice"
THUNDERING.verb_it = " tuona"
SING.verb_it       = " canta"
YELL.verb_it       = " urla"
SHOUT.verb_it      = " grida"
TELL.verb_it       = " [teal]comunica[close]"
GTELL.verb_it      = " [orange]gcomunica[close]"
CHAT.verb_it       = " [crimson]chatta[close]"
THINK.verb_it      = " [blueviolet]pensa[close]"
ADMTALK.verb_it    = " [blueviolet]AdminTalk[close]"

ADMTALK.trust = TRUST.MASTER

WHISPER.trigger_suffix    = "whisper"
MURMUR.trigger_suffix     = "murmur"
HISSING.trigger_suffix    = "hissing"
SAY.trigger_suffix        = "say"
THUNDERING.trigger_suffix = "thundering"
SING.trigger_suffix       = "sing"
YELL.trigger_suffix       = "yell"
SHOUT.trigger_suffix      = "shout"
# Gli altri canali non rpg non hanno un trigger di attivazione gamescript


#-------------------------------------------------------------------------------

finalize_enumeration(__name__)
