# -*- coding: UTF-8 -*-

# tools.py:
#  small functions or classes that don't have a home elsewhere
# from __future__ import generators

import string, urllib

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
	return apply( map, (None,)+tuple(result))

# HTTP Query takes as an argument an HTTP query request (from the url after ?)
#  and maps all of the pairs in itself as a dictionary.
# So: HTTPQuery( 'a=b&c=3&4=20' ) == { 'a':'b', 'c':'3', '4':'20' }
class HTTPQuery( dict ):
	def __init__( self, query ):
		if not self.isValidQuery( query ):
			raise ValueError, 'Invalid query: %s' % query
		items = string.split( query, '&' )
		splitEqual = lambda s: string.split( s, '=' )
		itemPairs = map( splitEqual, items )
		unquoteSequence = lambda l: map( urllib.unquote, l )
		itemPairs = map( unquoteSequence, itemPairs )
		self.update( dict( itemPairs ) )

	def isValidQuery( self, query ):
		return query

	def __repr__( self ):
		itemPairs = self.items()
		quoteSequence = lambda l: map( urllib.quote, l )
		itemPairs = map( quoteSequence, itemPairs )
		joinEqual = lambda l: string.join( l, '=' )
		items = map( joinEqual, itemPairs )
		return string.join( items, '&' )

def chunkGenerator( seq, size ):
	for i in range( 0, len(seq), size ):
		yield seq[i:i+size]

import time

class QuickTimer( object ):
	def __init__( self ):
		self.Start()

	def Start( self ):
		self.startTime = time.time()

	def Stop( self ):
		return time.time() - self.startTime

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
			\s*				# optional whitespace
			(?P<sec>\d+		# number of seconds
				(?:\.\d+)?	# optional fractional number of seconds (not saved separately)
			)				# (all saved as 'sec')
			\s*				# optional whitespace
			(?:("|sec))?	# optionally a minutes symbol or the word 'min' (not saved)
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
		isSouthOrWest = operator.truth( dmsMatch.groups()[-1] )
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

# deprecated with Python 2.3, use datetime.datetime
def ConvertToUTC( t, timeZoneName ):
	t = time.struct_time( t )
	tzi = TimeZoneInformation( timeZoneName )
	if t.tm_isdst in (1,-1):
		raise RuntimeError, 'DST is not currently supported in this function'
	elif t.tm_isdst == 0:
		result = map( operator.add, t, (0,0,0,0,tzi.standardBias,0,0,0,0) )
	else:
		raise ValueError, 'DST flag not in (-1,0-1)'
	result = time.localtime( time.mktime( result ) )
	return result

import os, win32api, win32con, struct, datetime
class Win32TimeZone( datetime.tzinfo ):
	def __init__( self, timeZoneName, fixedStandardTime=False ):
		self.timeZoneName = timeZoneName
		# this key works for WinNT+, but not for the Win95 line.
		tzRegKey = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones'
		tzRegKeyPath = os.path.join( tzRegKey, timeZoneName )
		try:
			key = win32api.RegOpenKeyEx( win32con.HKEY_LOCAL_MACHINE,
										 tzRegKeyPath,
										 0,
										 win32con.KEY_ALL_ACCESS )
		except:
			raise ValueError, 'Timezone Name %s not found.' % timeZoneName
		self.LoadInfoFromKey( key )
		self.fixedStandardTime = fixedStandardTime

	def LoadInfoFromKey( self, key ):
		self.displayName = win32api.RegQueryValueEx( key, "Display" )[0]
		self.standardName = win32api.RegQueryValueEx( key, "Std" )[0]
		self.daylightName = win32api.RegQueryValueEx( key, "Dlt" )[0]
		winTZI, type = win32api.RegQueryValueEx( key, "TZI" )
		winTZI = struct.unpack( '3l8h8h', winTZI )
		makeMinuteTimeDelta = lambda x: datetime.timedelta( minutes = x )
		self.bias, self.standardBiasOffset, self.daylightBiasOffset = \
				   map( makeMinuteTimeDelta, winTZI[:3] )
		self.daylightEnd, self.daylightStart = winTZI[3:11], winTZI[11:19]

	def __repr__( self ):
		return '%s( %s )' % ( self.__class__.__name__, self.timeZoneName )

	def __str__( self ):
		return self.displayName

	def tzname( self, dt ):
		if self.dst( dt ) == self.daylightBiasOffset:
			result = self.daylightName
		elif self.dst( dt ) == self.standardBiasOffset:
			result = self.standardName
		return result
		
	def _getStandardBias( self ):
		return self.bias + self.standardBiasOffset
	standardBias = property( _getStandardBias )

	def _getDaylightBias( self ):
		return self.bias + self.daylightBiasOffset
	daylightBias = property( _getDaylightBias )

	def utcoffset( self, dt ):
		return -( self.bias + self.dst( dt ) )

	def dst( self, dt ):
		assert dt.tzinfo is self

		dstStart = self.GetDSTStartTime( dt.year )
		dstEnd = self.GetDSTEndTime( dt.year )

		if dstStart <= dt.replace( tzinfo=None ) < dstEnd and not self.fixedStandardTime:
			result = self.daylightBiasOffset
		else:
			result = self.standardBiasOffset
		return result

	def GetDSTStartTime( self, year ):
		return self.LocateDay( year, self.daylightStart )

	def GetDSTEndTime( self, year ):
		return self.LocateDay( year, self.daylightEnd )
	
	def LocateDay( self, year, win32SystemTime ):
		month = win32SystemTime[ 1 ]
		# MS stores Sunday as 0, Python datetime stores Monday as zero
		targetWeekday = win32SystemTime[ 2 ] + 6 % 7
		# win32SystemTime[3] is the week of the month, so the following
		#  is the first possible day
		day = ( win32SystemTime[ 3 ] - 1 ) * 7 + 1
		hour, min, sec, msec = win32SystemTime[4:]
		result = datetime.datetime( year, month, day, hour, min, sec, msec )
		daysToGo = targetWeekday - result.weekday()
		result += datetime.timedelta( daysToGo )
		# if we selected a day in the month following the target month,
		#  move back a week or two.
		while result.month == month + 1:
			result -= datetime.timedelta( weeks = 1 )
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
	tLists = apply( zip, lists )
	tLists.reverse()
	return apply( zip, tLists )
	