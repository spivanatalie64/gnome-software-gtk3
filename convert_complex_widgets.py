#!/usr/bin/env python3
"""
Convert complex libadwaita widgets to GTK3 equivalents in .ui files.
This script handles structural transformations that require more than simple replacements.
"""

import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path


def preserve_formatting(element):
    """Preserve whitespace and indentation in XML."""
    # ElementTree typically preserves text and tail
    pass


def indent_xml(elem, level=0, indent_str="  "):
    """Add proper indentation to XML elements."""
    i = "\n" + level * indent_str
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent_str
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent_xml(child, level + 1, indent_str)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def find_property(element, name):
    """Find a property element by name."""
    for prop in element.findall('property'):
        if prop.get('name') == name:
            return prop
    return None


def remove_property(element, name):
    """Remove a property element by name."""
    for prop in element.findall('property'):
        if prop.get('name') == name:
            element.remove(prop)
            return True
    return False


def convert_adw_toolbar_view(toolbar_view):
    """Convert AdwToolbarView to GtkBox with vertical orientation."""
    # Create new GtkBox
    box = ET.Element('object')
    box.set('class', 'GtkBox')
    if toolbar_view.get('id'):
        box.set('id', toolbar_view.get('id'))
    
    # Add orientation property
    orientation = ET.SubElement(box, 'property')
    orientation.set('name', 'orientation')
    orientation.text = 'vertical'
    
    # Copy other properties (except content)
    for prop in toolbar_view.findall('property'):
        if prop.get('name') not in ['content']:
            new_prop = ET.SubElement(box, 'property')
            new_prop.set('name', prop.get('name'))
            new_prop.text = prop.text
            for attr_key, attr_val in prop.attrib.items():
                if attr_key != 'name':
                    new_prop.set(attr_key, attr_val)
    
    # Copy style classes
    for style in toolbar_view.findall('style'):
        box.append(style)
    
    # Process children in order: top, content, bottom
    # First, add top children
    for child in toolbar_view.findall('child'):
        if child.get('type') == 'top':
            new_child = ET.SubElement(box, 'child')
            child_obj = child.find('object')
            if child_obj is not None:
                new_child.append(child_obj)
    
    # Then, add content
    content_prop = find_property(toolbar_view, 'content')
    if content_prop is not None:
        content_obj = content_prop.find('object')
        if content_obj is not None:
            new_child = ET.SubElement(box, 'child')
            new_child.append(content_obj)
    
    # Finally, add bottom children
    for child in toolbar_view.findall('child'):
        if child.get('type') == 'bottom':
            new_child = ET.SubElement(box, 'child')
            child_obj = child.find('object')
            if child_obj is not None:
                new_child.append(child_obj)
    
    return box


