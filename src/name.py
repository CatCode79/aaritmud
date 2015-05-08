# -*- coding: utf-8 -*-

"""
Modulo per la creazione casuale di nomi fantasy.
"""


#= IMPORT ======================================================================

import random

from src.database import database
from src.element  import Element
from src.enums    import RACE, SEX
from src.utility  import is_same


#= VARIABLES ===================================================================

human_male_prefixs = [
    "a", "ab", "ac", "ad", "af", "agr", "ast", "as", "al", "adw", "adr", "ar",
    "b", "br",
    "c", "c", "c", "cr", "ch", "cad",
    "d", "dr", "dw",
    "ed", "et", "eth", "er", "el", "eow",
    "f", "fr",
    "g", "gr", "gw", "gw", "gal", "gl",
    "h", "ha",
    "ib",
    "j", "jer",
    "k", "ka", "ked",
    "l", "loth", "lar", "leg",
    "m", "mir",
    "n", "nyd",
    "ol", "oc", "on",
    "p", "pr",
    "q",
    "r", "rh",
    "s", "sev",
    "t", "tr", "th", "th",
    "ul", "um", "un",
    "v",
    "y", "yb",
    "z",
    "w", "w", "wic"]

human_male_middles = [
    "a", "ae", "ae", "au", "ao", "are", "ale", "ali", "ay", "ardo",
    "e", "edri", "ei", "ea", "ea", "eri", "era", "ela", "eli", "enda", "erra",
    "i", "ia", "ie", "ire", "ira", "ila", "ili", "ira", "igo",
    "o", "oha", "oma", "oa", "oi", "oe", "ore",
    "u",
    "y"]

human_male_suffixs = [
    "", "", "", "", "", "", "",
    "a", "and",
    "b", "bwyn", "baen", "bard",
    "c", "ch", "can",
    "d", "dan", "don", "der", "dric", "dus",
    "f",
    "g", "gord", "gan",
    "han", "har",
    "jar", "jan",
    "k", "kin", "kith", "kath", "koth", "kor", "kon",
    "l", "li", "lin", "lith", "lath", "loth", "ld", "ldan",
    "m", "mas", "mos", "mar", "mond",
    "n", "nydd", "nidd", "nnon", "nwan", "nyth", "nad", "nn", "nnor", "nd",
    "p",
    "r", "red", "ric", "rid", "rin", "ron", "rd",
    "s", "sh", "seth",
    "t", "th", "th", "tha", "tlan", "trem", "tram",
    "v", "vudd",
    "w", "wan", "win", "win", "wyn", "wyn", "wyr", "wyr", "with"]

human_female_prefixs = [
    "a", "ab", "ac", "ad", "af", "agr", "ast", "as", "al", "adw", "adr", "ar",
    "b", "br",
    "c", "c", "c", "cr", "ch", "cad",
    "d", "dr", "dw",
    "ed", "eth", "et", "er", "el", "eow",
    "f", "fr",
    "g", "gr", "gw", "gw", "gal", "gl",
    "h", "ha",
    "ib",
    "jer",
    "k", "ka", "ked",
    "l", "loth", "lar", "leg",
    "m", "mir",
    "n", "nyd",
    "ol", "oc", "on",
    "p", "pr",
    "q",
    "r", "rh",
    "s", "sev",
    "t", "tr", "th", "th",
    "ul", "um", "un",
    "v",
    "y", "yb",
    "z",
    "w", "w", "wic"]

human_female_middles = [
    "a", "a", "a", "ae", "ae", "au", "ao", "are", "ale", "ali", "ay", "ardo",
    "e", "e", "e", "ei", "ea", "ea", "eri", "era", "ela", "eli", "endi", "erra",
    "i", "i", "i", "ia", "ie", "ire", "ira", "ila", "ili", "ira", "igo",
    "o", "oa", "oi", "oe", "ore",
    "u",
    "y"]

human_female_suffixs = [
    "", "", "", "", "", "", "",
    "beth",
    "cia", "cien", "clya",
    "de", "dia", "dda", "dien", "dith", "dia",
    "lind", "lith", "lia", "lian", "lla", "llan", "lle",
    "ma", "mma", "mwen", "meth",
    "n", "n", "n", "nna", "ndra", "ng", "ni", "nia", "niel",
    "rith", "rien", "ria", "ri", "rwen",
    "sa", "sien", "ssa", "ssi", "swen",
    "thien", "thiel",
    "viel", "via", "ven", "veth",
    "wen", "wen", "wen", "wen", "wia", "weth", "wien", "wiel"]

archaic_prefixs = [
    "alaun", "ancient", "archen", "arvale", "arwe", "asper", "ax",
    "barley", "barren", "bat", "battle", "beeste", "bent", "birch", "blasted", "bowe", "bryony", "burnt",
    "castel", "castle", "clock", "cob", "cog", "cool", "corne", "crystal",
    "daemon", "daw", "divel", "dwale",
    "eld", "eldritch", "emerald",
    "fair", "fairy", "fallow", "far", "fayre", "fazart", "fell", "fey", "fire", "flittermouse", "flower", "foam", "forest", "fowle", "fox",
    "gate", "ghoot", "glass", "gleeke", "glen", "glome", "great", "grete", "grisful",
    "hammer", "hap", "hawking", "honey", "horn",
    "kynges",
    "lang", "leech", "lessing", "lichen", "lone", "lynge", "lyon",
    "madder", "meadow", "mickle", "mighty", "moon", "moor", "more", "moss", "muck",
    "neat",
    "onyx", "owles",
    "pine",
    "riven", "roaryng", "rocke", "rowan",
    "sand", "schyppe", "scree", "shadow", "shady", "sharpe", "smyth", "snow", "soft", "sovran", "sparth", "speer", "spleen", "springe", "stan", "star", "steep", "stone", "storme", "stour", "strake", "sunder", "swerd",
    "thistle", "throstle", "tower",
    "umble",
    "vine",
    "wan", "warre", "watchet", "wicker", "wilder", "wine", "wither", "withy", "wolver", "wood", "wych", "wyrd",
    "yce", "ymp"]

archaic_suffixs = [
    "bottom", "brooke", "burg",
    "cliffe", "combe", "coppice", "corrie", "course", "crag", "crest",
    "dal", "dale", "dayl",
    "felde", "fen", "forest", "frith",
    "garth", "glen", "grove", "gulf",
    "ham", "hampton", "heath", "hill", "holde", "horne", "howe", "hylles",
    "land", "lande", "londe",
    "marsh", "mere", "mire", "mouthe",
    "nock",
    "pass", "pike",
    "reach", "road", "ryver",
    "scarf", "scree", "sea", "stack", "strait", "strand", "strath", "stream", "style",
    "tethe", "tide", "ton", "tor", "towne",
    "vale", "ville",
    "water", "wick", "windle", "wold", "wood", "wort", "wyke",
    "ynge"]

eldar_prefixs = [
    "am", "amon", "an", "ar", "ara",
    "barad", "baran", "bel", "beleg",
    "dol", "don", "dun",
    "el",
    "galad", "gil", "gon", "gul",
    "isen",
    "loth",
    "mene", "mor",
    "naz",
    "orod"]

eldar_suffixs = [
    "adan", "amroth",
    "cirith",
    "dor", "duin",
    "falas",
    "gard", "gorn", "groth", "gul",
    "ia",
    "ost",
    "rain", "riel", "rond", "roth", "ruin",
    "thyryr"]

elf_prefixs = [
    "alder", "arrow", "ash",
    "bark", "battle", "bear", "beech", "bell", "birch", "black", "blue", "briar",
    "clear", "cloud", "cold", "crystal",
    "dark", "deep", "deer", "dew",
    "elder", "elm", "even", "ever",
    "fallen", "fell", "foam", "fog", "follow", "forest", "frost",
    "gem", "golden", "good", "green", "grey", "grim",
    "hard", "hawk", "hidden", "high", "hollow",
    "ice", "iron",
    "jewel",
    "larch", "leaf", "lone", "lost",
    "maple", "marsh", "mist", "moon", "morning", "moss", "mountian",
    "never", "new",
    "oak", "oaken", "old",
    "pine",
    "quiet",
    "rain", "raven", "red", "rose",
    "shadow", "silent", "silven", "silver", "snow", "sodden", "song", "sparrow", "spell", "storm", "sudden",
    "tall", "tree",
    "vale", "valley",
    "web", "wet", "white", "wild", "wilder", "wren",
    "yellow"]

elf_suffixs = [
    "arrow", "ash",
    "blossom", "brand", "bright", "brook", "brow",
    "call",
    "dale", "dark", "dell", "dew", "drop",
    "even", "ever", "eye",
    "fall", "fern", "field", "flower", "fruit",
    "glade", "gleam", "glen", "glitter", "gold", "grass", "green",
    "hand", "helm",
    "lake", "leaf", "light", "lock", "lore",
    "maiden", "marsh", "meadow", "meet",
    "oak",
    "path", "pool",
    "rain", "raven", "road", "rock",
    "shield", "silver", "singer", "sky", "slope", "song", "spell", "staff", "star", "stone", "storm", "stream", "strider", "sword",
    "thorn", "trail", "tree",
    "vale",
    "walker", "warden", "watcher", "water", "white", "wind", "wing", "wood"]

england_prefixs = [
    "aber", "ayles",
    "ban", "basing", "bath", "bed", "birming", "black", "bland", "bletch", "bourne", "brack", "brent", "bridge", "broms", "bur",
    "cam", "canter", "carl", "chat", "chelms", "chelten", "chester", "clee", "col", "cor", "covent", "crew",
    "dor", "dun",
    "east", "ex",
    "fal", "fleet", "folke",
    "gallo", "gals", "gates", "glaston", "grey", "grim", "grin",
    "ha", "harro", "hasle", "haver", "hay", "hels", "hemp", "here", "herne", "horn", "hors", "hum", "hunting",
    "ilfra", "inns", "ips",
    "ketter",
    "lei", "leo", "lich", "liver", "lyn",
    "maccles", "maid", "maiden", "mal", "mans", "mar", "marble", "mat", "mel", "mine", "mon", "more", "mow",
    "new", "nor", "north", "notting", "nunea",
    "oak", "oke", "old", "ox",
    "peter", "ponty", "ports",
    "rams", "rother",
    "sax", "scun", "shef", "sher", "shrews", "sid", "skeg", "south", "stam", "stan", "steven", "stock", "strat", "stroud", "suf",
    "tet", "trow", "tuan", "tun",
    "war", "ware", "warring", "wes", "wester", "white", "wil", "win", "wind", "wood", "wor", "working", "wy", "wyrm",
    "yar", "yeo"]

england_suffixs = [
    "age", "am", "avon",
    "borne", "borough", "bray", "bridge", "bury", "by",
    "cambe", "castle", "cester", "chester", "combe",
    "dare", "don",
    "field", "folk", "ford",
    "gate", "grove",
    "ham", "hampton", "haven", "head", "hill",
    "ing", "isle",
    "kerne",
    "land", "ley", "lock",
    "mere", "minster", "moor", "mouth",
    "ness", "nock", "north",
    "poole", "port",
    "ry",
    "shroud", "stable", "stead", "stock", "stoke", "stone",
    "thorpe", "ton",
    "vern", "vil",
    "ward", "water", "way", "wich", "wick", "wold", "wood", "wyvern"]

exotic_prefixs = [
    "ab", "ac", "ad", "af", "ag", "agh", "ah", "aj", "ak", "al", "am", "an", "ap", "ar", "as", "ash", "at", "ath", "av", "aw", "ax", "ay", "az",
    "bac", "bad", "bag", "baj", "bak", "bal", "bam", "ban", "bap", "bar", "bas", "bash", "bat", "bav", "baw", "bax", "bay", "beb", "bed", "bef", "beg", "beh", "bej", "bek", "bel", "bem", "ben", "bep", "ber", "bes", "bet", "beth", "bev", "bew", "bey", "bez", "bib", "bic", "bid", "bif", "big", "bij", "bik", "bil", "bim", "bin", "bip", "bir", "bis", "bit", "bith", "biv", "biz", "bob", "boc", "bod", "bof", "bor", "bos", "both", "boz", "brod", "brof", "brog", "broj", "bud", "buf", "bug", "bugh", "buj", "buk", "bul", "bum", "bun", "bup", "bur", "bus", "but", "buth", "buz",
    "char", "chur", "cul",
    "da", "dek", "drul", "dur",
    "ei", "eis", "eog",
    "gark", "gu",
    "hoth",
    "iar", "il", "ior", "ir", "ith",
    "ja", "jay",
    "kad", "kar", "ked", "ker", "ki", "kir", "kirin", "ku", "kul", "kus", "ky",
    "la", "ly",
    "mal", "mik", "my", "myr",
    "nar", "nex", "nom", "num",
    "or",
    "pel", "pha", "por",
    "ran", "rath", "re", "rul",
    "sha", "ste", "sul", "sum",
    "tan", "te", "ter", "tes", "teth", "thar", "tlil", "tur", "ty",
    "u",
    "va", "val", "var", "ves", "vog", "vur",
    "xen",
    "ya", "yug",
    "zir", "zor"]

exotic_middles = [
    "a", "aen", "an", "ar",
    "brax",
    "da", "dar", "do", "dra",
    "e", "el", "en", "er",
    "ga",
    "i", "ia", "il", "im", "in", "is", "ison", "iv",
    "ka", "kan",
    "mir",
    "o", "on", "or", "our",
    "ril", "rul",
    "sel",
    "ta",
    "uar"]

exotic_suffixs = [
    "a", "ae", "aj", "ak", "aki", "al", "an", "ana", "ari", "ax",
    "bon",
    "dae", "dar", "dek", "dir",
    "e", "ea", "el", "en", "es",
    "fean",
    "gor",
    "han",
    "ic", "im", "in", "ion", "is",
    "kari", "kin",
    "lar", "lik", "lo", "lon", "loss",
    "man", "mor", "mur",
    "na", "nac", "nir",
    "ok", "on", "or",
    "ra", "ri", "ric", "rik", "rion", "ris", "ron", "ruk",
    "sa", "sang", "sek",
    "tar", "tha", "than", "thon", "tice", "tok",
    "us",
    "vin",
    "yark"]

female_1_prefixs = [
    "ail", "ara", "ay",
    "bren",
    "cil",
    "dae", "dren", "dwen",
    "el", "erin", "eth",
    "fae", "fay",
    "gae", "gay", "glae", "gwen",
    "il",
    "jey",
    "lae", "lan", "lin",
    "mae", "mara", "mi", "min", "more",
    "ne", "nel",
    "pae", "pwen",
    "rae", "ray", "re", "ri",
    "sal", "say", "si",
    "tae", "te", "ti", "tin", "tir",
    "vi", "vul"]

female_1_suffixs = [
    "a", "alle", "ann", "arra", "aye",
    "da", "dolen",
    "ell", "enn", "eth", "eya",
    "fa", "fey",
    "ga", "gwenn",
    "hild",
    "ill", "ith",
    "la", "lana", "lar", "len", "lwen",
    "ma", "may",
    "na", "narra", "navia", "nwen",
    "ola",
    "pera", "pinn",
    "ra", "rann", "rell", "ress", "reth", "riss",
    "sa", "shann", "shara", "shea", "shell",
    "tarra", "tey", "ty",
    "unn", "ura",
    "valia", "vara", "vinn",
    "wen", "weth", "wynn", "wyrr",
    "ya", "ye", "yll", "ynd", "yrr", "yth"]

