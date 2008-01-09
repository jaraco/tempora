#! python
# -*- coding: UTF-8 -*-

# $Id$

"Date time utilities not available in stock python"

import datetime, time

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

def GregorianDate( year, julianDay ):
	result = datetime.date( year, 1, 1 )
	result += datetime.timedelta( days = julianDay - 1 )
	return result

def getPeriodSeconds( period ):
	"""
	return the number of seconds in the specified period
	"""
	if isinstance( period, basestring ):
		try:
			result = eval( 'secondsPer%s' % string.capwords( period ) )
		except NameError:
			raise ValueError, "period not in ( minute, hour, day, year )"
	elif isinstance( period, ( int, long ) ):
		result = period
	elif isinstance( period, datetime.timedelta ):
		result = period.days * getPeriodSeconds('day') + period.seconds
	else:
		raise TypeError, 'period must be a string or integer'
	return result

def getDateFormatString( period ):
	"""
	for a given period (e.g. 'month', 'day', or some numeric interval
	such as 3600 (in secs)), return the format string that can be
	used with strftime to format that time to specify the times
	across that interval, but no more detailed.
	so,
	getDateFormatString( 'month' ) == '%Y-%m'
	getDateFormatString( 3600 ) == getDateFormatString( 'hour' ) == '%Y-%m-%d %H'
	getDateFormatString( None ) -> raise TypeError
	getDateFormatString( 'garbage' ) -> raise ValueError
	"""
	# handle the special case of 'month' which doesn't have
	#  a static interval in seconds
	if isinstance( period, basestring ) and string.lower( period ) == 'month':
		result = '%Y-%m'
	else:
		filePeriodSecs = getPeriodSeconds( period )
		formatPieces = ( '%Y', '-%m-%d', ' %H', '-%M', '-%S' )
		intervals = ( secondsPerYear, secondsPerDay, secondsPerHour, secondsPerMinute, 1 )
		mods = map( lambda interval: filePeriodSecs % interval, intervals )
		formatPieces = formatPieces[ : mods.index( 0 ) + 1 ]
		result = string.join( formatPieces, '' )
	return result