def convert_adw_status_page(status_page):
    """Convert AdwStatusPage to GtkBox with centered layout."""
    # Create outer GtkBox
    box = ET.Element('object')
    box.set('class', 'GtkBox')
    if status_page.get('id'):
        box.set('id', status_page.get('id'))
    
    # Add orientation
    orientation = ET.SubElement(box, 'property')
    orientation.set('name', 'orientation')
    orientation.text = 'vertical'
    
    # Add alignment
    valign = ET.SubElement(box, 'property')
    valign.set('name', 'valign')
    valign.text = 'center'
    
    halign = ET.SubElement(box, 'property')
    halign.set('name', 'halign')
    halign.text = 'center'
    
    # Copy style classes
    for style in status_page.findall('style'):
        box.append(style)
    
    # Get properties
    icon_name_prop = find_property(status_page, 'icon_name')
    title_prop = find_property(status_page, 'title')
    description_prop = find_property(status_page, 'description')
    paintable_prop = find_property(status_page, 'paintable')
    
    # Add icon if present
    if icon_name_prop is not None:
        child = ET.SubElement(box, 'child')
        image = ET.SubElement(child, 'object')
        image.set('class', 'GtkImage')
        
        icon_prop = ET.SubElement(image, 'property')
        icon_prop.set('name', 'icon-name')
        icon_prop.text = icon_name_prop.text
        for attr_key, attr_val in icon_name_prop.attrib.items():
            if attr_key != 'name':
                icon_prop.set(attr_key, attr_val)
        
        pixel_size = ET.SubElement(image, 'property')
        pixel_size.set('name', 'pixel-size')
        pixel_size.text = '128'
    
    # Handle paintable (spinner) if present
    if paintable_prop is not None:
        spinner_obj = paintable_prop.find('.//object[@class="AdwSpinnerPaintable"]')
        if spinner_obj is not None:
            child = ET.SubElement(box, 'child')
            spinner = ET.SubElement(child, 'object')
            spinner.set('class', 'GtkSpinner')
            
            active = ET.SubElement(spinner, 'property')
            active.set('name', 'active')
            active.text = 'True'
            
            width = ET.SubElement(spinner, 'property')
            width.set('name', 'width-request')
            width.text = '32'
            
            height = ET.SubElement(spinner, 'property')
            height.set('name', 'height-request')
            height.text = '32'
    
    # Add title if present
    if title_prop is not None:
        child = ET.SubElement(box, 'child')
        label = ET.SubElement(child, 'object')
        label.set('class', 'GtkLabel')
        
        text_prop = ET.SubElement(label, 'property')
        text_prop.set('name', 'label')
        text_prop.text = title_prop.text
        for attr_key, attr_val in title_prop.attrib.items():
            if attr_key != 'name':
                text_prop.set(attr_key, attr_val)
        
        style = ET.SubElement(label, 'style')
        style_class = ET.SubElement(style, 'class')
        style_class.set('name', 'title-1')
    
    # Add description if present
    if description_prop is not None:
        child = ET.SubElement(box, 'child')
        label = ET.SubElement(child, 'object')
        label.set('class', 'GtkLabel')
        
        text_prop = ET.SubElement(label, 'property')
        text_prop.set('name', 'label')
        text_prop.text = description_prop.text
        for attr_key, attr_val in description_prop.attrib.items():
            if attr_key != 'name':
                text_prop.set(attr_key, attr_val)
        
        wrap = ET.SubElement(label, 'property')
        wrap.set('name', 'wrap')
        wrap.text = 'True'
    
    # Copy existing children
    for child in status_page.findall('child'):
        box.append(child)
    
    return box


def convert_adw_clamp(clamp):
    """Convert AdwClamp to GtkBox with max-width-request."""
    box = ET.Element('object')
    box.set('class', 'GtkBox')
    if clamp.get('id'):
        box.set('id', clamp.get('id'))
    
    # Add halign center
    halign = ET.SubElement(box, 'property')
    halign.set('name', 'halign')
    halign.text = 'center'
    
    # Convert maximum-size to max-width-request
    max_size_prop = find_property(clamp, 'maximum-size')
    if max_size_prop is not None:
        max_width = ET.SubElement(box, 'property')
        max_width.set('name', 'max-width-request')
        max_width.text = max_size_prop.text
    
    # Copy other properties
    for prop in clamp.findall('property'):
        if prop.get('name') not in ['maximum-size', 'tightening-threshold']:
            new_prop = ET.SubElement(box, 'property')
            new_prop.set('name', prop.get('name'))
            new_prop.text = prop.text
            for attr_key, attr_val in prop.attrib.items():
                if attr_key != 'name':
                    new_prop.set(attr_key, attr_val)
    
    # Copy style classes
    for style in clamp.findall('style'):
        box.append(style)
    
    # Copy children
    for child in clamp.findall('child'):
        box.append(child)
    
    return box


