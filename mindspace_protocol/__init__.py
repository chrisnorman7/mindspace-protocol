"""The mindspace library."""

import sys
from msgpack import loads, dumps
from attr import attrs, attrib, Factory

encoding = sys.getdefaultencoding()


class MindspaceError(Exception):
    pass


class ProtocolError(MindspaceError):
    pass


class CommandNotFound(MindspaceError):
    pass


@attrs
class MindspaceParser:
    """This parser contains a dictionary of name: Command pairs. Use its
    handle method to handle data retrieved from a network connection or other
    resource."""

    commands = attrib(default=Factory(dict))
    loads_kwargs = attrib(
        default=Factory(
            lambda: dict(
                encoding=encoding, unicode_errors='replace'
            )
        )
    )
    dumps_kwargs = attrib(default=Factory(dict))

    def handle(self, data, *args, **kwargs):
        """Handle a 3-part tuple or list containing (name, args, kwargs), where
        name is one of the keys of self.arguments. Any extra arguments are
        passed to any found function."""
        name, a, kw = data
        args = list(args)
        args.extend(a)
        kwargs.update(kw)
        return self.handle_command(name, *args, **kwargs)

    def handle_command(self, *args, **kwargs):
        name = args[0]
        args = args[1:]
        if name in self.commands:
            cmd = self.commands[name]
            cmd(*args, **kwargs)
            return cmd
        return self.huh(name, *args, **kwargs)

    def huh(self, name, *args, **kwargs):
        """No commands found."""
        raise CommandNotFound(name)

    def handle_string(self, string, *args, **kwargs):
        """Load yaml from a string and run it through self.handle."""
        data = loads(string, **self.loads_kwargs)
        if not hasattr(data, '__len__') or len(data) < 1 or len(data) > 3:
            raise ProtocolError(string)
        name = data[0]
        if hasattr(name, 'decode'):
            name = name.decode()
        if len(data) > 1:
            a = data[1]
        else:
            a = ()
        if len(data) == 3:
            kw = data[2]
        else:
            kw = {}
        data = (name, a, kw)
        return self.handle(data, *args, **kwargs)

    def command(self, func=None, name=None):
        """Decorate a command for this parser. If name is not None it will be
        used instead of func.__name__."""

        def inner(func):
            if name is None:
                _name = func.__name__
            else:
                _name = name
            self.commands[_name] = func
            return func

        if func is None:
            return inner
        else:
            return inner(func)

    def prepare_data(self, name, *args, **kwargs):
        """Prepare name, args and kwargs for sending."""
        return dumps([name, list(args), kwargs], **self.dumps_kwargs)


__all__ = [
    'MindspaceError', 'ProtocolError', 'CommandNotFound', 'MindspaceParser'
]
