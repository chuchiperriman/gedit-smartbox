# -*- coding: utf-8 -*-

#    Gedit smartbox plugin
#    Copyright (C) 2011  Jesús Barbero Rodríguez <chuchiperriman@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import GObject, Gtk, Gedit
from .core import Singleton
from .popup import Popup
from .currentdocsprovider import CurrentDocsProvider

class Message(Gedit.Message):
    view = GObject.property(type=Gedit.View)
    iter = GObject.property(type=Gtk.TextIter)

class Activate(Message):
    trigger = GObject.property(type=str)

class SmartBoxPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "SmartBoxPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self.manager = SmartBoxManager()
        self.timeout_id = GObject.timeout_add(5000, self.on_timeout, None)
        
        self.register_messages()
        self.insert_menu()
        
        self._popup = None
        
        self.current_docs_provider = CurrentDocsProvider()
        self.manager.add_provider(self.current_docs_provider)

    def do_deactivate(self):
        
        self.manager.remove_provider(self.current_docs_provider)
        self.unregister_messages()
        self.remove_menu()

    def do_update_state(self):
        pass
        
    def on_timeout(self, user_data=None):
        print '*' * 50
        for p in self.manager.providers:
            print p.get_name()
            for r in p.get_proposals():
                print r
            
        return True
        
    def _create_popup(self):
        self._popup = Popup(self.window, self.manager)
        self.window.get_group().add_window(self._popup)

        self._popup.set_default_size(*(450, 300))
        self._popup.set_transient_for(self.window)
        self._popup.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self._popup.connect('destroy', self.on_popup_destroy)
        
    def insert_menu(self):
        uimanager = self.window.get_ui_manager()

        self.action_group = Gtk.ActionGroup("GeditSmartBoxPluginActions")
        self.action_group.set_translation_domain('gedit')
        self.action_group.add_actions([('OpenBox', None,
                        'Open Smart _Box...', \
                        '<Primary><Alt>p', 'Open Smart Box', \
                        self.on_action_open_activate)])

        self.merge_id = uimanager.new_merge_id()
        uimanager.insert_action_group(self.action_group, -1)
        uimanager.add_ui(self.merge_id, '/MenuBar/ToolsMenu/ToolsOps_5', \
                        'OpenBox', 'OpenBox', Gtk.UIManagerItemType.MENUITEM, False)
                        
    def remove_menu(self):
        uimanager = self.window.get_ui_manager()
        uimanager.remove_ui(self.merge_id)
        uimanager.remove_action_group(self.action_group)
        self.action_group = None
        
    def register_messages(self):
        bus = self.window.get_message_bus()

        bus.register(Activate, '/plugins/smartbox', 'activate')

        self.signal_ids = set()

        sid = bus.connect('/plugins/smartbox', 'activate', self.on_message_activate, None)
        self.signal_ids.add(sid)

    def unregister_messages(self):
        bus = self.window.get_message_bus()
        for sid in self.signal_ids:
            bus.disconnect(sid)
        signal_ids = None
        bus.unregister_all('/plugins/smartbox')
                
    def on_action_open_activate(self, action):
        self.on_timeout()
        
        if not self._popup:
            self._create_popup()
            
        self._popup.show()
        
    def on_popup_destroy(self, popup, user_data=None):
        self._popup = None
        
    def on_message_activate(self, bus, message, userdata):
        
        view = message.props.view

        if not view:
            view = self.window.get_active_view()

        print 'mensaje recibido'
        
        """
        iter = message.props.iter

        if not iter:
            iter = view.get_buffer().get_iter_at_mark(view.get_buffer().get_insert())
        """

class SmartBoxManager(object):
    
    __metaclass__ = Singleton
    
    def __init__(self):
        self.providers = []
        
    def add_provider(self, provider):
        self.providers.append(provider)
        
    def remove_provider(self, provider):
        self.providers.remove(provider)
        
    def get_providers(self):
        return self.providers
