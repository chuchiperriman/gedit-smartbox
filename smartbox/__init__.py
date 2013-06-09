from gi.repository import GObject, Gtk, Gedit

class SmartBoxPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "SmartBoxPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self.manager = SmartBoxManager.get_instance()
        self.timeout_id = GObject.timeout_add(5000, self.on_timeout, None)
        
        self.insert_menu()

    def do_deactivate(self):
        self.remove_menu()

    def do_update_state(self):
        pass
        
    def on_timeout(self, user_data=None):
        print '*' * 50
        for p in self.manager.providers:
            print p.get_name()
        return True
        
    def insert_menu(self):
        manager = self.window.get_ui_manager()

        self.action_group = Gtk.ActionGroup("GeditSmartBoxPluginActions")
        self.action_group.set_translation_domain('gedit')
        self.action_group.add_actions([('OpenBox', None,
                        'Open Smart _Box...', \
                        None, 'Open Smart Box', \
                        self.on_action_open_activate)])

        self.merge_id = manager.new_merge_id()
        manager.insert_action_group(self.action_group, -1)
        manager.add_ui(self.merge_id, '/MenuBar/ToolsMenu/ToolsOps_5', \
                        'OpenBox', 'OpenBox', Gtk.UIManagerItemType.MENUITEM, False)
                        
    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        self.action_group = None
                
    def on_action_open_activate(self, action):
        self.on_timeout()
        
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def get_instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `get_instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class SmartBoxManager(object):
    
    def __init__(self):
        self.providers = []
        
    def add_provider(self, provider):
        self.providers.append(provider)       
