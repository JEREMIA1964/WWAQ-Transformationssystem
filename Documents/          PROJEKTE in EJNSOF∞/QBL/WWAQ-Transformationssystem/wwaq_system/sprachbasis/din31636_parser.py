import yaml

SCHREIBWEISEN = [
    {"falsch": ["Kabbala", "Kabbalah"], "korrekt": "Qabbala", "hebräisch": "קבלה"},
    {"falsch": ["Tzimtzum", "Tzimzum"], "korrekt": "Zimzum", "hebräisch": "צמצום"},
    # Weitere Begriffe ergänzen
]

class WWAQSprachbasis:
    def __init__(self):
        self.mapping = {}
        for eintrag in SCHREIBWEISEN:
            for falsch in eintrag["falsch"]:
                self.mapping[falsch.lower()] = eintrag["korrekt"]

def normalisiere_begriff(self, text):
    änderungen = []
    for falsch, korrekt in self.mapping.items():
        # Suchen unabhängig von Groß-/Kleinschreibung
        if falsch in text:
            text = text.replace(falsch, korrekt)
            änderungen.append((falsch, korrekt))
        # Auch mit erstem Buchstaben groß
        falsch_cap = falsch.capitalize()
        korrekt_cap = korrekt.capitalize()
        if falsch_cap in text:
            text = text.replace(falsch_cap, korrekt_cap)
            änderungen.append((falsch_cap, korrekt_cap))
    return text, änderungen


    def erstelle_glossar(self, dateiname="wwaq_glossar.yaml"):
        glossar = {e["korrekt"]: e["hebräisch"] for e in SCHREIBWEISEN}
        with open(dateiname, "w", encoding="utf-8") as f:
            yaml.dump(glossar, f, allow_unicode=True)

if __name__ == "__main__":
    basis = WWAQSprachbasis()
    basis.erstelle_glossar()
    print("Glossar erstellt.")

import yaml

SCHREIBWEISEN = [
    {"falsch": ["Kabbala", "Kabbalah"], "korrekt": "Qabbala", "hebräisch": "קבלה"},
    {"falsch": ["Tzimtzum", "Tzimzum"], "korrekt": "Zimzum", "hebräisch": "צמצום"},
    # Weitere Begriffe ergänzen!
]

class WWAQSprachbasis:
    def __init__(self):
        self.mapping = {}
        for eintrag in SCHREIBWEISEN:
            for falsch in eintrag["falsch"]:
                self.mapping[falsch.lower()] = eintrag["korrekt"]

    def normalisiere_begriff(self, text):
        änderungen = []
        for falsch, korrekt in self.mapping.items():
            # Ersetze unabhängig von Groß-/Kleinschreibung (auch am Satzanfang)
            # 1. Kleinbuchstaben
            if falsch in text:
                text = text.replace(falsch, korrekt)
                änderungen.append((falsch, korrekt))
            # 2. Groß am Satzanfang
            falsch_cap = falsch.capitalize()
            korrekt_cap = korrekt.capitalize()
            if falsch_cap in text:
                text = text.replace(falsch_cap, korrekt_cap)
                änderungen.append((falsch_cap, korrekt_cap))
        return text, änderungen

    def erstelle_glossar(self, dateiname="wwaq_glossar.yaml"):
        glossar = {e["korrekt"]: e["hebräisch"] for e in SCHREIBWEISEN}
        with open(dateiname, "w", encoding="utf-8") as f:
            yaml.dump(glossar, f, allow_unicode=True)

if __name__ == "__main__":
    basis = WWAQSprachbasis()
    basis.erstelle_glossar()
    print("Glossar erstellt.")

