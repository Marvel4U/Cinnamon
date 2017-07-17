#!/usr/bin/python2

import gi
gi.require_version("Gtk", "3.0")
import cgi
import gettext
from gi.repository import Gtk, Gdk, GLib
from gi.repository import Gio, Gtk, GObject, Gdk

from GSettingsWidgets import *
from SettingsWidgets import *
from KeybindingWidgets import CellRendererKeybinding

gettext.install("cinnamon", "/usr/share/locale")

CUSTOM_KEYS_PARENT_SCHEMA = "org.cinnamon.desktop.keybindings"
CUSTOM_KEYS_BASENAME = "/org/cinnamon/desktop/keybindings/custom-keybindings"
CUSTOM_KEYS_SCHEMA = "org.cinnamon.desktop.keybindings.custom-keybinding"


from os.path import expanduser, exists
from os import makedirs
from subprocess import call


KEY_BINDING_CONFIG = expanduser("~/.mouse_button_binding")
XBINDKEYS_PATH = expanduser("~/")

if not os.path.exists(KEY_BINDING_CONFIG):
    os.makedirs(KEY_BINDING_CONFIG)
if not os.path.exists(XBINDKEYS_PATH):
    os.makedirs(XBINDKEYS_PATH)



option_list = [
# hardcoded list of all available key binding labels
# structure: [unique id, label]
# id 0 is hardcoded to be the empty key binding
    [0, _("None")], 
    [1, _("Back")+_(" <Alt+Left>")], 
    [2, _("Forward")+_(" <Alt+Right>")], 
    [3, _("New Tab")+_(" <Ctrl+T>")], 
    [4, _("Close Tab")+_(" <Ctrl+F4>")],
    [5, _("Next Tab")+_(" <Ctrl+Tab>")],
    [6, _("Previous Tab")+_(" <Ctrl+Shift+Tab>")],
    [7, _("New Tab")+_(" <Ctrl+Shift+T>")], 
    [8, _("Close Tab")+_(" <Ctrl+Shift+W>")],
    [9, _("Next Tab")+_(" <Ctrl+Page Down>")],
    [10, _("Previous Tab")+_(" <Ctrl+Page Up>")],
    [11, _("Group")+_(" <Ctrl+g>")],
    [12, _("Ungroup")+_(" <Ctrl+Shift+g>")],
    [13, _("Delete")+_(" <Del>")],
    [14, _("Duplicate")+_(" <Ctrl+D>")],
    [15, _("Close Window")+_(" <Alt+F4>")],
    [16, _("Switch Window")+_(" <Alt+Tab>")],
    [17, _("Copy")+_(" <Ctrl+C>")],
    [18, _("Paste")+_(" <Ctrl+V>")],
    [19, _("Cut")+_(" <Ctrl+X>")],
    [20, _("Undo")+_(" <Ctrl+Z>")],
    [21, _("Redo")+_(" <Ctrl+Shift+Z>")]
    ]

shortcut_dict = {
# hardcoded list of all available key bindings
# number corresponds to option_list number
    1: "'keydown Alt_L' 'key Left' 'keyup Alt_L'", 
    2: "'keydown Alt_L' 'key Right' 'keyup Alt_L'", 
    3: "'keydown Control_L' 'key t' 'keyup Control_L'", 
    4: "'keydown Control_L' 'key F4' 'keyup Control_L'",
    5: "'keydown Control_L' 'key Tab' 'keyup Control_L'",
    6: "'keydown Control_L' 'keydown Shift_L' 'key Tab' 'keyup Shift_L' 'keyup Control_L'",
    7: "'keydown Control_L' 'keydown Shift_L' 'key T' 'keyup Shift_L' 'keyup Control_L'",
    8: "'keydown Control_L' 'keydown Shift_L' 'key W' 'keyup Shift_L' 'keyup Control_L'",
    9: "'keydown Control_L' 'key Page_Down' 'keyup Control_L'",
    10: "'keydown Control_L' 'key Page_Up' 'keyup Control_L'",
    11: "'keydown Control_L' 'key g' 'keyup Control_L'",
    12: "'keydown Control_L' 'keydown Shift_L' 'key g' 'keyup Shift_L' 'keyup Control_L'",
    13: "'key Delete'",
    14: "'keydown Control_L' 'key d' 'keyup Control_L'",
    15: "'keydown Alt_L' 'key F4' 'keyup Alt_L'",
    16: """'keydown Alt_L'
    sleep .05
    xte 'key Tab' 
    sleep .05
    xte 'keyup Alt_L' """,
    17: "'keydown Control_L' 'key c' 'keyup Control_L'",
    18: "'keydown Control_L' 'key v' 'keyup Control_L'",
    19: "'keydown Control_L' 'key x' 'keyup Control_L'",
    20: "'keydown Control_L' 'key z' 'keyup Control_L'",
    21: "'keydown Control_L' 'keydown Shift_L' 'key z' 'keyup Shift_L' 'keyup Control_L'"
    }

