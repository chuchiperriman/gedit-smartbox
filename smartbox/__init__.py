from gi.repository import GObject, Gtk, Gedit

class SmartBoxPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "SmartBoxPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self.manager = SmartBoxManager.get_instance()
        self.manager.add_provider(ExampleProvider())
        self.timeout_id = GObject.timeout_add(1000, self.on_timeout, None)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass
        
    def on_timeout(self, user_data):
        print '*' * 50
        for p in self.manager.providers:
            print p.get_name()
        return True

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
        print 'iniiiiiiiiiiiit'
        self.providers = []
        
    def add_provider(self, provider):
        self.providers.append(provider)
       
class ExampleProvider (object):

    def get_name(self):
        return "Example"
        
