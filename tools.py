# tools.py:
#  small functions or classes that don't have a home elsewhere
from __future__ import generators

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