#List of buttons that show up with combobox in GUI
PROGRAMMABLE_BUTTONS = [6,7,8,9,10,11,12,13,14,15]

PROGRAMS = [
# Definition of the program or shortcut categories with Label, internal id, icon 
# and ids of the shortcuts that make sense (are available) for this program.
#   Label                   id                  icon                                        shortcuts
    [_("General"),          "general",          "preferences-desktop-keyboard-shortcuts", [1,2,5,6,8,15,16,17,18,19,20,21]    ],
    [_("Chrome"),          "Google-chrome",      "google-chrome"                        , [1,2,3,4,5,6,15,16,17,18,19,20,21] ],
    [_("Chromium"),          "Chromium-browser", "chromium-browser"                     , [1,2,3,4,5,6,15,16,17,18,19,20,21] ],
    [_("Terminal"),          "Gnome-terminal",    "Gnome-terminal"                      , [7,8,9,10,15,16,17,18,19,20,21] ],
    [_("Inkscape"),          "Inkscape",          "inkscape"                            , [11,12,13,14,15,16,17,18,19,20,21] ]
]




# Helper functions to mediate between different shortcut list formats
category_options = {}
for cat in PROGRAMS:
    category_options[cat[1]]=cat[3]

def get_index_for_category(category, index):
    if index in category_options[category]:
        return category_options[category].index(index)+1
    else:
        return 0

def get_global_index(category, index):
    opt_plus_zero = [0]+category_options[category]
    return opt_plus_zero[index]






