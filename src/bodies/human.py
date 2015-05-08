# -*- coding: utf-8 -*-

"""
Modulo con la lista delle parti per la razza dell'umano.
"""


from src.part    import Part
from src.element import Element, Flags
from src.enums   import PART, PARTFLAG

parts = {}

# Corpo intero
parts[PART.BODY]                = Part(PART.BODY,             PART.NONE, None, [])
parts[PART.FLOATING]            = Part(PART.FLOATING,         PART.NONE, None, [])

# Parti attaccate al corpo
# http://www.italica.rai.it/principali/lingua/lexis/corpo_umano/parti_corpo.htm
parts[PART.HEAD]                = Part(PART.HEAD,             PART.BODY, None, [])
parts[PART.TORSO]               = Part(PART.TORSO,            PART.BODY, None, [])
parts[PART.LEFT_UPPER_LIMB]     = Part(PART.LEFT_UPPER_LIMB,  PART.BODY, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_UPPER_LIMB]    = Part(PART.RIGHT_UPPER_LIMB, PART.BODY, None, [PARTFLAG.RIGHT])
parts[PART.LEFT_LOWER_LIMB]     = Part(PART.LEFT_LOWER_LIMB,  PART.BODY, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_LOWER_LIMB]    = Part(PART.RIGHT_LOWER_LIMB, PART.BODY, None, [PARTFLAG.RIGHT])

# Parti della testa
# http://www.italica.rai.it/principali/lingua/lexis/corpo_umano/testa.htm
parts[PART.HAIR]                = Part(PART.HAIR,             PART.HEAD, None, [])
parts[PART.FOREHEAD]            = Part(PART.FOREHEAD,         PART.HEAD, None, [])
parts[PART.FACE]                = Part(PART.FACE,             PART.HEAD, None, [])
parts[PART.LEFT_EYEBROW]        = Part(PART.LEFT_EYEBROW,     PART.HEAD, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_EYEBROW]       = Part(PART.RIGHT_EYEBROW,    PART.HEAD, None, [PARTFLAG.RIGHT])
parts[PART.LEFT_EYELASH]        = Part(PART.LEFT_EYELASH,     PART.HEAD, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_EYELASH]       = Part(PART.RIGHT_EYELASH,    PART.HEAD, None, [PARTFLAG.RIGHT])
parts[PART.LEFT_EYE]            = Part(PART.LEFT_EYE,         PART.HEAD, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_EYE]           = Part(PART.RIGHT_EYE,        PART.HEAD, None, [PARTFLAG.RIGHT])
parts[PART.LEFT_EAR]            = Part(PART.LEFT_EAR,         PART.HEAD, None, [PARTFLAG.LEFT])
parts[PART.RIGHT_EAR]           = Part(PART.RIGHT_EAR,        PART.HEAD, None, [PARTFLAG.RIGHT])
parts[PART.NOSE]                = Part(PART.NOSE,             PART.HEAD, None, [])
parts[PART.MUSTACHE]            = Part(PART.MUSTACHE,         PART.HEAD, None, [])
parts[PART.LIP]                 = Part(PART.LIP,              PART.HEAD, None, [])
parts[PART.MOUTH]               = Part(PART.MOUTH,            PART.HEAD, None, [])
parts[PART.CHIN]                = Part(PART.CHIN,             PART.HEAD, None, [])
parts[PART.BEARD]               = Part(PART.BEARD,            PART.HEAD, None, [])
parts[PART.NAPE]                = Part(PART.NAPE,             PART.HEAD, None, [])
parts[PART.NECK]                = Part(PART.NECK,             PART.HEAD, None, [])
parts[PART.THROAT]              = Part(PART.THROAT,           PART.HEAD, None, [])  # (TD) da rimuovere penso
parts[PART.BRAIN]               = Part(PART.BRAIN,            PART.HEAD, None, [PARTFLAG.INTERNAL])

# Parti della bocca (TD)
#il dente      tooth
#la lingua      tongue

