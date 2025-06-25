#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WWAQ Validator
Prüft Texte auf WWAQ-Konformität

Stand: 29. Siwan 5785
Q! = Qawana! + DWEKUT!
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Ergebnis einer WWAQ-Validierung"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    transformations: List[Tuple[str, str]] = field(default_factory=list)
    score: float = 100.0


class WWAQValidator:
    """Hauptklasse für WWAQ-Validierung"""
    
    def __init__(self):
        # Zer-Transformationen
        self.zer_transformations = {
            'zerbrechen': 'bersten',
            'zerbrach': 'barst',
            'zerbrachen': 'barsten',
            'zerbricht': 'berstet',
            'zerbrochen': 'geborsten',
            'zerstören': 'wandeln',
            'zerstört': 'gewandelt',
            'zerstörte': 'wandelte',
            'zerstörten': 'wandelten',
            'zerreißen': 'öffnen',
            'zerriss': 'öffnete',
            'zerrissen': 'geöffnet',
            'zerfallen': 'sich wandeln',
            'zerfällt': 'wandelt sich',
            'zerfiel': 'wandelte sich',
            'zerschlagen': 'bersten',
            'zerschlug': 'barst'
        }
        
        # Q vs K Unterscheidung
        self.q_vs_k_terms = {
            'kabbala': 'Qabbala',
            'kabbalah': 'Qabbala',
            'kawana': 'Qawana',
            'kavanah': 'Qawana',
            'kavana': 'Qawana'
        }
        
        # Verbotene anthropomorphe Phrasen
        self.forbidden_phrases = [
            'von herz zu herz',
            'herz zu herz',
            'liebevoll',
            'sanft',
            'gemeinsam auf dem weg',
            'möge es in dir wachsen',
            'berühren die mitte',
            'seele der worte',
            'zauber',
            'magie'
        ]
        
        # DIN 31636 Schreibweisen
        self.din_corrections = {
            'tikkun': 'Tiqqun',
            'tikun': 'Tiqqun',
            'tzimtzum': 'Zimzum',
            'tzimzum': 'Zimzum',
            'dvekut': 'Dwekut',
            'devekut': 'Dwekut',
            'chaver': 'Chawer',
            'haver': 'Chawer',
            'atzilut': 'Azilut',
            'bnei baruch': 'Bnej Baruch'
        }
    
    def validate(self, text: str) -> ValidationResult:
        """
        Validiert einen Text auf WWAQ-Konformität
        
        Args:
            text: Zu validierender Text
            
        Returns:
            ValidationResult mit Details
        """
        result = ValidationResult()
        
        # Prüfe Zer-Präfixe
        self._check_zer_prefixes(text, result)
        
        # Prüfe Q vs K
        self._check_q_vs_k(text, result)
        
        # Prüfe Anthropomorphismen
        self._check_anthropomorphisms(text, result)
        
        # Prüfe DIN-Konformität
        self._check_din_conformity(text, result)
        
        # Prüfe Q! am Ende
        self._check_q_ending(text, result)
        
        # Berechne Score
        total_issues = len(result.errors) + (len(result.warnings) * 0.5)
        result.score = max(0, 100 - (total_issues * 10))
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def _check_zer_prefixes(self, text: str, result: ValidationResult):
        """Prüft auf Zer-Präfixe"""
        for zer_word, replacement in self.zer_transformations.items():
            pattern = rf'\b{zer_word}\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                result.errors.append(
                    f"Zer-Präfix gefunden: '{match.group()}' → sollte '{replacement}' sein"
                )
                result.transformations.append((match.group(), replacement))
    
    def _check_q_vs_k(self, text: str, result: ValidationResult):
        """Prüft Q vs K Unterscheidung"""
        for k_term, q_term in self.q_vs_k_terms.items():
            pattern = rf'\b{k_term}\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                # Ausnahme: Wenn über Berg Centre gesprochen wird
                context = text[max(0, match.start()-50):match.end()+50]
                if 'Berg' not in context and 'Centre' not in context:
                    result.errors.append(
                        f"K statt Q: '{match.group()}' → sollte '{q_term}' sein"
                    )
                    result.transformations.append((match.group(), q_term))
    
    def _check_anthropomorphisms(self, text: str, result: ValidationResult):
        """Prüft auf anthropomorphe Ausdrücke"""
        text_lower = text.lower()
        
        for phrase in self.forbidden_phrases:
            if phrase in text_lower:
                result.errors.append(
                    f"Anthropomorphismus gefunden: '{phrase}'"
                )
        
        # Prüfe auf Emojis
        emoji_pattern = re.compile(r'[😀-🙏]|❤️|💕|💖|✨|🌟|⭐')
        if emoji_pattern.search(text):
            result.errors.append("Emojis sind nicht WWAQ-konform")
    
    def _check_din_conformity(self, text: str, result: ValidationResult):
        """Prüft DIN 31636 Konformität"""
        for wrong, correct in self.din_corrections.items():
            pattern = rf'\b{wrong}\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                result.warnings.append(
                    f"DIN 31636: '{match.group()}' → sollte '{correct}' sein"
                )
                result.transformations.append((match.group(), correct))
    
    def _check_q_ending(self, text: str, result: ValidationResult):
        """Prüft auf Q! am Ende"""
        if not text.strip().endswith("Q!"):
            result.warnings.append("Text sollte mit 'Q!' enden")
    
    def transform(self, text: str) -> str:
        """
        Transformiert einen Text zu WWAQ-Konformität
        
        Args:
            text: Zu transformierender Text
            
        Returns:
            Transformierter Text
        """
        # Validiere zuerst
        validation = self.validate(text)
        
        # Wende alle Transformationen an
        transformed = text
        
        # Sortiere Transformationen nach Position (rückwärts)
        all_transforms = []
        
        # Sammle alle Transformationen mit Positionen
        for original, replacement in validation.transformations:
            for match in re.finditer(rf'\b{re.escape(original)}\b', transformed, re.IGNORECASE):
                all_transforms.append((match.start(), match.end(), original, replacement))
        
        # Sortiere rückwärts und wende an
        for start, end, original, replacement in sorted(all_transforms, reverse=True):
            # Behalte Großschreibung bei
            if transformed[start].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            
            transformed = transformed[:start] + replacement + transformed[end:]
        
        # Entferne anthropomorphe Phrasen
        for phrase in self.forbidden_phrases:
            pattern = rf'[^.!?]*{re.escape(phrase)}[^.!?]*[.!?]\s*'
            transformed = re.sub(pattern, '', transformed, flags=re.IGNORECASE)
        
        # Entferne Emojis
        emoji_pattern = re.compile(r'[😀-🙏]|❤️|💕|💖|✨|🌟|⭐')
        transformed = emoji_pattern.sub('', transformed)
        
        # Füge Q! hinzu wenn fehlt
        if not transformed.strip().endswith("Q!"):
            transformed = transformed.rstrip() + "\n\nQ!"
        
        return transformed


# Hilfsfunktion für direkten Aufruf
def validate_text(text: str) -> Dict:
    """Validiert einen Text und gibt Ergebnis als Dictionary zurück"""
    validator = WWAQValidator()
    result = validator.validate(text)
    
    return {
        'valid': result.is_valid,
        'score': result.score,
        'errors': result.errors,
        'warnings': result.warnings,
        'transformations': [(o, r) for o, r in result.transformations]
    }


if __name__ == "__main__":
    # Test
    test_text = "Die Kabbala lehrt dass die Kelim zerbrachen."
    
    validator = WWAQValidator()
    result = validator.validate(test_text)
    
    print(f"Text: {test_text}")
    print(f"Gültig: {result.is_valid}")
    print(f"Score: {result.score}")
    print(f"Fehler: {result.errors}")
    print(f"Transformiert: {validator.transform(test_text)}")
    
    print("\nQ!")
