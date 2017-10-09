"""Test the mindspace library."""

from pytest import raises
from mindspace_protocol import MindspaceParser, CommandNotFound


class Works(Exception):
    pass


class CustomMindspaceParser(MindspaceParser):
    def huh(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        raise Works()


parser = MindspaceParser()


class NoArgumentsWorks(Exception):
    pass


class WithArgumentsWorks(Exception):
    pass


class WithKwargsWorks(Exception):
    pass


class WithBothWorks(Exception):
    pass


@parser.command
def no_arguments():
    raise NoArgumentsWorks()


@parser.command
def with_arguments(first, second):
    assert first == 'hello'
    assert second == 'world'
    raise WithArgumentsWorks()


@parser.command
def with_kwargs(hello=None, this=None):
    assert hello == 'world'
    assert this == 'works'
    raise WithKwargsWorks()


@parser.command
def with_both(first, second, this, name):
    assert first == 'hello'
    assert second == 'world'
    assert this == 'works'
    assert name == __name__
    raise WithBothWorks()


def test_no_arguments():
    with raises(NoArgumentsWorks):
        parser.handle(['no_arguments', [], {}])


def test_with_arguments():
    with raises(WithArgumentsWorks):
        parser.handle(['with_arguments', ['hello', 'world'], {}])


def test_with_kwargs():
    with raises(WithKwargsWorks):
        parser.handle(['with_kwargs', [], {'hello': 'world', 'this': 'works'}])


def test_with_both():
    with raises(WithBothWorks):
        parser.handle(
            [
                'with_both', ['hello', 'world'],
                {'this': 'works', 'name': __name__}
            ]
        )


def test_command_not_found():
    with raises(CommandNotFound):
        parser.handle(('no command called this, hahahaha!', (), {}))


def test_custom_huh():
    p = CustomMindspaceParser()
    name = 'test'
    args = (1, 2, 3)
    kwargs = {'hello': 'world'}
    with raises(Works):
        p.handle((name, args, kwargs))
    assert p.name == name
    assert p.args == args
    assert p.kwargs == kwargs
