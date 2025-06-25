#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WWAQ Manifest Validator v1.0
Vollständige Validierung für WWAQ-Konformität
Stand: 29. Siwan 5785

Q! = Qawana! + DWEKUT!
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationError:
    """Strukturierte Fehlerdarstellung"""
    typ: str
    modul: str
    beschreibung: str
    schweregrad: str  # "kritisch", "warnung", "info"


class WWAQManifestValidator:
    """
    Umfassende Validierungsroutine für WWAQ HNS10-Manifeste
    Prüft Meta, Struktur, Pipeline und WWAQ-spezifische Regeln
    """
    
    HNS_PATTERN = re.compile(r"^\d{1,2}(\.\d{1,2}){9}$")
    SEFIRA_NAMEN = {
        "Keter", "Chochmah", "Binah", "Chesed", "Gewurah",
        "Tiferet", "Nezach", "Hod", "Jesod", "Malchut"
    }
    
    def __init__(self, manifest_path: str, strict_mode: bool = True):
        self.manifest_path = Path(manifest_path)
        self.strict_mode = strict_mode
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.manifest = self._load_manifest()
        
    def _load_manifest(self) -> Dict:
        """Lädt und parst YAML-Manifest"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest nicht gefunden: {self.manifest_path}")
            
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"YAML-Parse-Fehler: {e}")
    
    def validate_meta(self) -> bool:
        """Validiert Meta-Informationen"""
        erforderlich = {"version", "schema", "stand", "ort"}
        optional = {"quelle", "bemerkung", "sigillum_basis"}
        
        meta = self.manifest.get("meta", {})
        
        # Pflichtfelder prüfen
        fehlend = erforderlich - set(meta.keys())
        if fehlend:
            self.errors.append(ValidationError(
                typ="meta",
                modul="root",
                beschreibung=f"Fehlende Meta-Felder: {fehlend}",
                schweregrad="kritisch"
            ))
            return False
            
        # Schema-Version prüfen
        if meta.get("schema") != "HNS10" and self.strict_mode:
            self.errors.append(ValidationError(
                typ="schema",
                modul="root",
                beschreibung=f"Unerwartetes Schema: {meta.get('schema')}",
                schweregrad="kritisch"
            ))
            
        return len([e for e in self.errors if e.schweregrad == "kritisch"]) == 0
    
    def validate_struktur(self) -> bool:
        """Validiert Modul-Struktur"""
        struktur = self.manifest.get("struktur", [])
        
        if not struktur:
            self.errors.append(ValidationError(
                typ="struktur",
                modul="root",
                beschreibung="Keine Module in Struktur definiert",
                schweregrad="kritisch"
            ))
            return False
            
        hns_set = set()
        name_set = set()
        
        for idx, modul in enumerate(struktur):
            # HNS-Format
            hns = modul.get("hns", "")
            if not self.HNS_PATTERN.match(hns):
                self.errors.append(ValidationError(
                    typ="hns",
                    modul=modul.get("name", f"Modul_{idx}"),
                    beschreibung=f"Ungültiges HNS-Format: {hns}",
                    schweregrad="kritisch"
                ))
                
            # HNS-Duplikate
            if hns in hns_set:
                self.errors.append(ValidationError(
                    typ="duplikat",
                    modul=modul.get("name", f"Modul_{idx}"),
                    beschreibung=f"Dupliziertes HNS: {hns}",
                    schweregrad="kritisch"
                ))
            hns_set.add(hns)
            
            # Sefira-Validierung
            if "sefira" in modul and modul["sefira"] not in self.SEFIRA_NAMEN:
                if modul["sefira"] not in ["Über Malchut - Azilut selbst", "Keter-in-Chochmah"]:
                    self.warnings.append(ValidationError(
                        typ="sefira",
                        modul=modul.get("name", ""),
                        beschreibung=f"Unbekannte Sefira: {modul['sefira']}",
                        schweregrad="warnung"
                    ))
                    
        return len([e for e in self.errors if e.schweregrad == "kritisch"]) == 0
    
    def validate_pipeline(self) -> bool:
        """Validiert Pipeline-Definition"""
        pipeline = self.manifest.get("pipeline", {})
        
        if not pipeline:
            self.errors.append(ValidationError(
                typ="pipeline",
                modul="root",
                beschreibung="Keine Pipeline definiert",
                schweregrad="kritisch"
            ))
            return False
            
        # Verfügbare Module sammeln
        verfügbare_module = {
            modul["hns"]: modul["name"] 
            for modul in self.manifest.get("struktur", [])
        }
        
        # Pipeline-Sequenz prüfen
        for schritt in pipeline.get("sequenz", []):
            hns = schritt.get("hns", "")
            if hns not in verfügbare_module:
                self.errors.append(ValidationError(
                    typ="referenz",
                    modul=schritt.get("aktion", "Unbekannt"),
                    beschreibung=f"HNS {hns} nicht in Struktur gefunden",
                    schweregrad="kritisch"
                ))
                
        return len([e for e in self.errors if e.schweregrad == "kritisch"]) == 0
    
    def validate_wwaq_konformität(self) -> bool:
        """Prüft WWAQ-spezifische Anforderungen"""
        
        # 1. Q vs K Prüfung
        yaml_text = yaml.dump(self.manifest)
        
        # Kabbala mit K ist verboten (außer in Zitaten über Berg Centre)
        if re.search(r'\b[Kk]abbal[ah]?\b', yaml_text):
            if "Berg" not in yaml_text:  # Ausnahme für Zitate
                self.errors.append(ValidationError(
                    typ="wwaq_q_vs_k",
                    modul="global",
                    beschreibung="'Kabbala' mit K gefunden - muss 'Qabbala' sein",
                    schweregrad="kritisch"
                ))
        
        # 2. Zer-Präfix Prüfung
        zer_pattern = r'\bzer[a-zäöü]+\b'
        zer_matches = re.findall(zer_pattern, yaml_text, re.IGNORECASE)
        for match in zer_matches:
            self.warnings.append(ValidationError(
                typ="wwaq_zer",
                modul="global",
                beschreibung=f"Zer-Präfix gefunden: {match}",
                schweregrad="warnung"
            ))
        
        # 3. DIN 31636 Schreibweisen
        falsche_schreibweisen = {
            'tzimtzum': 'Zimzum',
            'tzimzum': 'Zimzum',
            'tikkun': 'Tiqqun',
            'tikun': 'Tiqqun',
            'dvekut': 'Dwekut',
            'devekut': 'Dwekut'
        }
        
        for falsch, korrekt in falsche_schreibweisen.items():
            if falsch.lower() in yaml_text.lower():
                self.warnings.append(ValidationError(
                    typ="wwaq_din",
                    modul="global",
                    beschreibung=f"Falsche Schreibweise '{falsch}' - sollte '{korrekt}' sein",
                    schweregrad="warnung"
                ))
        
        # 4. Sigillum-Prüfung
        if "sigillum" not in yaml_text.lower() and "𝌇" not in yaml_text:
            self.warnings.append(ValidationError(
                typ="wwaq_sigillum",
                modul="global",
                beschreibung="EOM Matrix Sigillum Referenz fehlt",
                schweregrad="info"
            ))
        
        # 5. Q! Präsenz
        if "q!" not in yaml_text.lower():
            self.warnings.append(ValidationError(
                typ="wwaq_q_bestaetigung",
                modul="global",
                beschreibung="Q! Bestätigung fehlt",
                schweregrad="info"
            ))
        
        return True
    
    def generate_report(self) -> str:
        """Generiert Validierungsbericht"""
        bericht = []
        bericht.append("="*60)
        bericht.append("WWAQ MANIFEST VALIDIERUNGSBERICHT")
        bericht.append("="*60)
        bericht.append(f"Manifest: {self.manifest_path}")
        bericht.append(f"Zeitstempel: {datetime.now().isoformat()}")
        bericht.append(f"Schema: {self.manifest.get('meta', {}).get('schema', 'Unbekannt')}")
        bericht.append(f"Version: {self.manifest.get('meta', {}).get('version', 'Unbekannt')}")
        bericht.append("")
        
        # Zusammenfassung
        kritische = len([e for e in self.errors if e.schweregrad == "kritisch"])
        warnungen = len(self.warnings)
        
        if kritische == 0:
            bericht.append("✓ VALIDIERUNG ERFOLGREICH")
        else:
            bericht.append(f"✗ VALIDIERUNG FEHLGESCHLAGEN ({kritische} kritische Fehler)")
            
        bericht.append(f"Warnungen: {warnungen}")
        bericht.append("")
        
        # Details
        if self.errors:
            bericht.append("FEHLER:")
            bericht.append("-"*40)
            for fehler in self.errors:
                bericht.append(f"[{fehler.schweregrad.upper()}] {fehler.modul}")
                bericht.append(f"  Typ: {fehler.typ}")
                bericht.append(f"  Beschreibung: {fehler.beschreibung}")
                bericht.append("")
                
        if self.warnings:
            bericht.append("WARNUNGEN:")
            bericht.append("-"*40)
            for warnung in self.warnings:
                bericht.append(f"[{warnung.schweregrad.upper()}] {warnung.modul}")
                bericht.append(f"  {warnung.beschreibung}")
                
        bericht.append("")
        bericht.append("Q!")
        
        return "\n".join(bericht)
    
    def run_all_validations(self) -> bool:
        """Führt alle Validierungen aus"""
        erfolg = all([
            self.validate_meta(),
            self.validate_struktur(),
            self.validate_pipeline(),
            self.validate_wwaq_konformität()
        ])
        
        return erfolg and len([e for e in self.errors if e.schweregrad == "kritisch"]) == 0


# CLI-Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="WWAQ Manifest Validator - Prüft HNS10-Manifeste auf Konformität"
    )
    parser.add_argument("manifest", help="Pfad zum YAML-Manifest")
    parser.add_argument("--strict", action="store_true", help="Strict Mode aktivieren")
    parser.add_argument("--output", help="Ausgabedatei für Bericht")
    
    args = parser.parse_args()
    
    try:
        validator = WWAQManifestValidator(args.manifest, args.strict)
        erfolg = validator.run_all_validations()
        bericht = validator.generate_report()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(bericht)
            print(f"Bericht gespeichert: {args.output}")
        else:
            print(bericht)
            
        exit(0 if erfolg else 1)
        
    except Exception as e:
        print(f"FEHLER: {e}")
        exit(2)