def convert_adw_preferences_page(pref_page):
    """Convert AdwPreferencesPage to GtkScrolledWindow + GtkBox."""
    scrolled = ET.Element('object')
    scrolled.set('class', 'GtkScrolledWindow')
    if pref_page.get('id'):
        scrolled.set('id', pref_page.get('id'))
    
    # Set hscrollbar policy
    hscroll = ET.SubElement(scrolled, 'property')
    hscroll.set('name', 'hscrollbar-policy')
    hscroll.text = 'never'
    
    # Create inner box
    child = ET.SubElement(scrolled, 'child')
    box = ET.SubElement(child, 'object')
    box.set('class', 'GtkBox')
    
    orientation = ET.SubElement(box, 'property')
    orientation.set('name', 'orientation')
    orientation.text = 'vertical'
    
    margin = ET.SubElement(box, 'property')
    margin.set('name', 'margin-start')
    margin.text = '12'
    
    margin = ET.SubElement(box, 'property')
    margin.set('name', 'margin-end')
    margin.text = '12'
    
    margin = ET.SubElement(box, 'property')
    margin.set('name', 'margin-top')
    margin.text = '12'
    
    margin = ET.SubElement(box, 'property')
    margin.set('name', 'margin-bottom')
    margin.text = '12'
    
    spacing = ET.SubElement(box, 'property')
    spacing.set('name', 'spacing')
    spacing.text = '18'
    
    # Copy children from preferences page
    for pref_child in pref_page.findall('child'):
        box.append(pref_child)
    
    return scrolled


def convert_adw_preferences_group(pref_group):
    """Convert AdwPreferencesGroup to GtkFrame + GtkListBox."""
    frame = ET.Element('object')
    frame.set('class', 'GtkFrame')
    if pref_group.get('id'):
        frame.set('id', pref_group.get('id'))
    
    # Get title
    title_prop = find_property(pref_group, 'title')
    if title_prop is not None:
        label_prop = ET.SubElement(frame, 'property')
        label_prop.set('name', 'label')
        label_prop.text = title_prop.text
        for attr_key, attr_val in title_prop.attrib.items():
            if attr_key != 'name':
                label_prop.set(attr_key, attr_val)
    
    # Get description
    description_prop = find_property(pref_group, 'description')
    
    # Handle header-suffix
    header_suffix_prop = find_property(pref_group, 'header-suffix')
    
    # Create listbox
    child = ET.SubElement(frame, 'child')
    listbox = ET.SubElement(child, 'object')
    listbox.set('class', 'GtkListBox')
    
    selection = ET.SubElement(listbox, 'property')
    selection.set('name', 'selection-mode')
    selection.text = 'none'
    
    style = ET.SubElement(listbox, 'style')
    style_class = ET.SubElement(style, 'class')
    style_class.set('name', 'boxed-list')
    
    # If there's a description, add it as first row
    if description_prop is not None:
        desc_child = ET.SubElement(listbox, 'child')
        desc_row = ET.SubElement(desc_child, 'object')
        desc_row.set('class', 'GtkListBoxRow')
        
        activatable = ET.SubElement(desc_row, 'property')
        activatable.set('name', 'activatable')
        activatable.text = 'False'
        
        row_child = ET.SubElement(desc_row, 'child')
        label = ET.SubElement(row_child, 'object')
        label.set('class', 'GtkLabel')
        
        label_text = ET.SubElement(label, 'property')
        label_text.set('name', 'label')
        label_text.text = description_prop.text
        for attr_key, attr_val in description_prop.attrib.items():
            if attr_key != 'name':
                label_text.set(attr_key, attr_val)
        
        wrap = ET.SubElement(label, 'property')
        wrap.set('name', 'wrap')
        wrap.text = 'True'
        
        xalign = ET.SubElement(label, 'property')
        xalign.set('name', 'xalign')
        xalign.text = '0'
    
    # Copy children from preferences group
    for group_child in pref_group.findall('child'):
        listbox.append(group_child)
    
    return frame