# Main class
class Module:
    comment = _("Control mouse and touchpad settings")
    name = "mouse"
    category = "hardware"

    def __init__(self, content_box):
        keywords = _("mouse, touchpad, synaptic, double-click")
        sidePage = SidePage(_("Mouse and Touchpad"), "cs-mouse", keywords, content_box, module=self)
        self.sidePage = sidePage
        
    def test_button_clicked(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            widget.set_label(_("Success!"))
            GLib.timeout_add(1000, self.reset_test_button, widget)
        return True

    def reset_test_button(self, widget):
        widget.set_label(_("Double-click test"))
        return False

    def on_module_selected(self):
        if not self.loaded:
            print "Loading Mouse module"

            self.sidePage.stack = SettingsStack()
            self.sidePage.add_widget(self.sidePage.stack)

            # Mouse

            page = SettingsPage()

            settings = page.add_section(_("General"))

            switch = GSettingsSwitch(_("Left handed (mouse buttons inverted)"), "org.cinnamon.settings-daemon.peripherals.mouse", "left-handed")
            settings.add_row(switch)

            switch = GSettingsSwitch(_("Show position of pointer when the Control key is pressed"), "org.cinnamon.settings-daemon.peripherals.mouse", "locate-pointer")
            settings.add_row(switch)

            switch = GSettingsSwitch(_("Emulate middle click by clicking both left and right buttons"), "org.cinnamon.settings-daemon.peripherals.mouse", "middle-button-enabled")
            settings.add_row(switch)

            spin = GSettingsSpinButton(_("Drag-and-drop threshold"), "org.cinnamon.settings-daemon.peripherals.mouse", "drag-threshold", _("pixels"), 1, 400)
            settings.add_row(spin)

            settings = page.add_section(_("Pointer size and speed"))

            widget = GSettingsRange(_("Size"), "org.cinnamon.desktop.interface", "cursor-size", _("Smaller"), _("Larger"), 5, 50, show_value=False)
            widget.add_mark(24.0, Gtk.PositionType.TOP, None)
            settings.add_row(widget)

            #widget = GSettingsSwitch(_("Custom Acceleration"), "org.cinnamon.settings-daemon.peripherals.mouse", "custom-acceleration")
            #settings.add_row(widget)

            #slider = GSettingsRange(_("Acceleration"), "org.cinnamon.settings-daemon.peripherals.mouse", "motion-acceleration", _("Slow"), _("Fast"), 1, 10, show_value=False)
            #settings.add_reveal_row(slider, "org.cinnamon.settings-daemon.peripherals.mouse", "custom-acceleration")

            slider = GSettingsRange(_("Acceleration"), "org.cinnamon.settings-daemon.peripherals.mouse", "motion-acceleration", _("Slow"), _("Fast"), 1, 10)
            settings.add_row(slider)

            #widget = GSettingsSwitch(_("Custom Sensitivity"), "org.cinnamon.settings-daemon.peripherals.mouse", "custom-threshold")
            #settings.add_row(widget)

            #slider = GSettingsRange(_("Sensitivity"), "org.cinnamon.settings-daemon.peripherals.mouse", "motion-threshold", _("Low"), _("High"), 1, 10, show_value=False, flipped=True)
            #settings.add_reveal_row(slider, "org.cinnamon.settings-daemon.peripherals.mouse", "custom-threshold")

            slider = GSettingsRange(_("Sensitivity"), "org.cinnamon.settings-daemon.peripherals.mouse", "motion-threshold", _("Low"), _("High"), 1, 10, invert=True)
            settings.add_row(slider)

            settings = page.add_section(_("Double-Click timeout"))

            slider = GSettingsRange(_("Timeout"), "org.cinnamon.settings-daemon.peripherals.mouse", "double-click", _("Short"), _("Long"), 100, 1000, show_value=False)
            settings.add_row(slider)

            box = SettingsWidget()
            widget = Gtk.Button.new_with_label(_("Double-click test"))
            widget.connect("button-press-event", self.test_button_clicked)
            box.pack_start(widget, True, True, 0)
            settings.add_row(box)

            self.sidePage.stack.add_titled(page, "mouse", _("Mouse"))

            # Touchpad

            page = SettingsPage()

            switch = GSettingsSwitch("", "org.cinnamon.settings-daemon.peripherals.touchpad", "touchpad-enabled")
            switch.label.set_markup("<b>%s</b>" % _("Enable touchpad"))
            switch.fill_row()
            page.pack_start(switch, False, True, 0)

            revealer = SettingsRevealer("org.cinnamon.settings-daemon.peripherals.touchpad", "touchpad-enabled")
            page.pack_start(revealer, False, True, 0)

            settings = SettingsBox(_("General"))
            revealer.add(settings)

            switch = GSettingsSwitch(_("Tap to click"), "org.cinnamon.settings-daemon.peripherals.touchpad", "tap-to-click")
            settings.add_row(switch)

            switch = GSettingsSwitch(_("Disable touchpad while typing"), "org.cinnamon.settings-daemon.peripherals.touchpad", "disable-while-typing")
            settings.add_row(switch)

            button_list = [[0, _("Disabled")], [1, _("Left button")], [2, _("Middle button")], [3, _("Right button")]]

            combo = GSettingsComboBox(_("Two-finger click emulation:"), "org.cinnamon.settings-daemon.peripherals.touchpad", "two-finger-click", button_list, valtype="int")
            settings.add_row(combo)

            combo = GSettingsComboBox(_("Three-finger click emulation:"), "org.cinnamon.settings-daemon.peripherals.touchpad", "three-finger-click", button_list, valtype="int")
            settings.add_row(combo)

            settings = SettingsBox(_("Scrolling"))
            revealer.add(settings)

            switch = GSettingsSwitch(_("Reverse scrolling direction"), "org.cinnamon.settings-daemon.peripherals.touchpad", "natural-scroll")
            settings.add_row(switch)

            switch = GSettingsSwitch(_("Vertical edge scrolling"), "org.cinnamon.settings-daemon.peripherals.touchpad", "vertical-edge-scrolling")
            settings.add_row(switch)
            switch = GSettingsSwitch(_("Horizontal edge scrolling"), "org.cinnamon.settings-daemon.peripherals.touchpad", "horizontal-edge-scrolling")
            settings.add_row(switch)
            switch = GSettingsSwitch(_("Vertical two-finger scrolling"), "org.cinnamon.settings-daemon.peripherals.touchpad", "vertical-two-finger-scrolling")
            settings.add_row(switch)    
            switch = GSettingsSwitch(_("Horizontal two-finger scrolling"), "org.cinnamon.settings-daemon.peripherals.touchpad", "horizontal-two-finger-scrolling")
            settings.add_row(switch)

            settings = SettingsBox(_("Pointer speed"))
            revealer.add(settings)

            #switch = GSettingsSwitch(_("Custom Acceleration"), "org.cinnamon.settings-daemon.peripherals.touchpad", "custom-acceleration")
            #settings.add_row(switch)

            #slider = GSettingsRange(_("Acceleration"), "org.cinnamon.settings-daemon.peripherals.touchpad", "motion-acceleration", _("Slow"), _("Fast"), 1, 10, show_value=False)
            #settings.add_reveal_row(slider, "org.cinnamon.settings-daemon.peripherals.touchpad", "custom-acceleration")

            slider = GSettingsRange(_("Acceleration"), "org.cinnamon.settings-daemon.peripherals.touchpad", "motion-acceleration", _("Slow"), _("Fast"), 1, 10)
            settings.add_row(slider)

            #switch = GSettingsSwitch(_("Custom Sensitivity"), "org.cinnamon.settings-daemon.peripherals.touchpad", "custom-threshold")
            #settings.add_row(switch)

            #slider = GSettingsRange(_("Sensitivity"), "org.cinnamon.settings-daemon.peripherals.touchpad", "motion-threshold", _("Low"), _("High"), 1, 10, show_value=False, flipped=True)
            #settings.add_reveal_row(slider, "org.cinnamon.settings-daemon.peripherals.touchpad", "custom-threshold")

            slider = GSettingsRange(_("Sensitivity"), "org.cinnamon.settings-daemon.peripherals.touchpad", "motion-threshold", _("Low"), _("High"), 1, 10, invert=True)
            settings.add_row(slider)

            self.sidePage.stack.add_titled(page, "touchpad", _("Touchpad"))


            
            ## Programmable mouse buttons
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.set_border_width(6)
            vbox.set_spacing(6)
            self.sidePage.stack.add_titled(vbox, "shortcuts", _("Programmable mouse buttons"))

            headingbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)
            mainbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 2)
            headingbox.pack_start(mainbox, True, True, 2)
            headingbox.pack_end(Gtk.Label.new(_("General settings are overwritten by program specific settings.")), False, False, 1)

            paned = Gtk.Paned(orientation = Gtk.Orientation.HORIZONTAL)
            Gtk.StyleContext.add_class(Gtk.Widget.get_style_context(paned), "wide")

            left_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)
            right_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)

            paned.add1(left_vbox)

            right_scroller = Gtk.ScrolledWindow.new(None, None)
            right_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
            right_scroller.add(right_vbox)
            paned.add2(right_scroller)

            category_scroller = Gtk.ScrolledWindow.new(None, None)
            category_scroller.set_shadow_type(Gtk.ShadowType.IN)

            kb_name_scroller = Gtk.ScrolledWindow.new(None, None)
            kb_name_scroller.set_shadow_type(Gtk.ShadowType.IN)

            right_vbox.pack_start(kb_name_scroller, True, True, 2)
            self.cat_tree = Gtk.TreeView.new()
            self.kb_tree = Gtk.TreeView.new()
            self.entry_tree = Gtk.TreeView.new()

            left_vbox.pack_start(category_scroller, True, True, 2)

            category_scroller.add(self.cat_tree)
            category_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

            settings = SettingsBox(_("Mouse botton bindings"))
            kb_name_scroller.add(settings)

            
            options = self.get_category_options('general')
            
            self.combodict = {}
            for btn in PROGRAMMABLE_BUTTONS:
                self.combodict[btn] = ComboBox(_("Button "+str(btn)), options)
                settings.add_row(self.combodict[btn])
            
            self.scripts = HandleXbindkeys_scripts(KEY_BINDING_CONFIG, XBINDKEYS_PATH, self.combodict, option_list)


            buttonbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
            self.save_settings = Gtk.Button.new_with_label(_("Save settings"))
            self.save_settings.connect('clicked', self.onSaveSettingsButtonClicked)
            buttonbox.pack_start(self.save_settings, False, False, 2)

            right_vbox.pack_end(buttonbox, False, False, 2)


            mainbox.pack_start(paned, True, True, 2)

            self.cat_store = Gtk.TreeStore(str,     # Icon name or None
                                           str,     # The category name
                                           object)  # The category object

            self.kb_store = Gtk.ListStore( str,   # Keybinding name
                                           object)# The keybinding object

            self.entry_store = Gtk.ListStore(str) # Accel string

            cell = Gtk.CellRendererText()
            cell.set_alignment(0,0)
            pb_cell = Gtk.CellRendererPixbuf()
            cat_column = Gtk.TreeViewColumn(_("Programs"))
            cat_column.pack_start(pb_cell, False)
            cat_column.pack_start(cell, True)
            cat_column.add_attribute(pb_cell, "icon-name", 0)
            cat_column.add_attribute(cell, "text", 1)

            cat_column.set_alignment(0)
            cat_column.set_property('min-width', 200)

            self.cat_tree.append_column(cat_column)
            self.cat_tree.connect("cursor-changed", self.onCategoryChanged)

            kb_name_cell = Gtk.CellRendererText()
            kb_name_cell.set_alignment(.5,.5)
            kb_column = Gtk.TreeViewColumn(_("Keyboard shortcuts"), kb_name_cell, text=0)
            kb_column.set_alignment(.5)
            self.kb_tree.append_column(kb_column)
            #self.kb_tree.connect("cursor-changed", self.onKeyBindingChanged)

            self.entry_tree.set_tooltip_text("%s\n%s\n%s" % (_("Click to set a new accelerator key."), _("Press Escape or click again to cancel the operation."), _("Press Backspace to clear the existing keybinding.")))

            self.main_store = []

            for cat in PROGRAMS:
            #                                          label, int_name, icon
                self.main_store.append(ProgramCategory(cat[0], cat[1], cat[2]))

            cat_iters = {}
            longest_cat_label = " "

            
            for category in self.main_store:
                cat_iters[category.int_name] = self.cat_store.append(None)
                if category.icon:
                    self.cat_store.set_value(cat_iters[category.int_name], 0, category.icon)
                self.cat_store.set_value(cat_iters[category.int_name], 1, category.label)
                self.cat_store.set_value(cat_iters[category.int_name], 2, category)
                if len(category.label) > len(longest_cat_label):
                    longest_cat_label = category.label

            layout = self.cat_tree.create_pango_layout(longest_cat_label)
            w, h = layout.get_pixel_size()

            paned.set_position(max(w, 200))

            #self.loadCustoms()
            self.cat_tree.set_model(self.cat_store)
            self.kb_tree.set_model(self.kb_store)
            self.entry_tree.set_model(self.entry_store)

            vbox.pack_start(headingbox, True, True, 0)


    def addNotebookTab(self, tab):
        self.notebook.append_page(tab.tab, Gtk.Label.new(tab.name))
        self.tabs.append(tab)

    def onCategoryChanged(self, tree):
        if tree.get_selection() is not None:
            categories, iter = tree.get_selection().get_selected()
            if iter:
                category = categories[iter][2]
                #if category.int_name is not "custom":
                self.scripts.store_button_bindings()
                options = self.get_category_options(category.int_name)
                for cbox in self.combodict.keys():
                    self.combodict[cbox].set_options(options)
                self.scripts.refresh_comboboxes(category.int_name)
        
    def onSaveSettingsButtonClicked(self, button):
        self.scripts.save_settings_to_files()
        
    def get_category_options(self, category):
        options = []
        index_list = category_options[category]
        for item in option_list:
            if item[0] in index_list or item[0]==0:
                options.append(item)
        return options
    


