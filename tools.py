# -*- coding: UTF-8 -*-

"""
tools.py:
  small functions or classes that don't have a home elsewhere
"""

__author__ = 'Jason R. Coombs <jaraco@sandia.gov>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import string, urllib, os
import logging

log = logging.getLogger( 'tools' )

# DictMap is much like the built-in function map.  It takes a dictionary
#  and applys a function to the values of that dictionary, returning a
#  new dictionary with the mapped values in the original keys.
def DictMap( function, dictionary ):
	return dict( zip( dictionary.keys(), map( function, dictionary.values() ) ) )

# CoerceType takes a value and attempts to convert it to a float, long, or int.
#  If none of the conversions are successful, the original value is returned.
def CoerceType( value ):
	result = value
	for transform in ( float, long, int ):
		try: result = transform( value )
		except ValueError: pass

	return result

# Make a list into rows of nColumns columns.
# So if list = [1,2,3,4,5] and nColumns = 2, result is
#  [[1,3],[2,4],[5,None]].  If nColumns = 3, result is
#  [[1,3,5],[2,4,None]].
def makeRows( list, nColumns ):
	# calculate the minimum number of rows necessary to fit the list in n Columns
	nRows = len(list) / nColumns
	if len(list) % nColumns:
		nRows += 1
	# chunk the list into n Columns of length nRows
	result = chunkGenerator( list, nRows )
	# result is now a list of columns... transpose it to return a list of rows
	return map( None, *result )

from urlparse import urlparse
class HTTPQuery( dict ):
	"""HTTP Query takes as an argument an HTTP query request
	(from the url after ?) or a URL and maps all of the query pairs
	in itself as a dictionary.
	>>> HTTPQuery( 'a=b&c=3&4=20' ) == { 'a':'b', 'c':'3', '4':'20' }
	True
	>>> HTTPQuery( 'http://www.jaraco.com/?test=30' ) == { 'test':'30'}
	True
	>>> HTTPQuery( 'http://www.jaraco.com/' ) == {}
	True
	>>> HTTPQuery( '' ) == {}
	True
	"""
	def __init__( self, query ):
		query = HTTPQuery.__QueryFromURL__( query ) or query
		if not re.match( r'(\w+=\w+(&\w+=\w+)*)*$', query ): query = ()
		if isinstance( query, basestring ):
			items = query.split( '&' )
			# remove any empty values
			items = filter( None, items )
			itemPairs = map( splitter( '=' ), items )
			unquoteSequence = lambda l: map( urllib.unquote, l )
			query = map( unquoteSequence, itemPairs )
		if isinstance( query, ( tuple, list ) ):
			query = dict( query )
		self.update( query )

	def __repr__( self ):
		return urllib.urlencode( self )

	def __QueryFromURL__( url ):
		"Return the query portion of a URL"
		return urlparse( url )[4]
	__QueryFromURL__ = staticmethod( __QueryFromURL__ )

def chunkGenerator( seq, size ):
	"""Take a sequence and break it up into chunks of the specified size.
The last chunk may be smaller than size.
>>> tuple( chunkGenerator( 'foobarbaz', 3 ) )
('foo', 'bar', 'baz')
>>> tuple( chunkGenerator( [], 42 ) )
()
>>> tuple( chunkGenerator( range(10), 3 ) )
([0, 1, 2], [3, 4, 5], [6, 7, 8], [9])
"""
	for i in range( 0, len(seq), size ):
		yield seq[i:i+size]

import datetime

class QuickTimer( object ):
	def __init__( self ):
		self.Start()

	def Start( self ):
		self.startTime = datetime.datetime.now()

	def Stop( self ):
		return datetime.datetime.now() - self.startTime

