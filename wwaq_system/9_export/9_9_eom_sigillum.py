import yaml
import hashlib
from datetime import datetime

class EOMMatrixSigillum:
    """Dynamische Sigillum-Verwaltung nach EOM Matrix v4.1"""
    SIGILLUM_GRUNDZEICHEN = "𝌇"
    MAX_SIGILLUM = 999

    def __init__(self, registry_file="eom_sigillum_registry.yaml"):
        self.registry_file = registry_file
        self.registry = self._lade_registry()

    def _lade_registry(self):
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def _speichere_registry(self):
        with open(self.registry_file, "w", encoding="utf-8") as f:
            yaml.dump(self.registry, f, allow_unicode=True)

    def _neues_sigillum(self):
        """Gibt das nächste freie Sigillum-Zahlen-Suffix zurück (spiralförmig 1–999)"""
        benutzt = {int(v["nummer"]) for v in self.registry.values() if "nummer" in v}
        for num in range(1, self.MAX_SIGILLUM + 1):
            if num not in benutzt:
                return num
        return 1  # Spiral: kehrt zu 1 zurück

    def generiere_sigillum(self, modul_name, hns_nummer):
        key = f"{modul_name}|{hns_nummer}"
        if key in self.registry:
            return self.registry[key]["sigillum"]

        nummer = self._neues_sigillum()
        welt = self._welt_from_hns(hns_nummer)
        sig_str = f"{self.SIGILLUM_GRUNDZEICHEN}_{nummer:03d} ({welt})"
        hashwert = hashlib.sha1(key.encode()).hexdigest()[:8]
        self.registry[key] = {
            "sigillum": sig_str,
            "nummer": nummer,
            "welt": welt,
            "hns": hns_nummer,
            "modul": modul_name,
            "hash": hashwert,
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }
        self._speichere_registry()
        return sig_str

    def versiegele_text(self, text, modul_name, hns_nummer):
        assert "Q!" in text, "Q!-Validierung fehlgeschlagen: Der Text enthält kein Q!"
        sigillum = self.generiere_sigillum(modul_name, hns_nummer)
        return f"{text}\n\nEOM Matrix Sigillum: {sigillum}"

    def _welt_from_hns(self, hns_nummer):
        """Weist eine Welt zu (Azilut/Beri'ah/Jezirah/Asijah), nach erster Zahl"""
        mapping = { "1": "Azilut", "2": "Beria", "3": "Jezira", "4": "Asija",
                    "5": "Tiferet", "6": "Nezach", "7": "Hod", "8": "Jessod", "9": "Malchut", "0": "Keter" }
        erste = str(hns_nummer).split(".")[0]
        return mapping.get(erste, "Keter")

    def statistik(self):
        welten = {}
        for v in self.registry.values():
            w = v.get("welt", "Unbekannt")
            welten[w] = welten.get(w, 0) + 1
        return welten

    def exportiere_registry(self, pfad="eom_sigillum_registry_export.yaml"):
        with open(pfad, "w", encoding="utf-8") as f:
            yaml.dump(self.registry, f, allow_unicode=True)

if __name__ == "__main__":
    # Demo/Test
    sig = EOMMatrixSigillum()
    beispieltext = "Dies ist ein WWAQ-Text mit Q!"
    ausgabe = sig.versiegele_text(beispieltext, "Testmodul", "3.2.0.0.0.0.0.0.0.0")
    print(ausgabe)
    print("Sigillum-Statistik:", sig.statistik())
