import datetime


from . import parse_timedelta

class DeadlineExceeded(Exception):
	pass


@singledispatch.register
def _make_delta(delta: str) -> datetime.timedelta:
	return parse_timedelta(delta)


@_make_delta.register
def _(delta: Number) -> datetime.timedelta:
    return datetime.timedelta(seconds=delta)



def run_timeout(delta, func):
    result = []

    def runner():
        try:
            result.append(func())
        except




def timeout(delta):
	"""
	Decorate a function to time out if the time delta is exceeded.
	"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = functools.partial(func, *args, **kwargs)
            return run_timeout(delta, bound)

        return wrapper

    return decorator


@timeout.
def _(delta: Number):