import re, operator
# some code to do conversions from DMS to DD
class DMS( object ):
	dmsPatterns = [
		# This pattern matches the DMS string that assumes little formatting.
		#  The numbers are bunched together, and it is assumed that the minutes
		#  and seconds are two digits each.
		"""
		(-)?			# optional negative sign
		(?P<deg>\d+)	# number of degrees (saved as 'deg')
		(?P<min>\d{2})	# number of minutes (saved as 'min')
		(?P<sec>\d{2})	# number of seconds (saved as 'sec')
		\s*				# optional whitespace
		([NSEW])?		# optional directional specifier
		$				# end of string
		""",
		# This pattern attempts to match all other possible specifications of
		#  DMS entry.
		"""
		(-)?			# optional negative sign
		(?P<deg>\d+		# number of degrees (saved as 'deg')
			(\.\d+)?	# optional fractional number of degrees (not saved separately)
		)				# all saved as 'deg'
		\s*				# optional whitespace
		(?:(°|deg))?	# optionally a degrees symbol or the word 'deg' (not saved)
		(?:				# begin optional minutes and seconds
			\s*?			# optional whitespace (matched minimally)
			[, ]?			# optional comma or space (as a delimiter)
			\s*				# optional whitespace
			(?P<min>\d+)	# number of minutes (saved as 'min')
			\s*				# optional whitespace
			(?:('|min))?	# optionally a minutes symbol or the word 'min' (not saved)
			\s*?			# optional whitespace (matched minimally)
			[, ]?			# optional comma or space (as a delimiter)
			(?:			# begin optional seconds
				\s*				# optional whitespace
				(?P<sec>\d+		# number of seconds
					(?:\.\d+)?	# optional fractional number of seconds (not saved separately)
				)				# (all saved as 'sec')
				\s*				# optional whitespace
				(?:("|sec))?	# optionally a minutes symbol or the word 'sec' (not saved)
			)?				# end optional seconds
		)?				# end optional minutes and seconds
		\s*				# optional whitespace
		([NSEW])?		# optional directional specifier
		$				# end of string
		"""
		]
	def __init__( self, DMSString = None ):
		self.SetDMS( DMSString )

	def __float__( self ):
		return self.dd

	def SetDMS( self, DMSString ):
		self.DMSString = string.strip( str( DMSString ) )
		matches = filter( None, map( self._doPattern, self.dmsPatterns ) )
		if len( matches ) == 0:
			raise ValueError, 'String %s did not match any DMS pattern' % self.DMSString
		bestMatch = matches[0]
		self.dd = self._getDDFromMatch( bestMatch )
		del self.DMSString

	def GetDMS( self ):
		deg = int( self.dd )
		fracMin = ( self.dd - deg ) * 60
		min = int( fracMin )
		sec = ( fracMin - min ) * 60
		return ( deg, min, sec )
	DMS = property( GetDMS, SetDMS )
	
	def _doPattern( self, pattern ):
		expression = re.compile( pattern, re.IGNORECASE | re.VERBOSE )
		return expression.match( self.DMSString )
	
	def _getDDFromMatch( self, dmsMatch ):
		# get the negative sign
		isNegative = operator.truth( dmsMatch.group(1) )
		# get SW direction
		isSouthOrWest = operator.truth( dmsMatch.groups()[-1] ) and dmsMatch.groups()[-1].lower() in ( 's', 'w' )
		d = dmsMatch.groupdict()
		# set min & sec to zero if they weren't matched
		if d['min'] is None: d['min'] = 0
		if d['sec'] is None: d['sec'] = 0
		# get the DMS and convert each to float
		d = DictMap( float, d )
		# convert the result to decimal format
		result = d['deg'] + d['min'] / 60 + d['sec'] / 3600
		if isNegative ^ isSouthOrWest: result = -result
		# validate the result
		if not ( 0 <= d['deg'] < 360 and 0 <= d['min'] < 60 and 0 <= d['sec'] < 60 and result >= -180 ):
			raise ValueError, 'DMS not given in valid range (%(deg)f°%(min)f\'%(sec)f").' % d
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

def ReplaceList( object, substitutions ):
	try:
		for old, new in substitutions:
			object = object.replace( old, new )
	except AttributeError:
		# object does not have a replace method
		pass
	return object

def ReverseLists( lists ):
	tLists = zip( *lists )
	tLists.reverse()
	return zip( *tLists )

# calculate the seconds for each period
secondsPerMinute = 60
secondsPerHour = 60 * secondsPerMinute
secondsPerDay = 24 * secondsPerHour
secondsPerYear = 365 * secondsPerDay

def getPeriodSeconds( period ):
	"""
	return the number of seconds in the specified period
	"""
	try:
		if isinstance( period, basestring ):
			result = eval( 'secondsPer%s' % string.capwords( period ) )
		elif isinstance( period, ( int, long ) ):
			result = period
		else:
			raise TypeError, 'period must be a string or integer'
	except NameError:
		raise ValueError, "period not in ( minute, hour, day, year )"
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

