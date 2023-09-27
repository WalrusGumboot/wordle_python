from random import choice
import logging

logging.basicConfig(level=logging.WARN)

# enkele helperfuncties
def woord_naar_voorkomsten(s: str) -> dict[str, int]:
    returnwaarde = {}
    for c in s:
        if c in returnwaarde:
            returnwaarde[c] += 1
        else:
            returnwaarde[c] = 1
    return returnwaarde

def bestand_naar_woordenlijst(pad: str) -> list[str]:
    with open(pad, "r") as file:
        woorden_ongefilterd = file.readlines()
        woorden = list(map(lambda elem: elem.strip(), woorden_ongefilterd))
        woorden = list(
            filter(
                # behoudt alleen woorden met vijf karakters
                lambda elem: len(elem) == 5
                # filtert woorden met hoofdletters eruit
                and elem.lower() == elem
                # filtert niet-ASCII karakters eruit
                and all([ord(c) < 127 for c in elem])
                # filtert ongebruikelijke karakters eruit
                and all([slecht_kar not in elem for slecht_kar in ["-", "'", " "]]),
                woorden,
            )
        )

    return woorden

# enkele constanten
goede_plaats_karakter = "\u001b[32m█\u001b[0m"
foute_plaats_karakter = "\u001b[33m█\u001b[0m"
niet_in_woord_karakter = "█"

woorden = bestand_naar_woordenlijst("woorden.txt")
woorden_uitbreiding = bestand_naar_woordenlijst("woorden_uitbreiding.txt")
geldige_gokken = woorden + woorden_uitbreiding

te_gokken_woord = choice(woorden)
speler_gok = ""

logging.info(f"het te gokken woord is {te_gokken_woord}")

gegokte_woorden: list[str] = []
pogingen = 0

# we kunnen deze vaakgebruikte waarde voorberekenen
# niet dat performance superveel uitmaakt, maar bon, kan geen kwaad
voorkomsten = woord_naar_voorkomsten(te_gokken_woord)

while speler_gok != te_gokken_woord and pogingen < 6:
    speler_gok = input(f"(poging {pogingen + 1}/6) typ je woord: ")
    if (
        speler_gok in gegokte_woorden
        or len(speler_gok) != 5
        or speler_gok not in geldige_gokken
    ):
        print("ongeldige gok.")
        continue

    # tegen dat we hier geraakt zijn is de gok geldig, dus kunnen we pogingen
    # hier incrementen.
    pogingen += 1

    logging.info(f"    poging {pogingen}")

    # correcte_posities is een lijst van indices met letters die juist staan
    correcte_posities = [
        (i, speler_gok[i]) for i in range(5) if list(speler_gok)[i] == list(te_gokken_woord)[i]
    ]

    logging.info(f"    sowieso juist: {correcte_posities}")

    # foute_posities is een lijst van tuples van een int en een str:
    # eerste is een index naar de plaats in de speler_gok, tweede
    # is naar welk karakter dat refereert in het te_gokken_woord
    foute_posities = []

    # indices in de speler_gok die sowieso fout zijn (niet in het
    # te_gokken_woord zitten of overtollig zijn)
    totaal_foute_karakters = []

    for idx, c in enumerate(speler_gok):
        logging.info(f"        rest berekenen; idx: {idx}, c: {c}")
        if idx in list(map(lambda t: t[0], correcte_posities)):
            logging.info(f"        {c} al in correcte_posities, overslaan")
            continue
        if c not in te_gokken_woord:
            logging.info(f"        {c} überhaupt niet in het woord")
            totaal_foute_karakters.append(idx)
            continue

        # tegen dat we hier geraakt zijn, zit het karakter c wel in het
        # te_gokken_woord, maar staat het niet op de juiste positie. we
        # tellen dus hoeveel keer c voorkomt in het te_gokken_woord, en
        # als we nog niet die hoeveelheid bereikt hebben met dit karakter
        # moet de letter geel worden. als we die grens overschrijden zitten
        # er dus te veel voorkomsten van c in de speler_gok, en moeten ze
        # vanaf dan grijs worden.

        max_voorkomsten = voorkomsten[c]
        aantal_al_berekend = len(list(filter(lambda t: t[1] == c, foute_posities)) + list(filter(lambda t: t[1] == c, correcte_posities)))
        logging.info(f"        karakter {c} mag maximaal {max_voorkomsten} keer voorkomen. tot nu toe hebben we er {aantal_al_berekend} al gezien.")
        if aantal_al_berekend >= max_voorkomsten:
            totaal_foute_karakters.append(idx)
            logging.info(f"        dit is er te veel aan, dus karakter {c} hier is fout")
        else:
            logging.info(f"        dit kan nog, dus karakter {c} hier is fout geplaatst maar juiste letter")
            foute_posities.append((idx, c))

    string_componenten = []
    for i in range(5):
        if i in list(map(lambda t: t[0], correcte_posities)):
            string_componenten.append(goede_plaats_karakter)
        elif i in list(map(lambda t: t[0], foute_posities)):
            string_componenten.append(foute_plaats_karakter)
        else:
            string_componenten.append(niet_in_woord_karakter)

    print(" " * 27 + "".join(string_componenten))

if speler_gok != te_gokken_woord:
    print(f"jammer! het woord was {te_gokken_woord}")
else:
    print("netjes gedaan!")