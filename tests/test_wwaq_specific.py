#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test WWAQ Specific
Testet WWAQ-spezifische Funktionalität

Stand: 29. Siwan 5785
"""

import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wwaq_system.validators.wwaq_validator import WWAQValidator, ValidationResult


def test_zer_detection():
    """Test Zer-Präfix Erkennung"""
    validator = WWAQValidator()
    
    test_cases = [
        ("Die Kelim zerbrachen", False, ['zerbrachen']),
        ("Der Tempel wurde zerstört", False, ['zerstört']),
        ("Die Gefäße barsten", True, []),
        ("Das Licht wandelte sich", True, []),
    ]
    
    for text, should_be_valid, expected_errors in test_cases:
        result = validator.validate(text)
        
        if should_be_valid:
            assert len([e for e in result.errors if 'Zer-Präfix' in e]) == 0, \
                f"Falsch-positiv für: {text}"
        else:
            found_zer = [e for e in result.errors if 'Zer-Präfix' in e]
            assert len(found_zer) > 0, f"Zer nicht erkannt in: {text}"
    
    print("✓ Zer-Präfix Erkennung funktioniert")


def test_q_vs_k_detection():
    """Test Q vs K Unterscheidung"""
    validator = WWAQValidator()
    
    test_cases = [
        ("Die Kabbala lehrt uns", False, "Kabbala sollte Qabbala sein"),
        ("Die Qabbala lehrt uns", True, None),
        ("Berg Kabbalah Centre", True, None),  # Ausnahme
        ("Mit Kawana beten", False, "Kawana sollte Qawana sein"),
        ("Mit Qawana beten", True, None),
    ]
    
    for text, should_be_valid, expected_error in test_cases:
        result = validator.validate(text)
        
        k_errors = [e for e in result.errors if 'K statt Q' in e]
        
        if should_be_valid:
            assert len(k_errors) == 0, f"Falsch-positiv für: {text}"
        else:
            assert len(k_errors) > 0, f"K nicht erkannt in: {text}"
            if expected_error:
                assert any(expected_error in e for e in k_errors)
    
    print("✓ Q vs K Erkennung funktioniert")


def test_anthropomorphism_detection():
    """Test Anthropomorphismus-Erkennung"""
    validator = WWAQValidator()
    
    forbidden_texts = [
        "Von Herz zu Herz teilen wir",
        "Die liebevolle Aufnahme",
        "Sanfte Korrektur",
        "Der Zauber der Qabbala",
        "❤️ Liebe",
    ]
    
    for text in forbidden_texts:
        result = validator.validate(text)
        assert len(result.errors) > 0, f"Anthropomorphismus nicht erkannt: {text}"
        assert any('Anthropomorphismus' in e or 'Emoji' in e for e in result.errors)
    
    print("✓ Anthropomorphismus-Erkennung funktioniert")


def test_din_conformity():
    """Test DIN 31636 Konformität"""
    validator = WWAQValidator()
    
    test_cases = [
        ("Tikkun olam", ['Tiqqun']),
        ("Tzimtzum Prozess", ['Zimzum']),
        ("Dvekut erreichen", ['Dwekut']),
        ("Tiqqun Prozess", []),  # Bereits korrekt
    ]
    
    for text, expected_corrections in test_cases:
        result = validator.validate(text)
        
        if expected_corrections:
            assert len(result.warnings) > 0, f"DIN-Fehler nicht erkannt: {text}"
            for correction in expected_corrections:
                assert any(correction in w for w in result.warnings)
        else:
            din_warnings = [w for w in result.warnings if 'DIN' in w]
            assert len(din_warnings) == 0, f"Falsche DIN-Warnung für: {text}"
    
    print("✓ DIN 31636 Prüfung funktioniert")


def test_transformation():
    """Test Text-Transformation"""
    validator = WWAQValidator()
    
    original = "Die Kabbala lehrt dass die Kelim zerbrachen durch Tzimtzum."
    expected_parts = ["Qabbala", "barsten", "Zimzum", "Q!"]
    
    transformed = validator.transform(original)
    
    for part in expected_parts:
        assert part in transformed, f"'{part}' fehlt in transformiertem Text"
    
    # Prüfe dass keine verbotenen Wörter mehr da sind
    assert "Kabbala" not in transformed
    assert "zerbrachen" not in transformed
    assert "Tzimtzum" not in transformed
    
    print("✓ Transformation funktioniert")


def test_complete_validation():
    """Test vollständige Validierung"""
    validator = WWAQValidator()
    
    # Gültiger WWAQ-Text
    valid_text = """Die Qabbala lehrt uns über die Einheit.
Die Gefäße barsten beim Überfluss des Lichts.
Nach Baal HaSulam ist Tiqqun der Weg.

Q!"""
    
    result = validator.validate(valid_text)
    assert result.is_valid, "Gültiger Text wurde als ungültig markiert"
    assert result.score > 90, f"Score zu niedrig: {result.score}"
    
    # Ungültiger Text
    invalid_text = """Die Kabbala lehrt liebevoll von Herz zu Herz.
Die Gefäße zerbrachen mit sanfter Magie ❤️
Tikkun durch Tzimtzum."""
    
    result = validator.validate(invalid_text)
    assert not result.is_valid, "Ungültiger Text wurde als gültig markiert"
    assert result.score < 50, f"Score zu hoch: {result.score}"
    assert len(result.errors) >= 4, "Zu wenige Fehler erkannt"
    
    print("✓ Vollständige Validierung funktioniert")


def test_edge_cases():
    """Test Grenzfälle"""
    validator = WWAQValidator()
    
    # Leerer Text
    result = validator.validate("")
    assert len(result.warnings) > 0  # Sollte Q! vermissen
    
    # Nur Q!
    result = validator.validate("Q!")
    assert result.is_valid
    
    # Gemischte Groß-/Kleinschreibung
    result = validator.validate("Die KABBALA und kabbala")
    assert len(result.errors) == 2  # Beide Varianten sollten erkannt werden
    
    print("✓ Grenzfälle korrekt behandelt")


if __name__ == "__main__":
    print("\nWWAQ SPECIFIC TESTS")
    print("="*40)
    
    try:
        test_zer_detection()
        test_q_vs_k_detection()
        test_anthropomorphism_detection()
        test_din_conformity()
        test_transformation()
        test_complete_validation()
        test_edge_cases()
        
        print("\n✓ Alle WWAQ-Tests bestanden!")
        print("\nQ!")
    except AssertionError as e:
        print(f"\n✗ Test fehlgeschlagen: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        sys.exit(1)