import logging, time
class TimestampFileHandler( logging.StreamHandler ):
	"""
	A logging handler which will log to a file, similar to
	logging.handlers.RotatingFileHandler, but instead of
	appending a number, uses a timestamp to periodically select
	new file names to log to.
	"""
	def __init__( self, baseFilename, mode='a', period='day' ):
		self.baseFilename = baseFilename
		self.mode = mode
		self._setPeriod( period )
		logging.StreamHandler.__init__( self, None )

	def _setPeriod( self, period ):
		"""
		Set the period for the timestamp.  If period is 0 or None, no period will be used.
		"""
		self._period = period
		if period:
			self._periodSeconds = getPeriodSeconds( self._period )
			self._dateFormat = getDateFormatString( self._periodSeconds )
		else:
			self._periodSeconds = 0
			self._dateFormat = ''

	def _getPeriod( self ):
		return self._period
	period = property( _getPeriod, _setPeriod )
	
	def _useFile( self, filename ):
		self._ensureDirectoryExists( filename )
		self.stream = open( filename, self.mode )

	def _ensureDirectoryExists( self, filename ):
		dirname = os.path.dirname( filename )
		if dirname and not os.path.exists( dirname ):
			os.makedirs( dirname )

	def getFilename( self, t ):
		"""
		Return the appropriate filename for the given time
		based on the defined period.
		"""
		root, ext = os.path.splitext( self.baseFilename )
		# remove seconds not significant to the period
		if self._periodSeconds:
			t -= t % self._periodSeconds
		# convert it to a datetime object for formatting
		dt = datetime.datetime.utcfromtimestamp( t )
		# append the datestring to the filename
		# workaround for datetime.strftime not handling '' properly
		if not self._dateFormat == '':
			appendedDate = dt.strftime( self._dateFormat )
		else:
			appendedDate = ''
		if appendedDate:
			# in the future, it would be nice for this format
			#  to be supplied as a parameter.
			result = root + ' ' + appendedDate + ext
		else:
			result = self.baseFilename
		return result

	def emit(self, record):
		"""
		Emit a record.

		Output the record to the file, ensuring that the currently-
		opened file has the correct date.
		"""
		now = time.time()
		currentName = self.getFilename( now )
		try:
			if not self.stream.name == currentName:
				self._useFile( currentName )
		except AttributeError:
			# a stream has not been created, so create one.
			self._useFile( currentName )
		logging.StreamHandler.emit(self, record)

	def close( self ):
		"""
		Closes the stream.
		"""
		try:
			self.stream.close()
		except AttributeError: pass

class LogFileWrapper( object ):
	"""
	Emulates a file to replace stdout or stderr or
	anothe file object and redirects its output to
	a logger.
	
	Since data will often be send in partial lines or
	multiple lines, data is queued up until a new line
	is received.  Each line of text is send to the
	logger separately.
	"""
	def __init__(self, name, lvl = logging.DEBUG ):
		self.logger = logging.getLogger( name )
		self.lvl = lvl
		self.queued = ''

	def write(self, data):
		data = self.queued + data
		data = string.split( data, '\n')
		for line in data[:-1]:
			self.logger.log( self.lvl, line )
		self.queued = data[-1]

class splitter( object ):
	"""object that will split a string with the given arguments for each call
	>>> s = splitter( ',' )
	>>> s( 'hello, world, this is your, master calling' )
	['hello', ' world', ' this is your', ' master calling']
"""
	def __init__( self, *args ):
		self.args = args

	def __call__( self, s ):
		return string.split( s, *self.args )

class odict( dict ):
	"""ordered dictionary: behaves like a dictionary except calls to keys(), values(), items(), etc
	returns results in the order they were added"""

	def __init__( self, *args ):
		dict.__init__( self, *args )
		try:
			if isinstance( args[0], odict ):
				self._keys = args[0]._keys[:]
			elif isinstance( args[0], tuple ):
				self._keys = zip( *args[0] )[0]
			else:
				self._keys = dict.keys( self )
		except IndexError:
			self._keys = []
		
	def __delitem__( self, key ):
		dict.__delitem__( self, key )
		self._keys.remove( key )

	def __setitem__( self, key, item ):
		dict.__setitem__( self, key, item )
		self._addkey( key )

	def _addkey( self, key ):
		try:
			self._keys.remove( key )
		except: pass
		self._keys.append( key )

	def clear( self ):
		dict.clear( self )
		self._keys = []

	def copy( self ):
		result = odict( self )
		result._keys = self._keys[:]
		return result

	def items( self ):
		return zip( self._keys, self.values() )

	def keys( self ):
		return self._keys[:]

	def popitem( self ):
		try:
			key = self._keys[-1]
		except IndexError:
			raise KeyError( 'dictionary is empty' )
		val = self[key]
		del self[key]

		return ( key, val )

	def setdefault( self, key, failobj = None ):
		dict.setdefault( self, key, failobj )
		self._addkey( key )

	def update( self, new ):
		dict.update( self, new )
		for newkey in new.keys():
			self._addkey( newkey )

	def values( self ):
		return map( self.get, self._keys )

