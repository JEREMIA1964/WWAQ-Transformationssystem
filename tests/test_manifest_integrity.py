#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite für WWAQ Manifest Integrität
Pytest-basierte Tests für HNS10-Konformität
Stand: 29. Siwan 5785

Q! = Qawana! + DWEKUT!
"""

import pytest
import yaml
from pathlib import Path
import sys

# Füge Parent-Directory zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent.parent))

from wwaq_system.validators.wwaq_validator import WWAQManifestValidator, ValidationError


class TestManifestIntegrity:
    """Test-Suite für Manifest-Integrität"""
    
    @pytest.fixture
    def manifest_path(self):
        """Fixture für Manifest-Pfad"""
        # Suche Manifest relativ zum Test-Verzeichnis
        test_dir = Path(__file__).parent
        manifest = test_dir.parent / "hns10_manifest.yaml"
        
        if not manifest.exists():
            pytest.skip(f"Manifest nicht gefunden: {manifest}")
            
        return str(manifest)
    
    @pytest.fixture
    def validator(self, manifest_path):
        """Fixture für Validator-Instanz"""
        return WWAQManifestValidator(manifest_path)
    
    def test_manifest_exists(self, manifest_path):
        """Test: Manifest-Datei existiert"""
        assert Path(manifest_path).exists(), "hns10_manifest.yaml nicht gefunden"
    
    def test_valid_yaml(self, manifest_path):
        """Test: Manifest ist gültiges YAML"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                assert isinstance(data, dict), "Manifest muss Dictionary sein"
            except yaml.YAMLError as e:
                pytest.fail(f"YAML-Parse-Fehler: {e}")
    
    def test_meta_vollständig(self, validator):
        """Test: Alle Meta-Felder vorhanden"""
        erfolg = validator.validate_meta()
        
        # Prüfe auf kritische Fehler
        kritische = [e for e in validator.errors if e.schweregrad == "kritisch" and e.typ == "meta"]
        assert len(kritische) == 0, f"Meta-Validierung fehlgeschlagen: {kritische}"
    
    def test_hns_format(self, validator):
        """Test: HNS-Nummern haben korrektes Format"""
        validator.validate_struktur()
        
        # Prüfe auf HNS-Format-Fehler
        hns_fehler = [e for e in validator.errors if e.typ == "hns"]
        assert len(hns_fehler) == 0, f"Ungültige HNS-Formate: {hns_fehler}"
    
    def test_keine_duplikate(self, validator):
        """Test: Keine duplizierten HNS oder Namen"""
        validator.validate_struktur()
        
        # Prüfe auf Duplikate
        duplikate = [e for e in validator.errors if e.typ == "duplikat"]
        assert len(duplikate) == 0, f"Duplikate gefunden: {duplikate}"
    
    def test_pipeline_referenzen(self, validator):
        """Test: Alle Pipeline-Referenzen existieren"""
        validator.validate_struktur()
        validator.validate_pipeline()
        
        # Prüfe auf fehlende Referenzen
        ref_fehler = [e for e in validator.errors if e.typ == "referenz"]
        assert len(ref_fehler) == 0, f"Fehlende Referenzen: {ref_fehler}"
    
    def test_sefira_zuordnung(self, validator):
        """Test: Sefira-Namen sind gültig"""
        validator.validate_struktur()
        
        # Prüfe auf ungültige Sefirot
        sefira_warnungen = [w for w in validator.warnings if w.typ == "sefira"]
        
        # Erlaubte Spezialfälle
        erlaubt = ["Über Malchut - Azilut selbst", "Keter-in-Chochmah"]
        
        for warnung in sefira_warnungen:
            # Prüfe ob es ein erlaubter Spezialfall ist
            gefunden = False
            for erlaubter in erlaubt:
                if erlaubter in warnung.beschreibung:
                    gefunden = True
                    break
            
            assert gefunden, f"Ungültige Sefira: {warnung.beschreibung}"
    
    def test_wwaq_konformität(self, validator):
        """Test: WWAQ-spezifische Regeln eingehalten"""
        validator.validate_wwaq_konformität()
        
        # Prüfe auf kritische WWAQ-Verstöße
        wwaq_kritisch = [e for e in validator.errors 
                        if e.schweregrad == "kritisch" and "wwaq" in e.typ]
        
        assert len(wwaq_kritisch) == 0, f"WWAQ-Verstöße: {wwaq_kritisch}"
    
    def test_vollständige_validierung(self, validator):
        """Test: Gesamtvalidierung erfolgreich"""
        erfolg = validator.run_all_validations()
        
        if not erfolg:
            print("\n" + validator.generate_report())
            
        assert erfolg, "Manifest-Validierung fehlgeschlagen"
    
    def test_struktur_hat_module(self, validator):
        """Test: Mindestens ein Modul definiert"""
        struktur = validator.manifest.get("struktur", [])
        assert len(struktur) > 0, "Keine Module in Struktur definiert"
    
    def test_pipeline_hat_schritte(self, validator):
        """Test: Pipeline hat mindestens einen Schritt"""
        pipeline = validator.manifest.get("pipeline", {})
        sequenz = pipeline.get("sequenz", [])
        assert len(sequenz) > 0, "Pipeline hat keine Schritte"


# Zusätzliche Integrationstests
class TestManifestContent:
    """Tests für Manifest-Inhalte"""
    
    @pytest.fixture
    def manifest_data(self, manifest_path):
        """Lädt Manifest-Daten"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_version_format(self, manifest_data):
        """Test: Version hat korrektes Format"""
        version = manifest_data.get("meta", {}).get("version", "")
        assert re.match(r'^\d+\.\d+\.\d+', version), f"Ungültiges Versionsformat: {version}"
    
    def test_schema_ist_hns10(self, manifest_data):
        """Test: Schema ist HNS10"""
        schema = manifest_data.get("meta", {}).get("schema", "")
        assert schema == "HNS10", f"Unerwartetes Schema: {schema}"
    
    def test_kritische_pipeline_schritte(self, manifest_data):
        """Test: Kritische Schritte markiert"""
        pipeline = manifest_data.get("pipeline", {})
        sequenz = pipeline.get("sequenz", [])
        
        kritische = [s for s in sequenz if s.get("kritisch", False)]
        assert len(kritische) > 0, "Keine kritischen Pipeline-Schritte definiert"


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v"])
