#! python
# -*- coding: UTF-8 -*-

# $Id$

"Date time utilities not available in stock python"

import datetime
import time

#TODO: replace this with dateutil.parser.parse()
class Parser( object ):
	"""Datetime parser: parses a date-time string using multiple possible formats.
	>>> p = Parser( ( '%H%M', '%H:%M' ) )
	>>> p.parse( '1319' )
	(1900, 1, 1, 13, 19, 0, 0, 1, -1)
	>>> dateParser = Parser( ( '%m/%d/%Y', '%Y-%m-%d', '%d-%b-%Y' ) )
	>>> dateParser.parse( '2003-12-20' )
	(2003, 12, 20, 0, 0, 0, 5, 354, -1)
	>>> dateParser.parse( '16-Dec-1994' )
	(1994, 12, 16, 0, 0, 0, 4, 350, -1)
	>>> dateParser.parse( '5/19/2003' )
	(2003, 5, 19, 0, 0, 0, 0, 139, -1)
	>>> dtParser = Parser( ( '%Y-%m-%d %H:%M:%S', '%a %b %d %H:%M:%S %Y' ) )
	>>> dtParser.parse( '2003-12-20 19:13:26' )
	(2003, 12, 20, 19, 13, 26, 5, 354, -1)
	>>> dtParser.parse( 'Tue Jan 20 16:19:33 2004' )
	(2004, 1, 20, 16, 19, 33, 1, 20, -1)

	Be forewarned:
	>>> Parser( ( '%H%M', '%H%M%S' ) ).parse( '732' )
	Traceback (most recent call last):
		...
	ValueError: More than one format string matched target 732.
	"""

	# default to some common formats
	formats = ( '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d-%b-%Y', '%d-%b-%y' )
	def __init__( self, formats = None ):
		if formats:
			self.formats = formats

	def parse( self, target ):
		self.target = target
		results = filter( None, map( self._parse, self.formats ) )
		del self.target
		if not results:
			raise ValueError, "No format strings matched the target %s." % target
		if not len( results ) == 1:
			raise ValueError, "More than one format string matched target %s." % target
		return results[0]

	def _parse( self, format ):
		try:
			result = time.strptime( self.target, format )
		except ValueError:
			result = False
		return result

# some useful constants
# mean vernal equinox year expressed in oscillations of atomic cesium at the year 2000
# see http://webexhibits.org/calendars/timeline.html for more info
osc_per_year = 290091329207984000
osc_per_second = 9192631770
seconds_per_year = 31556940
seconds_per_minute = 60
minutes_per_hour = 60
hours_per_day = 24
seconds_per_hour = seconds_per_minute * minutes_per_hour
seconds_per_day = seconds_per_hour * hours_per_day
days_per_year = float( seconds_per_year ) / seconds_per_day
six_months = datetime.timedelta(days=days_per_year/2)
thirty_days = datetime.timedelta(days=30)

def strftime( fmt, t ):
	"""A class to replace the strftime in datetime package or time module.
	Identical to strftime behavior in those modules except supports any
	year.
	Also supports datetime.datetime times.
	Also supports milliseconds using %s
	Also supports microseconds using %u"""
	if isinstance( t, ( time.struct_time, tuple ) ):
		t = datetime.datetime( *t[:6] )
	assert isinstance( t, ( datetime.datetime, datetime.time, datetime.date ) )
	try:
		year = t.year
		if year < 1900: t = t.replace( year = 1900 )
	except AttributeError:
		year = 1900
	subs = (
		( '%Y', '%04d' % year ),
		( '%y', '%02d' % ( year % 100 ) ),
		( '%s', '%03d' % ( t.microsecond / 1000 ) ),
		( '%u', '%03d' % ( t.microsecond % 1000 ) )
		)
	doSub = lambda s, sub: s.replace( *sub )
	doSubs = lambda s: reduce( doSub, subs, s )
	fmt = '%%'.join( map( doSubs, fmt.split( '%%' ) ) )
	return t.strftime( fmt )