female_2_prefixs = [
    "ab", "aeb", "aed", "ael", "aelf", "aeln", "aen", "aer", "aeth", "ail", "ailf", "air", "airl", "airth", "aith", "al", "alf", "am", "an", "ath", "aul", "aw", "ayn", "ayth",
    "baer", "bain", "bair", "bal", "ban", "ber", "berl", "bern", "beth", "brael", "braen", "bran", "bren", "bur", "byl", "byr",
    "cal", "cam", "cath", "cel", "cen", "cern", "ceth", "cew", "chain", "chen", "cher", "cir", "cith", "clen", "cler", "clun", "coen", "coer", "craen", "craith", "crul", "cruth", "cul", "cun", "cur", "cuth", "cyl", "cyn", "cyr", "cyth",
    "daen", "daer", "dal", "del", "der", "dew", "dir", "dorn", "dul", "dun", "dur", "dwan", "dwen", "dwer", "dyn", "dyr",
    "ef", "el", "em", "en", "er", "eth", "ey",
    "fael", "faen", "faer", "faeth", "fain", "fal", "far", "fel", "fen", "fer", "feth", "fey", "fur", "fwen", "fwyr",
    "gal", "gan", "gar", "gel", "ger", "geth", "gew", "gral", "grel", "gren", "grew", "gwaen", "gwaer", "gwal", "gwan", "gwen", "gwer", "gweth", "gwyl", "gwyth",
    "haen", "haer", "hal", "han", "hath", "hel", "her", "hew", "hoel", "hoeth", "hul", "hur",
    "il", "in", "ir", "ith",
    "laer", "laeth", "lain", "lair", "lath", "law", "len", "ler", "lew", "loen", "loer", "lyn", "lyr", "lyth",
    "mael", "maen", "mel", "mer", "meth", "mir", "mith", "moer", "myn", "myr",
    "nael", "nel", "nen", "ner", "neth", "ney", "nil", "nim", "nin", "nir", "nul", "nyl", "nyr", "nyth",
    "oel", "oen", "oer", "oeth", "oew",
    "paen", "pal", "pan", "pel", "pen", "per", "peth", "pir", "pwel", "pwen", "pwer", "pyl", "pyn", "pyr",
    "rael", "raem", "raen", "raer", "raeth", "ran", "raw", "rel", "rer", "rey", "ryl", "ryn",
    "tael", "taen", "taer", "taeth", "tail", "tain", "tel", "ten", "ter", "tew", "then", "ther", "tir", "traen", "tral", "tran", "tyl", "tyr", "tyw",
    "ul", "ur",
    "wel", "wen", "wer", "weth", "wil", "wyl", "wyn", "wyr", "wyth"]

female_2_suffixs = [
    "all", "ann", "arel", "arenn", "areth", "arr", "ath", "athen", "ay", "ayell", "ayenn", "ayeth",
    "ber",
    "ell", "ellyn", "enn", "err", "eth",
    "henn",
    "ill", "inn", "innen", "iren", "ith",
    "lann", "lew", "lewen", "lynn", "lyren", "lyrr", "lyth",
    "marenn", "mareth", "marr",
    "orellen", "orenn", "orethen", "othen", "owenn",
    "rayll", "raynn", "ren", "renneth", "reth",
    "thall", "thirren", "thyr",
    "uren", "ureth",
    "warren", "waynn", "wayth", "well", "wenn", "weth", "wethen", "wyll", "wynn", "wyth",
    "yall", "yaynn", "yayth", "yell", "yeth", "ynn"]

goblin_prefixs = [
    "az",
    "balkh", "bol",
    "durba",
    "ghash",
    "lurg", "luz",
    "og",
    "tarkh",
    "urg", "uruk",
    "vol",
    "yazh"]

goblin_suffixs = [
    "agal",
    "gar",
    "mog",
    "narb",
    "og",
    "rod",
    "ubal"]

greek_prefixs = [
    "ab", "abad", "abel", "abyss", "ad", "adelph", "adiak", "adik", "adok", "adyn", "aer", "aeth", "agall", "agamemn", "agap", "agath", "ageneal", "agenealog", "agn", "agog", "agor", "agorax", "aichmal", "aid", "ain", "ainigm", "aion", "air", "aisch", "aischr", "aischrot", "aisth", "aisthan", "aisthet", "ait", "aitem", "ak", "akair", "akak", "akarp", "akatakr", "akatast", "akathars", "akathart", "aker", "akolouth", "akrogon", "akrop", "akyr", "alal", "alalaz", "alaz", "alazon", "aleiph", "aleth", "all", "alleg", "allel", "allog", "alloph", "allos", "allotr", "allotriep", "alog", "alyp", "am", "amempt", "amen", "ametan", "amiant", "amn", "amom", "amp", "ampel", "an", "anabain", "anadeikn", "anadeix", "anagen", "anagenn", "anagin", "anagn", "anakain", "anakr", "analamb", "analemp", "analemps", "analog", "analys", "anamart", "anamartet", "anamn", "anan", "anang", "anangel", "anankamom", "anap", "anaph", "anapl", "anaps", "anast", "anastaur", "anastr", "anat", "anathem", "anatith", "anatol", "anax", "anaz", "andr", "andriz", "anech", "anekt", "aneleem", "anenkl", "anepil", "aner", "anes", "anex", "anexer", "anexereun", "anexichn", "anexik", "anexikak", "ang", "angel", "aniem", "anipt", "anist", "anoch", "anos", "anot", "anoth", "ant", "antagon", "antall", "antallagm", "antan", "antanapl", "antap", "antapodid", "anthom", "anthomol", "anthomolog", "anthropar", "antilamb", "antilemp", "antilytr", "antimisth", "antityp", "anypotakt", "aorat", "apait", "apall", "apallotr", "apang", "apangel", "apant", "aparab", "aparch", "aparn", "apat", "apaug", "apeith", "apekd", "apeleuth", "apelp", "aperitm", "aph", "aphil", "aphilag", "apier", "apist", "apod", "apodech", "apodid", "apogign", "apokarad", "apokatall", "apokatast", "apokath", "apokol", "apoll", "apolytr", "apophtheng", "apops", "aposk", "apost", "aposyn", "apoth", "apothn", "aprosk", "aprosopol", "ar", "arch", "archang", "aren", "aresk", "aret", "arg", "aridion", "arist", "arithm", "ark", "arn", "arneom", "arrab", "arret", "art", "artigenn", "as", "aseb", "aselg", "ask", "asot", "aspasm", "aspaz", "asphal", "aspil", "ast", "astat", "asth", "asthen", "astr", "asyn", "atakt", "ath", "athanas", "athem", "athen", "athesm", "athet", "athl", "aug", "autark", "auth", "authad", "ax",
    "b", "bain", "bapt", "bar", "barb", "barbar", "basan", "basil", "basilik", "bask", "bast", "bath", "battal", "battar", "bdelygm", "bdelykt", "bdelyss", "beb", "bebel", "bel", "biast", "biaz", "bibl", "blasph", "blep", "boul", "brab", "brach", "brom", "bront", "bros", "brych", "brygm", "bybl",
    "ch", "chair", "char", "charagm", "charism", "charit", "charybd", "cher", "chil", "chliar", "chr", "chremat", "chrest", "chrisn", "christ", "chrom", "chron",
    "d", "daim", "daimon", "daktyl", "dech", "dees", "deikn", "deipn", "deisidaimon", "dek", "dekt", "deom", "desm", "despot", "dex", "diabol", "diagong", "diair", "diak", "dial", "diall", "dialog", "diamartyr", "diang", "diangel", "diaph", "diaphth", "diask", "diastr", "diat", "diath", "dichost", "did", "didakt", "dierch", "diermen", "diex", "dik", "diorth", "dips", "disk", "doch", "dodek", "dogm", "dok", "dokim", "dor", "doul", "dox", "drak", "drom", "dyn", "dynam", "dynat", "dysn",
    "ech", "echidn", "echth", "echthr", "eid", "eidol", "eik", "eim", "eir", "eiren", "eis", "eisak", "eiserch", "eisk", "eisod", "eisph", "eispor", "ekb", "ekbal", "ekch", "ekchyn", "ekd", "ekdik", "ekkath", "ekkent", "ekkl", "ekkopt", "ekkrem", "ekl", "eklamp", "ekleg", "eklekt", "ekmykt", "ekneph", "ekpipt", "ekpn", "ekporn", "ekriz", "ekten", "ektenest", "ekthamb", "ektrom", "el", "elach", "eleem", "elegm", "elench", "elenx", "eleuth", "ellog", "elp", "embat", "emm", "emperip", "emph", "emphys", "empn", "en", "endem", "endox", "eng", "enkak", "enkal", "enklem", "enkr", "enkrat", "enn", "enoch", "ent", "entell", "enthym", "ep", "epagon", "epair", "epaisch", "epak", "epakol", "epakolouth", "epanap", "epang", "epanorth", "epar", "eparat", "ephap", "epib", "epig", "epign", "epik", "epikatar", "epil", "epilys", "epis", "episk", "epistr", "epistre", "epit", "epithes", "epitith", "er", "erem", "ereun", "erg", "ergas", "ergat", "erith", "erot", "esch", "eschat", "esop", "esoptr", "est", "esth", "eth", "ethel", "ethn", "euarest", "euch", "euchom", "euk", "eulab", "eurisk", "euseb", "ex", "exagor", "exait", "exakolouth", "exanast", "exang", "exanist", "exap", "exapat", "exapost", "exaragoraz", "exart", "exeg", "exer", "exerch", "exest", "exist", "exod", "exolothr", "exomol", "exork", "exypn",
    "g", "gal", "galat", "gam", "geenn", "gegr", "gel", "gen", "geneal", "genn", "geuom", "gign", "gin", "ginosk", "gloss", "gnes", "gnom", "gnor", "gnos", "goes", "gon", "gong", "gongysm", "gongyst", "gonyp", "gorg", "gramm", "graph", "gymn", "gyn",
    "h", "had", "hag", "hagiasm", "hagiot", "hagn", "hagnism", "haim", "haimatek", "haimatekch", "hair", "hairetik", "hal", "hamart", "hap", "hapl", "harp", "harpagm", "hekon", "hel", "helik", "hem", "herk", "herod", "hetair", "heter", "hetoim", "hier", "hikan", "hiket", "hilar", "hilask", "hilasm", "hilast", "hip", "hist", "hodeg", "hol", "holokl", "holot", "hom", "homol", "hopl", "hor", "hork", "horm", "hos", "hot", "hout", "hyb", "hybrist", "hyd", "hyg", "hymn", "hyp", "hypak", "hypek", "hypn", "hypod", "hypokr", "hypomn", "hyst",
    "iak", "iam", "iamb", "iann", "iatr", "ichn", "ichth", "icles", "id", "idiot", "ierem", "ion", "ios", "ir", "isang", "isangel", "isch", "isot",
    "k", "kain", "kair", "kak", "kal", "kalym", "kalypt", "kamel", "kamph", "kard", "karp", "karter", "katab", "katad", "katagel", "katagon", "kataisch", "katall", "katang", "katangel", "katar", "katarasth", "katarg", "katart", "katathem", "katax", "kateg", "kath", "kathap", "kathar", "kathek", "kathist", "kaum", "keim", "kelt", "kenod", "kent", "keph", "kephal", "kerd", "kin", "klas", "klasm", "klauthm", "kleis", "klem", "klept", "kler", "kleron", "knoss", "koin", "kokk", "kol", "kolak", "kolaph", "koloss", "kolp", "kopt", "korb", "kosm", "kr", "krasp", "krat", "krem", "kreman", "krin", "krit", "ktis", "ktist", "kymb", "kyr",
    "l", "lach", "lakt", "lal", "lamb", "lamp", "lanch", "latr", "leg", "likm", "lim", "linab", "lith", "log", "loid", "loutr", "lychn", "lyk", "lyp", "lytr",
    "m", "main", "makar", "makel", "makr", "malak", "manth", "maran", "mart", "mas", "mast", "mat", "math", "mathet", "med", "meg", "megal", "mel", "memph", "memps", "men", "mer", "mes", "metall", "metan", "meth", "metoch", "metr", "mikr", "mimet", "mimn", "misth", "mn", "mog", "mol", "mom", "momph", "mon", "mor", "morph", "mosch", "mykt", "myr", "myst", "myth",
    "n", "nekr", "neom", "nep", "neph", "nest", "nik", "nipt", "nom", "nomik", "nomoth", "nos", "nothr", "nouth", "nymph", "nyn", "nyx",
    "ochl", "ochyr", "od", "odyn", "odyr", "odyrm", "odyss", "oid", "oik", "oikodesp", "oikonom", "oiktir", "olig", "oligop", "olol", "oloth", "olothr", "olymp", "omn", "on", "onk", "onom", "oph", "ophiel", "ophthal", "opis", "opisth", "opson", "opt", "optan", "or", "oreg", "orex", "org", "orgil", "orph", "orth", "osph", "ot", "otar", "ouran", "ous", "ox",
    "p", "pach", "pagis", "paid", "pal", "palingen", "pang", "papyr", "par", "parab", "parabl", "parag", "parait", "parak", "parakolouth", "paramen", "paren", "pares", "parous", "parox", "parrh", "parthen", "pat", "path", "patr", "patrik", "peg", "pegas", "peith", "pelasg", "pemp", "penth", "per", "perik", "peril", "perim", "perips", "perit", "ph", "phan", "phant", "phatn", "pher", "phil", "philadelph", "philag", "philip", "phob", "phon", "phor", "phort", "phos", "phosph", "phost", "phot", "phr", "phron", "phth", "phyl", "phylak", "phys", "pier", "pieth", "pimpl", "pin", "pipt", "pist", "pkr", "pl", "plan", "plass", "plast", "plen", "pleon", "pler", "pleth", "pn", "pneum", "poim", "polit", "polyl", "pom", "pon", "por", "porn", "pos", "pot", "pr", "prag", "pragm", "prakt", "pras", "praut", "prax", "presb", "proag", "prog", "progin", "progn", "progr", "prograph", "prok", "prokatang", "prom", "prosag", "prosagog", "prosanatith", "prosdeom", "prosk", "prosopol", "prost", "prot", "proth", "psalm", "psalt", "pseph", "pseust", "psych", "pt", "ptom", "ptos", "ptyx", "pygm", "pyk", "pykt", "pyl", "pyr", "pyrr", "pyth",
    "rh", "rhab", "rhabd", "rhad", "rhant", "rhem", "rhipt", "rhomb", "rhomp", "rhyom", "romph",
    "s", "sain", "sakk", "sal", "salp", "sam", "sark", "seb", "sem", "set", "sik", "sin", "sk", "skand", "sken", "skirt", "skler", "skol", "skolek", "skop", "skorp", "skot", "skyb", "smyrn", "som", "soph", "sophr", "sor", "sot", "spart", "speir", "sph", "sphrag", "splanchn", "st", "stas", "staur", "steg", "stek", "stel", "sten", "ster", "stigm", "stilb", "stoich", "stom", "str", "strat", "streph", "styl", "syk", "sykom", "sykoph", "syl", "syllamb", "syllyp", "symbas", "symph", "syn", "synag", "synaichmal", "synakolouth", "synantilamb", "synathl", "syngn", "synist", "synk", "synkl", "synt", "syntr", "syss", "syst", "syz",
    "t", "tagm", "tap", "tas", "tekn", "tel", "temn", "ter", "tessar", "tessarak", "tetart", "th", "thamb", "than", "thanat", "tharr", "thars", "thaum", "thel", "themel", "theodid", "theokr", "theom", "theor", "theos", "theot", "ther", "therap", "thesaur", "thessalon", "thlips", "thnesk", "thnet", "thor", "thren", "thresk", "thron", "thym", "thyr", "thys", "tim", "tith", "tithem", "tolm", "top", "tr", "trap", "trech", "trit", "trog", "tryg", "tynch", "typ", "typhl", "typik",
    "xen", "xyl",
    "yon",
    "z", "zel", "zelot", "zem", "zest", "zet", "zon", "zonn", "zoog", "zoop", "zyg", "zym"]

