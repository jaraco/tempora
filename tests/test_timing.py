import datetime

import mock

from jaraco import timing


def test_IntervalGovernor():
	"""
	IntervalGovernor should prevent a function from being called more than
	once per interval.
	"""
	func_under_test = mock.MagicMock()
	# to look like a function, it needs a __name__ attribute
	func_under_test.__name__ = 'func_under_test'
	interval = datetime.timedelta(seconds=1)
	governed = timing.IntervalGovernor(interval)(func_under_test)
	governed('a')
	governed('b')
	governed(3, 'sir')
	func_under_test.assert_called_once_with('a')