class ciString( str ):
	"""A case insensitive string class; behaves just like str
	except compares equal when the only variation is case.
	>>> s = ciString( 'hello world' )
	>>> s == 'Hello World'
	True
	>>> 'Hello World' == s
	True
	"""
	def __cmp__( self, other ):
		return self.lower().__cmp__( other.lower() )
	def __eq__( self, other ):
		return self.lower() == other.lower()
	def __hash__( self ):
		return hash( self.lower() )
	# cache lower since it's likely to be called frequently.
	def lower( self ):
		try:
			return self._lower
		except AttributeError:
			self._lower = str.lower( self )
			return self._lower

class ciDict( dict ):
	"""A case-insensitive dictionary (keys are compared as insensitive
	if they are strings.
	>>> d = ciDict()
	>>> d['heLlo'] = 'world'
	>>> d
	{'heLlo': 'world'}
	>>> d['hello']
	'world'
	>>> ciDict( { 'heLlo': 'world' } )
	{'heLlo': 'world'}
	>>> d = ciDict( { 'heLlo': 'world' } )
	>>> d['hello']
	'world'
	>>> d
	{'heLlo': 'world'}
	>>> d = ciDict( { 'heLlo': 'world', 'Hello': 'world' } )
	>>> d
	{'heLlo': 'world'}
	"""
	def __setitem__( self, key, val ):
		if isinstance( key, basestring ):
			key = ciString( key )
		dict.__setitem__( self, key, val )

	def __init__( self, *args, **kargs ):
		# build a dictionary using the default constructs
		d = dict( *args, **kargs )
		# build this dictionary using case insensitivity.
		map( self.__setitem__, d.keys(), d.values() )

class DTParser( object ):
	"""Datetime parser: parses a date-time string using multiple possible formats.
	>>> p = DTParser( ( '%H%M', '%H:%M' ) )
	>>> p.parse( '1319' )
	(1900, 1, 1, 13, 19, 0, 0, 1, -1)
	>>> dateParser = DTParser( ( '%m/%d/%Y', '%Y-%m-%d', '%d-%b-%Y' ) )
	>>> dateParser.parse( '2003-12-20' )
	(2003, 12, 20, 0, 0, 0, 5, 354, -1)
	>>> dateParser.parse( '16-Dec-1994' )
	(1994, 12, 16, 0, 0, 0, 4, 350, -1)
	>>> dateParser.parse( '5/19/2003' )
	(2003, 5, 19, 0, 0, 0, 0, 139, -1)
	>>> dtParser = DTParser( ( '%Y-%m-%d %H:%M:%S', '%a %b %d %H:%M:%S %Y' ) )
	>>> dtParser.parse( '2003-12-20 19:13:26' )
	(2003, 12, 20, 19, 13, 26, 5, 354, -1)
	>>> dtParser.parse( 'Tue Jan 20 16:19:33 2004' )
	(2004, 1, 20, 16, 19, 33, 1, 20, -1)

	Be forewarned:
	>>> DTParser( ( '%H%M', '%H%M%S' ) ).parse( '732' )
	Traceback (most recent call last):
		...
	ValueError: More than one format string matched target 732.
	"""
	formats = ( )
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

def randbytes( n ):
	"Returns n random bytes"
	for i in xrange( n / 4 ):
		for byte in struct.pack( 'f', random.random() ):
			yield byte
	for byte in struct.pack( 'f', random.random() )[: n % 4 ]:
		yield byte

def flatten( l ):
	"""flatten takes a list of lists and returns a single list with each element from the
	sublists.  For example,
	>>> flatten( ['a','b',['c','d',['e','f'],'g'],'h'] ) == ['a','b','c','d','e','f','g','h']
	True
	"""
	if not isinstance( l, ( list, tuple ) ):
		result = [ l ]
	elif filter( lambda x: isinstance( x, (list, tuple) ), l ):
		result = []
		map( result.extend, map( flatten, l ) )
	else:
		result = l
	return result

def readChunks( file, chunkSize = 2048, updateFunc = lambda x: None ):
	"""Read file in chunks of size chunkSize (or smaller).
	If updateFunc is specified, call it on every chunk with the amount read."""
	while( 1 ):
		res = file.read( chunkSize )
		if not res: break
		updateFunc( len( res ) )
		yield res