greek_suffixs = [
    "a", "aea", "aean", "aeuo", "age", "agma", "ai", "aino", "aio", "aios", "aira", "airia", "airo", "akos", "alaia", "aleo", "alia", "alizo", "almos", "alotos", "alypto", "amai", "ambano", "aminos", "ano", "anomai", "anon", "anteo", "ao", "aom", "aomai", "aos", "ar", "archeo", "ardia", "arenos", "argeo", "arios", "arites", "arma", "aros", "arotes", "arx", "as", "ascho", "asia", "asis", "askalos", "asma", "asso", "astole", "ateia", "ateus", "atheke", "athes", "athos", "atoo", "atos", "atres", "auid", "auo", "auroo", "auson", "ax", "axus", "azo",
    "e", "echos", "ege", "eia", "eias", "eilema", "eimma", "einos", "eion", "eioo", "eios", "eira", "eirao", "eksos", "eleuo", "eleus", "elia", "elion", "ello", "ellon", "elomai", "elos", "ema", "emai", "emeo", "empsia", "enion", "enis", "enos", "ens", "enteo", "eo", "eomai", "eon", "eoreo", "eos", "ephele", "epho", "eras", "erdos", "eresis", "ergos", "erion", "eron", "eros", "eryno", "eryx", "es", "es", "esia", "esis", "esko", "etes", "etos", "euma", "eunao", "euo", "euomai", "euos", "eus", "eusma", "euxis", "exia",
    "ia", "ias", "iasis", "iasmos", "iastos", "iazo", "ikao", "ikles", "ileo", "ilioi", "imos", "inia", "ino", "inoi", "inos", "ion", "ios", "iosyne", "iotes", "ipto", "irmon", "irmos", "is", "isis", "iskopos", "ismos", "ites", "itos", "ix", "izo",
    "o", "oche", "oe", "oema", "oeo", "oer", "oetheia", "oetos", "og", "oge", "ogeo", "ogia", "oia", "oichon", "oida", "oietos", "okles", "olex", "ologeo", "ologia", "olos", "omai", "omeo", "omos", "omphe", "on", "onia", "onios", "onos", "oo", "oomai", "oon", "oos", "ophe", "opia", "opia", "opoe", "opon", "opos", "ops", "ora", "oras", "oreo", "oria", "orimos", "oros", "orphos", "os", "osia", "osis", "osko", "oste", "ostos", "osyne", "otes", "oteuo", "othen", "otizo", "otle", "otos", "otus", "oul", "oulia", "ouni", "ouo", "outheo", "outhion", "oxazo", "oxos",
    "uios",
    "ygma", "ykos", "ylon", "ylos", "ymeo", "ymi", "ymia", "ymma", "ymos", "yn", "yno", "ynthos", "ynx", "yo", "ypte", "ypto", "yreo", "yria", "yrion", "yrna", "yroma", "yromai", "yros", "ys", "ysia", "ysmos", "ysso", "ystes", "yteros", "ythos", "ytos", "yx", "yxis", "yzo"]

hyboria_prefixs = [
    "agh", "alim", "aquil", "ar", "arg", "as",
    "bel", "boss", "bry",
    "cim", "cor",
    "dar",
    "er",
    "gal", "gun",
    "hal", "hyp", "hyr",
    "ian", "ir",
    "kass", "kesh", "khaur", "khaw", "khem", "khit", "khor", "khor", "khor", "kor", "kord", "koth", "kush", "kuth",
    "larsh", "lux",
    "mes",
    "nem", "num",
    "oph",
    "pte", "punt",
    "sam", "shad", "sham", "shang", "styg", "sukh", "sul",
    "tan", "taur", "tur", "tyb",
    "van", "vendh", "vil",
    "xa", "xuch", "xuth",
    "zam", "zarkh", "zing"]

hyboria_suffixs = [
    "a", "ai", "aja", "al", "ali", "an", "ane", "ar", "ara", "as", "ava",
    "borea", "boula",
    "chem",
    "der",
    "e", "eba", "ed", "en", "er", "eria", "es",
    "far",
    "gal", "gard",
    "heim",
    "i", "ia", "ia", "in", "ir", "ish", "ism", "istan",
    "jun",
    "kan",
    "land",
    "mer", "met",
    "og", "on", "onia", "or", "ora", "org", "os", "ot", "otl",
    "par", "pur",
    "ra",
    "san", "shem",
    "tana", "the", "thia", "thun", "tia",
    "uk", "ul", "un", "ur", "us",
    "ver",
    "ya", "yet",
    "zar"]

jdh_prefixs = [
    "ad", "ae", "af", "ag", "ai", "ak", "al", "am", "an", "ap", "ar", "as", "ash", "ath", "au", "av", "ay",
    "ba", "bad", "bal", "ban", "bar", "bath", "bed", "beg", "bel", "ben", "ber", "beth", "bil", "bin", "bir", "bith", "bod", "bof", "bog", "bol", "bon", "bor", "bow", "bul", "bum", "bun", "bur", "bus", "bush", "but", "by", "byd", "bye", "byl", "byr", "byth",
    "ca", "cae", "caf", "cag", "cai", "cal", "cam", "can", "car", "cat", "cath", "ce", "ced", "cel", "cem", "cen", "cer", "ceth", "cha", "chad", "chae", "chaf", "chag", "chai", "chak", "chal", "cham", "chan", "char", "chas", "chath", "chau", "chay", "che", "chea", "chel", "chem", "chen", "cher", "ches", "chet", "chev", "chex", "chey", "chi", "chia", "chie", "chil", "chim", "chin", "chir", "chis", "chit", "chiv", "cho", "chog", "chogh", "chol", "chom", "chon", "chor", "chot", "choth", "chu", "chud", "chugh", "chul", "chum", "chur", "chuth", "chux", "chyd", "chyl", "chyn", "chyr", "chys", "chyth", "chyu", "ci", "cia", "cil", "cim", "cin", "cip", "cir", "cis", "cish", "cit", "cith", "co", "cod", "coe", "cof", "cog", "col", "com", "con", "cop", "cor", "cos", "cot", "coth", "cu", "cuch", "cug", "cugh", "cui", "cul", "cum", "cun", "cup", "cur", "cus", "cush", "cut", "cuth", "cuw", "cy", "cyd", "cyf", "cyl", "cym", "cyr", "cyth",
    "da", "dach", "dad", "dae", "daf", "dag", "dagh", "dai", "dal", "dam", "dan", "dar", "das", "dash", "dath", "daw", "day", "de", "dea", "deb", "def", "deg", "degh", "del", "dem", "den", "der", "deth", "dev", "dew", "dex", "dey", "di", "dia", "dil", "dim", "din", "dir", "dith", "do", "doch", "doe", "dof", "dog", "dogh", "dol", "dom", "don", "doo", "dop", "dor", "dos", "dosh", "dot", "doth", "dou", "dov", "dow", "du", "duch", "due", "duf", "dug", "dugh", "dui", "dul", "dum", "dun", "dup", "dur", "dus", "dush", "duth", "duv", "duw", "duy", "dy", "dych", "dye", "dyf", "dyl", "dyr", "dyth",
    "ed", "ee", "ef", "eg", "ei", "ek", "el", "em", "en", "ep", "er", "es", "esh", "eth", "eu", "ev", "ey",
    "fa", "fach", "fad", "fae", "fagh", "fai", "fal", "fam", "fan", "far", "fas", "fath", "faw", "fax", "fay", "fe", "fea", "fec", "fed", "fel", "fem", "fen", "fer", "fes", "fesh", "feth", "few", "fey", "fi", "fia", "fil", "fim", "fin", "fir", "fith", "fo", "foch", "fod", "foe", "fog", "fogh", "fol", "fom", "fon", "for", "fox", "fu", "fuch", "fud", "fue", "fugh", "fui", "ful", "fum", "fun", "fur", "fus", "futh", "fuw", "fy", "fyl", "fym", "fyr", "fyx",
    "ga", "gab", "gach", "gad", "gae", "gaf", "gag", "gagh", "gah", "gai", "gal", "gam", "gan", "gap", "gar", "gas", "gash", "gath", "gau", "gav", "gaw", "gax", "gay", "ge", "ged", "gel", "gem", "gen", "geo", "ger", "geth", "gi", "gid", "gif", "gil", "gim", "gir", "go", "god", "goe", "gof", "gol", "gom", "gon", "goo", "gor", "goth", "gov", "gow", "gu", "gud", "gue", "guf", "gui", "gul", "gun", "gur", "gus", "gut", "guth", "guv", "guw", "guy", "gy", "gye", "gyf", "gygh", "gyl", "gyr", "gysh", "gyth",
    "ha", "hach", "had", "hae", "haf", "hag", "hagh", "hai", "hal", "ham", "han", "hap", "har", "has", "hash", "hat", "hath", "hau", "hav", "haw", "hax", "hay", "he", "hel", "hem", "her", "hew", "hex", "hi", "hig", "hil", "him", "hin", "hir", "his", "hit", "hith", "ho", "hoch", "hod", "hoe", "hof", "hog", "hogh", "hoh", "hol", "hom", "hon", "hor", "hoth", "hov", "how", "hox", "hu", "hue", "hugh", "hul", "hum", "hun", "hur", "huth", "huv", "huw", "hux", "hy", "hych", "hye", "hyf", "hyl", "hyr", "hyth", "hyx",
    "id", "ie", "if", "ig", "ii", "ik", "il", "im", "in", "ip", "ir", "is", "ish", "ith", "iv", "iy",
    "ka", "kach", "kad", "kae", "kag", "kagh", "kah", "kai", "kak", "kal", "kam", "kan", "kar", "kas", "kash", "kat", "kath", "kau", "kav", "kaw", "kay", "ke", "kea", "kef", "kegh", "kel", "kem", "ken", "ker", "kes", "kesh", "ket", "keth", "keu", "kew", "key", "ki", "kia", "kig", "kigh", "kil", "kim", "kin", "kip", "kir", "kis", "kish", "kit", "kith", "kiu", "kiv", "kiw", "ko", "koch", "kod", "koe", "kog", "kogh", "koh", "kol", "kom", "kon", "koo", "kop", "kor", "kos", "kosh", "kot", "koth", "kou", "kov", "kow", "kox", "ku", "kud", "kue", "kugh", "kui", "kul", "kum", "kup", "kur", "kus", "kush", "kuth", "kuv", "kuw", "ky", "kyr", "kys", "kysh",
    "la", "lad", "lae", "laf", "lag", "lagh", "lai", "lal", "lam", "lan", "lap", "lar", "las", "lash", "lat", "lath", "lav", "law", "lax", "lay", "le", "lea", "lech", "led", "lee", "leg", "lei", "lel", "lem", "len", "ler", "les", "lesh", "let", "leth", "lew", "lex", "li", "lich", "lid", "lie", "lif", "ligh", "lil", "lim", "lin", "lir", "lith", "lo", "loch", "lod", "loe", "lof", "log", "logh", "loi", "lol", "lom", "lon", "lor", "los", "losh", "lot", "loth", "low", "lox", "loy", "lu", "lud", "lue", "lug", "lugh", "lun", "lur", "lus", "lush", "luth", "lux", "ly", "lye", "lyn", "lyr", "lysh", "lyth", "lyw", "lyx",
    "ma", "mab", "mac", "mach", "mad", "mae", "mag", "magh", "mai", "mal", "mar", "mas", "mat", "math", "max", "may", "me", "mech", "med", "mee", "meg", "megh", "mei", "mel", "mem", "men", "mer", "mes", "mesh", "met", "meth", "meu", "mew", "mex", "mey", "mi", "mic", "mich", "mid", "mil", "min", "mir", "mis", "mish", "mith", "miw", "mo", "mob", "moch", "moe", "mogh", "mol", "mor", "mosh", "moth", "mu", "mud", "mue", "mug", "mugh", "mui", "mul", "mun", "mur", "mux", "my", "myc", "mych", "myd", "mygh", "myh", "myl", "myr", "mys", "mysh", "myth", "myx",
    "na", "nach", "nad", "nae", "nagh", "nai", "nal", "nam", "nan", "nap", "nar", "nas", "nay", "ne", "nec", "nel", "nem", "nen", "neth", "ni", "nil", "nim", "nin", "nir", "nith", "no", "noch", "nod", "noe", "noi", "nol", "nom", "non", "nor", "nos", "nosh", "not", "noth", "nov", "now", "nu", "nua", "nud", "nue", "nugh", "nui", "nul", "num", "nun", "nur", "ny", "nye", "nyl", "nyr",
    "od", "oe", "of", "og", "oi", "ok", "ol", "om", "on", "op", "or", "os", "osh", "oth", "ou", "ov",
    "pa", "pach", "pad", "pae", "pagh", "pai", "pal", "pam", "pan", "par", "pas", "pash", "pat", "path", "pav", "pax", "pe", "ped", "pel", "pen", "per", "pesh", "pet", "peth", "pi", "pil", "pin", "pir", "pis", "pish", "pith", "po", "pol", "pom", "pon", "pop", "por", "pos", "posh", "pot", "poth", "pox", "pu", "puc", "puch", "pud", "pugh", "pul", "pun", "pur", "push", "put", "py", "pyl", "pyn", "pyr",
    "ra", "rac", "rach", "rad", "rae", "raf", "rag", "ragh", "rai", "ral", "ram", "ran", "rap", "rar", "ras", "rash", "rath", "rau", "rav", "raw", "rax", "ray", "re", "red", "rei", "rel", "rem", "ren", "rer", "res", "resh", "ret", "reth", "reu", "rew", "rey", "ri", "ria", "rib", "rich", "rie", "righ", "ril", "rim", "rin", "rir", "ris", "rish", "rith", "riu", "riv", "riw", "ro", "roc", "roch", "rod", "roe", "rof", "rog", "rogh", "roi", "rol", "rom", "ron", "ror", "ros", "rosh", "roth", "rov", "row", "roy", "ru", "ruc", "ruch", "rud", "rue", "ruf", "rug", "rugh", "rui", "rul", "rum", "run", "rup", "rur", "rus", "rush", "rut", "ruth", "ruv", "ruw", "ry", "rya", "rych", "ryd", "rye", "ryh", "ryl", "ryn", "ryth",
    "sa", "sab", "sad", "sae", "saf", "sag", "sagh", "sal", "sam", "san", "sar", "sash", "sath", "sax", "se", "sed", "sel", "sem", "sen", "ser", "ses", "set", "seth", "sev", "sew", "sey", "sha", "shab", "shach", "shad", "shae", "shaf", "shag", "shagh", "shal", "sham", "shan", "shar", "shas", "shat", "shath", "shau", "shaw", "shax", "she", "shea", "shed", "shee", "shef", "shel", "shem", "shen", "sher", "shet", "shev", "shew", "shey", "shi", "shil", "shin", "shir", "shit", "sho", "shod", "shoe", "shol", "shon", "shoo", "shop", "shor", "shos", "shot", "shou", "show", "shu", "shuc", "shud", "shue", "shui", "shul", "shun", "shur", "shuv", "shuw", "shy", "shya", "shye", "shyf", "shyl", "shyn", "shyr", "si", "sid", "sie", "sil", "sim", "sin", "sir", "sis", "sith", "so", "sod", "soe", "sol", "som", "son", "sor", "sov", "sow", "sox", "su", "sub", "sud", "sue", "sugh", "sul", "sum", "sun", "sur", "sut", "suth", "suv", "sy", "sye", "syl", "syn", "syr", "syv", "syx",
    "ta", "tab", "tac", "tach", "tad", "tae", "taf", "tag", "tagh", "tai", "tak", "tal", "tam", "tan", "tap", "tar", "tas", "tash", "tat", "tath", "tau", "tav", "taw", "tax", "te", "tea", "tec", "tech", "ted", "tek", "tel", "tem", "ten", "ter", "tes", "tesh", "teth", "teu", "tew", "tha", "thab", "thach", "thad", "thae", "thag", "thai", "thal", "than", "thar", "thas", "that", "thau", "thav", "thax", "the", "thel", "them", "then", "ther", "thes", "thev", "thi", "thia", "thil", "thin", "thio", "thir", "this", "thiv", "tho", "thoch", "thod", "thoe", "thof", "thog", "thok", "thol", "thon", "thor", "thov", "thox", "thu", "thua", "thud", "thug", "thul", "thum", "thun", "thur", "thus", "thuv", "thux", "thuy", "thy", "thych", "thye", "thyl", "thym", "thyn", "thyr", "thys", "ti", "tia", "til", "tim", "tin", "tir", "tis", "to", "toc", "toch", "tod", "toe", "tol", "tom", "ton", "tor", "tos", "tosh", "toth", "tu", "tua", "tuc", "tuch", "tud", "tue", "tug", "tugh", "tui", "tul", "tum", "tun", "tur", "tus", "tush", "tuv", "tuw", "ty", "tya", "tych", "tye", "tyl", "tym", "tyn", "tyr", "tys", "tysh",
    "ud", "uf", "ug", "ui", "uk", "ul", "um", "un", "up", "ur", "us", "ush", "uth", "uv",
    "va", "vach", "vad", "vae", "vag", "vagh", "vai", "val", "vam", "van", "var", "vas", "vash", "vat", "vath", "vau", "vax", "ve", "vel", "ven", "ver", "ves", "vesh", "vey", "vi", "vid", "vil", "vin", "vir", "vish", "vo", "voch", "vog", "vogh", "vol", "vor", "vu", "vui", "vul", "vur", "vux", "vy", "vye", "vyl", "vym", "vyr", "vyx",
    "wa", "wach", "wad", "wae", "wai", "wal", "wan", "war", "was", "wath", "wau", "wax", "way", "we", "wel", "wen", "wer", "wes", "wesh", "weth", "weu", "wex", "wi", "wil", "win", "wir", "wis", "with", "wix", "wo", "woe", "wol", "wor", "wox", "wud", "wugh", "wul", "wur", "wuth", "wux", "wy", "wye", "wyl", "wyn", "wyr", "wyth", "wyx",
    "yd", "ye", "yf", "yg", "yk", "yl", "ym", "yn", "yp", "yr", "ys", "ysh", "yth", "yu", "yv"]

