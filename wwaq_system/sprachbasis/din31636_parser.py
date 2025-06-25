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
        aenderungen = []
        for falsch, korrekt in self.mapping.items():
            # Suchen unabhängig von Groß-/Kleinschreibung
            if falsch in text:
                text = text.replace(falsch, korrekt)
                aenderungen.append((falsch, korrekt))
            # Auch mit erstem Buchstaben groß
            falsch_cap = falsch.capitalize()
            korrekt_cap = korrekt.capitalize()
            if falsch_cap in text:
                text = text.replace(falsch_cap, korrekt_cap)
                aenderungen.append((falsch_cap, korrekt_cap))
        return text, aenderungen

    def erstelle_oeffentliches_glossar(self, dateiname="wwaq_glossar.yaml"):
        """Exportiert nur wissenschaftliche Begriffe."""
        glossar = {e["korrekt"]: e["hebräisch"] for e in SCHREIBWEISEN}
        with open(dateiname, "w", encoding="utf-8") as f:
            yaml.dump(glossar, f, allow_unicode=True)

if __name__ == "__main__":
    basis = WWAQSprachbasis()
    basis.erstelle_oeffentliches_glossar()
    print("Öffentliches Glossar erstellt.")

