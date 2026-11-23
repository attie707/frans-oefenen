"""Leerstof: être, avoir en regelmatige -er werkwoorden.

Wil je werkwoorden toevoegen? Zet ze in ER_VERBS hieronder:
  "frans": ("nederlands infinitief", "ik-vorm", "jij/hij-vorm", "meervoud", "achtervoegsel")
Het achtervoegsel is voor scheidbare werkwoorden, bv. ("opruimen", "ruim", "ruimt", "ruimen", "op").
"""
import random

PRONOUNS = ["je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"]

# Nederlandse weergave van elk Frans persoonlijk voornaamwoord + welke NL vorm erbij hoort
NL_PRON = {
    "je": ("ik", "ik"), "tu": ("jij", "jij"), "il": ("hij", "hij"),
    "elle": ("zij (ev.)", "hij"), "on": ("men", "hij"), "nous": ("wij", "mv"),
    "vous": ("jullie", "mv"), "ils": ("zij (mv.)", "mv"), "elles": ("zij (mv.)", "mv"),
}

IRREGULAR = {
    "être":  {"je": "suis", "tu": "es", "il": "est", "nous": "sommes", "vous": "êtes", "ils": "sont"},
    "avoir": {"je": "ai", "tu": "as", "il": "a", "nous": "avons", "vous": "avez", "ils": "ont"},
}

NL = {
    "être":  ("zijn", "ben", "bent", "is", "zijn", ""),
    "avoir": ("hebben", "heb", "hebt", "heeft", "hebben", ""),
}

# frans: (nl infinitief, ik, jij/hij, meervoud, achtervoegsel)
ER_VERBS = {
    "aimer": ("houden van", "houd", "houdt", "houden", "van"),
    "détester": ("haten", "haat", "haat", "haten", ""),
    "parler": ("praten", "praat", "praat", "praten", ""),
    "jouer": ("spelen", "speel", "speelt", "spelen", ""),
    "regarder": ("kijken", "kijk", "kijkt", "kijken", ""),
    "écouter": ("luisteren", "luister", "luistert", "luisteren", ""),
    "habiter": ("wonen", "woon", "woont", "wonen", ""),
    "travailler": ("werken", "werk", "werkt", "werken", ""),
    "chanter": ("zingen", "zing", "zingt", "zingen", ""),
    "danser": ("dansen", "dans", "danst", "dansen", ""),
    "chercher": ("zoeken", "zoek", "zoekt", "zoeken", ""),
    "trouver": ("vinden", "vind", "vindt", "vinden", ""),
    "donner": ("geven", "geef", "geeft", "geven", ""),
    "porter": ("dragen", "draag", "draagt", "dragen", ""),
    "arriver": ("aankomen", "kom", "komt", "komen", "aan"),
    "entrer": ("binnenkomen", "kom", "komt", "komen", "binnen"),
    "rester": ("blijven", "blijf", "blijft", "blijven", ""),
    "marcher": ("lopen", "loop", "loopt", "lopen", ""),
    "penser": ("denken", "denk", "denkt", "denken", ""),
    "préparer": ("klaarmaken", "maak", "maakt", "maken", "klaar"),
    "aider": ("helpen", "help", "helpt", "helpen", ""),
    "inviter": ("uitnodigen", "nodig", "nodigt", "nodigen", "uit"),
    "visiter": ("bezoeken", "bezoek", "bezoekt", "bezoeken", ""),
    "dessiner": ("tekenen", "teken", "tekent", "tekenen", ""),
    "fermer": ("sluiten", "sluit", "sluit", "sluiten", ""),
    "oublier": ("vergeten", "vergeet", "vergeet", "vergeten", ""),
    "étudier": ("studeren", "studeer", "studeert", "studeren", ""),
    "cuisiner": ("koken", "kook", "kookt", "koken", ""),
    "téléphoner": ("bellen", "bel", "belt", "bellen", ""),
    # lastige spelling bij 'nous'
    "manger": ("eten", "eet", "eet", "eten", ""),
    "nager": ("zwemmen", "zwem", "zwemt", "zwemmen", ""),
    "voyager": ("reizen", "reis", "reist", "reizen", ""),
    "ranger": ("opruimen", "ruim", "ruimt", "ruimen", "op"),
    "commencer": ("beginnen", "begin", "begint", "beginnen", ""),
    "lancer": ("gooien", "gooi", "gooit", "gooien", ""),
}
for _v, _d in ER_VERBS.items():
    NL[_v] = (_d[0], _d[1], _d[2], _d[2], _d[3], _d[4])

VOWELS = "aeiouéèêàâîïôûh"
TRICKY = [v for v in ER_VERBS if v.endswith(("ger", "cer"))]
ELISION = [v for v in ER_VERBS if v[0] in VOWELS]
NEG_VERBS = ["être", "avoir", "aimer", "parler", "jouer", "regarder", "écouter", "habiter", "travailler", "manger"]


def base_pron(p):
    return {"elle": "il", "on": "il", "elles": "ils"}.get(p, p)


def conjugate(verb, pron):
    p = base_pron(pron)
    if verb in IRREGULAR:
        return IRREGULAR[verb][p]
    stem = verb[:-2]
    if p == "nous":
        if verb.endswith("ger"):
            return stem + "eons"
        if verb.endswith("cer"):
            return stem[:-1] + "çons"
    return stem + {"je": "e", "tu": "es", "il": "e", "nous": "ons", "vous": "ez", "ils": "ent"}[p]


def with_pron(pron, form):
    if pron == "je" and form[0] in VOWELS:
        return "j'" + form
    return pron + " " + form


def phrase(verb, pron, neg=False):
    form = conjugate(verb, pron)
    if not neg:
        return with_pron(pron, form)
    ne = "n'" if form[0] in VOWELS else "ne "
    return f"{pron} {ne}{form} pas"