class HandleXbindkeys_scripts():
    # Bindings are stored in several places:
    # - internally in button_bindings
    # - on the HD in the config file in config_scripts_path
    # - per button in an individual script in config_scripts_path
    # - the button scripts are executed through the xbindkeys config file 
    #   which only lists the scripted buttons
    def __init__(self, config_scripts_path, xbindkeys_path, combodict, option_list):
        self.scripts_path = config_scripts_path
        self.config_file = config_scripts_path+"/config"
        self.xbindkeys_file = xbindkeys_path+"/.xbindkeysrc"
        self.combodict = combodict
        self.option_list = option_list
        self.read_config_file()
        self.refresh_comboboxes('general')
        self.current_category = 'general'
        
    def store_button_bindings(self):
        # store combobox selections in internal button_binding variable
        for cbox in self.combodict.keys():
            active = get_global_index(self.current_category, self.combodict[cbox].content_widget.get_active())
            if active==0:
                if (self.current_category, cbox) in self.button_bindings.keys():
                    del self.button_bindings[(self.current_category, cbox)]
            else:
                self.button_bindings[(self.current_category, cbox)] = active
    
    def refresh_comboboxes(self, category):
        # change combobox settings for new category displayed according to internal button_binding variable
        self.current_category = category
        for cbox in self.combodict.keys():
            self.combodict[cbox].content_widget.set_active(0)
        for key in self.button_bindings.keys():
            binding = [ key[0], key[1], self.button_bindings[key] ]
            if binding[0] == category:
                if int(binding[1]) in self.combodict.keys():
                    self.combodict[binding[1]].content_widget.set_active(get_index_for_category(self.current_category, binding[2]))
        

    def get_button_list(self):
        return list(set([key[1] for key in self.button_bindings.keys()]))
    
    def save_settings_to_files(self):
        # write internal button_binding information to config file and scripts
        self.store_button_bindings()
        self.write_config_file()
        button_list = self.get_button_list()
        self.write_xbindkeys_file(button_list)
        self.write_scripts(button_list)
        call(["xbindkeys", "-p"])
        
    def read_config_file(self):
        with open(self.config_file, 'r') as config:
            button_bindings_list = config.readlines()
        self.button_bindings = {}
        for line in button_bindings_list:
            splitline = line.split()
            splitline[1] = int(splitline[1])
            splitline[2] = int(splitline[2])
            self.button_bindings[(splitline[0], splitline[1])] = splitline[2]
    
    def write_config_file(self):
        with open(self.config_file, 'w') as config:
            for key in self.button_bindings.keys():
                binding = [ key[0], key[1], self.button_bindings[key] ]
                config.write(' '.join([str(b) for b in binding]) )
                config.write('\n')
    
    def write_xbindkeys_file(self, button_list):
        with open(self.xbindkeys_file,'w') as xbind:
            xbind.write(self.xbindkey_config_top)
            for btn in button_list:
                xbind.write(self.xbindkey_config_item_top+str(btn)+'\n')
                xbind.write('"'+self.scripts_path+'/mouse_button_'+str(btn)+'_binding.sh"\n')
                xbind.write('  b:'+str(btn)+'\n \n')
            xbind.write(self.xbindkey_config_bottom)
    
    def write_scripts(self, button_list):
        # generate scripts that allow execution of program dependent mouse binding
        for btn in button_list:
            FirstItem = True

            ## The three strings "if_closer", "else_keyword" and "else_command" make sure that the general 
            ## condition is written correctly. If it is the only setting, there shuld not be an "else" or
            ## an "if". If the general condition is not set, there should be no "else" eiher.
            
            with open(self.scripts_path+'/mouse_button_'+str(btn)+'_binding.sh','w') as s:
                s.write(self.button_scripts_top)
                if_closer = ''
                else_keyword = ''
                else_command = ''
                
                for key in self.button_bindings.keys():
                    binding = [ key[0], key[1], self.button_bindings[key] ]
                    if binding[1] == btn:
                        if binding[0] == 'general':
                            else_keyword = '''\nelse '''
                            else_command = '''\n   xte '''+shortcut_dict[binding[2]]+'''\n'''
                            continue
                        
                        if FirstItem:
                            FirstItem = False;
                            if_closer = self.button_scripts_bottom
                        else:
                            s.write('el')
                        s.write(self.button_scripts_item_top + binding[0] + 
                                self.button_scripts_item_mid + 
                                shortcut_dict[binding[2]] +
                                self.button_scripts_item_bottom)
                
                if if_closer!='' and else_command!='':
                    s.write(else_keyword)
                s.write(else_command)
                
                s.write(if_closer)
                
    xbindkey_config_top ='''# For the benefit of emacs users: -*- shell-script -*-
###########################
# xbindkeys configuration #
###########################

"xbindkeys_show" 
  control+shift + q

'''
    xbindkey_config_bottom='''
##################################
# End of xbindkeys configuration #
##################################
'''
    xbindkey_config_item_top='# Flexible b'
    
    button_scripts_top = '''#!/bin/bash
W=`xdotool getactivewindow`
S1=`xprop -id ${W} |awk '/WM_CLASS/{print $4}'` 

'''
    button_scripts_bottom = '''
fi
'''
    button_scripts_item_top = '''if [ $S1 = '"'''
    button_scripts_item_mid = '''"' ]; then                                                          
   xte '''
    button_scripts_item_bottom = '''\n'''


class ProgramCategory():
    def __init__(self, label, int_name, icon):
        self.label = label
        self.icon = icon
        self.int_name = int_name
