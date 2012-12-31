from __future__ import unicode_literals, absolute_import

import datetime
import functools

class Stopwatch(object):
	"""
	A simple stopwatch which starts automatically.

	>>> w = Stopwatch()
	>>> _1_sec = datetime.timedelta(seconds=1)
	>>> w.split() < _1_sec
	True
	>>> import time
	>>> time.sleep(1.0)
	>>> w.split() >= _1_sec
	True
	>>> w.stop() >= _1_sec
	True
	>>> w.reset()
	>>> w.start()
	>>> w.split() < _1_sec
	True
	"""
	def __init__(self):
		self.reset()
		self.start()

	def reset(self):
		self.elapsed = datetime.timedelta(0)
		if hasattr(self, 'start_time'):
			del self.start_time

	def start(self):
		self.start_time = datetime.datetime.now()

	def stop(self):
		stop_time = datetime.datetime.now()
		self.elapsed += stop_time - self.start_time
		del self.start_time
		return self.elapsed

	def split(self):
		local_duration = datetime.datetime.now() - self.start_time
		return self.elapsed + local_duration

	# context manager support
	__enter__ = start

	def __exit__(self, exc_type, exc_value, traceback):
		self.stop()

class IntervalGovernor(object):
	"""
	Decorate a function to only allow it to be called once per
	min_interval. Otherwise, it returns None.
	"""
	def __init__(self, min_interval):
		if isinstance(min_interval, (int, long)):
			min_interval = datetime.timedelta(seconds=min_interval)
		self.min_interval = min_interval
		self.last_call = None

	def decorate(self, func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			allow = (
				not self.last_call
				or self.last_call.split() > self.min_interval
			)
			if allow:
				self.last_call = Stopwatch()
				return func(*args, **kwargs)
		return wrapper

	__call__ = decorate