# Parti del torso
parts[PART.CHEST]               = Part(PART.CHEST,            PART.TORSO, None, [])  # torace
parts[PART.BREAST]              = Part(PART.BREAST,           PART.TORSO, None, [])  # petto
parts[PART.BELLY]               = Part(PART.BELLY,            PART.TORSO, None, [])  # pancia
parts[PART.BELLYBUTTON]         = Part(PART.BELLYBUTTON,      PART.TORSO, None, [])  # ombelico
parts[PART.WAIST]               = Part(PART.WAIST,            PART.TORSO, None, [])  # vita
parts[PART.LEFT_HIP]            = Part(PART.LEFT_HIP,         PART.TORSO, None, [])  # fianco
parts[PART.RIGHT_HIP]           = Part(PART.RIGHT_HIP,        PART.TORSO, None, [])  # fianco
parts[PART.BACK]                = Part(PART.BACK,             PART.TORSO, None, [])  # schiena
parts[PART.GROIN]               = Part(PART.GROIN,            PART.TORSO, None, [])  # inguine
parts[PART.ASS]                 = Part(PART.ASS,              PART.TORSO, None, [])  # culo
parts[PART.LEFT_LUNG]           = Part(PART.LEFT_LUNG,        PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.RIGHT_LUNG]          = Part(PART.RIGHT_LUNG,       PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.HEART]               = Part(PART.HEART,            PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.STOMACH]             = Part(PART.STOMACH,          PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.LIVER]               = Part(PART.LIVER,            PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.LEFT_KIDNEY]         = Part(PART.LEFT_KIDNEY,      PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.RIGHT_KIDNEY]        = Part(PART.RIGHT_KIDNEY,     PART.TORSO, None, [PARTFLAG.INTERNAL])
parts[PART.GUTS]                = Part(PART.GUTS,             PART.TORSO, None, [PARTFLAG.INTERNAL])

# http://www.italica.rai.it/principali/lingua/lexis/corpo_umano/gli_arti.htm
# Parti del braccio sinistro
parts[PART.LEFT_SHOULDER]       = Part(PART.LEFT_SHOULDER,     PART.TORSO, None, [])
parts[PART.LEFT_BICEPS]         = Part(PART.LEFT_BICEPS,       PART.LEFT_UPPER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_ELBOW]          = Part(PART.LEFT_ELBOW,        PART.LEFT_UPPER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_FOREARM]        = Part(PART.LEFT_FOREARM,      PART.LEFT_UPPER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_WRIST]          = Part(PART.LEFT_WRIST,        PART.LEFT_UPPER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_HAND]           = Part(PART.LEFT_HAND,         PART.LEFT_UPPER_LIMB, None, [PARTFLAG.LEFT])

# Parti del braccio destro
parts[PART.RIGHT_SHOULDER]      = Part(PART.RIGHT_SHOULDER,    PART.TORSO, None, [])
parts[PART.RIGHT_BICEPS]        = Part(PART.RIGHT_BICEPS,      PART.RIGHT_UPPER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_ELBOW]         = Part(PART.RIGHT_ELBOW,       PART.RIGHT_UPPER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_FOREARM]       = Part(PART.RIGHT_FOREARM,     PART.RIGHT_UPPER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_WRIST]         = Part(PART.RIGHT_WRIST,       PART.RIGHT_UPPER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_HAND]          = Part(PART.RIGHT_HAND,        PART.RIGHT_UPPER_LIMB, None, [PARTFLAG.RIGHT])

# Parti della mano sinistra
parts[PART.LEFT_BACKHAND]       = Part(PART.LEFT_BACKHAND,     PART.LEFT_HAND, None, [PARTFLAG.LEFT])
parts[PART.LEFT_PALM]           = Part(PART.LEFT_PALM,         PART.LEFT_HAND, None, [PARTFLAG.LEFT])
parts[PART.LEFT_THUMB]          = Part(PART.LEFT_THUMB,        PART.LEFT_HAND, None, [PARTFLAG.LEFT], "sulle dita")  # pollice
parts[PART.LEFT_FOREFINGER]     = Part(PART.LEFT_THUMB,        PART.LEFT_HAND, None, [PARTFLAG.LEFT], "sulle dita")  # indice
parts[PART.LEFT_MIDDLE_FINGER]  = Part(PART.LEFT_THUMB,        PART.LEFT_HAND, None, [PARTFLAG.LEFT], "sulle dita")  # medio
parts[PART.LEFT_RING_FINGER]    = Part(PART.LEFT_THUMB,        PART.LEFT_HAND, None, [PARTFLAG.LEFT], "sulle dita")  # anulare
parts[PART.LEFT_LITTLE_FINGER]  = Part(PART.LEFT_THUMB,        PART.LEFT_HAND, None, [PARTFLAG.LEFT], "sulle dita")  # mignolo
parts[PART.LEFT_NAILS]          = Part(PART.LEFT_NAILS,        PART.LEFT_HAND, None, [PARTFLAG.LEFT])