jdh_suffixs = [
    "a", "ach", "ad", "ae", "ag", "agh", "al", "am", "an", "ap", "ar", "as", "ash", "at", "ath", "aw", "ax", "ay",
    "bach", "bal", "ban", "bar", "bath", "bay", "bel", "ben", "ber", "beth", "bil", "bin", "bir", "bith", "bon", "bor", "bul", "bun", "bur", "by", "byn", "byr", "bysh", "byth",
    "cad", "cagh", "cal", "cam", "can", "car", "cath", "cel", "cen", "ceth", "cil", "cin", "cir", "cith", "col", "con", "cor", "cul", "cum", "cur", "cuth", "cy", "cyl", "cym", "cyn", "cyr", "cyth",
    "dach", "dagh", "dak", "dal", "dam", "dan", "dar", "dash", "dath", "day", "dek", "del", "den", "deth", "dil", "din", "dir", "dith", "doch", "dogh", "don", "dor", "doth", "duch", "dul", "dun", "dur", "dy", "dyl", "dyn", "dyr", "dyth",
    "e", "ea", "ed", "egh", "ek", "el", "em", "en", "er", "esh", "eth", "ey",
    "fa", "fach", "fal", "far", "fax", "fel", "fen", "feth", "fey", "fil", "fin", "fir", "foch", "fol", "for", "ful", "fur", "fy", "fya", "fyl", "fyn", "fyth",
    "g", "ga", "gal", "gam", "gan", "gar", "gash", "gath", "gay", "ge", "gee", "gel", "gen", "ger", "geth", "gia", "gil", "gin", "gir", "gith", "gol", "gon", "gor", "goth", "gud", "gul", "gum", "gun", "gur", "gwal", "gwar", "gwen", "gweth", "gwir", "gwyl", "gwyn", "gwyth", "gy", "gyl", "gyn", "gyr",
    "ha", "hach", "had", "hal", "ham", "han", "har", "hath", "hax", "hay", "hel", "hen", "hia", "hil", "hin", "hir", "hod", "hogh", "hond", "hor", "hoth", "hud", "hug", "hugh", "hul", "hum", "hun", "hur", "hwar", "hwath", "hwil", "hwir", "hyn", "hyr", "hyth",
    "i", "ia", "ic", "ich", "igh", "il", "im", "in", "ir", "ith",
    "ka", "kach", "kad", "kag", "kagh", "kal", "kam", "kan", "kar", "kas", "kash", "kath", "kel", "kem", "ken", "kesh", "keth", "kia", "kil", "kin", "kir", "kish", "kith", "koch", "kol", "kon", "kor", "koth", "kud", "kul", "kum", "kun", "kur", "kush", "kuth", "ky", "kya", "kye", "kygh", "kyh", "kyl", "kyn", "kyr", "kysh", "kyth",
    "la", "lac", "lach", "lad", "lag", "lagh", "lak", "lal", "lam", "lan", "lar", "las", "lash", "lat", "lath", "law", "lax", "lay", "le", "legh", "lel", "len", "les", "leth", "li", "lia", "lich", "lim", "lin", "lir", "lith", "loch", "lod", "logh", "lon", "lor", "loth", "lox", "lugh", "lum", "lur", "luth", "ly", "lya", "lyl", "lyn", "lyr", "lysh",
    "ma", "mach", "mad", "magh", "mal", "man", "mar", "mara", "maran", "mas", "mat", "math", "max", "me", "mea", "mel", "melen", "men", "mer", "meth", "mia", "mil", "min", "mir", "mira", "mith", "moch", "mogh", "mon", "mor", "moth", "much", "mud", "mul", "mum", "mun", "mur", "my", "myl", "myn", "myr", "myth",
    "na", "nal", "nam", "nan", "nar", "nath", "nel", "nen", "neth", "nia", "nil", "nim", "nin", "nir", "nish", "nith", "noch", "nod", "nogh", "nom", "non", "nor", "noth", "nox", "nua", "nul", "nun", "nur", "ny", "nya", "nyl", "nyr",
    "och", "od", "og", "ogh", "ol", "om", "on", "or", "orach", "oran", "oryth", "os", "osh", "ot", "oth", "ow", "owar", "owen", "oweth", "owil", "owin", "ox",
    "pa", "pal", "par", "path", "pel", "pen", "peth", "pia", "pil", "pin", "pir", "pith", "po", "pon", "por", "pul", "pun", "pus", "py", "pyl", "pyn", "pyr",
    "ra", "rach", "rad", "rae", "rag", "ragh", "ral", "ram", "ran", "rar", "ras", "rash", "rat", "rath", "raw", "rax", "ray", "rea", "red", "rel", "rem", "ren", "res", "resh", "reth", "rey", "ri", "ria", "ric", "rich", "ril", "rim", "rin", "ris", "rit", "roch", "rod", "rom", "ron", "ros", "roth", "row", "rud", "rul", "rush", "ruth", "ry", "rya", "rych", "ryl", "rym", "ryn", "ryr", "rys", "rysh", "ryth", "ryx",
    "sa", "sal", "sam", "san", "sar", "sash", "sath", "sax", "say", "sel", "sem", "sen", "seth", "sha", "shach", "shad", "shag", "shagh", "shal", "sham", "shan", "shar", "shas", "shat", "shath", "shaw", "shax", "shay", "she", "shea", "shee", "shel", "shem", "shen", "sheth", "shex", "shia", "shin", "shir", "shis", "shod", "shog", "shom", "shon", "shor", "shul", "shun", "shur", "shy", "shya", "shyl", "shym", "shyn", "shyr", "shyth", "sia", "sil", "sim", "sir", "sis", "sish", "sith", "son", "sor", "soth", "such", "sud", "sul", "sum", "sun", "sur", "sy", "syc", "syl", "syr", "sysh", "syth", "syx",
    "ta", "tac", "tach", "tad", "tag", "tal", "tam", "tan", "tar", "tas", "tash", "tath", "tea", "tech", "tel", "tem", "ten", "teth", "tha", "thac", "thach", "thad", "thag", "thal", "tham", "than", "thar", "thas", "thaw", "thay", "thea", "thed", "thel", "them", "then", "ther", "they", "thia", "thil", "thin", "thir", "this", "thish", "thoch", "thod", "thog", "thol", "thom", "thon", "thor", "thul", "thur", "thus", "thuy", "thy", "thya", "thyl", "thym", "thyr", "tia", "til", "tin", "tir", "tish", "toch", "ton", "tor", "tul", "tum", "tun", "tur", "tus", "tuth", "ty", "tya", "tye", "tyl", "tym", "tyn", "tyr", "tys", "tysh", "tyth",
    "u", "ua", "ud", "uk", "ul", "um", "un", "ur", "us", "ush",
    "va", "vad", "val", "van", "var", "vas", "vash", "vath", "vax", "ve", "vea", "vel", "ven", "vesh", "veth", "via", "vin", "von", "vor", "voth", "vul", "vun", "vy", "vya", "vyn", "vyth",
    "wa", "wach", "wad", "wae", "wal", "wald", "wan", "war", "ward", "was", "wash", "wath", "wax", "way", "we", "wea", "wed", "wel", "wen", "wer", "west", "weth", "wex", "wia", "wil", "win", "wir", "wish", "with", "wix", "won", "wor", "wul", "wulf", "wun", "wur", "wy", "wya", "wych", "wyl", "wym", "wyn", "wyr", "wys", "wysh", "wyth", "wyx",
    "y", "ya", "yc", "ych", "yd", "ye", "yl", "ym", "yn", "yr", "ys", "ysh", "yth", "yx"]

khuzdul_prefixs = [
    "ad", "agar", "agaz", "amen", "an", "ar", "az",
    "barak", "baraz", "baruk", "bin", "bizar", "bizul", "bul", "buzar",
    "d",
    "en", "erek",
    "garak", "gil", "gilin", "gog", "gor", "gorog", "gothol", "guzib",
    "ibin", "ibiz", "imik", "in", "inil", "iz", "izil", "izuk",
    "kal", "kek", "kel", "kelek", "kezan", "khel", "kheled", "khelek", "khim", "khimil", "khuz", "khuzor", "kibil", "kinil", "kul", "kun",
    "laral", "laruk", "lil", "luz",
    "mab", "mazar", "min", "mor", "moran", "moril", "muzar",
    "nibin", "nog", "nukul",
    "ran", "riz", "ror",
    "thak", "thor", "thuk", "thuz",
    "undur", "uz",
    "zibin", "zikul", "zok", "zul"]

khuzdul_suffixs = [
    "agul", "akar", "amen", "an", "arakh",
    "bar",
    "dithil", "dul", "dum", "duruk",
    "genek", "gib", "githin", "gog", "gol", "gul", "guluth", "gundag", "gundil", "guzar", "guzun",
    "lemen", "lib", "lizil", "lomol", "loth",
    "mab", "marak", "mazal", "mor", "moreth", "mormuk", "moruk", "mud", "mur",
    "nazar", "nigin", "niz", "nizil", "nuz", "nuzum",
    "thag", "thagar", "thak", "thibil", "thidul", "thin", "thizar", "thrin", "thuk",
    "u", "ubil", "ulin", "uzar", "uzun",
    "za", "zabin", "zad", "zadh", "zakar", "zal", "zalak", "zaluth", "zam", "zan", "zanik", "zanil", "zarak", "zaral", "zarath", "zath", "zebil", "zebin", "zeg", "zek", "zekel", "zerek", "zibith", "zikil", "zith", "zizil", "zokh", "zu", "zukum", "zuzin"]

male_1_prefixs = [
    "ache", "aim",
    "bald", "bear", "blush", "boar", "boast", "boil", "boni", "bower", "boy",
    "churl", "corn", "cuff",
    "dark", "dire", "dour", "dross", "dupe", "dusk", "dwar", "dwarf",
    "ebb", "el", "elf",
    "fag", "fate", "fay", "fell", "fly", "fowl",
    "gard", "gay", "gilt", "girth", "glut", "goad", "gold", "gorge", "grey", "groan",
    "haft", "hale", "haught", "hawk", "hiss", "hock", "hoof", "hook", "horn",
    "kin", "kith",
    "lank", "leaf", "lewd", "louse", "lure",
    "man", "mars", "meed", "moat", "mould", "muff", "muse",
    "not", "numb",
    "odd", "ooze", "ox",
    "pale", "port",
    "quid",
    "rau", "red", "rich", "rob", "rod", "rud", "ruff", "run", "rush",
    "scoff", "skew", "sky", "sly", "sow", "stave", "steed", "swar",
    "thor", "tort", "twig", "twit",
    "vain", "vent", "vile",
    "wail", "war", "whip", "wise", "worm",
    "yip"]

male_1_suffixs = [
    "ander", "ard",
    "bald", "ban", "baugh", "bert", "brand",
    "cas", "celot", "cent", "cester", "cott",
    "dane", "dard", "doch", "dolph", "don", "doric", "dower", "dred",
    "fird", "ford", "fram", "fred", "frid", "fried",
    "gal", "gard", "gernon", "gill", "gurd", "gus",
    "ham", "hard", "hart", "helm", "horne",
    "ister",
    "kild",
    "lan", "lard", "ley", "lisle", "loch",
    "man", "mar", "mas", "mon", "mond", "mour", "mund",
    "nald", "nard", "nath", "ney",
    "olas",
    "pold",
    "rad", "ram", "rard", "red", "rence", "reth", "rick", "ridge", "riel", "ron", "rone", "roth",
    "sander", "sard", "shall", "shaw", "son", "steen", "stone",
    "ter", "than", "ther", "thon", "thur", "ton", "tor", "tran", "tus",
    "ulf",
    "vald", "van", "vard", "ven", "vid", "vred",
    "wald", "wallader", "ward", "werth", "wig", "win", "wood",
    "yard"]