def convert_adw_action_row(action_row):
    """Convert AdwActionRow to GtkListBoxRow with proper layout."""
    row = ET.Element('object')
    row.set('class', 'GtkListBoxRow')
    if action_row.get('id'):
        row.set('id', action_row.get('id'))
    
    # Copy activatable-widget property
    activatable_prop = find_property(action_row, 'activatable-widget')
    if activatable_prop is not None:
        new_prop = ET.SubElement(row, 'property')
        new_prop.set('name', 'activatable')
        new_prop.text = 'True'
    
    # Copy selectable property
    selectable_prop = find_property(action_row, 'selectable')
    if selectable_prop is not None:
        new_prop = ET.SubElement(row, 'property')
        new_prop.set('name', 'selectable')
        new_prop.text = selectable_prop.text
    
    # Create main horizontal box
    child = ET.SubElement(row, 'child')
    hbox = ET.SubElement(child, 'object')
    hbox.set('class', 'GtkBox')
    
    orientation = ET.SubElement(hbox, 'property')
    orientation.set('name', 'orientation')
    orientation.text = 'horizontal'
    
    spacing = ET.SubElement(hbox, 'property')
    spacing.set('name', 'spacing')
    spacing.text = '12'
    
    margin = ET.SubElement(hbox, 'property')
    margin.set('name', 'margin-start')
    margin.text = '12'
    
    margin = ET.SubElement(hbox, 'property')
    margin.set('name', 'margin-end')
    margin.text = '12'
    
    margin = ET.SubElement(hbox, 'property')
    margin.set('name', 'margin-top')
    margin.text = '12'
    
    margin = ET.SubElement(hbox, 'property')
    margin.set('name', 'margin-bottom')
    margin.text = '12'
    
    # Add prefix children
    for prefix_child in action_row.findall("child[@type='prefix']"):
        hbox.append(prefix_child)
    
    # Create center box for title/subtitle
    center_child = ET.SubElement(hbox, 'child')
    vbox = ET.SubElement(center_child, 'object')
    vbox.set('class', 'GtkBox')
    
    orientation = ET.SubElement(vbox, 'property')
    orientation.set('name', 'orientation')
    orientation.text = 'vertical'
    
    hexpand = ET.SubElement(vbox, 'property')
    hexpand.set('name', 'hexpand')
    hexpand.text = 'True'
    
    valign = ET.SubElement(vbox, 'property')
    valign.set('name', 'valign')
    valign.text = 'center'
    
    spacing = ET.SubElement(vbox, 'property')
    spacing.set('name', 'spacing')
    spacing.text = '3'
    
    # Add title
    title_prop = find_property(action_row, 'title')
    use_markup_prop = find_property(action_row, 'use-markup')
    use_underline_prop = find_property(action_row, 'use-underline')
    
    if title_prop is not None:
        title_child = ET.SubElement(vbox, 'child')
        title_label = ET.SubElement(title_child, 'object')
        title_label.set('class', 'GtkLabel')
        
        label_text = ET.SubElement(title_label, 'property')
        label_text.set('name', 'label')
        label_text.text = title_prop.text
        for attr_key, attr_val in title_prop.attrib.items():
            if attr_key != 'name':
                label_text.set(attr_key, attr_val)
        
        xalign = ET.SubElement(title_label, 'property')
        xalign.set('name', 'xalign')
        xalign.text = '0'
        
        if use_markup_prop is not None and use_markup_prop.text.lower() == 'true':
            markup = ET.SubElement(title_label, 'property')
            markup.set('name', 'use-markup')
            markup.text = 'True'
        
        if use_underline_prop is not None and use_underline_prop.text.lower() == 'true':
            underline = ET.SubElement(title_label, 'property')
            underline.set('name', 'use-underline')
            underline.text = 'True'
    
    # Add subtitle
    subtitle_prop = find_property(action_row, 'subtitle')
    if subtitle_prop is not None:
        subtitle_child = ET.SubElement(vbox, 'child')
        subtitle_label = ET.SubElement(subtitle_child, 'object')
        subtitle_label.set('class', 'GtkLabel')
        
        label_text = ET.SubElement(subtitle_label, 'property')
        label_text.set('name', 'label')
        label_text.text = subtitle_prop.text
        for attr_key, attr_val in subtitle_prop.attrib.items():
            if attr_key != 'name':
                label_text.set(attr_key, attr_val)
        
        xalign = ET.SubElement(subtitle_label, 'property')
        xalign.set('name', 'xalign')
        xalign.text = '0'
        
        style = ET.SubElement(subtitle_label, 'style')
        style_class = ET.SubElement(style, 'class')
        style_class.set('name', 'dim-label')
    
    # Add suffix children
    for suffix_child in action_row.findall("child[@type='suffix']"):
        hbox.append(suffix_child)
    
    return row


