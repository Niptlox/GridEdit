import functools
import os

all_classes = {}


def get_class_path(cls) -> str:
    return repr(cls).split()[0][1:]


def wrap_cls(original_class):
    def __init__(self, *args, **kws):
        self._id = self.__class__.__name__
        if self._id in all_classes:
            self._id += "__" + str(id(self))
        self.get_id = lambda _self=self: _self._id
        orig_init(self, *args, **kws)  # Call the original __init__
        all_classes[self._id] = self

    orig_init = original_class.__init__
    original_class.__init__ = __init__  # Set the class' __init__ to the new one
    return original_class


class CommandHistory:
    def __init__(self, print_to_console=True, filename="CommandHistory.txt"):
        self.print_to_console = print_to_console
        self.filename = filename
        if not os.path.exists(self.filename):
            open(self.filename, "w").close()

    def new(self, *st):
        s = "".join(map(str, st))
        with open(self.filename, "a") as f:
            f.write(s + "\n")
        if self.print_to_console:
            print(s)
        # self.run(s)

    def wrap(self, func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            s_kwargs = ", ".join([str(key) + "=" + str(val) for key, val in kwargs.items()])
            s_kwargs = (", " + s_kwargs) if s_kwargs else ""
            self.new(func.__name__, "(", ", ".join(map(str, args)), s_kwargs, ")")
            result = func(*args, **kwargs)
            return result

        return _wrapper

    def wrap_self(self, func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cls = args[0].get_id()
            args = args[1:]
            s_kwargs = ", ".join([str(key) + "=" + repr(val) for key, val in kwargs.items()])
            s_kwargs = (", " + s_kwargs) if s_kwargs else ""
            self.new(cls, ".", func.__name__, "(", ", ".join(map(repr, args)), s_kwargs, ")")

            return result
        return _wrapper

    def run(self, command):
        exec(command, all_classes, globals())



ch = CommandHistory()