male_2_prefixs = [
    "ag", "al", "am", "an", "and", "ath",
    "brel", "bren",
    "cel", "con", "cor", "cul", "cur",
    "der", "don",
    "el", "en",
    "fal",
    "gal", "gar", "gav", "glan", "glar", "glen", "grim",
    "il", "in",
    "kar", "kel", "kol", "krel", "kren", "kul",
    "ol", "or",
    "rel", "rol", "roth",
    "tal", "tar", "tel", "tir",
    "ul", "ur"]

male_2_suffixs = [
    "ach", "al", "ald", "an", "and", "ath",
    "bran", "brand",
    "dan", "dar", "dor",
    "en", "end",
    "gar", "grim",
    "ir",
    "lan", "land", "lian",
    "nal", "nath",
    "owin", "owyn",
    "slade", "staff",
    "tar", "thar", "thor",
    "un", "und", "ur",
    "ward"]

male_3_prefixs = [
    "al", "am", "ar",
    "con",
    "dun",
    "fal",
    "gal", "grim",
    "mor",
    "ol",
    "rol",
    "tal", "tol"]

male_3_suffixs = [
    "ain", "and", "ann",
    "bar",
    "dain", "dan",
    "ion",
    "lain", "land", "lor",
    "mir",
    "owen",
    "rain", "ren",
    "slade", "sor",
    "thain", "thor",
    "uld",
    "ward", "wynn"]

male_4_prefixs = [
    "ab", "ach", "ad", "aeb", "aech", "aed", "ael", "aeld", "aen", "aend", "aer", "aeth", "aid", "ail", "aild", "aith", "al", "ald", "am", "an", "and", "ar", "arch", "ard", "arl", "arm", "arn", "arrb", "arth", "ath", "aul", "ayn", "ayth",
    "bad", "baech", "baer", "bain", "bair", "bal", "bald", "ban", "band", "bar", "barch", "bard", "bech", "ber", "berd", "bern", "brach", "brael", "braen", "brag", "bran", "brand", "bren", "brend", "bul", "bur", "byl", "byr",
    "cal", "cam", "car", "carn", "cath", "ced", "cel", "celd", "cen", "chain", "chen", "cher", "cir", "cith", "clad", "clar", "clun", "con", "cor", "crach", "craen", "craith", "cruch", "crul", "cruth", "cuch", "cul", "cun", "cur", "cuth", "cyl", "cyn", "cyr", "cyth",
    "dach", "daen", "daer", "dal", "dar", "dor", "dorn", "dul", "dun", "dur", "dwan", "dwar", "dwen", "dwend", "dwer", "dyn", "dyr",
    "ech", "ed", "el", "eld", "em", "en", "end", "er", "eth", "ey",
    "fael", "faer", "fal", "fald", "far", "fel", "feld", "fen", "fer", "fur",
    "gal", "gan", "gand", "gar", "gath", "gaw", "gel", "gor", "gral", "grud", "grul", "grun", "gruw", "gwaen", "gwaer", "gwal", "gwan", "gwar", "gwath", "gwen", "gwyl", "gwyth",
    "had", "haen", "haer", "hal", "han", "har", "hath", "hel", "hew", "hol", "hoth", "hul", "hur",
    "il", "in", "ind", "ir",
    "lach", "laech", "laer", "lain", "lair", "lan", "lar", "lath", "law", "lew", "loch", "lon", "lond", "lor", "lyn", "lyr", "lyth",
    "mach", "mael", "maen", "mal", "mar", "math", "mid", "mir", "mith", "mor", "myn", "myr",
    "nach", "nad", "nael", "nal", "nan", "nar", "nath", "nel", "nen", "ney", "nil", "nim", "nin", "nir", "noch", "non", "nor", "nul", "nyl", "nyth",
    "och", "og", "ol", "on", "or", "oth", "ow",
    "paen", "pal", "pan", "par", "path", "pel", "pen", "pir", "pwel", "pwen", "pwer", "pyl", "pyn", "pyr",
    "rad", "raen", "ral", "ram", "ran", "rand", "rar", "rath", "rel", "rey", "roch", "ror", "ryl", "ryn",
    "tad", "tael", "taen", "taer", "taeth", "tail", "tain", "tal", "tan", "tap", "tar", "taw", "ted", "tel", "thor", "thul", "tin", "tir", "tor", "trach", "traen", "tral", "tran", "traw", "trul", "tyl", "tyr", "tyw",
    "ul", "un", "ur", "urch", "url", "uth",
    "wal", "war", "wel", "wen", "wer", "weth", "wil", "wyd", "wyl", "wyn", "wyr", "wyth",
    "ych", "yl", "yld", "yn", "ynd", "yr", "yrn", "yw"]

male_4_suffixs = [
    "ach", "ad", "aech", "ael", "aeld", "aen", "aend", "aer", "aich", "ain", "air", "aith", "al", "ald", "alder", "an", "and", "ander", "ar", "ard", "arl", "arm", "arn", "arth", "ath", "athen", "ay", "ayl", "ayn",
    "baen", "baend", "bald",
    "dach", "dal", "dar", "darren", "doch", "dor", "doth",
    "ech", "ed", "el", "eld", "ellen", "en", "end", "ender", "er", "eth",
    "gar", "gon", "gond", "gor", "gwel", "gwen", "gyr",
    "hach", "han", "hand",
    "ich", "id", "il", "ild", "ilden", "in", "indor", "inen", "ir", "iren", "ith", "ithor",
    "lach", "lag", "lew", "lewen", "lor", "lyn", "lyr", "lyren", "lyth",
    "mach", "marth", "mor", "mord",
    "nad", "noch", "nor",
    "on", "ond", "or", "orel", "oreld", "oren", "oreth", "othen", "owen",
    "rach", "rail", "rain", "raind", "ran", "ranth", "ror", "roth",
    "thach", "thad", "thal", "thald", "thalor", "thin", "thir", "thor", "thyr",
    "ur", "urd", "urn", "urth",
    "wach", "wain", "waith", "wal", "war", "ward", "wel", "wen", "weth", "wor", "wyl", "wyn", "wyth",
    "yach", "yain", "yaith", "yel", "yeld", "yl", "yld", "yn", "ynd", "yr", "yth"]

name_1_prefixs = [
    "aber", "ache", "adag", "aef", "aeg", "ael", "aelf", "aeltar", "aem", "aemen", "aer", "aes", "aessar", "aethew", "aewil", "ag", "aglon", "aglor", "ail", "airen", "al", "alat", "aldreth", "allar", "almor", "am", "amnos", "ampir", "amteg", "anlath", "annur", "appor", "ar", "arel", "arras", "athel", "athor", "avan",
    "baer", "baeth", "baf", "balan", "bar", "baras", "beg", "bel", "ben", "blan", "blar", "blew", "blom", "bor", "boron", "brach", "bralsor", "brel", "bren", "bum", "bur",
    "cael", "caer", "caeroch", "caeron", "caf", "caid", "cal", "cam", "camas", "car", "caral", "cel", "celon", "ceneth", "cereth", "cew", "clam", "clar", "clel", "clen", "clon", "cloth", "clun", "color", "crew", "cron", "cul", "cur", "cwel",
    "dael", "daer", "dal", "dam", "deth", "doch", "doran", "dorn", "drath", "dref", "drol", "dun", "dun", "dunar", "dunil", "dur", "duras", "duren", "durul", "dwal", "dwar", "dwef", "dwen",
    "ealen", "ear", "ebcar", "ech", "eg", "eglir", "el", "elar", "elen", "elep", "eles", "eleth", "elew", "embor", "empir", "empul", "en", "endel", "epeth", "er", "ereb", "erech", "ered", "eref", "ereg", "erel", "erem", "eres", "ereth", "erew", "es", "eth", "evor", "eyas",
    "faer", "faerl", "faf", "falan", "far", "farad", "faras", "farf", "farn", "fas", "fel", "felan", "feloth", "fil", "fin", "flag", "flam", "flammaf", "fleb", "flew", "fley", "flin", "flith", "flod", "flof", "flor", "flud", "flun", "for", "foth", "frun", "fun",
    "gaem", "gaen", "gaer", "gaes", "gal", "gelem", "glad", "glaf", "glam", "glan", "glas", "gler", "gleth", "glew", "glog", "goch", "gog", "gor", "gorof", "gorth", "goth", "gurg", "gwal", "gwar", "gwaran", "gwen", "gweth", "gwim", "gwir",
    "hach", "haeg", "hal", "ham", "har", "hath", "hech", "hel", "heler", "hul", "hun", "hwar", "hwem", "hwil",
    "iar", "icar", "icil", "il", "ilcar", "ilcim", "ilcoth", "ilis", "ilmar", "ilon", "ilor", "ilrin", "im", "imon", "imril", "in", "ir", "iril", "irin", "iroth", "is", "isor", "ital", "itar", "itew", "ith", "itoch", "itom", "itul", "itur", "iw",
    "jal", "jan", "jarak", "julur",
    "kar", "karal", "karan", "kel", "keth", "kew", "khan", "khar", "khem", "khul", "klor", "kol", "kolod", "kor",
    "lach", "lad", "lael", "laen", "laf", "lal", "lan", "las", "leg", "lem", "ler", "leres", "lew", "llan", "llas", "llin", "llir", "lloch", "llud", "llugh", "lof", "lon", "lor", "lot", "lul", "luth",
    "maes", "mal", "man", "map", "mec", "mel", "mem", "men", "mer", "meth", "methen", "methil", "mew", "mich", "mif", "mil", "min", "mir", "mith", "mithar", "mog", "mol", "mor", "morp", "moth", "mul", "mur",
    "nal", "nas", "nav", "neb", "nec", "nem", "neth", "nil", "nim", "nin", "nip", "nod", "nog", "non", "nor", "nuf", "nun", "nur", "nush",
    "ocar", "ocil", "od", "og", "ol", "on", "or", "os", "oth",
    "pac", "pal", "pam", "par", "parad", "paral", "parath", "pel", "pem", "pen", "per", "plar", "plen", "ples", "pleth", "por", "pub", "pul", "pur", "pwar", "pweth", "pwil", "pwin",
    "quaer", "qual", "quan", "quen", "quil", "quor",
    "rach", "raeh", "ral", "ran", "rap", "rat", "rav", "rec", "ref", "rem", "reth", "rew", "rhal", "rhalar", "rhas", "rheg", "rhen", "rhil", "rhin", "rhip", "rhon", "rhov", "rhow", "rhum", "ril", "rim", "rith", "roch", "rog", "rom", "ror", "rot", "rov", "rud", "rul", "run", "rus", "ruth",
    "sal", "sar", "sec", "sel", "seth", "shal", "sham", "shan", "shar", "shel", "shes", "shon", "shul", "sil", "silen", "sir", "sith", "slad", "slag", "slem", "sleth", "slew", "slor", "slow", "slun", "slur", "sof", "sor", "sord", "sorn", "sun", "sur", "swan", "swas", "swil", "swim",
    "tach", "taef", "taeg", "tael", "taen", "taer", "tah", "tan", "tap", "tar", "tas", "tec", "tel", "tem", "ten", "ter", "tew", "thal", "thar", "thed", "thef", "them", "thet", "thew", "thog", "thor", "thul", "thun", "tif", "til", "tip", "tir", "toh", "ton", "tor", "tosh", "tow", "tral", "tran", "trel", "trew", "trim", "trip", "tris", "trog", "tuc", "tul", "tum", "tur", "turm",
    "ul", "ulas", "um", "un", "urag",
    "val", "valach", "var", "vash", "ven", "venen", "vor", "vosh", "vur",
    "wag", "wal", "war", "werel", "wereth", "wes", "weth", "wich", "wil", "win", "wol", "wor", "wun", "wuth",
    "ych", "yd", "yf", "yh", "yl", "yldor", "ylen", "yles", "yltar", "ym", "ymer", "yn", "ynych", "yp", "yr", "yrel", "yres", "yrhen", "yron", "ys", "yth", "ywen"]

name_1_middles = [
    "ael", "aem", "aer", "an", "ar",
    "el", "em", "eth",
    "fal", "far", "fir",
    "ir",
    "ow",
    "sel", "sem", "sen", "seth", "sor", "sul",
    "tal", "tan", "tar", "tyr",
    "ul", "un", "ur",
    "var"]

name_1_suffixs = [
    "a", "ac", "ace", "ach", "ack", "act", "ad", "adar", "adh", "ae", "aec", "aed", "aef", "aeg", "ael", "aem", "aen", "aer", "aere", "aes", "aeth", "af", "aff", "ag", "agh", "ah", "ai", "ail", "aild", "ailis", "ailn", "air", "aire", "al", "alas", "alch", "ald", "ale", "alea", "alf", "alis", "alla", "allia", "allith", "alm", "alp", "alt", "alth", "am", "amar", "amas", "amfe", "amn", "amp", "amth", "an", "and", "ang", "anga", "ange", "angea", "angia", "ant", "anth", "ap", "apar", "apas", "apus", "ar", "ara", "arc", "arda", "are", "area", "aria", "arl", "arla", "as", "ash", "ass", "at", "ate", "ath", "athea", "aur", "avar", "aw", "ay",
    "cel",
    "dan", "del", "dor", "doth", "dur",
    "ea", "eal", "eam", "eamb", "ean", "ear", "eara", "earas", "eare", "earen", "eareth", "earis", "eas", "eath", "ech", "eck", "ed", "edd", "ee", "eff", "eg", "ei", "el", "ela", "elar", "elas", "elc", "eld", "ele", "elea", "eleb", "elem", "elemb", "elf", "elg", "elia", "eliar", "elis", "elith", "elk", "ell", "elle", "elm", "eln", "elon", "elor", "eloth", "elt", "elth", "em", "eme", "emea", "emia", "emiar", "emn", "emp", "emt", "en", "enc", "end", "ent", "enth", "ep", "er", "erd", "ere", "erea", "erev", "erl", "ern", "ers", "ert", "erth", "es", "esh", "essa", "esse", "est", "ewd", "ewen", "ey",
    "fa", "far", "farf", "fe", "fia", "ful",
    "ga", "gal", "ge", "gia", "gor", "goth", "gur",
    "ia", "iach", "iad", "iah", "ial", "iald", "ialf", "iall", "ialle", "ialt", "ialth", "iamb", "iamme", "ian", "iand", "ianne", "iant", "iaph", "iar", "iare", "iarg", "iarh", "iarsh", "iarth", "ias", "iath", "ick", "iech", "ieff", "ieg", "iel", "ield", "ielle", "ielm", "ieln", "iem", "ien", "iend", "ient", "ienthe", "iesh", "iet", "ieth", "iff", "ift", "igh", "il", "ild", "ile", "ilin", "ilir", "ilith", "ill", "ille", "ilon", "ilor", "iloth", "ilt", "ilth", "im", "imar", "imb", "imp", "in", "ind", "inir", "inth", "ioc", "ioch", "iog", "iogh", "ion", "ior", "ios", "ioth", "ir", "iras", "irich", "iril", "irin", "irith", "irre", "is", "isla", "iss", "issa", "isse", "ith",
    "kelis", "kelor", "kor", "koth",
    "la", "las", "lath", "le", "lem", "loch", "lock", "lor",
    "ma", "man", "mar", "mara", "mas", "menos", "mer", "mere", "meth", "mor",
    "nach", "noch", "nor", "noth", "nul", "nur", "nura", "nure",
    "pal", "par", "para", "pare", "pir", "poth",
    "ra", "ras", "rash", "re", "rech", "rel", "reld", "rem", "ren", "ril", "ris", "roch", "ron", "roth", "run", "rut", "rych",
    "sa", "sar", "se", "sen", "shar", "sor",
    "tam", "tar", "thar", "tor",
    "uc", "uch", "ud", "ue", "uff", "ulare", "ulch", "uld", "ulm", "ulon", "ulth", "ulus", "umn", "un", "unne", "ur", "urr", "urre", "us",
    "va", "var", "ve", "velis", "veris",
    "wa", "war", "waran", "wen", "weth", "wi", "wil", "win",
    "ya", "yche", "ye", "yore", "yoth", "yrre", "ys", "ythe"]

