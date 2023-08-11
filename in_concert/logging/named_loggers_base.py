"""A module containing LoggedClass mixins to provide loggers with meaningful names to any inheriting class."""
import logging
import sys


class LoggedClassMeta(type):
    """Helper metaclass to give the logger a name equal to the class name."""

    def __new__(mcs, name, bases, namespace, **kwds):
        result = type.__new__(mcs, name, bases, dict(namespace))
        result.logger = logging.getLogger(result.__qualname__)
        return result


class LoggedClass(metaclass=LoggedClassMeta):
    """Mixin class to be inherited by class to be logged.

    Example usage:

    >>> class Player(LoggedClass):
    ...     def __init__(self):
    ...         self.logger.debug("Example log statement.")

    >>> player = Player()
    DEBUG:Player:Example log statement.
    """

    logger: logging.Logger


class AuditedClassMeta(LoggedClassMeta):
    """Extend LoggedClassMeta by allowing different kinds of loggers per class."""

    def __new__(mcs, name, bases, namespace, **kwds):
        result = LoggedClassMeta.__new__(mcs, name, bases, dict(namespace))
        for item, type_ref in result.__annotations__.items():
            if issubclass(type_ref, logging.Logger):
                prefix = "" if item == "logger" else f"{item}."
                logger = logging.getLogger(f"{prefix}{result.__qualname__}")
                setattr(result, item, logger)
        return result


class AuditedClass(LoggedClass, metaclass=AuditedClassMeta):
    """Mixin class to be inherited by class to be logged.

    Extend LoggedClass by allowing audit and standard named logs per class.

    Example usage:
    Note that names of loggers equal audit.class_name and class name respectively.

    >>> class Table(AuditedClass):
    ...
    ...    def bet(self, bet: str, amount: int) -> None:
    ...        self.logger.info("Betting %d on %s", amount, bet)
    ...        self.audit.info("Bet:%r, Amount:%r", bet, amount)
    >>> table = Table()
    >>> table.bet(bet='a', amount=1)
    INFO:Table:Betting 1 on a
    INFO:audit.Table:Bet:'a', Amount:1
    """

    audit: logging.Logger
    pass


if __name__ == "__main__":
    import doctest

    # some custom logic to make doctest display and test against the logging outputs
    dt_runner = doctest.DocTestRunner()
    tests = doctest.DocTestFinder().find(sys.modules[__name__])
    logging.basicConfig(level=logging.DEBUG, stream=dt_runner._fakeout)
    for t in tests:
        dt_runner.run(t)