def strptime( s, fmt, tzinfo = None ):
	"""A function to replace strptime in the time module.  Should behave identically
	to the strptime function except it returns a datetime.datetime object instead of
	a time.struct_time object.
	Also takes an optional tzinfo parameter which is a time zone info object."""
	res = time.strptime( s, fmt )
	return datetime.datetime( tzinfo = tzinfo, *res[:6] )

def ConstructDatetime( *args, **kargs ):
	"""Construct a datetime.datetime from a number of different time
	types found in python and pythonwin"""
	if len( args ) == 1:
		arg = args[0]
		method = __GetDTConstructor__( type( arg ).__module__, type( arg ).__name__ )
		result = method( arg )
		try:
			result = result.replace( tzinfo = kargs.pop( 'tzinfo' ) )
		except KeyError:
			pass
		if kargs:
			raise TypeError, "%s is an invalid keyword argument for this function." % kargs.keys()[0]
	else:
		result = datetime.datetime( *args, **kargs )
	return result

def __GetDTConstructor__( moduleName, name ):
	try:
		return eval( '__dt_from_%(moduleName)s_%(name)s__' % vars() )
	except NameError:
		raise TypeError, "No way to construct datetime.datetime from %s.%s" % ( moduleName, name )

def __dt_from_datetime_datetime__( source ):
	dtattrs = ( 'year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond', 'tzinfo' )
	attrs = map( lambda a: getattr( source, a ), dtattrs )
	return datetime.datetime( *attrs )

def __dt_from___builtin___time__( pyt ):
	"Construct a datetime.datetime from a pythonwin time"
	fmtString = '%Y-%m-%d %H:%M:%S'
	result = strptime( pyt.Format( fmtString ), fmtString )
	# get milliseconds and microseconds.  The only way to do this is
	#  to use the __float__ attribute of the time, which is in days.
	microseconds_per_day = seconds_per_day * 1000000
	microseconds = float( pyt ) * microseconds_per_day
	microsecond = int( microseconds % 1000000 )
	result = result.replace( microsecond = microsecond )
	return result

def __dt_from_timestamp__( timestamp ):
	return datetime.datetime.utcfromtimestamp( timestamp )
__dt_from___builtin___float__ = __dt_from_timestamp__
__dt_from___builtin___long__ = __dt_from_timestamp__
__dt_from___builtin___int__ = __dt_from_timestamp__

def __dt_from_time_struct_time__( s ):
	return datetime.datetime( *s[:6] )

def DatetimeMod( dt, period, start = None ):
	"""Find the time which is the specified date/time truncated to the time delta
	relative to the start date/time.
	By default, the start time is midnight of the same day as the specified date/time.
	>>> DatetimeMod( datetime.datetime( 2004, 1, 2, 3 ), datetime.timedelta( days = 1.5 ), start = datetime.datetime( 2004, 1, 1 ) )
	datetime.datetime(2004, 1, 1, 0, 0)
	>>> DatetimeMod( datetime.datetime( 2004, 1, 2, 13 ), datetime.timedelta( days = 1.5 ), start = datetime.datetime( 2004, 1, 1 ) )
	datetime.datetime(2004, 1, 2, 12, 0)
	>>> DatetimeMod( datetime.datetime( 2004, 1, 2, 13 ), datetime.timedelta( days = 7 ), start = datetime.datetime( 2004, 1, 1 ) )
	datetime.datetime(2004, 1, 1, 0, 0)
	>>> DatetimeMod( datetime.datetime( 2004, 1, 10, 13 ), datetime.timedelta( days = 7 ), start = datetime.datetime( 2004, 1, 1 ) )
	datetime.datetime(2004, 1, 8, 0, 0)
"""
	if start is None:
		# use midnight of the same day
		start = datetime.datetime.combine( dt.date(), datetime.time() )
	# calculate the difference between the specified time and the start date.
	delta = dt - start
	# now aggregate the delta and the period into microseconds
	# I use microseconds because that's the highest precision of these time pieces.  Also,
	#  using microseconds ensures perfect precision (no floating point errors).
	GetTimeDeltaMicroseconds = lambda td: ( td.days * seconds_per_day + td.seconds ) * 1000000 + td.microseconds
	delta, period = map( GetTimeDeltaMicroseconds , ( delta, period ) )
	offset = datetime.timedelta( microseconds = delta % period )
	# the result is the original specified time minus the offset
	result = dt - offset
	return result

