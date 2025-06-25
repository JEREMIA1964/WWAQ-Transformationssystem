#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Manifest Integrity
Prüft die HNS 10.0.0.0.0.0.0.0.0.0 Manifest-Struktur

Stand: 29. Siwan 5785
"""

import yaml
import os
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_manifest_exists():
    """Test ob Manifest existiert"""
    manifest_path = project_root / "hns10_manifest.yaml"
    assert manifest_path.exists(), f"Manifest nicht gefunden: {manifest_path}"
    print("✓ Manifest existiert")


def test_manifest_structure():
    """Test ob Manifest korrekte Struktur hat"""
    manifest_path = project_root / "hns10_manifest.yaml"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    
    # Prüfe Hauptstruktur
    assert 'hierarchical_structure' in manifest, "hierarchical_structure fehlt"
    assert 'hns_10_0_0_0_0_0_0_0_0_0' in manifest['hierarchical_structure'], "HNS 10 fehlt"
    
    hns10 = manifest['hierarchical_structure']['hns_10_0_0_0_0_0_0_0_0_0']
    
    # Prüfe Beschreibung
    assert 'description' in hns10, "Description fehlt"
    assert 'WWAQ' in hns10['description'], "WWAQ nicht in Description"
    
    # Prüfe Subsysteme
    assert 'subsystems' in hns10, "Subsystems fehlen"
    subsystems = hns10['subsystems']
    
    # Prüfe alle 10 Subsysteme
    expected_subsystems = [
        'hns_10_1', 'hns_10_2', 'hns_10_3', 'hns_10_4', 'hns_10_5',
        'hns_10_6', 'hns_10_7', 'hns_10_8', 'hns_10_9', 'hns_10_0'
    ]
    
    for subsystem in expected_subsystems:
        assert subsystem in subsystems, f"Subsystem {subsystem} fehlt"
        assert 'name' in subsystems[subsystem], f"Name fehlt in {subsystem}"
        assert 'modules' in subsystems[subsystem], f"Module fehlen in {subsystem}"
    
    print("✓ Manifest-Struktur korrekt")


def test_all_modules_defined():
    """Test ob alle Module definiert sind"""
    manifest_path = project_root / "hns10_manifest.yaml"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    
    hns10 = manifest['hierarchical_structure']['hns_10_0_0_0_0_0_0_0_0_0']
    total_modules = 0
    
    for subsystem_key, subsystem in hns10['subsystems'].items():
        modules = subsystem.get('modules', [])
        total_modules += len(modules)
        
        # Prüfe Modul-Struktur
        for module in modules:
            assert 'id' in module, f"ID fehlt in Modul von {subsystem_key}"
            assert 'name' in module, f"Name fehlt in Modul von {subsystem_key}"
            assert 'file' in module, f"File fehlt in Modul von {subsystem_key}"
    
    # Sollten mindestens 100 Module sein (10x10)
    assert total_modules >= 100, f"Nur {total_modules} Module gefunden, erwartet >= 100"
    
    print(f"✓ {total_modules} Module definiert")


def test_file_paths_valid():
    """Test ob Dateipfade gültige Python-Modulnamen sind"""
    manifest_path = project_root / "hns10_manifest.yaml"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    
    hns10 = manifest['hierarchical_structure']['hns_10_0_0_0_0_0_0_0_0_0']
    invalid_paths = []
    
    for subsystem_key, subsystem in hns10['subsystems'].items():
        for module in subsystem.get('modules', []):
            file_path = module['file']
            
            # Prüfe ob Pfad mit .py endet
            if not file_path.endswith('.py'):
                invalid_paths.append(f"{module['id']}: {file_path} (nicht .py)")
            
            # Prüfe ob Pfad gültige Python-Module sind
            parts = file_path.replace('.py', '').split('/')
            for part in parts:
                if not part.replace('_', '').isalnum():
                    invalid_paths.append(f"{module['id']}: {file_path} (ungültiger Modulname)")
    
    assert len(invalid_paths) == 0, f"Ungültige Pfade gefunden:\n" + "\n".join(invalid_paths)
    
    print("✓ Alle Dateipfade gültig")


def test_no_duplicate_ids():
    """Test ob alle Modul-IDs eindeutig sind"""
    manifest_path = project_root / "hns10_manifest.yaml"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    
    hns10 = manifest['hierarchical_structure']['hns_10_0_0_0_0_0_0_0_0_0']
    all_ids = []
    
    for subsystem_key, subsystem in hns10['subsystems'].items():
        for module in subsystem.get('modules', []):
            all_ids.append(module['id'])
    
    # Prüfe auf Duplikate
    duplicates = [id for id in all_ids if all_ids.count(id) > 1]
    unique_duplicates = list(set(duplicates))
    
    assert len(unique_duplicates) == 0, f"Doppelte IDs gefunden: {unique_duplicates}"
    
    print(f"✓ Alle {len(all_ids)} IDs sind eindeutig")


if __name__ == "__main__":
    print("\nMANIFEST INTEGRITY TESTS")
    print("="*40)
    
    try:
        test_manifest_exists()
        test_manifest_structure()
        test_all_modules_defined()
        test_file_paths_valid()
        test_no_duplicate_ids()
        
        print("\n✓ Alle Tests bestanden!")
        print("\nQ!")
    except AssertionError as e:
        print(f"\n✗ Test fehlgeschlagen: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        sys.exit(1)