name_2_prefixs = [
    "abbe", "ad", "aker", "al", "apel", "ar",
    "black", "blom", "bor", "bran", "by", "byr",
    "cal", "clay", "com",
    "for",
    "gal", "ger", "giron", "gor", "goran", "goren", "gun",
    "hall", "har", "her",
    "jan", "janne", "jar", "jarre", "jes", "johan", "jonas",
    "kahn", "kame", "keal", "kjel", "klem",
    "lanner", "lena",
    "malm", "man", "mats", "mel", "mor", "moran", "moras",
    "nemer",
    "olle",
    "radel", "rag", "rig",
    "sash", "shul", "silver", "slag", "styr",
    "tarn", "thor",
    "ulf", "um"]

name_2_suffixs = [
    "am", "an", "ander",
    "back", "backen", "bek", "bjorn", "bold",
    "cat",
    "dal", "dell", "der", "duin",
    "el", "er", "es",
    "falk", "fors",
    "graaf", "gren", "gut",
    "ki",
    "lata", "len", "ler", "lien", "lund",
    "man", "moor", "mor", "muid",
    "ne", "nom", "nusson",
    "pool",
    "ram", "re", "rell", "rick", "rin", "roir", "rooth",
    "sen", "steen", "stone",
    "ty",
    "well",
    "zom"]

new_prefixs = [
    "ab", "aban", "abant", "ach", "adn", "ael", "aeld", "aelt", "aen", "aend", "aer", "aerd", "aerm", "aerth", "aes", "aesk", "aest", "aew", "aff", "aich", "aim", "air", "al", "alf", "alm", "almir", "alp", "alth", "am", "amal", "amar", "amb", "amf", "amh", "amm", "amn", "amp", "amr", "amril", "ams", "amth", "amv", "an", "and", "ank", "ant", "anz", "ap", "apc", "apm", "aps", "apth", "ar", "arel", "arh", "arin", "ark", "arl", "arld", "arm", "armc", "armt", "arn", "arnd", "aron", "arth", "arv", "arw", "as", "asc", "ash", "ask", "asm", "ath", "aud", "aul", "aulc", "aulm", "auln", "ault", "aur", "av", "avaj", "avajd", "avajt", "avat", "avb", "avd", "aven", "avenb", "avsh", "avt", "aw",
    "b", "baav", "bad", "bal", "bald", "balg", "balm", "balog", "balth", "bar", "bard", "barf", "barg", "barl", "bart", "bartus", "bav", "bavol", "baym", "beam", "bear", "beer", "beg", "bel", "belar", "belc", "beld", "belf", "belg", "belj", "belm", "beln", "bels", "belt", "ber", "bern", "bes", "besid", "bew", "blan", "bland", "blar", "blarn", "blog", "bog", "bogn", "bol", "bolg", "bor", "borb", "borbin", "bord", "borg", "boror", "bororg", "boryn", "bran", "brant", "brel", "bren", "brod", "brog", "bros", "bryk", "bul", "bular", "bun", "bw", "byn", "byr", "byrn", "byrnh", "byt",
    "c", "cabm", "cadn", "caef", "caeh", "cael", "caem", "caer", "caes", "caeth", "caew", "caf", "cagh", "cah", "caigh", "cain", "cair", "cairh", "caith", "caiv", "cal", "calan", "calar", "calk", "calm", "cals", "calt", "cam", "camb", "camh", "camp", "can", "cand", "cant", "cap", "car", "card", "carf", "carg", "carh", "carl", "carm", "carn", "cars", "carv", "carw", "cas", "casc", "cask", "cast", "cat", "cath", "cav", "caw", "cef", "ceg", "cel", "celb", "celd", "celeg", "celn", "celow", "celt", "cer", "cern", "cew", "chal", "chald", "chan", "chang", "char", "chat", "chiim", "chul", "chum", "chumen", "chur", "churk", "cif", "cih", "cil", "cild", "cilm", "cim", "cin", "cir", "cith", "clar", "clas", "claw", "clen", "cler", "clew", "clif", "clor", "clorh", "clun", "cod", "con", "conal", "conan", "cond", "cor", "corh", "coris", "cors", "cow", "cral", "cralm", "crem", "crim", "crimb", "cris", "crog", "crot", "crul", "crun", "cryn", "cul", "culor", "culorg", "cus", "cush", "cusp", "cwal", "cwar", "cyr", "cyron",
    "d", "dach", "dakoth", "dan", "dank", "danris", "daor", "daorg", "dar", "dek", "dekdar", "desh", "deshk", "dev", "devash", "devn", "devon", "dith", "dog", "dogen", "dol", "dolan", "doln", "don", "dond", "dor", "dox", "draj", "drash", "drashv", "drav", "dravd", "dravj", "dren", "drul", "drun", "dur", "durak", "duran", "durf", "durin", "durk", "durn", "durof", "dys", "dyst",
    "eal", "ealw", "eam", "eamb", "ear", "earw", "eas", "east", "eath", "eb", "ebm", "ebon", "ecg", "ef", "eg", "egm", "eh", "eid", "eidol", "eis", "eiss", "el", "elar", "elf", "elfos", "elg", "ellis", "elm", "em", "emb", "emn", "emp", "empus", "en", "enb", "enbar", "eog", "er", "erab", "ered", "ereth", "eron", "erul", "erus", "es", "esc", "esd", "esf", "esg", "esj", "esk", "esm", "esn", "esp", "ess", "essem", "est", "esw", "eth", "ethar", "ew", "ex", "exp", "ez", "ezar",
    "f", "fag", "fair", "fairn", "fal", "falak", "falg", "falsh", "fam", "famb", "far", "faron", "fasc", "fask", "fasp", "fast", "fel", "feld", "felog", "felyw", "fen", "fend", "fenw", "fest", "few", "fey", "feyan", "ff", "ffaf", "ffal", "ffan", "ffar", "ffew", "ffil", "ffim", "fil", "fin", "fines", "fir", "fisc", "fish", "fisht", "fisk", "fism", "fist", "flam", "flamb", "flar", "flax", "flin", "flos", "fol", "folen", "fom", "fomen", "for", "ford", "fork", "forn", "fos", "fost", "fran", "frey", "fros", "fusc", "fust", "fyd", "fydon",
    "g", "gaj", "gal", "galt", "galth", "gam", "gamb", "gan", "gand", "gang", "gar", "gark", "garrol", "gasc", "gasf", "gasg", "gask", "gasm", "gasp", "gass", "gast", "gasv", "gel", "ger", "geram", "get", "getan", "gh", "ghog", "ghor", "ghut", "glam", "glamar", "glar", "glas", "glasc", "glask", "glasm", "glasp", "glast", "glew", "glid", "glin", "glism", "glisp", "glist", "glon", "glor", "gog", "gogh", "gol", "gor", "gord", "gorl", "gorm", "gorv", "gosf", "gosp", "gost", "gow", "gown", "grael", "grag", "gras", "grask", "grasp", "gres", "gresh", "grin", "gris", "grist", "grod", "grog", "gron", "grul", "gul", "gund", "gur", "gurb", "guy", "guyas", "guyasc", "gwar", "gwas", "gwen", "gweth", "gwil", "gwin", "gwir", "gwyn", "gyl", "gys", "gysan",
    "h", "haf", "hafm", "hal", "halc", "hald", "half", "halt", "ham", "hamb", "hamel", "hamp", "har", "harol", "harold", "hask", "hasp", "hast", "hav", "haver", "havers", "haverst", "havor", "havorn", "hel", "helas", "helm", "her", "heral", "herald", "hew", "hir", "hiras", "hof", "hofg", "hofm", "hog", "hogen", "hor", "horoth", "hosh", "hot", "hoth", "hothor", "hothos", "hran", "hrand", "hrof", "hrol", "hur", "hus", "husc",
    "iam", "iamb", "iamp", "iar", "iars", "ich", "ichar", "id", "idiyv", "ij", "ijv", "il", "illew", "illon", "ilour", "im", "imb", "imer", "imor", "imp", "in", "ing", "ior", "iorak", "ipm", "ipn", "ips", "ipth", "ir", "iruar", "is", "isc", "ish", "ishg", "ishm", "isht", "isk", "ism", "isp", "ist", "it", "it", "ith", "ithul", "its", "itus", "iv", "iven", "iw", "ix", "ixon", "iyl", "iylar",
    "j", "jaim", "jal", "jalk", "jalm", "jalt", "jam", "jamp", "jams", "jar", "jarb", "jarl", "jas", "jasd", "jasf", "jask", "jasm", "jasp", "jast", "jat", "jatar", "jays", "jen", "jenal", "jer", "jern", "jes", "jesc", "jest", "jom", "jomel", "jor", "jorun", "jotun", "jun", "jur", "jural", "juralg",
    "k", "kad", "kadaen", "kaden", "kaj", "kajd", "kajf", "kal", "kalix", "kan", "kant", "kantyr", "kar", "kard", "karil", "karon", "ked", "kel", "ker", "keron", "kerq", "kes", "kest", "kew", "kh", "khal", "kham", "khar", "khaz", "khel", "khem", "khim", "khor", "khug", "khul", "khuz", "kier", "kil", "kild", "kiln", "kim", "kiman", "kir", "kirin", "kirk", "koh", "kohel", "kor", "koy", "kral", "kran", "kras", "krasod", "krin", "krul", "krush", "kul", "kulak", "kulan", "kuld", "kulth", "kuor", "kus", "kusk", "kyn", "kynac", "kynd", "kyr", "kyt",
    "l", "laen", "laend", "laer", "lah", "lahk", "lal", "lan", "land", "lar", "las", "lasc", "lasp", "lass", "last", "lath", "leb", "lebyn", "leg", "lem", "leman", "lemand", "lemar", "len", "lend", "lent", "ler", "lerym", "less", "leth", "llach", "llag", "llan", "lland", "llar", "lleg", "llew", "llir", "llun", "lor", "loren", "los", "losyl", "lug", "lyd", "lydek",
    "m", "mab", "mabin", "mal", "mald", "malim", "malm", "malon", "malv", "map", "mar", "mas", "masm", "math", "mathor", "mel", "meld", "melm", "mer", "merc", "merel", "meren", "mereth", "merw", "mes", "mesh", "met", "meth", "methan", "meton", "mew", "mewyn", "mik", "mikor", "mil", "mild", "mir", "mirh", "miril", "mirith", "mish", "miss", "mith", "moch", "mochm", "mogh", "mol", "molt", "mom", "mor", "moran", "morc", "morch", "mord", "moreg", "moren", "morg", "morh", "morin", "moryn", "mosc", "mosh", "mosk", "moth", "mow", "mul", "mur", "mus", "musar", "musg", "musk", "myk", "mykel", "myr", "myrh",
    "n", "nac", "nar", "nars", "naug", "neb", "nec", "nel", "nen", "neng", "nex", "ney", "nil", "nim", "niol", "nir", "nish", "nog", "nogel", "nol", "nold", "nolf", "nolt", "nom", "nomik", "nor", "nord", "norm", "norn", "nos", "nud", "nul", "nult", "num", "numb", "numn", "nur", "nurin", "nyf", "nyft", "nym", "nymon",
    "ob", "oben", "och", "od", "odren", "og", "ogh", "ogm", "ogn", "ognur", "oj", "ojar", "ojarn", "ol", "old", "olf", "olg", "om", "omp", "on", "ond", "onel", "oner", "op", "opal", "opar", "oplex", "oq", "or", "oral", "oran", "orb", "ord", "orf", "org", "orgh", "orh", "orhan", "orian", "orj", "orl", "orm", "orn", "ornal", "ornel", "orol", "orqual", "orques", "orquon", "orth", "orv", "orw", "orz", "os", "osc", "osp", "oss", "ost", "oth", "ow",
    "p", "pac", "pah", "paj", "pal", "palan", "palar", "palas", "pald", "palg", "palt", "pan", "panj", "par", "pas", "pasc", "pasik", "path", "pav", "pel", "pelax", "pelon", "pem", "pemb", "pen", "pend", "pent", "per", "perth", "perw", "ph", "phal", "phaon", "phar", "phew", "phog", "phor", "phos", "phul", "pil", "pilor", "pin", "pir", "plac", "plod", "plon", "plug", "pol", "polon", "pon", "pond", "ponj", "por", "porel", "pos", "post", "prel", "prew", "prun", "pud", "puff", "pul", "pulm", "pux", "puxt", "pyl", "pys", "pysk",
    "qel", "qeloth", "qir", "qirin", "quad", "quaff", "quag", "qual", "quan", "quand", "quanf", "quanj", "quant", "quar", "quej", "quel", "quen", "quer", "ques", "quest", "quib", "quich", "quil", "quin", "quit", "quor", "quot",
    "r", "raf", "rafir", "rail", "raim", "rain", "raith", "raj", "rajn", "rajp", "rajv", "ral", "rald", "ralf", "ralg", "ralm", "ralp", "ralt", "ralv", "ram", "ramb", "ramon", "ramp", "ran", "rand", "rank", "rant", "ras", "rasc", "rasp", "rasul", "rat", "rath", "rav", "ravir", "raw", "rean", "rem", "ren", "renal", "renald", "rend", "reth", "rethan", "rew", "rh", "rhan", "rhap", "rhas", "rhin", "rhod", "rhomb", "rhomp", "rhon", "rhos", "rhov", "rhow", "rhozh", "rhyl", "rid", "rif", "ril", "rim", "rimf", "rin", "rind", "rir", "ris", "risc", "rist", "rith", "roc", "roch", "rock", "rog", "rogar", "rogard", "rogyr", "rol", "rold", "rom", "romb", "ron", "rond", "ros", "roth", "rother", "row", "rowyn", "rox", "roxin", "ruch", "rud", "ruech", "ruem", "rul", "rular", "rum", "rumt", "rumtif", "rus", "rush", "rust",
    "s", "sab", "sabal", "sal", "salaz", "sam", "samb", "samp", "san", "sand", "sanj", "sanv", "sar", "sarc", "sard", "sarn", "sax", "saxb", "scab", "scael", "scaes", "scan", "scand", "scap", "scar", "scath", "scol", "scum", "scumb", "scun", "scur", "sef", "seft", "sem", "semb", "sen", "send", "ser", "seth", "sew", "sh", "shad", "shaf", "shaft", "shag", "shal", "shalc", "shald", "shalt", "sham", "shamp", "shan", "shand", "shang", "shann", "shar", "shard", "sharm", "shat", "shath", "shav", "shaw", "shel", "shem", "shen", "sher", "sherid", "shiv", "shivj", "shor", "show", "shud", "shul", "shulv", "shun", "shund", "sid", "sif", "sij", "sil", "silk", "sim", "simb", "simp", "sin", "sind", "sint", "sir", "sirh", "sith", "siv", "skaf", "skag", "skagh", "skal", "skan", "skand", "skar", "skel", "skes", "skew", "skol", "skor", "skul", "skun", "skund", "skuth", "skyn", "skyr", "skyt", "slach", "slack", "slaer", "slaf", "slag", "slam", "slan", "sland", "slar", "sleg", "sleth", "slew", "slob", "slod", "slogh", "slun", "slund", "slur", "slurd", "slurg", "slurm", "soh", "sohl", "spal", "spam", "spar", "spic", "spif", "spin", "spind", "spok", "spun", "spur", "spurf", "spurg", "spurm", "spurn", "sron", "srond", "st", "stac", "staf", "stal", "star", "stear", "steard", "stel", "sten", "steng", "stren", "strep", "stun", "stur", "sul", "sulem", "sulf", "sulin", "sulth", "sum", "sumen", "sumend", "sun", "sund", "sur", "surd", "surf", "swan", "swil", "swin", "swir",
    "t", "tadj", "taj", "tajd", "tajk", "tajm", "tam", "tan", "tanar", "tannig", "tar", "tarh", "tarm", "tarn", "tas", "tasc", "task", "tasp", "tav", "tavd", "tavj", "taw", "tec", "tef", "teg", "teh", "tel", "teles", "telest", "telf", "telm", "telp", "telyn", "tem", "temb", "temm", "temp", "ten", "tend", "ter", "teras", "terasp", "terh", "teris", "tes", "tesp", "test", "teth", "tethan", "th", "thac", "thach", "thagh", "thail", "thain", "thair", "thal", "than", "thar", "tharor", "thas", "thast", "thastm", "thaw", "thec", "theg", "thel", "them", "themin", "then", "thend", "theol", "theon", "theor", "thom", "thomar", "thor", "thoran", "thos", "thosque", "thul", "thulin", "thus", "thusk", "thuv", "thyn", "tif", "tig", "tih", "til", "tim", "timb", "tiol", "tip", "tir", "tith", "tlil", "tob", "tobel", "tol", "tom", "tomb", "tomp", "ton", "tonam", "tor", "torb", "torek", "tort", "tov", "trag", "tral", "tram", "tramb", "tramg", "tramt", "tras", "trasc", "trask", "trog", "troh", "trohm", "trol", "tron", "trond", "truc", "trul", "trus", "trusc", "trust", "tryn", "tuk", "tukyn", "tul", "tulg", "tulk", "tulsc", "tult", "tulv", "tun", "tunt", "tup", "tur", "turl", "tusc", "tuv", "tyes",
    "uj", "ujd", "ul", "ulyash", "um", "umb", "umn", "ump", "ums", "un", "unc", "und", "unir", "unth", "ur", "urh", "urij", "urul", "us", "usc", "usf", "usg", "usk", "ust", "uth", "uv", "uw",
    "v", "vaas", "vad", "vadj", "vadk", "vads", "vaj", "vajs", "val", "valan", "valar", "valas", "valath", "valris", "vam", "vamp", "van", "vand", "var", "varg", "varin", "vas", "vasd", "vash", "vashd", "vashk", "vasht", "vasj", "vask", "vasth", "ver", "veron", "ves", "vest", "vin", "vind", "vir", "virk", "virkan", "vog", "vor", "vul", "vulf", "vuln", "vulv",
    "w", "wen", "weng", "wer", "werth", "wh", "wham", "whar", "what", "when", "wher", "whir", "whis", "wig", "wil", "wild", "wilt", "wim", "wimp", "wims", "win", "wind", "wit", "witch", "with", "wom", "womb", "wor", "wul", "wur", "wurak", "wurl", "wurm", "wurs", "wurt", "wurv", "wyl", "wylan", "wyland", "wyr", "wyrm",
    "x", "xach", "xan", "xar", "xec", "xen", "xer", "xon", "xor", "xorg", "xoth", "xug", "xugh", "xul", "xur", "xyl",
    "y", "yael", "yaer", "yal", "yalt", "yam", "yd", "ydem", "yel", "yen", "yend", "yer", "yerh", "yesp", "yess", "yest", "yeth", "yew", "yil", "yin", "yink", "yinok", "yl", "yod", "yof", "yogh", "yoh", "yol", "yon", "yonc", "yond", "yor", "yp", "yps", "ypsil", "yr", "yrp", "yrpar", "ys", "ysm", "ysman", "yug", "yugal", "yugh", "yum", "yumb", "yumgh", "yun", "yunt", "yurd", "yurf", "yurg", "yurh", "yurj", "yurk", "yurm", "yurp", "yuw", "yuwan",
    "z", "zaub", "zauber", "zh", "zir", "ziriv", "zirivk", "zor", "zord", "zos", "zosm"]

