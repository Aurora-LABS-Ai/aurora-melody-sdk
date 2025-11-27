#!/usr/bin/env python3
"""
Aurora Melody Plugin Packager (aurora-pack)
============================================

Package plugin folders into .aml files for Aurora Melody.

Usage:
    aurora-pack <plugin_folder> [options]
    
Examples:
    aurora-pack ./my-plugin
    aurora-pack ./my-plugin -o ./output/my-plugin.aml
    aurora-pack ./my-plugin --quiet

The plugin folder must contain:
    - manifest.json (required) - Plugin metadata
    - main.py (required) - Entry point
    - icon.png (optional) - Plugin icon
"""

import os
import sys
import json
import zipfile
import argparse
from pathlib import Path
from typing import Tuple, Dict, Any, Optional


def validate_manifest(manifest_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate manifest.json and return (valid, error_message, manifest_data).
    """
    if not manifest_path.exists():
        return False, "manifest.json not found", {}
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in manifest.json: {e}", {}
    
    # Required fields
    required = ['id', 'name', 'version', 'author', 'entry']
    missing = [field for field in required if field not in manifest]
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}", {}
    
    # Validate version format
    version = manifest.get('version', '')
    if not version or not any(c.isdigit() for c in version):
        return False, f"Invalid version format: {version}", {}
    
    return True, "", manifest


def validate_entry_point(plugin_dir: Path, entry_point: str) -> Tuple[bool, str]:
    """
    Validate that the entry point file exists and has valid syntax.
    """
    entry_path = plugin_dir / entry_point
    if not entry_path.exists():
        return False, f"Entry point not found: {entry_point}"
    
    # Basic Python syntax check
    try:
        with open(entry_path, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, str(entry_path), 'exec')
    except SyntaxError as e:
        return False, f"Syntax error in {entry_point}: {e}"
    
    return True, ""


def create_package(plugin_dir: Path, output_path: Path, verbose: bool = True) -> Tuple[bool, str]:
    """
    Create the .aml package (ZIP file).
    """
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(plugin_dir):
                # Skip hidden and cache directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    # Skip hidden and compiled files
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(plugin_dir)
                    
                    if verbose:
                        print(f"  Adding: {arcname}")
                    zf.write(file_path, arcname)
        
        return True, ""
    
    except Exception as e:
        return False, f"Failed to create package: {e}"


def pack(
    plugin_dir: str,
    output_path: Optional[str] = None,
    verbose: bool = True
) -> bool:
    """
    Package a plugin folder into an .aml file.
    
    Args:
        plugin_dir: Path to the plugin folder
        output_path: Optional output path for .aml file
        verbose: Print progress messages
    
    Returns:
        True if successful
    """
    plugin_path = Path(plugin_dir).resolve()
    
    if not plugin_path.exists():
        print(f"Error: Plugin folder not found: {plugin_path}")
        return False
    
    if not plugin_path.is_dir():
        print(f"Error: Not a directory: {plugin_path}")
        return False
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Aurora Melody Plugin Packager")
        print(f"{'='*60}")
        print(f"Source: {plugin_path}")
    
    # Validate manifest
    manifest_path = plugin_path / "manifest.json"
    valid, error, manifest = validate_manifest(manifest_path)
    
    if not valid:
        print(f"Error: {error}")
        return False
    
    if verbose:
        print(f"\nPlugin: {manifest['name']} v{manifest['version']}")
        print(f"Author: {manifest['author']}")
        print(f"Entry:  {manifest['entry']}")
    
    # Validate entry point
    valid, error = validate_entry_point(plugin_path, manifest['entry'])
    if not valid:
        print(f"Error: {error}")
        return False
    
    # Determine output path
    if output_path:
        out_path = Path(output_path)
    else:
        plugin_name = manifest.get('id', plugin_path.name).replace('.', '-')
        out_path = plugin_path.parent / f"{plugin_name}.aml"
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"\nOutput: {out_path}")
        print(f"\nPackaging files:")
    
    # Create package
    valid, error = create_package(plugin_path, out_path, verbose)
    
    if not valid:
        print(f"Error: {error}")
        return False
    
    size_kb = out_path.stat().st_size / 1024
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"SUCCESS! Created: {out_path.name} ({size_kb:.1f} KB)")
        print(f"{'='*60}")
        print(f"\nInstall: Drag {out_path.name} into Aurora Melody")
    
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aurora-pack",
        description="Package Aurora Melody plugins into .aml files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    aurora-pack ./my-plugin
    aurora-pack ./my-plugin -o ./output/my-plugin.aml
    aurora-pack ./my-plugin --quiet

Required files in plugin folder:
    manifest.json   Plugin metadata (id, name, version, author, entry)
    main.py         Entry point Python file (or as specified in manifest)
        """
    )
    
    parser.add_argument(
        'plugin_folder',
        help='Path to the plugin folder to package'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output path for .aml file'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - only print errors'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='aurora-pack 1.0.0 (Aurora Melody SDK)'
    )
    
    args = parser.parse_args()
    
    success = pack(
        args.plugin_folder,
        args.output,
        verbose=not args.quiet
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