def nl_phrase(verb, pron, neg=False):
    inf, ik, jij, hij, mv, rest = NL[verb]
    label, kind = NL_PRON[pron]
    form = {"ik": ik, "jij": jij, "hij": hij, "mv": mv}[kind]
    parts = [label, form] + (["niet"] if neg else []) + ([rest] if rest else [])
    return " ".join(parts)


def accepted(verb, pron, neg=False):
    """Alle goede antwoorden bij een vertaalvraag (zij mv. = ils of elles)."""
    if pron in ("ils", "elles"):
        return [phrase(verb, "ils", neg), phrase(verb, "elles", neg)]
    return [phrase(verb, pron, neg)]


# ---------- items ----------
ITEMS = {}


def _add(verb, pron, neg=False):
    iid = f"{verb}:{pron}" + (":neg" if neg else "")
    ITEMS[iid] = {"id": iid, "verb": verb, "pron": pron, "neg": neg}
    return iid


ETRE_AVOIR = [_add(v, p) for v in ("être", "avoir") for p in PRONOUNS]
REGULAR = [_add(v, p) for v in ER_VERBS if v not in TRICKY for p in PRONOUNS]
TRICKY_ITEMS = [_add(v, p) for v in TRICKY for p in PRONOUNS] + [f"{v}:je" for v in ELISION]
NEG_ITEMS = [_add(v, p, True) for v in NEG_VERBS for p in PRONOUNS]
ALL_ER = REGULAR + [_add(v, p) for v in TRICKY for p in PRONOUNS]

LEVELS = [
    {"n": 1, "name": "être & avoir", "desc": "Vul de juiste vorm in: nous ___ (avoir)", "fmt": "fill", "items": ETRE_AVOIR},
    {"n": 2, "name": "-er werkwoorden", "desc": "Vul de vorm in: tu ___ (jouer)", "fmt": "fill", "items": REGULAR},
    {"n": 3, "name": "Vertalen", "desc": "Typ de hele zin: wij hebben → nous avons", "fmt": "translate", "items": ETRE_AVOIR + REGULAR},
    {"n": 4, "name": "Lastige gevallen", "desc": "nous mangeons, nous commençons, j'aime ...", "fmt": "translate", "items": TRICKY_ITEMS},
    {"n": 5, "name": "Ontkenning", "desc": "ik ben niet → je ne suis pas", "fmt": "translate", "items": NEG_ITEMS},
]
LEVEL_UNLOCK_WINDOW = 20      # laatste 20 antwoorden op een niveau ...
LEVEL_UNLOCK_SCORE = 0.8      # ... minstens 80% goed => volgend niveau open

MC_FOCUS = {
    "etre_avoir": ("être & avoir", ETRE_AVOIR),
    "er": ("-er werkwoorden", ALL_ER),
    "all": ("Alles door elkaar", ETRE_AVOIR + ALL_ER),
}


# ---------- vragen ----------
def _fill_prompt(item):
    verb, pron = item["verb"], item["pron"]
    form = conjugate(verb, pron)
    shown = "j'" if (pron == "je" and form[0] in VOWELS) else pron
    return {"fr": f"{shown} ___", "inf": verb, "nl": nl_phrase(verb, pron)}


def _form_distractors(verb, pron):
    correct = conjugate(verb, pron)
    pool = {conjugate(verb, p) for p in PRONOUNS}
    if verb in IRREGULAR:
        other = "avoir" if verb == "être" else "être"
        pool.add(conjugate(other, pron))
    else:
        stem = verb[:-2]
        pool.add(stem + "ont")
        if verb.endswith("ger"):
            pool.add(stem + "ons")
        if verb.endswith("cer"):
            pool.add(stem + "ons")
            pool.add(stem[:-1] + "çez")
    pool.discard(correct)
    return list(pool)


def _phrase_distractors(verb, pron):
    correct = phrase(verb, pron)
    pool = {with_pron(pron, f) for f in _form_distractors(verb, pron)}
    if pron == "je" and correct.startswith("j'"):
        pool.add("je " + conjugate(verb, pron))
    if verb in IRREGULAR:
        other = "avoir" if verb == "être" else "être"
        pool.add(phrase(other, pron))
    pool -= set(accepted(verb, pron))
    return list(pool)


def make_question(item_id, fmt, mc=False):
    item = ITEMS[item_id]
    verb, pron, neg = item["verb"], item["pron"], item["neg"]
    q = {"item": item_id, "verb": verb, "pron": pron, "fmt": fmt}
    if fmt == "fill":
        q["prompt"] = _fill_prompt(item)
        q["answer"] = conjugate(verb, pron)
        q["accepted"] = [q["answer"]]
        distr = _form_distractors(verb, pron)
    else:
        q["prompt"] = {"nl": nl_phrase(verb, pron, neg)}
        q["accepted"] = accepted(verb, pron, neg)
        q["answer"] = q["accepted"][0]
        distr = _phrase_distractors(verb, pron)
    q["say"] = phrase(verb, pron, neg)
    if mc:
        opts = random.sample(distr, min(4, len(distr))) + [q["answer"]]
        random.shuffle(opts)
        q["options"] = opts
    return q


def table(verb, pron):
    rows = []
    hl = base_pron(pron)
    for p, label in [("je", None), ("tu", None), ("il", "il / elle / on"),
                     ("nous", None), ("vous", None), ("ils", "ils / elles")]:
        form = conjugate(verb, p)
        if label is None:
            label = "j'" if (p == "je" and form[0] in VOWELS) else p
        rows.append({"pron": label, "form": form, "hl": p == hl})
    return {"verb": verb, "nl": NL[verb][0], "rows": rows}