def convert_adw_switch_row(switch_row):
    """Convert AdwSwitchRow to GtkListBoxRow + GtkSwitch."""
    # Start like action row
    row = convert_adw_action_row(switch_row)
    
    # Find the horizontal box we created
    hbox = row.find(".//object[@class='GtkBox']")
    
    # Add switch at the end
    switch_child = ET.SubElement(hbox, 'child')
    switch = ET.SubElement(switch_child, 'object')
    switch.set('class', 'GtkSwitch')
    if switch_row.get('id'):
        # Use the row id for the switch for binding purposes
        switch.set('id', switch_row.get('id') + '_switch')
    
    valign = ET.SubElement(switch, 'property')
    valign.set('name', 'valign')
    valign.text = 'center'
    
    return row


def convert_adw_window_title(window_title):
    """Convert AdwWindowTitle to GtkLabel."""
    label = ET.Element('object')
    label.set('class', 'GtkLabel')
    if window_title.get('id'):
        label.set('id', window_title.get('id'))
    
    # Get title property
    title_prop = find_property(window_title, 'title')
    if title_prop is not None:
        label_prop = ET.SubElement(label, 'property')
        label_prop.set('name', 'label')
        label_prop.text = title_prop.text
        for attr_key, attr_val in title_prop.attrib.items():
            if attr_key != 'name':
                label_prop.set(attr_key, attr_val)
    
    # Add style class
    style = ET.SubElement(label, 'style')
    style_class = ET.SubElement(style, 'class')
    style_class.set('name', 'title')
    
    # Copy other properties and bindings
    for prop in window_title.findall('property'):
        if prop.get('name') not in ['title', 'subtitle']:
            label.append(prop)
    
    return label


def unwrap_viewstack_page(parent):
    """Remove AdwViewStackPage wrapper, convert properties to child properties."""
    for child in parent.findall('child'):
        obj = child.find('object')
        if obj is not None and obj.get('class') == 'AdwViewStackPage':
            # Get the name property
            name_prop = find_property(obj, 'name')
            name_value = name_prop.text if name_prop is not None else None
            
            # Get title property
            title_prop = find_property(obj, 'title')
            title_value = title_prop.text if title_prop is not None else None
            
            # Get icon-name property
            icon_prop = find_property(obj, 'icon-name')
            icon_value = icon_prop.text if icon_prop is not None else None
            
            # Get the child property
            child_prop = find_property(obj, 'child')
            if child_prop is not None:
                inner_obj = child_prop.find('object')
                if inner_obj is not None:
                    # Replace the AdwViewStackPage object with the inner object
                    child.remove(obj)
                    child.append(inner_obj)
                    
                    # Add child properties to the child element
                    if name_value:
                        child_packing = ET.Element('packing')
                        name_pack = ET.SubElement(child_packing, 'property')
                        name_pack.set('name', 'name')
                        name_pack.text = name_value
                        child.insert(0, child_packing)
                    
                    # For GTK3, we need to use GtkStackPage or child packing
                    # Let's use the name as a child type
                    if name_value:
                        child.set('type', name_value)


