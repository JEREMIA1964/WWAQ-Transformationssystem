from wwaq_system.sprachbasis.din31636_parser import WWAQSprachbasis

text = "Die Kabbala lehrt Tzimtzum durch Qawana."
basis = WWAQSprachbasis()
korrekt, aenderungen = basis.normalisiere_begriff(text)

print("Original:", text)
print("Korrigiert:", korrekt)
print("Änderungen:", aenderungen)