def binarySplit( seq, func = bool ):
	"""Split a sequence into two sequences:  the first is elements that return
	True for func( element ) and the second for False == func( element ).
	By default, func = bool, so uses the truth value of the object."""
	queues = hashSplit( seq, func )
	return queues.getFirstNQueues( 2 )

class hashSplit( dict ):
	"""Split a sequence into n sequences where n is determined by the number
	of distinct values returned by hash( func( element ) ) for each element in the sequence.
	>>> truthsplit = hashSplit( [ 'Test', '', 30, None ], bool )
	>>> trueItems = truthsplit[True]
	>>> falseItems = truthsplit[False]
	>>> tuple( falseItems )
	('', None)
	>>> tuple( trueItems )
	('Test', 30)
	>>> everyThirdSplit = hashSplit( xrange( 99 ), lambda n: n%3 )
	>>> zeros = everyThirdSplit[0]
	>>> ones = everyThirdSplit[1]
	>>> twos = everyThirdSplit[2]
	>>> zeros.next()
	0
	>>> zeros.next()
	3
	>>> ones.next()
	1
	>>> twos.next()
	2
	>>> ones.next()
	4
	"""
	def __init__( self, sequence, func = lambda x: x ):
		self.sequence = iter( sequence )
		self.func = func

	def __getitem__( self, i ):
		try:
			return dict.__getitem__( self, i )
		except KeyError:
			return self.__searchForItem__( i )

	def __getNext__( self ):
		"get the next item from the sequence and queue it up"
		item = self.sequence.next()
		try:
			queue = dict.__getitem__( self, self.func( item ) )
		except KeyError:
			queue = iterQueue( self.__getNext__ )
			self[ self.func( item ) ] = queue
		queue.enqueue( item )

	def __searchForItem__( self, i ):
		"search for the queue that would hold item i"
		try:
			self.__getNext__()
			return self[ i ]
		except StopIteration:
			return iter([])

	def getFirstNQueues( self, n ):
		"""Run through the sequence until n queues are created and return
		them.  If fewer are created, return those plus empty iterables to
		compensate."""
		try:
			while len( self ) < n:
				self.__getNext__()
		except StopIteration:
			pass
		createEmptyIterable = lambda x: iter([])
		return self.values() + map( createEmptyIterable, xrange( n - len( self ) ) )

class iterQueue( object ):
	def __init__( self, getNext ):
		self.queued = []
		self.getNext = getNext

	def __iter__( self ):
		return self

	def next( self ):
		while not self.queued:
			self.getNext()
		return self.queued.pop()

	def enqueue( self, item ):
		self.queued.insert( 0, item )

class testSplit( hashSplit ):
	def __init__( self, sequence ):
		raise NotImplementedError, 'This class is just an idea.  Don\'t use it'
		self.sequence = iter( sequence )

	def __getitem__( self, test ):
		try:
			return dict.__getitem__( self, test )
		except KeyError:
			return self.__searchForTest__( test )

	def __searchForTest__( self, test ):
		"search for the queue that holds items that return true for test"
		try:
			self[ test ] = self.__getNext__()
			return self[ test ]
		except StopIteration:
			return iter([])

	def __getNext__( self ):
		"get the next item from the sequence and queue it up"
		item = self.sequence.next()
		try:
			queue = dict.__getitem__( self, self.func( item ) )
		except KeyError:
			queue = iterQueue( self.__getNext__ )
			self[ self.func( item ) ] = queue
		queue.enqueue( item )


def ordinalth(n):
	"""Return the ordinal with 'st', 'th', or 'nd' appended as appropriate.
	>>> map( ordinalth, xrange( -5, 22 ) )
	['-5th', '-4th', '-3rd', '-2nd', '-1st', '0th', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st']
	"""
	# zero through three map to 'th', 'st', 'nd', 'rd'
	t = ( 'th', 'st', 'nd', 'rd' )
	# special case: ones digit is > 3
	ones = abs( n ) % 10
	forceth = ones > 3
	# special case: n ends in 11, 12, 13
	forceth |= abs( n ) % 100 in (11, 12, 13)
	index = [ ones, 0 ][forceth]
	return '%d%s' % ( n, t[index] )

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
	microsecondsPerDay = secondsPerDay * 1000000
	microseconds = float( pyt ) * microsecondsPerDay
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
	GetTimeDeltaMicroseconds = lambda td: ( td.days * secondsPerDay + td.seconds ) * 1000000 + td.microseconds
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
	