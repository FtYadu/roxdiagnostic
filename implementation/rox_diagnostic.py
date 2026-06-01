#!/usr/bin/env python3
"""
ROX 01 Diagnostic Tool - Main CLI Interface
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from rox_diagnostic_core import ROX01DiagnosticTool
    from protocol import UDSService
except ImportError:
    print("ERROR: Missing dependencies. Run: python windows-setup.ps1")
    sys.exit(1)

__version__ = "1.0.0"

class Config:
    def __init__(self):
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "can_interface": "can0",
                "can_bitrate": 500000,
            }
    
    def get(self, key, default=None):
        return self.data.get(key, default)

config = Config()

@click.group()
@click.version_option(__version__)
def cli():
    """ROX 01 Diagnostic Tool"""
    pass

@cli.group()
def firmware():
    """Firmware operations"""
    pass

@firmware.command()
@click.option('--output', default=f"firmware_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin", help='Output file')
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def extract(output, interface):
    """Extract firmware from vehicle"""
    click.echo("[*] Initializing...")
    
    try:
        tool = ROX01DiagnosticTool(interface)
        
        if not tool.start_diagnostic_session():
            click.echo("[!] Failed to start session", err=True)
            sys.exit(1)
        
        click.echo(f"[*] Extracting to {output}...")
        if tool.extract_firmware(output):
            click.echo(f"[+] SUCCESS: {output}")
            size = Path(output).stat().st_size / 1024 / 1024
            click.echo(f"[+] Size: {size:.2f} MB")
        else:
            click.echo("[!] FAILED", err=True)
        
        tool.end_diagnostic_session()
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@firmware.command()
@click.argument('firmware_file')
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def update(firmware_file, interface):
    """Update ECU firmware"""
    if not click.confirm("WARNING: Firmware update can damage vehicle. Continue?"):
        return
    
    try:
        tool = ROX01DiagnosticTool(interface)
        if tool.upload_firmware(firmware_file):
            click.echo("[+] SUCCESS")
        else:
            click.echo("[!] FAILED", err=True)
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def live_data(interface):
    """Read live data"""
    click.echo("[*] Connecting...")
    
    try:
        tool = ROX01DiagnosticTool(interface)
        
        if not tool.start_diagnostic_session():
            click.echo("[!] Failed", err=True)
            sys.exit(1)
        
        data = tool.read_live_data()
        for name, value in data.items():
            click.echo(f"  {name}: {value:.2f}")
        
        tool.end_diagnostic_session()
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def read_faults(interface):
    """Read fault codes"""
    click.echo("[*] Connecting...")
    
    try:
        tool = ROX01DiagnosticTool(interface)
        
        if not tool.start_diagnostic_session():
            click.echo("[!] Failed", err=True)
            sys.exit(1)
        
        dtcs = tool.read_dtc()
        if dtcs:
            for code in dtcs:
                click.echo(f"  {code}")
        else:
            click.echo("  No faults found")
        
        tool.end_diagnostic_session()
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def clear_faults(interface):
    """Clear fault codes"""
    if not click.confirm("Clear all faults?"):
        return
    
    try:
        tool = ROX01DiagnosticTool(interface)
        
        if not tool.start_diagnostic_session():
            click.echo("[!] Failed", err=True)
            sys.exit(1)
        
        if tool.clear_dtc():
            click.echo("[+] Cleared")
        else:
            click.echo("[!] Failed", err=True)
        
        tool.end_diagnostic_session()
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--type', type=click.Choice(['soft', 'hard', 'full']), default='soft')
@click.option('--interface', default=config.get('can_interface'), help='CAN interface')
def reset(type, interface):
    """Reset ECU"""
    if not click.confirm(f"Perform {type} reset?"):
        return
    
    try:
        tool = ROX01DiagnosticTool(interface)
        
        if not tool.start_diagnostic_session():
            click.echo("[!] Failed", err=True)
            sys.exit(1)
        
        if tool.reset_ecu(type):
            click.echo("[+] Reset complete")
        else:
            click.echo("[!] Failed", err=True)
        
        tool.end_diagnostic_session()
    except Exception as e:
        click.echo(f"[!] Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def info():
    """Show tool info"""
    click.echo(f"""
╔══════════════════════════════════════════════════════════╗
║     ROX 01 DIAGNOSTIC TOOL v{__version__}                   ║
╚══════════════════════════════════════════════════════════╝

Features:
  ✅ Firmware extraction
  ✅ Live data reading
  ✅ DTC management
  ✅ ECU reset
  ✅ Firmware updates

Config:
  Interface:  {config.get('can_interface')}
  Bitrate:    {config.get('can_bitrate')} bps

GitHub: https://github.com/FtYadu/roxdiagnostic
License: MIT
""")

@cli.command()
def help():
    """Show help"""
    click.echo("""
USAGE:
  python rox_diagnostic.py firmware extract          # Extract firmware
  python rox_diagnostic.py live-data                 # Read live data
  python rox_diagnostic.py read-faults               # Read fault codes
  python rox_diagnostic.py clear-faults              # Clear faults
  python rox_diagnostic.py reset --type soft         # Reset ECU
  python rox_diagnostic.py firmware update FILE      # Update firmware
  python rox_diagnostic.py info                      # Show info
""")

if __name__ == '__main__':
    cli()
