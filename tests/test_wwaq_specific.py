#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WWAQ-spezifische Tests
Prüft Einhaltung aller WWAQ-Konformitätsregeln
Stand: 29. Siwan 5785

Q! = Qawana! + DWEKUT!
"""

import pytest
import yaml
import re
from pathlib import Path
import sys

# Füge Parent-Directory zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from wwaq_system.validators.wwaq_validator import WWAQManifestValidator


class TestWWAQSpecific:
    """WWAQ-spezifische Konformitätstests"""
    
    @pytest.fixture
    def manifest_path(self):
        """Fixture für Manifest-Pfad"""
        test_dir = Path(__file__).parent
        manifest = test_dir.parent / "hns10_manifest.yaml"
        
        if not manifest.exists():
            # Versuche alternative Pfade
            manifest = test_dir.parent / "wwaq_hns10_manifest.yaml"
            
        if not manifest.exists():
            pytest.skip(f"Manifest nicht gefunden")
            
        return str(manifest)
    
    @pytest.fixture
    def manifest_text(self, manifest_path):
        """Lädt Manifest als Text"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def manifest_data(self, manifest_path):
        """Lädt Manifest als Dictionary"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_no_k_in_qabbala(self, manifest_text):
        """Test: Keine falsche Schreibweise 'Kabbala' mit K"""
        # Suche nach Kabbala/Kabbalah mit K
        k_pattern = r'\b[Kk]abbal[ah]*\b'
        matches = re.findall(k_pattern, manifest_text)
        
        # Ausnahme: Wenn "Berg" im Kontext (Zitat über Berg Centre)
        if matches and "Berg" not in manifest_text:
            pytest.fail(f"Falsche Schreibweise gefunden: {matches}. Muss 'Qabbala' mit Q sein!")
    
    def test_correct_qabbala_usage(self, manifest_text):
        """Test: 'Qabbala' wird korrekt verwendet"""
        q_pattern = r'\b[Qq]abbala\b'
        matches = re.findall(q_pattern, manifest_text)
        
        # Wenn Kabbala-Begriffe vorkommen, sollten sie mit Q sein
        if "abbal" in manifest_text.lower():
            assert len(matches) > 0, "Kabbala-Begriffe müssen mit Q geschrieben werden"
    
    def test_no_zer_prefixes(self, manifest_text):
        """Test: Keine zer- Präfixe"""
        zer_pattern = r'\bzer[a-zäöüß]+\b'
        matches = re.findall(zer_pattern, manifest_text, re.IGNORECASE)
        
        if matches:
            pytest.fail(f"Zer-Präfixe gefunden: {matches}. Diese müssen eliminiert werden!")
    
    def test_din_conformity(self, manifest_text):
        """Test: DIN 31636 konforme Schreibweisen"""
        falsche_schreibweisen = {
            'tzimtzum': 'Zimzum',
            'tzimzum': 'Zimzum', 
            'tikkun': 'Tiqqun',
            'tikun': 'Tiqqun',
            'dvekut': 'Dwekut',
            'devekut': 'Dwekut',
            'bnei baruch': 'Bnej Baruch',
            'atzilut': 'Azilut'
        }
        
        gefundene_fehler = []
        
        for falsch, korrekt in falsche_schreibweisen.items():
            if falsch.lower() in manifest_text.lower():
                gefundene_fehler.append(f"{falsch} → {korrekt}")
        
        assert len(gefundene_fehler) == 0, \
            f"Falsche DIN 31636 Schreibweisen: {', '.join(gefundene_fehler)}"
    
    def test_sigillum_present(self, manifest_text):
        """Test: Sigillum-Referenz vorhanden"""
        # Suche nach Sigillum oder 𝌇
        has_sigillum = ("sigillum" in manifest_text.lower() or "𝌇" in manifest_text)
        
        # Warnung statt Fehler, da nicht immer erforderlich
        if not has_sigillum:
            pytest.skip("Sigillum-Referenz fehlt (optional)")
    
    def test_q_confirmation(self, manifest_text):
        """Test: Q! Bestätigung vorhanden"""
        has_q = "Q!" in manifest_text or "q!" in manifest_text
        
        # Info statt Fehler
        if not has_q:
            pytest.skip("Q! Bestätigung fehlt (empfohlen)")
    
    def test_no_anthropomorphisms(self, manifest_text):
        """Test: Keine anthropomorphen Begriffe"""
        verbotene_begriffe = [
            'liebevoll', 'sanft', 'herzlich', 'behutsam',
            'wächter', 'beschützer', 'herrscher', 'richter',
            'von herz zu herz', 'gemeinsam auf dem weg'
        ]
        
        gefunden = []
        for begriff in verbotene_begriffe:
            if begriff.lower() in manifest_text.lower():
                gefunden.append(begriff)
        
        assert len(gefunden) == 0, \
            f"Anthropomorphe Begriffe gefunden: {', '.join(gefunden)}"
    
    def test_no_poetry(self, manifest_text):
        """Test: Keine poetischen Elemente"""
        poetische_marker = ['♪', '♫', '❤', '💕', '✨', '🌟', '~~~', '***']
        
        gefunden = []
        for marker in poetische_marker:
            if marker in manifest_text:
                gefunden.append(marker)
        
        assert len(gefunden) == 0, \
            f"Poetische Elemente gefunden: {', '.join(gefunden)}"
    
    def test_valid_sources(self, manifest_data):
        """Test: Nur erlaubte Quellen verwendet"""
        erlaubte_quellen = {
            'ARI', 'Rabbi Jizchak Luria', 'Ez Chajim',
            'Baal HaSulam', 'Rabbi Jehuda Aschlag', 'TES',
            'Rabash', 'Rabbi Baruch Aschlag',
            'Rav Laitman', 'Rav Michael Laitman',
            'Sohar', 'Zohar'
        }
        
        verbotene_quellen = {
            'Berg', 'Kabbalah Centre', 'Madonna',
            'ChatGPT', 'AI', 'KI'
        }
        
        # Prüfe Meta-Quelle
        quelle = manifest_data.get('meta', {}).get('quelle', '')
        
        if quelle:
            # Prüfe ob verbotene Quelle
            for verboten in verbotene_quellen:
                assert verboten.lower() not in quelle.lower(), \
                    f"Verbotene Quelle gefunden: {verboten}"
    
    def test_hns_consistency(self, manifest_data):
        """Test: HNS-Nummern sind konsistent"""
        struktur = manifest_data.get('struktur', [])
        
        # Sammle alle HNS
        alle_hns = []
        for modul in struktur:
            hns = modul.get('hns', '')
            if hns:
                alle_hns.append(hns)
        
        # Prüfe auf korrekte Sortierung (optional)
        sortiert = sorted(alle_hns)
        if alle_hns != sortiert:
            pytest.skip("HNS nicht sortiert (optional)")
    
    def test_complete_manifest_structure(self, manifest_data):
        """Test: Manifest hat vollständige Struktur"""
        erforderliche_felder = ['meta', 'struktur', 'pipeline']
        
        for feld in erforderliche_felder:
            assert feld in manifest_data, f"Erforderliches Feld fehlt: {feld}"
        
        # Meta sollte nicht leer sein
        assert len(manifest_data.get('meta', {})) > 0, "Meta ist leer"
        
        # Struktur sollte Module haben
        assert len(manifest_data.get('struktur', [])) > 0, "Keine Module definiert"
        
        # Pipeline sollte Sequenz haben
        assert 'sequenz' in manifest_data.get('pipeline', {}), "Pipeline-Sequenz fehlt"


# Negative Tests (sollten fehlschlagen)
class TestWWAQNegative:
    """Negative Tests - prüfen dass Validator Fehler findet"""
    
    def test_validator_findet_k_fehler(self):
        """Test: Validator erkennt falsche K-Schreibweise"""
        test_manifest = {
            'meta': {'version': '1.0', 'schema': 'HNS10', 'stand': 'test', 'ort': 'test'},
            'struktur': [{
                'hns': '1.0.0.0.0.0.0.0.0.0',
                'name': 'Kabbala-Modul',  # Fehler!
                'beschreibung': 'Test mit falscher Schreibweise'
            }],
            'pipeline': {'sequenz': []}
        }
        
        # Schreibe temporäres Manifest
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_manifest, f)
            temp_path = f.name
        
        try:
            validator = WWAQManifestValidator(temp_path)
            validator.validate_wwaq_konformität()
            
            # Sollte Fehler finden
            k_fehler = [e for e in validator.errors if e.typ == "wwaq_q_vs_k"]
            assert len(k_fehler) > 0, "Validator hat K-Fehler nicht erkannt"
        finally:
            Path(temp_path).unlink()
    
    def test_validator_findet_zer_fehler(self):
        """Test: Validator erkennt zer-Präfixe"""
        test_manifest = {
            'meta': {'version': '1.0', 'schema': 'HNS10', 'stand': 'test', 'ort': 'test'},
            'struktur': [{
                'hns': '1.0.0.0.0.0.0.0.0.0',
                'name': 'Test-Modul',
                'beschreibung': 'Modul zum zerbrechen von Strukturen'  # Fehler!
            }],
            'pipeline': {'sequenz': []}
        }
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_manifest, f)
            temp_path = f.name
        
        try:
            validator = WWAQManifestValidator(temp_path)
            validator.validate_wwaq_konformität()
            
            # Sollte Warnung generieren
            zer_warnungen = [w for w in validator.warnings if w.typ == "wwaq_zer"]
            assert len(zer_warnungen) > 0, "Validator hat zer-Präfix nicht erkannt"
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v", "--tb=short"])
