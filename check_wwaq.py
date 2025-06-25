#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WWAQ Quick Checker
Prüft Text auf häufige WWAQ-Verstöße

Verwendung: python3 check_wwaq.py "Dein Text hier"
"""

import sys
import re

class WWAQQuickChecker:
    def __init__(self):
        # Falsche Schreibweisen
        self.falsche_schreibweisen = {
            # Sefirot
            r'\bKether\b': 'Keter',
            r'\bChochmah\b': 'Chochma',
            r'\bBinah\b': 'Bina',
            r'\bChesed\b': 'Chessed',
            r'\bGewurah\b': 'Gewura',
            r'\bGeburah\b': 'Gewura',
            r'\bTifferet\b': 'Tiferet',
            r'\bNetzach\b': 'Nezach',
            r'\bJesod\b': 'Jessod',
            r'\bYesod\b': 'Jessod',
            r'\bMalkuth\b': 'Malchut',
            
            # Q vs K
            r'\bKabbala\b': 'Qabbala',
            r'\bKabbalah\b': 'Qabbala',
            r'\bKawana\b': 'Qawana',
            r'\bKavanah\b': 'Qawana',
            
            # DIN 31636
            r'\bTikkun\b': 'Tiqqun',
            r'\bTzimtzum\b': 'Zimzum',
            r'\bTzimzum\b': 'Zimzum',
            r'\bDvekut\b': 'Dwekut',
            r'\bDevekut\b': 'Dwekut',
            r'\bZohar\b': 'Sohar',
            r'\bAtzilut\b': 'Azilut',
            r'\bPartzufim\b': 'Parzufim',
        }
        
        # Zer-Wörter
        self.zer_woerter = {
            'zerbrechen': 'bersten',
            'zerbrach': 'barst', 
            'zerbrachen': 'barsten',
            'zerbricht': 'berstet',
            'zerbrochen': 'geborsten',
            'zerstören': 'wandeln',
            'zerstört': 'gewandelt',
            'zerstörte': 'wandelte',
            'zerreißen': 'öffnen',
            'zerfallen': 'sich wandeln'
        }
        
        # Verbotene Phrasen
        self.verbotene_phrasen = [
            'von herz zu herz',
            'liebevoll',
            'sanft',
            'zauber',
            'magie',
            'gemeinsam auf dem weg'
        ]
    
    def check(self, text):
        """Prüft Text und gibt Fehler aus"""
        fehler = []
        
        # Prüfe falsche Schreibweisen
        for falsch, richtig in self.falsche_schreibweisen.items():
            matches = re.finditer(falsch, text, re.IGNORECASE)
            for match in matches:
                fehler.append(f"❌ '{match.group()}' → sollte '{richtig}' sein")
        
        # Prüfe Zer-Präfixe
        for zer_wort, ersatz in self.zer_woerter.items():
            if zer_wort.lower() in text.lower():
                fehler.append(f"❌ '{zer_wort}' → sollte '{ersatz}' sein")
        
        # Prüfe verbotene Phrasen
        text_lower = text.lower()
        for phrase in self.verbotene_phrasen:
            if phrase in text_lower:
                fehler.append(f"❌ Verbotene Phrase: '{phrase}'")
        
        # Prüfe auf Q! am Ende
        if not text.strip().endswith("Q!"):
            fehler.append("❌ Text sollte mit 'Q!' enden")
        
        # Ausgabe
        if fehler:
            print("WWAQ-VERSTÖSSE GEFUNDEN:")
            print("-" * 40)
            for f in fehler:
                print(f)
            print("-" * 40)
            print(f"Gesamt: {len(fehler)} Verstöße")
            return False
        else:
            print("✓ Text ist WWAQ-konform!")
            return True

def main():
    if len(sys.argv) < 2:
        print("Verwendung: python3 check_wwaq.py \"Dein Text hier\"")
        print("Oder: python3 check_wwaq.py datei.txt")
        sys.exit(1)
    
    checker = WWAQQuickChecker()
    
    # Prüfe ob Argument eine Datei ist
    arg = sys.argv[1]
    if arg.endswith('.txt') or arg.endswith('.md'):
        try:
            with open(arg, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Prüfe Datei: {arg}")
        except FileNotFoundError:
            print(f"Datei nicht gefunden: {arg}")
            sys.exit(1)
    else:
        # Behandle als direkten Text
        text = ' '.join(sys.argv[1:])
        print("Prüfe Text...")
    
    print()
    checker.check(text)
    print("\nQ!")

if __name__ == "__main__":
    main()