def unwrap_leaflet_page(parent):
    """Remove AdwLeafletPage wrapper."""
    for child in parent.findall('child'):
        obj = child.find('object')
        if obj is not None and obj.get('class') == 'AdwLeafletPage':
            # Get the name property
            name_prop = find_property(obj, 'name')
            name_value = name_prop.text if name_prop is not None else None
            
            # Get the child property
            child_prop = find_property(obj, 'child')
            if child_prop is not None:
                inner_obj = child_prop.find('object')
                if inner_obj is not None:
                    # Replace the AdwLeafletPage object with the inner object
                    child.remove(obj)
                    child.append(inner_obj)
                    
                    # Use name as child type if present
                    if name_value:
                        child.set('type', name_value)


def replace_in_parent(parent, old_elem, new_elem):
    """Replace an element in its parent while preserving position."""
    try:
        idx = list(parent).index(old_elem)
        parent.remove(old_elem)
        parent.insert(idx, new_elem)
    except (ValueError, AttributeError):
        # If we can't find it, just append
        parent.append(new_elem)


def process_element(element):
    """Recursively process an element and its children."""
    # Process children first (depth-first)
    for child in list(element):
        process_element(child)
    
    # Then process object elements
    for obj in list(element.findall('object')):
        class_name = obj.get('class')
        new_obj = None
        
        if class_name == 'AdwToolbarView':
            new_obj = convert_adw_toolbar_view(obj)
        elif class_name == 'AdwStatusPage':
            new_obj = convert_adw_status_page(obj)
        elif class_name == 'AdwClamp':
            new_obj = convert_adw_clamp(obj)
        elif class_name == 'AdwPreferencesPage':
            new_obj = convert_adw_preferences_page(obj)
        elif class_name == 'AdwPreferencesGroup':
            new_obj = convert_adw_preferences_group(obj)
        elif class_name == 'AdwActionRow':
            new_obj = convert_adw_action_row(obj)
        elif class_name == 'AdwSwitchRow':
            new_obj = convert_adw_switch_row(obj)
        elif class_name == 'AdwButtonRow':
            new_obj = convert_adw_action_row(obj)
        elif class_name == 'AdwWindowTitle':
            new_obj = convert_adw_window_title(obj)
        
        if new_obj is not None:
            replace_in_parent(element, obj, new_obj)
    
    # Handle unwrapping
    unwrap_viewstack_page(element)
    unwrap_leaflet_page(element)
    
    # Also process property children
    for prop in list(element.findall('property')):
        for obj in list(prop.findall('object')):
            class_name = obj.get('class')
            new_obj = None
            
            if class_name == 'AdwToolbarView':
                new_obj = convert_adw_toolbar_view(obj)
            elif class_name == 'AdwStatusPage':
                new_obj = convert_adw_status_page(obj)
            elif class_name == 'AdwClamp':
                new_obj = convert_adw_clamp(obj)
            elif class_name == 'AdwWindowTitle':
                new_obj = convert_adw_window_title(obj)
            
            if new_obj is not None:
                replace_in_parent(prop, obj, new_obj)


def convert_file(filepath):
    """Convert a single .ui file."""
    print(f"Converting {filepath}...")
    
    try:
        # Parse the XML file
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Process the tree
        process_element(root)
        
        # Fix indentation
        indent_xml(root)
        
        # Write back
        tree.write(filepath, encoding='UTF-8', xml_declaration=True)
        
        # Validate it's still valid XML
        ET.parse(filepath)
        
        print(f"  ✓ Successfully converted {filepath}")
        return True
        
    except ET.ParseError as e:
        print(f"  ✗ XML parsing error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error converting {filepath}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    src_dir = Path('src')
    
    if not src_dir.exists():
        print("Error: src/ directory not found")
        sys.exit(1)
    
    # Find all .ui files
    ui_files = list(src_dir.glob('*.ui'))
    
    if not ui_files:
        print("No .ui files found in src/")
        sys.exit(1)
    
    print(f"Found {len(ui_files)} .ui files to convert")
    print()
    
    success_count = 0
    fail_count = 0
    
    for ui_file in sorted(ui_files):
        if convert_file(ui_file):
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print(f"Conversion complete: {success_count} succeeded, {fail_count} failed")
    
    if fail_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