# Here's some ruby code I found that they us efor parsing dates.  It seems
#  to be pretty robust.  Why doesn't python have this?
#
#reform_dates = {
#    'italy': 2299161, # 1582-10-15
#    'england': 2361222, # 1752-09-14
#}
#
#
#def parse(str='-4712-01-01T00:00:00Z', comp=false, sg=reform_dates['italy']):
#    """Create a new datetime object by parsing from a String, without
#    specifying the format.
#    
#    str is a string holding a date-time representation.  comp specifies whether
#    to interpret 2-digit years as 19XX (>=69) or 20XX (< 69); the default is
#    not to.  The method will attempt to parse a date-time from the String using
#    various heuristics; see _parse for more details. If parsing fails, a
#    ValueError will be raised. 
#
#    The default str is ’-4712-01-01T00:00:00Z’; this is Julian Day Number day
#    0. 
#
#    sg specifies the Day of Calendar Reform.
#    """
#    elem = _parse( str, comp )
#    return new_with_hash( elem, sg )
#
#def _parse( str, comp ):
#    str = str.dup
#
#    str.gsub!(/[^-+,.\/:0-9a-z]+/ino, ' ')
#
#    # day
#    if str.sub!(/(#{PARSE_DAYPAT})\S*/ino, ' ')
#      wday = ABBR_DAYS[$1.downcase]
#    end
#
#    # time
#    if str.sub!(
#                /(\d+):(\d+)
#                 (?:
#                   :(\d+)(?:[,.](\d*))?
#                 )?
#                 (?:
#                   \s*
#                   ([ap])(?:m\b|\.m\.)
#                 )?
#                 (?:
#                   \s*
#                   (
#                     [a-z]+(?:\s+dst)?\b
#                   |
#                     [-+]\d+(?::?\d+)
#                   )
#                 )?
#                /inox,
#                ' ')
#      hour = $1.to_i
#      min = $2.to_i
#      sec = $3.to_i if $3
#      if $4
#        sec_fraction = $4.to_i.to_r / (10**$4.size)
#      end
#
#      if $5
#        hour %= 12
#        if $5.downcase == 'p'
#          hour += 12
#        end
#      end
#
#      if $6
#        zone = $6
#      end
#    end
#
#    # eu
#    if str.sub!(
#                /(\d+)\S*
#                 \s+
#                 (#{PARSE_MONTHPAT})\S*
#                 (?:
#                   \s+
#                   (-?\d+)
#                 )?
#                /inox,
#                ' ')
#      mday = $1.to_i
#      mon = ABBR_MONTHS[$2.downcase]
#
#      if $3
#        year = $3.to_i
#        if $3.size > 2
#          comp = false
#        end
#      end
#
#    # us
#    elsif str.sub!(
#                   /(#{PARSE_MONTHPAT})\S*
#                    \s+
#                    (\d+)\S*
#                    (?:
#                      \s+
#                      (-?\d+)
#                    )?
#                   /inox,
#                   ' ')
#      mon = ABBR_MONTHS[$1.downcase]
#      mday = $2.to_i
#
#      if $3
#        year = $3.to_i
#        if $3.size > 2
#          comp = false
#        end
#      end
#
#    # iso
#    elsif str.sub!(/([-+]?\d+)-(\d+)-(-?\d+)/no, ' ')
#      year = $1.to_i
#      mon = $2.to_i
#      mday = $3.to_i
#
#      if $1.size > 2
#        comp = false
#      elsif $3.size > 2
#        comp = false
#        mday, mon, year = year, mon, mday
#      end
#
#    # jis
#    elsif str.sub!(/([MTSH])(\d+)\.(\d+)\.(\d+)/ino, ' ')
#      e = { 'm'=>1867,
#            't'=>1911,
#            's'=>1925,
#            'h'=>1988
#          }[$1.downcase]
#      year = $2.to_i + e
#      mon = $3.to_i
#      mday = $4.to_i
#
#    # vms
#    elsif str.sub!(/(-?\d+)-(#{PARSE_MONTHPAT})[^-]*-(-?\d+)/ino, ' ')
#      mday = $1.to_i
#      mon = ABBR_MONTHS[$2.downcase]
#      year = $3.to_i
#
#      if $1.size > 2
#        comp = false
#        year, mon, mday = mday, mon, year
#      elsif $3.size > 2
#        comp = false
#      end
#
#    # sla
#    elsif str.sub!(%r|(-?\d+)/(\d+)(?:/(-?\d+))?|no, ' ')
#      mon = $1.to_i
#      mday = $2.to_i
#
#      if $3
#        year = $3.to_i
#        if $3.size > 2
#          comp = false
#        end
#      end
#
#      if $3 && $1.size > 2
#        comp = false
#        year, mon, mday = mon, mday, year
#      end
#
#    # ddd
#    elsif str.sub!(
#                   /([-+]?)(\d{4,14})
#                    (?:
#                      \s*
#                      T?
#                      \s*
#                      (\d{2,6})(?:[,.](\d*))?
#                    )?
#                    (?:
#                      \s*
#                      (
#                        Z
#                      |
#                        [-+]\d{2,4}
#                      )
#                      \b
#                    )?
#                   /inox,
#                   ' ')
#      case $2.size
#      when 4
#        mon  = $2[ 0, 2].to_i
#        mday = $2[ 2, 2].to_i
#      when 6
#        year = ($1 + $2[ 0, 2]).to_i
#        mon  = $2[ 2, 2].to_i
#        mday = $2[ 4, 2].to_i
#      when 8, 10, 12, 14
#        year = ($1 + $2[ 0, 4]).to_i
#        mon  = $2[ 4, 2].to_i
#        mday = $2[ 6, 2].to_i
#        hour = $2[ 8, 2].to_i if $2.size >= 10
#        min  = $2[10, 2].to_i if $2.size >= 12
#        sec  = $2[12, 2].to_i if $2.size >= 14
#        comp = false
#      end
#      if $3
#        case $3.size
#        when 2, 4, 6
#          hour = $3[ 0, 2].to_i
#          min  = $3[ 2, 2].to_i if $3.size >= 4
#          sec  = $3[ 4, 2].to_i if $3.size >= 6
#        end
#      end
#      if $4
#        sec_fraction = $4.to_i.to_r / (10**$4.size)
#      end
#      if $5
#        zone = $5
#      end
#    end
#
#    if str.sub!(/\b(bc\b|bce\b|b\.c\.|b\.c\.e\.)/ino, ' ')
#      if year
#        year = -year + 1
#      end
#    end
#
#    if comp and year
#      if year >= 0 and year <= 99
#        if year >= 69
#          year += 1900
#        else
#          year += 2000
#        end
#      end
#    end
#
#    elem = {}
#    elem[:year] = year if year
#    elem[:mon] = mon if mon
#    elem[:mday] = mday if mday
#    elem[:hour] = hour if hour
#    elem[:min] = min if min
#    elem[:sec] = sec if sec
#    elem[:sec_fraction] = sec_fraction if sec_fraction
#    elem[:zone] = zone if zone
#    offset = zone_to_diff(zone) if zone
#    elem[:offset] = offset if offset
#    elem[:wday] = wday if wday
#    elem
#  end