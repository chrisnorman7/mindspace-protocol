"""The mindspace library."""

from attr import attrs, attrib, Factory


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

    def handle_command(self, *args, **kwargs):
        """Handle a command from the commands dictionary. This method should
        probably be called as a result of a network resource receiving a
        string."""
        name = args[0]  # Prevent multiple arguments named name.
        args = args[1:]
        if name in self.commands:
            cmd = self.commands[name]
            cmd(*args, **kwargs)
            return cmd
        return self.huh(name, *args, **kwargs)

    def huh(self, name, *args, **kwargs):
        """No commands found."""
        raise CommandNotFound(name)

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


__all__ = [
    'MindspaceError', 'ProtocolError', 'CommandNotFound', 'MindspaceParser'
]