def DatetimeRound( dt, period, start = None ):
	"""Find the nearest even period for the specified date/time.
	>>> DatetimeRound( datetime.datetime( 2004, 11, 13, 8, 11, 13 ), datetime.timedelta( hours = 1 ) )
	datetime.datetime(2004, 11, 13, 8, 0)
	>>> DatetimeRound( datetime.datetime( 2004, 11, 13, 8, 31, 13 ), datetime.timedelta( hours = 1 ) )
	datetime.datetime(2004, 11, 13, 9, 0)
	>>> DatetimeRound( datetime.datetime( 2004, 11, 13, 8, 30 ), datetime.timedelta( hours = 1 ) )
	datetime.datetime(2004, 11, 13, 9, 0)
	"""
	result = DatetimeMod( dt, period, start )
	if abs( dt - result ) >= period / 2:
		result += period
	return result

# This function takes a Julian day and infers a year by choosing the
#  nearest year to that date.
def GetNearestYearForDay( day ):
	now = time.gmtime()
	result = now.tm_year
	# if the day is far greater than today, it must be from last year
	if day - now.tm_yday > 365/2:
		result -= 1
	# if the day is far less than today, it must be for next year.
	if now.tm_yday - day > 365/2:
		result += 1
	return result

def gregorian_date(year, julian_day):
	"""
	Gregorian Date is defined as a year and a julian day (1-based
	index into the days of the year).
	>>> gregorian_date(2007, 15)
	datetime.date(2007, 1, 15)
	"""
	result = datetime.date(year, 1, 1)
	result += datetime.timedelta(days = julian_day - 1)
	return result

def get_period_seconds(period):
	"""
	return the number of seconds in the specified period
	"""
	if isinstance(period, basestring):
		try:
			result = eval('seconds_per_%s' % period.lower())
		except NameError:
			raise ValueError, "period not in (minute, hour, day, year)"
	elif isinstance(period, (int, long)):
		result = period
	elif isinstance(period, datetime.timedelta):
		result = period.days * getPeriodSeconds('day') + period.seconds
	else:
		raise TypeError, 'period must be a string or integer'
	return result

def get_date_format_string( period ):
	"""
	for a given period (e.g. 'month', 'day', or some numeric interval
	such as 3600 (in secs)), return the format string that can be
	used with strftime to format that time to specify the times
	across that interval, but no more detailed.
	so,
	get_date_format_string('month') == '%Y-%m'
	get_date_format_string(3600) == get_date_format_string('hour') == '%Y-%m-%d %H'
	get_date_format_string(None) -> raise TypeError
	get_date_format_string('garbage') -> raise ValueError
	"""
	# handle the special case of 'month' which doesn't have
	#  a static interval in seconds
	if isinstance(period, basestring) and string.lower(period) == 'month':
		result = '%Y-%m'
	else:
		file_period_secs = get_period_seconds(period)
		format_pieces = ('%Y', '-%m-%d', ' %H', '-%M', '-%S')
		intervals = (
			seconds_per_year,
			seconds_per_day,
			seconds_per_hour,
			seconds_per_minute,
			1, # seconds_per_second
			)
		mods = map(lambda interval: file_period_secs % interval, intervals)
		format_pieces = format_pieces[ : mods.index( 0 ) + 1 ]
		result = ''.join(format_pieces)
	return result

def divide_timedelta_float( td, divisor ):
	# td is comprised of days, seconds, microseconds
	dsm = [ getattr( td, attr ) for attr in ( 'days', 'seconds', 'microseconds' ) ]
	dsm = map( lambda elem: elem/divisor, dsm )
	return timedelta( *dsm )

# for backward compatibility
getPeriodSeconds = get_period_seconds
getDateFormatString = get_date_format_string
GregorianDate = gregorian_date