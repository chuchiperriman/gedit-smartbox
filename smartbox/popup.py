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

import os
import functools
import fnmatch
from gi.repository import Gio, GObject, Pango, Gtk, Gdk, Gedit
import xml.sax.saxutils

class Popup(Gtk.Dialog):
    __gtype_name__ = "SmartBoxPopup"

    def __init__(self, window, manager):
        Gtk.Dialog.__init__(self,
                    title=_('Smart Box'),
                    parent=window,
                    flags=Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL,
                    buttons=None)

        self.manager = manager
        
        self._build_ui()

        self._size = (0, 0)
        self._cursor = None

        accel_group = Gtk.AccelGroup()
        accel_group.connect(Gdk.KEY_l, Gdk.ModifierType.CONTROL_MASK, 0, self.on_focus_entry)

        self.add_accel_group(accel_group)

        self.connect('show', self.on_show)

    def get_final_size(self):
        return self._size

    def _build_ui(self):
        self.set_border_width(2)
        vbox = self.get_content_area()
        vbox.set_spacing(2)
        action_area = self.get_action_area()
        action_area.set_border_width(5)
        action_area.set_spacing(6)

        self._entry = Gtk.SearchEntry()
        self._entry.set_placeholder_text(_('Type to search...'))

        self._entry.connect('changed', self.on_changed)
        self._entry.connect('key-press-event', self.on_key_press_event)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.set_shadow_type(Gtk.ShadowType.OUT)

        tv = Gtk.TreeView()
        tv.set_headers_visible(False)

        self._store = Gtk.ListStore(Gio.Icon, str, GObject.Object)
        tv.set_model(self._store)

        self._treeview = tv
        tv.connect('row-activated', self.on_row_activated)

        column = Gtk.TreeViewColumn()

        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, "gicon", 0)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "markup", 1)

        column.set_cell_data_func(renderer, self.on_cell_data_cb, None)

        tv.append_column(column)
        sw.add(tv)

        vbox.pack_start(self._entry, False, False, 0)
        vbox.pack_start(sw, True, True, 0)

        vbox.show_all()

    def on_cell_data_cb(self, column, cell, model, piter, user_data):
        path = model.get_path(piter)

        if self._cursor and path == self._cursor.get_path():
            style = self._treeview.get_style()
            bg = style.bg[Gtk.StateType.PRELIGHT]

            cell.set_property('cell-background-gdk', bg)
            cell.set_property('style', Pango.Style.ITALIC)
        else:
            cell.set_property('cell-background-set', False)
            cell.set_property('style-set', False)

    def _icon_from_stock(self, stock):
        theme = Gtk.icon_theme_get_default()
        size = Gtk.icon_size_lookup(Gtk.IconSize.MENU)
        pixbuf = theme.load_icon(stock, size[0], Gtk.IconLookupFlags.USE_BUILTIN)

        return pixbuf

    def _compare_entries(self, a, b, lpart):
        if lpart in a:
            if lpart in b:
                if a.index(lpart) < b.index(lpart):
                    return -1
                elif a.index(lpart) > b.index(lpart):
                    return 1
                else:
                    return 0
            else:
                return -1
        elif lpart in b:
            return 1
        else:
            return 0

    def _match_glob(self, s, glob):
        if glob:
            glob += '*'

        return fnmatch.fnmatch(s, glob)

    def _replace_insensitive(self, s, find, rep):
        out = ''
        l = s.lower()
        find = find.lower()
        last = 0

        if len(find) == 0:
            return xml.sax.saxutils.escape(s)

        while True:
            m = l.find(find, last)

            if m == -1:
                break
            else:
                out += xml.sax.saxutils.escape(s[last:m]) + rep % (xml.sax.saxutils.escape(s[m:m + len(find)]),)
                last = m + len(find)

        return out + xml.sax.saxutils.escape(s[last:])


    def _get_icon(self, f):
        query = f.query_info(Gio.FILE_ATTRIBUTE_STANDARD_ICON,
                             Gio.FileQueryInfoFlags.NONE,
                             None)

        if not query:
            return None
        else:
            return query.get_icon()

    def _append_to_store(self, item):
        if item not in self._stored_items:
            self._store.append(item)
            self._stored_items[item] = True

    def _clear_store(self):
        self._store.clear()
        self._stored_items = {}

    def _remove_cursor(self):
        if self._cursor:
            path = self._cursor.get_path()
            self._cursor = None

            self._store.row_changed(path, self._store.get_iter(path))

    def do_search(self):
        self._remove_cursor()

        text = self._entry.get_text().strip()
        self._clear_store()

        for provider in self.manager.get_providers():
            for p in provider.get_proposals():
                #TODO Search and appent to store
                self._append_to_store((None, p, None))
                
        piter = self._store.get_iter_first()
        if piter:
            self._treeview.get_selection().select_path(self._store.get_path(piter))

    #FIXME: override doesn't work anymore for some reason, if we override
    # the widget is not realized
    def on_show(self, data=None):
        #Gtk.Window.do_show(self)

        self._entry.grab_focus()
        self._entry.set_text("")

        self.do_search()

    def on_changed(self, editable):
        self.do_search()

    def _shift_extend(self, towhere):
        selection = self._treeview.get_selection()

        if not self._shift_start:
            model, rows = selection.get_selected_rows()
            start = rows[0]

            self._shift_start = Gtk.TreeRowReference.new(self._store, start)
        else:
            start = self._shift_start.get_path()

        selection.unselect_all()
        selection.select_range(start, towhere)

    def _select_index(self, idx):
        path = (idx,)
        self._treeview.get_selection().select_path(path)

        self._treeview.scroll_to_cell(path, None, True, 0.5, 0)
        self._remove_cursor()

    def _activate(self):
        model, rows = self._treeview.get_selection().get_selected_rows()
        ret = True

        for row in rows:
            s = model.get_iter(row)
            info = model.get(s, 2, 3)

            if info[1] != Gio.FileType.DIRECTORY:
                ret = ret and self._handler(info[0])
            else:
                text = self._entry.get_text()

                for i in range(len(text) - 1, -1, -1):
                    if text[i] == os.sep:
                        break

                self._entry.set_text(os.path.join(text[:i], os.path.basename(info[0].get_uri())) + os.sep)
                self._entry.set_position(-1)
                self._entry.grab_focus()
                return True

        if rows and ret:
            self.destroy()

        return False

    def toggle_cursor(self):
        if not self._cursor:
            return

        path = self._cursor.get_path()
        selection = self._treeview.get_selection()

        if selection.path_is_selected(path):
            selection.unselect_path(path)
        else:
            selection.select_path(path)

    def on_key_press_event(self, widget, event):
        move_mapping = {
            Gdk.KEY_Down: 1,
            Gdk.KEY_Up: -1,
            Gdk.KEY_Page_Down: 5,
            Gdk.KEY_Page_Up: -5
        }

        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        elif event.keyval in move_mapping:
            return self._move_selection(move_mapping[event.keyval], event.state & Gdk.ModifierType.CONTROL_MASK, event.state & Gdk.ModifierType.SHIFT_MASK)
        elif event.keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab]:
            return self._activate()
        elif event.keyval == Gdk.KEY_space and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.toggle_cursor()

        return False

    def on_row_activated(self, view, path, column):
        self._activate()

    def do_response(self, response):
        if response != Gtk.ResponseType.ACCEPT or not self._activate():
            self.destroy()

    def do_configure_event(self, event):
        if self.get_realized():
            alloc = self.get_allocation()
            self._size = (alloc.width, alloc.height)

        return Gtk.Dialog.do_configure_event(self, event)

    def on_focus_entry(self, group, accel, keyval, modifier):
        self._entry.grab_focus()

# ex:ts=4:et:
