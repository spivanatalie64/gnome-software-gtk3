#!/usr/bin/env python3
"""
Simpler, more reliable GTK4/libadwaita to GTK3 UI file converter.
"""

import re
import sys
from pathlib import Path

def convert_ui_file(filepath):
    """Convert a single UI file from GTK4/libadwaita to GTK3."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Update requires statements - SIMPLE replacements
    content = content.replace('<requires lib="gtk" version="4.0"/>', 
                              '<requires lib="gtk+" version="3.0"/>')
    content = re.sub(r'  <requires lib="adwaita" version="[^"]+"/>\n', '', content)
    
    # 2. Simple class name replacements (no structural changes)
    replacements = [
        ('AdwApplicationWindow', 'GtkApplicationWindow'),
        ('AdwHeaderBar', 'GtkHeaderBar'),
        ('AdwViewStack', 'GtkStack'),
        ('AdwViewSwitcher', 'GtkStackSwitcher'),
        ('AdwViewSwitcherBar', 'GtkStackSwitcher'),
        ('AdwSpinner', 'GtkSpinner'),
        ('AdwNavigationView', 'GtkStack'),
        ('AdwNavigationPage', 'GtkBox'),
        ('AdwLeaflet', 'GtkStack'),
    ]
    
    for old, new in replacements:
        content = content.replace(f'<object class="{old}"', f'<object class="{new}"')
    
    # 3. Remove GTK4-specific properties that don't exist in GTK3
    lines_to_remove = [
        r'.*<property name="primary">.*',
        r'.*<property name="can-navigate-back">.*',
        r'.*<property name="can-unfold">.*',
        r'.*<property name="propagation-phase">.*',
    ]
    
    for pattern in lines_to_remove:
        content = re.sub(pattern + r'\n', '', content)
    
    # 4. Remove GTK4-only event controllers (keep structure intact)
    # Remove entire <child>...</child> blocks for controllers
    content = re.sub(
        r'    <child>\n      <object class="GtkEventControllerKey">.*?</object>\n    </child>\n',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'    <child>\n      <object class="GtkShortcutController">.*?</object>\n    </child>\n',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'    <child>\n      <object class="GtkGestureClick">.*?</object>\n    </child>\n',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'    <child>\n      <object class="AdwBreakpoint">.*?</object>\n    </child>\n',
        '', content, flags=re.DOTALL
    )
    
    # 5. Simple unwrapping - AdwToastOverlay
    # Just remove the wrapper, keep the child
    content = unwrap_simple_container(content, 'AdwToastOverlay')
    content = unwrap_simple_container(content, 'GtkWindowHandle')
    content = unwrap_simple_container(content, 'AdwBin')
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def unwrap_simple_container(content, class_name):
    """Remove a simple wrapper container, keeping its child."""
    # Match pattern: <object class="ClassName" ...> with child property
    pattern = (
        rf'<object class="{class_name}"[^>]*>\s*'
        r'<property name="child">\s*'
        r'(.*?)'
        r'</property>\s*'
        r'</object>'
    )
    
    def replacer(match):
        return match.group(1)
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    # Also handle direct <child> pattern
    pattern2 = (
        rf'<object class="{class_name}"[^>]*>\s*'
        r'<child>\s*'
        r'(.*?)'
        r'</child>\s*'
        r'</object>'
    )
    content = re.sub(pattern2, replacer, content, flags=re.DOTALL)
    
    return content

def main():
    """Main function to process all UI files."""
    src_dir = Path('src')
    ui_files = list(src_dir.glob('*.ui'))
    
    print(f"Found {len(ui_files)} UI files to convert (Phase 1: Simple replacements)")
    
    converted = 0
    for ui_file in sorted(ui_files):
        print(f"Processing {ui_file.name}...", end=' ')
        if convert_ui_file(ui_file):
            print("✓ converted")
            converted += 1
        else:
            print("- no changes")
    
    print(f"\nPhase 1 complete: {converted}/{len(ui_files)} files modified")
    print("\nNote: Complex widgets (AdwToolbarView, AdwPreferencesDialog, etc.)")
    print("will need manual conversion or Phase 2 processing.")

if __name__ == '__main__':
    main()