new_suffixs = [
    "a", "aal", "aalk", "aang", "aari", "aasun", "aaven", "aax", "abon", "ac", "ach", "ack", "ad", "adh", "ador", "ae", "ael", "aen", "aena", "aend", "aenha", "aff", "affon", "afir", "ag", "age", "agg", "agh", "agur", "ai", "ai", "ail", "ailub", "aim", "aiman", "ain", "ainey", "air", "airn", "aj", "ak", "akan", "akang", "aki", "al", "alaza", "ald", "aldo", "alf", "alfex", "alg", "algi", "alim", "alion", "alior", "alioth", "alix", "all", "allion", "allyo", "alm", "almyk", "alog", "alon", "alre", "alris", "alt", "alth", "althan", "alto", "alvin", "am", "ama", "amai", "amb", "ambir", "amel", "ammon", "amon", "amor", "amse", "an", "ana", "anach", "anaki", "anan", "anar", "anara", "and", "andae", "andra", "ang", "ange", "ani", "ann", "annel", "anris", "ant", "ante", "anth", "antys", "anyr", "aon", "aor", "aorgor", "ar", "ara", "ard", "arda", "ardan", "ardy", "are", "arel", "aren", "arend", "areor", "arey", "areyn", "arg", "argh", "ari", "aric", "arin", "arion", "aris", "ark", "arle", "arley", "arn", "arold", "aron", "arone", "arr", "arrol", "arryn", "arsang", "arse", "arth", "artok", "artuss", "aruk", "aryk", "as", "ash", "asik", "asp", "assa", "ast", "astman", "asul", "asun", "atar", "ath", "athog", "au", "auber", "auin", "aven", "avir", "avorn", "ax", "axas", "axby", "axh", "axx", "ay", "aym", "aymon", "ayn", "ayse", "aysek", "aza", "azh", "azi",
    "e", "ea", "ean", "eann", "eard", "eardan", "ebon", "ebrin", "ebyn", "ech", "echa", "edra", "edrik", "eiss", "eissa", "ekan", "el", "ela", "elass", "elassa", "elax", "elg", "elgh", "elgin", "elia", "eliage", "elias", "elkin", "ell", "ellion", "ellis", "ellisa", "eloth", "eloto", "elyn", "elyr", "em", "emal", "eman", "emand", "emar", "emer", "emmler", "en", "ena", "enal", "enald", "enby", "end", "endar", "ende", "eng", "enge", "engor", "enia", "enium", "enla", "enlon", "enlor", "enloth", "enol", "enyr", "eog", "eor", "eora", "er", "erale", "eran", "eras", "erasp", "eray", "erayn", "eria", "erida", "eridan", "eris", "erise", "ern", "erna", "ernan", "eron", "erone", "erq", "erqod", "erque", "erth", "erwe", "erwin", "erym", "es", "esca", "escea", "ese", "esea", "esh", "eshan", "eshe", "eshea", "ess", "essa", "essan", "essar", "esse", "est", "este", "ester", "estia", "et", "etan", "eth", "ethan", "ethar", "ethia", "ethian", "eton", "eugir", "eva", "eve", "evon", "ewen", "ewyn", "ex", "exus", "exyn", "ey", "eyan", "eyn", "ezar",
    "i", "ia", "iage", "ian", "iana", "iand", "ias", "iasse", "ic", "ice", "ich", "ichar", "ick", "icke", "ida", "idan", "ier", "iere", "ieron", "ifer", "ifusel", "ig", "igan", "igh", "ik", "ikori", "ikos", "il", "ila", "ilan", "ile", "ill", "illar", "ille", "illon", "ilok", "ilon", "ilor", "ilos", "iloth", "ilour", "iloura", "ilub", "im", "im", "iman", "imen", "imen", "imer", "imeria", "imm", "immer", "in", "inai", "inak", "ind", "iness", "ineth", "iney", "inka", "inn", "inok", "inor", "inuss", "iol", "iola", "ion", "ior", "iora", "iorak", "ir", "iraj", "irazi", "ire", "irin", "irn", "is", "isa", "isar", "isen", "isha", "ison", "isone", "isonen", "iss", "issa", "ist", "iste", "iston", "istyr", "ith", "itus", "ium", "ive", "iven", "ivkari", "ix", "ixon", "iyva",
    "laki", "lan", "lana", "land", "lande", "landra", "lane", "lani", "lar", "lare", "larhe", "lari", "laris", "laron", "larre", "lary", "laryk", "las", "lase", "lassa", "last", "late", "lath", "lauin", "laur", "law", "lawe", "laxx", "lay", "laye", "laza", "les", "lesk", "lesp", "less", "lessa", "lesse", "leste", "lester", "leu", "leugir", "lew", "lewe", "lex", "lexyn", "ley", "leye", "li", "lia", "liad", "liaff", "liage", "liagh", "lialle", "lian", "liar", "liare", "lias", "liath", "liaw", "lice", "lich", "lick", "lid", "liffe", "ligh", "lik", "lil", "lille", "lilok", "lim", "limb", "lin", "lind", "lion", "liond", "lior", "liose", "lioth", "lisa", "liss", "lok", "lon", "lonian", "lorgh", "lorgor", "lorus", "loss", "loto", "lour", "loura", "ly", "lya", "lyn", "lyo", "lyr", "lywan",
    "o", "oa", "oc", "och", "ock", "od", "oder", "odh", "odin", "odur", "oe", "ofay", "off", "offe", "og", "ogan", "ogard", "ogel", "ogen", "ogh", "ogli", "ogyr", "ohel", "ohman", "oisha", "ok", "oki", "ol", "ola", "olan", "olani", "old", "olde", "oldin", "olen", "olle", "ollor", "ollyn", "olon", "oltar", "olth", "om", "omar", "omas", "omath", "omin", "omm", "on", "onam", "once", "ond", "ondi", "one", "onel", "onen", "onian", "onle", "only", "onse", "onth", "ood", "oon", "oor", "oosh", "ooth", "or", "orak", "oran", "oranyr", "orb", "ord", "ordan", "ordon", "ordyn", "ore", "oreg", "orel", "oren", "org", "orga", "orgash", "orge", "orgen", "orgor", "orhan", "orhe", "ori", "origh", "orla", "orley", "orliss", "orn", "ornal", "ornel", "orot", "orrin", "ors", "orus", "orvan", "oryn", "os", "ose", "osh", "osia", "osk", "osmyr", "osque", "oss", "osse", "ost", "osten", "osyl", "oth", "othal", "othe", "other", "otil", "oto", "ottr", "our", "oura", "ove", "owe", "owyn", "ox", "oxle", "oxley", "oy", "ozh", "ozhann",
    "ra", "raax", "rabon", "rack", "rae", "rael", "raeld", "raele", "rag", "ragh", "ralg", "rama", "ramai", "ramon", "ran", "range", "rant", "rante", "ranth", "ranyr", "ras", "rasp", "ray", "rayn", "razi", "re", "reck", "reg", "rekan", "reme", "remer", "ren", "rene", "renol", "reo", "reor", "resh", "resha", "reshan", "rey", "reyn", "ri", "ria", "ric", "rid", "ridan", "rik", "ril", "rill", "rillar", "rilon", "rim", "rimm", "rin", "rinai", "rine", "rineth", "rinn", "rinor", "rion", "ris", "risar", "rise", "rist", "riston", "rod", "roder", "rofay", "roff", "roff", "rog", "rogan", "rogli", "rohman", "roki", "rol", "rold", "rolf", "ron", "rond", "rondi", "rone", "rorg", "rorgor", "rosia", "rot", "rotil", "roy", "rul", "ruld", "rule", "rum", "run", "rund", "rune", "runt", "rus", "rush", "rust", "ryk", "ryn", "rynne", "rynoth", "rys",
    "sule", "sulini",
    "u", "uar", "uaric", "uau", "uber", "ue", "uecha", "ugal", "ugir", "ugyr", "uin", "ukyn", "ul", "ulan", "ulana", "uld", "uldir", "ulem", "ulf", "ulfea", "ulfean", "ulfen", "ulli", "ulo", "ulth", "ulthea", "ulthon", "ulya", "um", "uma", "umarr", "ume", "umen", "und", "under", "une", "unir", "uor", "ur", "ura", "urak", "ural", "uralg", "urbak", "urd", "ure", "urk", "url", "urlik", "uroff", "us", "usa", "usarr", "use", "usel", "ush", "usk", "uskan", "uss", "ust", "ut", "utas", "uth", "utha", "uun", "uwan", "uwe", "ux", "uxtan",
    "y", "ya", "yd", "ydek", "ydon", "ye", "yes", "yft", "yftan", "yk", "ykel", "yl", "yla", "ylan", "yland", "ylandra", "ylia", "ylian", "ylon", "ym", "ymon", "yn", "yna", "ynac", "yne", "ynla", "ynlas", "ynne", "ynoth", "yo", "yr", "yri", "yrne", "yrone", "yrpar", "ys", "ysa", "ysan", "yse", "ysek", "ysk", "ysma", "ysman", "yste", "ysten", "ytor", "yva", "ywa", "ywan"]

