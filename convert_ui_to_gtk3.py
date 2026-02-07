#!/usr/bin/env python3
"""
Convert GTK4/libadwaita UI files to GTK3 format.
"""

import sys
import re
import os
from pathlib import Path

def convert_ui_file(filepath):
    """Convert a single UI file from GTK4/libadwaita to GTK3."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Update requires statements
    content = re.sub(r'<requires lib="gtk" version="4\.0"/>', 
                     '<requires lib="gtk+" version="3.0"/>', content)
    content = re.sub(r'<requires lib="adwaita" version="[^"]+"/>\n?', '', content)
    
    # 2. Replace AdwApplicationWindow with GtkApplicationWindow
    content = re.sub(r'parent="AdwApplicationWindow"', 
                     'parent="GtkApplicationWindow"', content)
    
    # 3. Replace AdwPreferencesDialog with GtkDialog
    content = re.sub(r'parent="AdwPreferencesDialog"', 
                     'parent="GtkDialog"', content)
    
    # 4. Replace AdwToolbarView with GtkBox + GtkHeaderBar
    # This is complex - need to handle the structure
    content = convert_toolbar_view(content)
    
    # 5. Replace AdwHeaderBar with GtkHeaderBar
    content = re.sub(r'<object class="AdwHeaderBar"', 
                     '<object class="GtkHeaderBar"', content)
    
    # 6. Replace AdwViewStack with GtkStack
    content = re.sub(r'<object class="AdwViewStack"', 
                     '<object class="GtkStack"', content)
    
    # 7. Replace AdwViewStackPage with direct child
    content = convert_view_stack_pages(content)
    
    # 8. Replace AdwViewSwitcher with GtkStackSwitcher
    content = re.sub(r'<object class="AdwViewSwitcher"', 
                     '<object class="GtkStackSwitcher"', content)
    
    # 9. Replace AdwViewSwitcherBar with GtkStackSwitcher
    content = re.sub(r'<object class="AdwViewSwitcherBar"', 
                     '<object class="GtkStackSwitcher"', content)
    
    # 10. Replace AdwStatusPage with GtkBox
    content = convert_status_page(content)
    
    # 11. Replace AdwClamp with GtkBox
    content = convert_clamp(content)
    
    # 12. Replace AdwSpinner with GtkSpinner
    content = re.sub(r'<object class="AdwSpinner"', 
                     '<object class="GtkSpinner"', content)
    
    # 13. Replace AdwToastOverlay with GtkOverlay
    content = convert_toast_overlay(content)
    
    # 14. Replace AdwPreferencesPage with GtkBox
    content = convert_preferences_page(content)
    
    # 15. Replace AdwPreferencesGroup with GtkFrame
    content = convert_preferences_group(content)
    
    # 16. Replace AdwActionRow with GtkListBoxRow
    content = convert_action_row(content)
    
    # 17. Replace AdwSwitchRow with GtkListBoxRow + GtkSwitch
    content = convert_switch_row(content)
    
    # 18. Replace AdwButtonRow with GtkListBoxRow
    content = convert_button_row(content)
    
    # 19. Replace AdwWindowTitle with GtkLabel
    content = convert_window_title(content)
    
    # 20. Replace AdwLeaflet with GtkStack
    content = convert_leaflet(content)
    
    # 21. Replace AdwLeafletPage with direct child
    content = convert_leaflet_page(content)
    
    # 22. Replace AdwBreakpoint (remove, not supported in GTK3)
    content = remove_breakpoints(content)
    
    # 23. Replace AdwBin with direct child or GtkBin
    content = convert_bin(content)
    
    # 24. Replace AdwNavigationPage with GtkBox
    content = re.sub(r'<object class="AdwNavigationPage"', 
                     '<object class="GtkBox"', content)
    
    # 25. Replace AdwNavigationView with GtkStack
    content = re.sub(r'<object class="AdwNavigationView"', 
                     '<object class="GtkStack"', content)
    
    # 26. Update property names for GTK3
    content = update_properties(content)
    
    # 27. Remove GTK4-specific event controllers
    content = remove_gtk4_controllers(content)
    
    # Write back only if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def convert_toolbar_view(content):
    """Convert AdwToolbarView to GtkBox with vertical orientation."""
    # Pattern to match AdwToolbarView and its content
    pattern = r'<object class="AdwToolbarView"([^>]*)>(.*?)</object>'
    
    def replace_toolbar(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract top children (headers)
        top_children = []
        top_pattern = r'<child type="top">(.*?)</child>'
        for top_match in re.finditer(top_pattern, inner, re.DOTALL):
            top_children.append(top_match.group(1))
        
        # Extract bottom children
        bottom_children = []
        bottom_pattern = r'<child type="bottom">(.*?)</child>'
        for bottom_match in re.finditer(bottom_pattern, inner, re.DOTALL):
            bottom_children.append(bottom_match.group(1))
        
        # Extract content
        content_pattern = r'<property name="content">(.*?)</property>'
        content_match = re.search(content_pattern, inner, re.DOTALL)
        content_child = content_match.group(1) if content_match else ''
        
        # Build new structure
        result = f'<object class="GtkBox"{attrs}>\n'
        result += '            <property name="orientation">vertical</property>\n'
        
        # Add top children
        for top in top_children:
            result += f'            <child>\n{top}            </child>\n'
        
        # Add content
        if content_child:
            result += f'            <child>\n{content_child}            </child>\n'
        
        # Add bottom children
        for bottom in bottom_children:
            result += f'            <child>\n{bottom}            </child>\n'
        
        result += '          </object>'
        return result
    
    return re.sub(pattern, replace_toolbar, content, flags=re.DOTALL)

def convert_view_stack_pages(content):
    """Convert AdwViewStackPage to direct GtkStack children."""
    # Pattern to match AdwViewStackPage
    pattern = r'<object class="AdwViewStackPage"([^>]*)>(.*?)</object>'
    
    def replace_page(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract properties
        name = extract_property(inner, 'name')
        title = extract_property(inner, 'title')
        icon_name = extract_property(inner, 'icon-name')
        child_content = extract_child_property(inner, 'child')
        
        # Build new structure - direct child with name
        result = ''
        if child_content:
            # Add as direct child with name property
            result = f'          <child>\n            <object class="GtkStackChild">\n'
            if name:
                result += f'              <property name="name">{name}</property>\n'
            if title:
                result += f'              <property name="title">{title}</property>\n'
            if icon_name:
                result += f'              <property name="icon-name">{icon_name}</property>\n'
            result += f'{child_content}'
            result += '            </object>\n          </child>'
        
        return result
    
    content = re.sub(pattern, replace_page, content, flags=re.DOTALL)
    
    # Also handle simple case where child property is used
    # Replace <property name="child"> with direct <child>
    content = re.sub(r'<property name="child">\s*<object', '<child>\n              <object', content)
    content = re.sub(r'</object>\s*</property>\s*</object>\s*</child>', 
                     '</object>\n            </child>', content)
    
    return content

def convert_status_page(content):
    """Convert AdwStatusPage to GtkBox with centered content."""
    pattern = r'<object class="AdwStatusPage"([^>]*)>(.*?)</object>'
    
    def replace_status(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract properties
        icon_name = extract_property(inner, 'icon_name') or extract_property(inner, 'icon-name')
        title = extract_property(inner, 'title')
        description = extract_property(inner, 'description')
        
        # Extract style classes
        style = extract_style(inner)
        
        # Extract child content
        child_pattern = r'<child>(.*?)</child>'
        child_matches = re.findall(child_pattern, inner, re.DOTALL)
        
        # Build new structure
        result = f'<object class="GtkBox"{attrs}>\n'
        result += '            <property name="orientation">vertical</property>\n'
        result += '            <property name="valign">center</property>\n'
        result += '            <property name="halign">center</property>\n'
        result += '            <property name="vexpand">True</property>\n'
        result += '            <property name="hexpand">True</property>\n'
        result += '            <property name="spacing">12</property>\n'
        if style:
            result += style
        
        # Add icon if present
        if icon_name:
            result += '            <child>\n'
            result += '              <object class="GtkImage">\n'
            result += f'                <property name="icon_name">{icon_name}</property>\n'
            result += '                <property name="pixel-size">128</property>\n'
            result += '                <property name="halign">center</property>\n'
            result += '              </object>\n'
            result += '            </child>\n'
        
        # Add title if present
        if title:
            result += '            <child>\n'
            result += '              <object class="GtkLabel">\n'
            result += f'                <property name="label">{title}</property>\n'
            result += '                <property name="halign">center</property>\n'
            result += '                <style>\n'
            result += '                  <class name="title-1"/>\n'
            result += '                </style>\n'
            result += '              </object>\n'
            result += '            </child>\n'
        
        # Add description if present
        if description:
            result += '            <child>\n'
            result += '              <object class="GtkLabel">\n'
            result += f'                <property name="label">{description}</property>\n'
            result += '                <property name="halign">center</property>\n'
            result += '                <property name="wrap">True</property>\n'
            result += '              </object>\n'
            result += '            </child>\n'
        
        # Add any child elements
        for child in child_matches:
            result += f'            <child>{child}</child>\n'
        
        result += '          </object>'
        return result
    
    return re.sub(pattern, replace_status, content, flags=re.DOTALL)

def convert_clamp(content):
    """Convert AdwClamp to GtkBox with max-width-request."""
    pattern = r'<object class="AdwClamp"([^>]*)>(.*?)</object>'
    
    def replace_clamp(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract maximum-size property
        max_size = extract_property(inner, 'maximum-size') or extract_property(inner, 'maximum_size')
        
        # Extract child
        child_pattern = r'<child>(.*?)</child>'
        child_match = re.search(child_pattern, inner, re.DOTALL)
        child_content = child_match.group(1) if child_match else ''
        
        # Build new structure
        result = f'<object class="GtkBox"{attrs}>\n'
        result += '            <property name="halign">center</property>\n'
        if max_size:
            result += f'            <property name="max-width-request">{max_size}</property>\n'
        
        if child_content:
            result += f'            <child>{child_content}</child>\n'
        
        result += '          </object>'
        return result
    
    return re.sub(pattern, replace_clamp, content, flags=re.DOTALL)

def convert_toast_overlay(content):
    """Convert AdwToastOverlay to GtkOverlay or just remove it."""
    # For simplicity, we'll just unwrap it and keep the child
    pattern = r'<object class="AdwToastOverlay"([^>]*)>(.*?)</object>'
    
    def replace_toast(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract the child property
        child_match = re.search(r'<property name="child">(.*?)</property>', inner, re.DOTALL)
        if child_match:
            return child_match.group(1).strip()
        
        # Or extract direct child
        child_match = re.search(r'<child>(.*?)</child>', inner, re.DOTALL)
        if child_match:
            return child_match.group(1).strip()
        
        return match.group(0)  # Keep original if can't parse
    
    return re.sub(pattern, replace_toast, content, flags=re.DOTALL)

def convert_preferences_page(content):
    """Convert AdwPreferencesPage to GtkBox."""
    pattern = r'<object class="AdwPreferencesPage"([^>]*)>(.*?)</object>'
    
    def replace_page(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract children
        children = re.findall(r'<child>(.*?)</child>', inner, re.DOTALL)
        
        # Build new structure
        result = f'<object class="GtkScrolledWindow"{attrs}>\n'
        result += '        <property name="hscrollbar-policy">never</property>\n'
        result += '        <child>\n'
        result += '          <object class="GtkViewport">\n'
        result += '            <child>\n'
        result += '              <object class="GtkBox">\n'
        result += '                <property name="orientation">vertical</property>\n'
        result += '                <property name="margin-top">32</property>\n'
        result += '                <property name="margin-bottom">32</property>\n'
        result += '                <property name="margin-start">12</property>\n'
        result += '                <property name="margin-end">12</property>\n'
        result += '                <property name="spacing">24</property>\n'
        
        for child in children:
            result += f'                <child>{child}</child>\n'
        
        result += '              </object>\n'
        result += '            </child>\n'
        result += '          </object>\n'
        result += '        </child>\n'
        result += '      </object>'
        return result
    
    return re.sub(pattern, replace_page, content, flags=re.DOTALL)

def convert_preferences_group(content):
    """Convert AdwPreferencesGroup to GtkFrame."""
    pattern = r'<object class="AdwPreferencesGroup"([^>]*)>(.*?)</object>'
    
    def replace_group(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract title
        title = extract_property(inner, 'title')
        
        # Extract header-suffix
        header_suffix_match = re.search(r'<property name="header-suffix">(.*?)</property>', inner, re.DOTALL)
        header_suffix = header_suffix_match.group(1).strip() if header_suffix_match else None
        
        # Extract children
        children = re.findall(r'<child>(.*?)</child>', inner, re.DOTALL)
        
        # Build new structure
        result = f'<object class="GtkFrame"{attrs}>\n'
        if title:
            result += f'          <property name="label">{title}</property>\n'
        result += '          <child>\n'
        result += '            <object class="GtkListBox">\n'
        result += '              <property name="selection-mode">none</property>\n'
        result += '              <style>\n'
        result += '                <class name="boxed-list"/>\n'
        result += '              </style>\n'
        
        for child in children:
            result += f'              <child>{child}</child>\n'
        
        result += '            </object>\n'
        result += '          </child>\n'
        result += '        </object>'
        return result
    
    return re.sub(pattern, replace_group, content, flags=re.DOTALL)

def convert_action_row(content):
    """Convert AdwActionRow to GtkListBoxRow."""
    pattern = r'<object class="AdwActionRow"([^>]*)>(.*?)</object>'
    
    def replace_row(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract properties
        title = extract_property(inner, 'title')
        subtitle = extract_property(inner, 'subtitle')
        use_underline = extract_property(inner, 'use-underline')
        activatable_widget = extract_property(inner, 'activatable-widget')
        
        # Extract prefix/suffix children
        prefix_children = []
        suffix_children = []
        
        prefix_pattern = r'<child type="prefix">(.*?)</child>'
        for prefix_match in re.finditer(prefix_pattern, inner, re.DOTALL):
            prefix_children.append(prefix_match.group(1))
        
        suffix_pattern = r'<child type="suffix">(.*?)</child>'
        for suffix_match in re.finditer(suffix_pattern, inner, re.DOTALL):
            suffix_children.append(suffix_match.group(1))
        
        # Build new structure
        result = f'<object class="GtkListBoxRow"{attrs}>\n'
        if activatable_widget:
            result += f'          <property name="activatable">True</property>\n'
        result += '          <child>\n'
        result += '            <object class="GtkBox">\n'
        result += '              <property name="spacing">12</property>\n'
        result += '              <property name="margin-top">12</property>\n'
        result += '              <property name="margin-bottom">12</property>\n'
        result += '              <property name="margin-start">12</property>\n'
        result += '              <property name="margin-end">12</property>\n'
        
        # Add prefix
        for prefix in prefix_children:
            result += f'              <child>{prefix}</child>\n'
        
        # Add title/subtitle box
        result += '              <child>\n'
        result += '                <object class="GtkBox">\n'
        result += '                  <property name="orientation">vertical</property>\n'
        result += '                  <property name="hexpand">True</property>\n'
        
        if title:
            result += '                  <child>\n'
            result += '                    <object class="GtkLabel">\n'
            result += f'                      <property name="label">{title}</property>\n'
            result += '                      <property name="xalign">0</property>\n'
            if use_underline:
                result += f'                      <property name="use-underline">{use_underline}</property>\n'
            result += '                    </object>\n'
            result += '                  </child>\n'
        
        if subtitle:
            result += '                  <child>\n'
            result += '                    <object class="GtkLabel">\n'
            result += f'                      <property name="label">{subtitle}</property>\n'
            result += '                      <property name="xalign">0</property>\n'
            result += '                      <style>\n'
            result += '                        <class name="dim-label"/>\n'
            result += '                      </style>\n'
            result += '                    </object>\n'
            result += '                  </child>\n'
        
        result += '                </object>\n'
        result += '              </child>\n'
        
        # Add suffix
        for suffix in suffix_children:
            result += f'              <child>{suffix}</child>\n'
        
        result += '            </object>\n'
        result += '          </child>\n'
        result += '        </object>'
        return result
    
    return re.sub(pattern, replace_row, content, flags=re.DOTALL)

def convert_switch_row(content):
    """Convert AdwSwitchRow to GtkListBoxRow with switch."""
    pattern = r'<object class="AdwSwitchRow"([^>]*)>(.*?)</object>'
    
    def replace_row(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract properties
        title = extract_property(inner, 'title')
        subtitle = extract_property(inner, 'subtitle')
        use_underline = extract_property(inner, 'use-underline')
        
        # Build new structure with switch
        result = f'<object class="GtkListBoxRow"{attrs}>\n'
        result += '          <property name="activatable">False</property>\n'
        result += '          <child>\n'
        result += '            <object class="GtkBox">\n'
        result += '              <property name="spacing">12</property>\n'
        result += '              <property name="margin-top">12</property>\n'
        result += '              <property name="margin-bottom">12</property>\n'
        result += '              <property name="margin-start">12</property>\n'
        result += '              <property name="margin-end">12</property>\n'
        
        # Add title/subtitle box
        result += '              <child>\n'
        result += '                <object class="GtkBox">\n'
        result += '                  <property name="orientation">vertical</property>\n'
        result += '                  <property name="hexpand">True</property>\n'
        
        if title:
            result += '                  <child>\n'
            result += '                    <object class="GtkLabel">\n'
            result += f'                      <property name="label">{title}</property>\n'
            result += '                      <property name="xalign">0</property>\n'
            if use_underline:
                result += f'                      <property name="use-underline">{use_underline}</property>\n'
            result += '                    </object>\n'
            result += '                  </child>\n'
        
        if subtitle:
            result += '                  <child>\n'
            result += '                    <object class="GtkLabel">\n'
            result += f'                      <property name="label">{subtitle}</property>\n'
            result += '                      <property name="xalign">0</property>\n'
            result += '                      <style>\n'
            result += '                        <class name="dim-label"/>\n'
            result += '                      </style>\n'
            result += '                    </object>\n'
            result += '                  </child>\n'
        
        result += '                </object>\n'
        result += '              </child>\n'
        
        # Add switch
        result += '              <child>\n'
        result += '                <object class="GtkSwitch">\n'
        result += '                  <property name="valign">center</property>\n'
        result += '                </object>\n'
        result += '              </child>\n'
        
        result += '            </object>\n'
        result += '          </child>\n'
        result += '        </object>'
        return result
    
    return re.sub(pattern, replace_row, content, flags=re.DOTALL)

def convert_button_row(content):
    """Convert AdwButtonRow to GtkListBoxRow."""
    # Similar to AdwActionRow
    content = re.sub(r'<object class="AdwButtonRow"', 
                     '<object class="AdwActionRow"', content)
    return content

def convert_window_title(content):
    """Convert AdwWindowTitle to GtkLabel."""
    pattern = r'<object class="AdwWindowTitle"([^>]*)>(.*?)</object>'
    
    def replace_title(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract title property or binding
        title_prop = extract_property(inner, 'title')
        title_bind = extract_bind_source(inner, 'title')
        
        # Build simple label
        result = f'<object class="GtkLabel"{attrs}>\n'
        if title_prop:
            result += f'          <property name="label">{title_prop}</property>\n'
        if title_bind:
            result += title_bind
        result += '          <style>\n'
        result += '            <class name="title"/>\n'
        result += '          </style>\n'
        result += '        </object>'
        return result
    
    return re.sub(pattern, replace_title, content, flags=re.DOTALL)

def convert_leaflet(content):
    """Convert AdwLeaflet to GtkStack."""
    content = re.sub(r'<object class="AdwLeaflet"', 
                     '<object class="GtkStack"', content)
    # Remove AdwLeaflet-specific properties
    content = re.sub(r'<property name="can-navigate-back">.*?</property>\n?', '', content)
    content = re.sub(r'<property name="can-unfold">.*?</property>\n?', '', content)
    return content

def convert_leaflet_page(content):
    """Convert AdwLeafletPage to direct child."""
    pattern = r'<object class="AdwLeafletPage"([^>]*)>(.*?)</object>'
    
    def replace_page(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Extract name
        name = extract_property(inner, 'name')
        
        # Extract child property
        child_match = re.search(r'<property name="child">(.*?)</property>', inner, re.DOTALL)
        if child_match:
            child_content = child_match.group(1).strip()
            result = child_content
            return result
        
        return match.group(0)
    
    return re.sub(pattern, replace_page, content, flags=re.DOTALL)

def remove_breakpoints(content):
    """Remove AdwBreakpoint elements."""
    pattern = r'<child>\s*<object class="AdwBreakpoint">.*?</object>\s*</child>\n?'
    return re.sub(pattern, '', content, flags=re.DOTALL)

def convert_bin(content):
    """Convert AdwBin to direct child or GtkBin."""
    pattern = r'<object class="AdwBin"([^>]*)>(.*?)</object>'
    
    def replace_bin(match):
        attrs = match.group(1)
        inner = match.group(2)
        
        # Just unwrap it
        child_match = re.search(r'<child>(.*?)</child>', inner, re.DOTALL)
        if child_match:
            return child_match.group(1).strip()
        
        return match.group(0)
    
    return re.sub(pattern, replace_bin, content, flags=re.DOTALL)

def update_properties(content):
    """Update property names for GTK3 compatibility."""
    # icon_name vs icon-name (both work, but standardize)
    # No major property renames needed for basic widgets
    
    # Remove GTK4-specific properties
    content = re.sub(r'<property name="primary">.*?</property>\n?', '', content)
    
    # Update accessibility to accessible
    content = re.sub(r'<accessibility>', '<accessibility>', content)
    
    return content

def remove_gtk4_controllers(content):
    """Remove GTK4-specific event controllers."""
    # Remove GtkEventControllerKey
    content = re.sub(r'<child>\s*<object class="GtkEventControllerKey">.*?</object>\s*</child>\n?', 
                     '', content, flags=re.DOTALL)
    
    # Remove GtkShortcutController
    content = re.sub(r'<child>\s*<object class="GtkShortcutController">.*?</object>\s*</child>\n?', 
                     '', content, flags=re.DOTALL)
    
    # Remove GtkGestureClick
    content = re.sub(r'<child>\s*<object class="GtkGestureClick">.*?</object>\s*</child>\n?', 
                     '', content, flags=re.DOTALL)
    
    # Remove GtkWindowHandle
    pattern = r'<object class="GtkWindowHandle"([^>]*)>(.*?)</object>'
    
    def replace_handle(match):
        inner = match.group(2)
        # Extract child and unwrap
        child_match = re.search(r'<child>(.*?)</child>', inner, re.DOTALL)
        if child_match:
            return child_match.group(1).strip()
        return match.group(0)
    
    content = re.sub(pattern, replace_handle, content, flags=re.DOTALL)
    
    return content

def extract_property(content, prop_name):
    """Extract a property value from UI content."""
    # Handle both name="value" and name>value formats
    pattern1 = rf'<property name="{prop_name}">([^<]*)</property>'
    match = re.search(pattern1, content)
    if match:
        return match.group(1)
    
    pattern2 = rf'<property name="{prop_name}" ([^>]*)>([^<]*)</property>'
    match = re.search(pattern2, content)
    if match:
        return match.group(2)
    
    return None

def extract_child_property(content, prop_name):
    """Extract a child property value."""
    pattern = rf'<property name="{prop_name}">(.*?)</property>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def extract_style(content):
    """Extract style classes."""
    pattern = r'<style>(.*?)</style>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(0) + '\n'
    return ''

def extract_bind_source(content, prop_name):
    """Extract bind-source for a property."""
    pattern = rf'<property name="{prop_name}"[^>]*bind-source="([^"]*)"[^>]*bind-property="([^"]*)"[^>]*>'
    match = re.search(pattern, content)
    if match:
        return f'          <property name="label" bind-source="{match.group(1)}" bind-property="{match.group(2)}" bind-flags="sync-create"/>\n'
    return ''

def main():
    """Main function to process all UI files."""
    src_dir = Path('src')
    ui_files = list(src_dir.glob('*.ui'))
    
    print(f"Found {len(ui_files)} UI files to convert")
    
    converted = 0
    for ui_file in sorted(ui_files):
        print(f"Processing {ui_file.name}...", end=' ')
        if convert_ui_file(ui_file):
            print("✓ converted")
            converted += 1
        else:
            print("- no changes")
    
    print(f"\nConversion complete: {converted}/{len(ui_files)} files modified")

if __name__ == '__main__':
    main()