# Parti della mano destra
parts[PART.RIGHT_BACKHAND]      = Part(PART.RIGHT_BACKHAND,     PART.RIGHT_HAND, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_PALM]          = Part(PART.RIGHT_PALM,         PART.RIGHT_HAND, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_THUMB]         = Part(PART.RIGHT_THUMB,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT], "sulle dita")  # pollice
parts[PART.RIGHT_FOREFINGER]    = Part(PART.RIGHT_THUMB,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT], "sulle dita")  # indice
parts[PART.RIGHT_MIDDLE_FINGER] = Part(PART.RIGHT_THUMB,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT], "sulle dita")  # medio
parts[PART.RIGHT_RING_FINGER]   = Part(PART.RIGHT_THUMB,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT], "sulle dita")  # anulare
parts[PART.RIGHT_LITTLE_FINGER] = Part(PART.RIGHT_THUMB,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT], "sulle dita")  # mignolo
parts[PART.RIGHT_NAILS]         = Part(PART.RIGHT_NAILS,        PART.RIGHT_HAND, None, [PARTFLAG.RIGHT])

# Parti della gamba sinistra
parts[PART.LEFT_THIGH]          = Part(PART.LEFT_THIGH,        PART.LEFT_LOWER_LIMB, None, [PARTFLAG.LEFT]) # coscia
parts[PART.LEFT_KNEE]           = Part(PART.LEFT_KNEE,         PART.LEFT_LOWER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_TIBIA]          = Part(PART.LEFT_TIBIA,        PART.LEFT_LOWER_LIMB, None, [PARTFLAG.LEFT]) # gamba
parts[PART.LEFT_ANKLE]          = Part(PART.LEFT_ANKLE,        PART.LEFT_LOWER_LIMB, None, [PARTFLAG.LEFT])
parts[PART.LEFT_FOOT]           = Part(PART.LEFT_FOOT,         PART.LEFT_LOWER_LIMB, None, [PARTFLAG.LEFT])

# Parti della gamba destra
parts[PART.RIGHT_THIGH]         = Part(PART.RIGHT_THIGH,      PART.RIGHT_LOWER_LIMB, None, [PARTFLAG.RIGHT]) # coscia
parts[PART.RIGHT_KNEE]          = Part(PART.RIGHT_KNEE,       PART.RIGHT_LOWER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_TIBIA]         = Part(PART.RIGHT_TIBIA,      PART.RIGHT_LOWER_LIMB, None, [PARTFLAG.RIGHT]) # gamba
parts[PART.RIGHT_ANKLE]         = Part(PART.RIGHT_ANKLE,      PART.RIGHT_LOWER_LIMB, None, [PARTFLAG.RIGHT])
parts[PART.RIGHT_FOOT]          = Part(PART.RIGHT_FOOT,       PART.RIGHT_LOWER_LIMB, None, [PARTFLAG.RIGHT])

# Parti del piede sinistro
#parts[PART.LEFT_HEEL]          = Part(PART.LEFT_HEEL,       PART.LEFT_FOOT, None, [PARTFLAG.LEFT]) # tallone
#l'alluce     toe

# Struttura particolare per i destri e i mancini, le parti sono flaggate come
# da non visualizzare perché vengono gestite in maniera particolare:
parts_right_handed = parts.copy()
parts_right_handed[PART.WIELD] = Part(PART.WIELD, PART.RIGHT_HAND, None, [PARTFLAG.RIGHT, PARTFLAG.NO_EQUIP_LIST])
parts_right_handed[PART.HOLD]  = Part(PART.HOLD,  PART.LEFT_HAND,  None, [PARTFLAG.LEFT, PARTFLAG.NO_EQUIP_LIST])

# Struttura particolare per i mancini:
parts_left_handed = parts.copy()
parts_left_handed[PART.WIELD] = Part(PART.WIELD, PART.LEFT_HAND,  None, [PARTFLAG.LEFT, PARTFLAG.NO_EQUIP_LIST])
parts_left_handed[PART.HOLD]  = Part(PART.HOLD,  PART.RIGHT_HAND, None, [PARTFLAG.RIGHT, PARTFLAG.NO_EQUIP_LIST])
