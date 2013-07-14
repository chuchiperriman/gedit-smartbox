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

class Proposal(object):

    def __init__(self, title, description):
        self.title = title
        self.description = description
        
    def get_title(self):
        return self.title
        
    def get_description(self):
        return self.description


class CloseAllProposal(Proposal):        
    
    def __init__(self, window):
        super(CloseAllProposal, self).__init__('Close all documents', '')
        self.window = window
        
    def activate(self):
        self.window.close_all_tabs()
        

class CloseCurrentProposal(Proposal):        
    
    def __init__(self, window):
        super(CloseCurrentProposal, self).__init__('Close the current document', '')
        self.window = window
        
    def activate(self):
        self.window.close_tab(self.window.get_active_tab())


class CurrentDocsProvider(object):
    
    def __init__(self, window):
        self.window = window
    
    def get_name(self):
        return "Current documents utilities"
        
    def get_proposals(self):
        return [CloseAllProposal(self.window),
                CloseCurrentProposal(self.window)]