shadow_prefixs = [
    "ab", "abant", "al", "alf", "alm", "almir", "alth", "am", "amb", "amm", "amr", "amril", "amth", "an", "and", "ar", "arel", "arin", "aron", "aven", "avenb",
    "b", "baav", "bal", "balog", "bar", "barl", "bart", "bartus", "bav", "bavol", "baym", "bel", "belar", "ber", "bern", "bes", "besid", "bol", "bor", "borb", "borbin", "bord", "borg", "boror", "bororg", "boryn", "bran", "brant", "brod", "brog", "bros", "bryk", "bul", "bular", "byn", "byrn", "byrnh", "byt",
    "c", "chan", "chang", "char", "chiim", "chum", "chumen", "chur", "churk", "cod", "cor", "coris", "cors", "cralm", "crem", "crim", "crog", "crot", "cryn", "cul", "culor", "culorg", "cyr", "cyron",
    "d", "dak", "dakoth", "dan", "danris", "daor", "daorg", "dar", "dek", "dekdar", "dev", "devon", "dit", "dog", "dogen", "dol", "dolan", "don", "dox", "dren", "drul", "drun", "dur", "durak", "duran", "durof", "dys", "dyst",
    "eb", "ebon", "ef", "eid", "eidol", "eis", "eiss", "el", "elf", "elfos", "elg", "ellis", "em", "emp", "empus", "en", "enb", "enbar", "eog", "er", "erab", "eron", "eth", "ethar", "ex", "exp", "ez", "ezar",
    "f", "fag", "fair", "fairn", "fal", "falak", "falg", "falsh", "far", "faron", "fel", "felog", "felyw", "fen", "fenw", "fey", "feyan", "ff", "fin", "fines", "flax", "fol", "folen", "fos", "fost", "fyd", "fydon",
    "g", "gal", "galt", "galth", "gam", "gamb", "gan", "gar", "gark", "garrol", "ger", "geram", "get", "getan", "gh", "ghut", "gor", "gorl", "gorv", "grael", "grag", "gresh", "grin", "gris", "grist", "gul", "gur", "gurb", "guy", "guyas", "guyasc", "gwyn", "gys", "gysan",
    "h", "haf", "hafm", "ham", "hamel", "har", "harol", "harold", "hav", "haver", "havers", "haverst", "havor", "havorn", "hel", "helas", "her", "heral", "herald", "hir", "hiraz", "hof", "hofg", "hog", "hogen", "hor", "horot", "hosh", "hot", "hoth", "hothor", "hothorg", "hran", "hrang",
    "iar", "iars", "ich", "ichar", "id", "idiyv", "il", "illon", "ilour", "im", "imer", "ior", "iorak", "ir", "iruar", "it", "ith", "ithl", "itl", "itus", "iv", "iven", "ix", "ixon", "iyl", "iylar",
    "j", "jaim", "jam", "jams", "jat", "jatar", "jays", "jen", "jenal", "jer", "jom", "jomel", "jor", "jur", "jural", "juralg",
    "k", "kad", "kadaen", "kaden", "kal", "kalix", "kan", "kant", "kantyr", "kar", "kard", "karil", "ked", "ker", "keron", "kerq", "kh", "kham", "khug", "kier", "kim", "kiman", "kir", "kirin", "koh", "kohel", "kor", "koy", "kras", "krasod", "krin", "krush", "kul", "kulak", "kulan", "kuld", "kulth", "kuor", "kus", "kusk", "kyn", "kynac", "kyr", "kyt",
    "l", "laen", "lah", "lahk", "lath", "leb", "lebyn", "lem", "leman", "lemand", "lemar", "ler", "lerym", "lor", "loren", "los", "losyl", "lug", "lyd", "lydek",
    "m", "mal", "malim", "malon", "malv", "met", "meth", "methan", "meton", "mew", "mewyn", "mik", "mikor", "moish", "mol", "molt", "mor", "moran", "mord", "moreg", "moren", "morg", "morin", "moryn", "mur", "mus", "musar", "myk", "mykel", "myr",
    "n", "nar", "nars", "neb", "nel", "nen", "neng", "nex", "ney", "nim", "niol", "nish", "nog", "nogel", "nom", "nomik", "num", "nur", "nurin", "nyf", "nyft", "nym", "nymon",
    "ob", "oben", "od", "odren", "og", "ogn", "ognur", "oj", "ojar", "ojarn", "on", "onel", "oner", "op", "opl", "oplex", "or", "oral", "oran", "orh", "orhan", "orian", "orn", "ornal", "ornel", "orol",
    "p", "pas", "pasik", "pel", "pelax", "pelon", "per", "perw", "ph", "phaon", "pil", "pilor", "plon", "pol", "polon", "por", "porel", "pos", "post", "pux", "puxt", "pyl", "pys", "pysk",
    "qel", "qeloth", "qir", "qirin",
    "r", "raf", "rafir", "rain", "ral", "rald", "ram", "ramon", "ran", "rand", "ras", "rasul", "rath", "rav", "ravir", "rean", "ren", "renal", "renald", "reth", "rethan", "rh", "rhin", "rhozh", "rhyl", "rog", "rogar", "rogard", "rogyr", "rol", "rold", "roth", "rother", "row", "rowyn", "rox", "roxin", "ruech", "ruem", "rul", "rular", "rum", "rumt", "rumtif",
    "s", "sab", "sabal", "sal", "salaz", "sax", "saxb", "sef", "seft", "ser", "sh", "shaal", "shaalk", "sher", "sherid", "soh", "sohl", "sron", "srond", "st", "staf", "stear", "steard", "sten", "steng", "sul", "sulem", "sulf", "sulin", "sulth", "sum", "sumen", "sumend", "sun", "sund",
    "t", "tan", "tanar", "tannig", "tas", "tel", "teles", "telest", "telyn", "ter", "teras", "terasp", "teris", "tes", "teth", "tethan", "th", "thail", "thar", "tharor", "thas", "thast", "thastm", "them", "themin", "thom", "thomar", "thor", "thoran", "thos", "thosque", "thus", "thusk", "thyn", "tiol", "tlil", "tob", "tobel", "ton", "tonam", "tor", "torb", "torek", "tort", "tov", "trag", "trog", "troh", "trohm", "tryn", "tuk", "tukyn", "tur", "turl", "tyes",
    "ul", "ulyash", "un", "unir", "ur", "urul", "uth",
    "v", "vaas", "val", "valris", "var", "varg", "varin", "ver", "veron", "ves", "vest", "vir", "virk", "virkan", "vog", "vor", "vul", "vulf",
    "w", "wen", "weng", "wer", "werth", "wh", "wom", "wul", "wur", "wurak", "wyl", "wylan", "wyland", "wyr", "wyrm",
    "x", "xan", "xen", "xon", "xor", "xorg",
    "yael", "yal", "yalt", "yd", "ydem", "yen", "yend", "yin", "yink", "yinok", "yl", "yp", "yps", "ypsil", "yr", "yrp", "yrpar", "ys", "ysm", "ysman", "yug", "yugal", "yuw", "yuwan",
    "z", "zaub", "zauber", "zh", "zir", "ziriv", "zirivk", "zor", "zord", "zos", "zosm"]

shadow_suffixs = [
    "a", "aai", "aal", "aalk", "aang", "aari", "aasun", "aaven", "aax", "abon", "ac", "ad", "ador", "ae", "ael", "aen", "aena", "affon", "afir", "ag", "age", "agg", "agur", "ai", "ailub", "aiman", "ainey", "airn", "aj", "ak", "akang", "aki", "al", "alaza", "ald", "aldo", "alfex", "alg", "algi", "alim", "alix", "allion", "allyo", "almyk", "alog", "alon", "alris", "althan", "alto", "alvin", "am", "ama", "amai", "ambir", "amel", "ammon", "amon", "amor", "amse", "an", "ana", "anaki", "anan", "anara", "and", "andae", "andra", "ang", "ange", "ani", "ann", "annel", "anris", "ante", "antys", "anyr", "aon", "aorgor", "ar", "ara", "ard", "ardan", "ardy", "areor", "areyn", "ari", "aric", "arin", "arion", "aris", "ark", "arley", "arn", "arold", "aron", "arone", "arr", "arrol", "arryn", "arsang", "artok", "artuss", "aruk", "aryk", "as", "ash", "asik", "asp", "assa", "astman", "asul", "asun", "atar", "ath", "athog", "au", "auber", "auin", "aven", "avir", "avorn", "ax", "axas", "axby", "axx", "ay", "aymon", "ayn", "aysek", "aza", "azh", "azi",
    "e", "ea", "ean", "eann", "eardan", "ebon", "ebrin", "ebyn", "echa", "edrik", "eissa", "ekan", "el", "elassa", "elax", "elgg", "elgin", "eliage", "elias", "elkin", "ellion", "ellisa", "eloth", "eloto", "elyn", "elyr", "em", "emal", "eman", "emand", "emar", "emer", "emmler", "en", "ena", "enal", "enald", "enby", "endar", "eng", "engor", "enium", "enlon", "enol", "enyr", "eog", "eor", "er", "eran", "erasp", "erayn", "eria", "eridan", "eris", "ernan", "eron", "erone", "erq", "erqod", "erth", "erwin", "erym", "es", "esea", "eshan", "essan", "ester", "estia", "etan", "eth", "ethan", "ethar", "ethian", "eton", "eugir", "evon", "ewyn", "ex", "exus", "exyn", "ey", "eyan", "eyn", "ezar",
    "i", "ia", "iage", "ian", "iana", "ias", "ic", "ice", "ichar", "ida", "idan", "ieron", "ifusel", "ig", "igan", "iig", "iimen", "ikori", "ikos", "il", "ilan", "illar", "illon", "ilok", "ilon", "ilor", "iloura", "ilub", "im", "iman", "imen", "imeria", "imm", "immer", "in", "inai", "inak", "ineth", "iney", "inka", "inn", "inok", "inor", "inuss", "iol", "iola", "ion", "iorak", "ir", "iraj", "irazi", "ire", "irin", "irn", "is", "isa", "isar", "isha", "isonen", "iss", "issa", "iston", "istyr", "itus", "ium", "iven", "ivkari", "ix", "ixon", "iyva",
    "laki", "lana", "landra", "lani", "lar", "lari", "laris", "laron", "laryk", "las", "lassa", "lauin", "laxx", "laza", "lester", "leugir", "lexyn", "ley", "li", "liage", "lias", "lik", "lilok", "lion", "lisa", "liss", "lok", "lon", "lonian", "lorgor", "lorus", "loss", "loto", "loura", "ly", "lya", "lyn", "lyo", "lyr", "lywan",
    "ock", "od", "oder", "odur", "ofay", "off", "og", "ogan", "ogard", "ogel", "ogen", "ogli", "ogyr", "ohel", "ohman", "oisha", "ok", "oki", "ol", "ola", "olani", "old", "oldin", "olen", "ollor", "ollyn", "olon", "oltar", "om", "omar", "omm", "on", "onam", "ondi", "one", "onel", "onen", "onian", "only", "onth", "ood", "or", "orak", "oran", "oranyr", "orb", "ordan", "ordon", "ordyn", "oreg", "orel", "oren", "org", "orgash", "orgen", "orgor", "orhan", "ori", "oriig", "orley", "orliss", "orn", "ornal", "ornel", "orot", "orrin", "ors", "orus", "orvan", "oryn", "osh", "osia", "osmyr", "osque", "oss", "osse", "ost", "osten", "osyl", "oth", "othal", "other", "otil", "oto", "ottr", "oura", "ove", "owyn", "oxley", "oy", "ozhann",
    "ra", "raax", "rabon", "rael", "rag", "ragg", "rak", "ralg", "rama", "ramai", "ramon", "ran", "range", "rante", "ranyr", "rasp", "rayn", "razi", "re", "reg", "rekan", "remer", "ren", "renol", "reor", "reshan", "reyn", "ri", "ria", "ric", "ridan", "rik", "rillar", "rilon", "rim", "rimm", "rin", "rinai", "rineth", "rinn", "rinor", "rion", "ris", "risar", "riston", "roder", "rofay", "roff", "rog", "rogan", "rogli", "rohman", "roki", "rol", "rold", "ron", "rondi", "rone", "rorgor", "rosia", "rot", "rotil", "roy", "rul", "rune", "rus", "rush", "ryk", "ryn", "rynne", "rynoth", "rys",
    "sulini",
    "u", "uaric", "uau", "uber", "ue", "uecha", "ugal", "ugir", "ugyr", "uin", "ukyn", "ul", "ulan", "ulana", "uldir", "ulem", "ulfean", "ulfen", "ulli", "ulo", "ulthea", "ulthon", "ulya", "um", "uma", "umarr", "umen", "under", "une", "unir", "uor", "ur", "ura", "urak", "uralg", "urbak", "urk", "urlik", "uroff", "us", "usa", "usarr", "usel", "ush", "uskan", "uss", "ut", "utas", "utha", "uun", "uwan", "uxtan",
    "y", "ya", "yd", "ydek", "ydon", "ye", "yes", "yftan", "yk", "ykel", "yl", "ylandra", "ylian", "ylon", "ym", "ymon", "yn", "ynac", "yne", "ynlas", "ynne", "ynoth", "yo", "yr", "yri", "yrne", "yrone", "yrpar", "ys", "ysan", "ysek", "ysk", "ysman", "ysten", "ytor", "yva", "ywan"]

took_prefixs = [
    "adal", "adam",
    "bando", "bella",
    "donna",
    "eglan", "esmer", "estel", "ever",
    "ferdi", "ferum", "flam", "fortin", "fred",
    "geron",
    "hildi",
    "isem", "isen", "isum",
    "meri", "mira",
    "odov",
    "pala", "pere", "pervin", "pimper",
    "regin", "rosam",
    "sara", "sigis"]

took_suffixs = [
    "acar", "adoc", "and", "anta", "ard",
    "bard", "bella", "bold", "brand", "bras",
    "ca",
    "din", "doc", "donna",
    "egar",
    "fons",
    "gar", "gard", "grim", "grin",
    "la", "lard",
    "mira", "mond",
    "nand", "nel",
    "tine", "tius",
    "unda"]


#= FUNZIONI ====================================================================

def create_random_name(race=RACE.NONE, sex=SEX.NONE, is_player_name=False):
    """
    Funzione che crea casualmente un nome rpg a seconda della razza e del
    sesso passato.
    """
    if not race:
        log.bug("race non è un parametro valido: %r" % race)
        return ""

    if not sex:
        log.bug("sex non è un parametro valido: %r" % sex)
        return ""

    # -------------------------------------------------------------------------

    # Se la razza è NONE ne scegli una a caso (TD) per ora non supportate
    race = Element(race)
    if race == RACE.NONE:
        race.randomize()

    # Se il sesso è NONE ne sceglie uno a caso
    sex = Element(sex)
    if sex == SEX.NONE:
        sex.randomize()

    # Sceglie a caso il nome
    if sex == SEX.MALE:
        name  = random.choice(human_male_prefixs)
        name += random.choice(human_male_middles)
        name += random.choice(human_male_suffixs)
    else:
        name  = random.choice(human_female_prefixs)
        name += random.choice(human_female_middles)
        name += random.choice(human_female_suffixs)

    # Se il nome è già esistente ne crea uno differente
    if is_player_name:
        for player_code in database["players"]:
            # Visto che il codice di player è un nome ripulito il confronto
            # può andare bene, non eseguo dei controlli sulla ricorsione
            # perché è molto improbabile e può capitare solo con Mud saturi
            # di player
            if is_same(player_code, name):
                return create_random_name(race, sex, is_player_name)

    return name.capitalize()
#- Fine Funzione -


if __name__ == "__main__":
    """
    Script di test scritto così tanto per provarne le funzionalità del modulo.
    """
    for array in globals():
        if not array.endswith("_prefixs"):
            continue
        array = array.replace("_prefixs", "")
        print("\n")
        print("- %s ---------------------------------------------------------" % array)
        prefixs = globals()["%s_prefixs" % array]
        middles = []
        if "%s_middles" % array in globals():
            middles = globals()["%s_middles" % array]
        suffixs = globals()["%s_suffixs" % array]
        x = 0
        while x < 30:
            name = random.choice(prefixs)
            if middles:
                name += random.choice(middles)
            name += random.choice(suffixs)
            print(name)
            x += 1
