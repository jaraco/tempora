#!/usr/bin/python

"Many of the functions in this module were taken from Ruby"

import datetime

reform_dates = {
    'italy': 2299161, # 1582-10-15
    'england': 2361222, # 1752-09-14
}


def parse(str='-4712-01-01T00:00:00Z', comp=false, sg=reform_dates['italy']):
    """Create a new datetime object by parsing from a String, without
    specifying the format.
    
    str is a string holding a date-time representation.  comp specifies whether
    to interpret 2-digit years as 19XX (>=69) or 20XX (< 69); the default is
    not to.  The method will attempt to parse a date-time from the String using
    various heuristics; see _parse for more details. If parsing fails, a
    ValueError will be raised. 

    The default str is ’-4712-01-01T00:00:00Z’; this is Julian Day Number day
    0. 

    sg specifies the Day of Calendar Reform.
    """
    elem = _parse( str, comp )
    return new_with_hash( elem, sg )

def _parse( str, comp ):
    str = str.dup

    str.gsub!(/[^-+,.\/:0-9a-z]+/ino, ' ')

    # day
    if str.sub!(/(#{PARSE_DAYPAT})\S*/ino, ' ')
      wday = ABBR_DAYS[$1.downcase]
    end

    # time
    if str.sub!(
                /(\d+):(\d+)
                 (?:
                   :(\d+)(?:[,.](\d*))?
                 )?
                 (?:
                   \s*
                   ([ap])(?:m\b|\.m\.)
                 )?
                 (?:
                   \s*
                   (
                     [a-z]+(?:\s+dst)?\b
                   |
                     [-+]\d+(?::?\d+)
                   )
                 )?
                /inox,
                ' ')
      hour = $1.to_i
      min = $2.to_i
      sec = $3.to_i if $3
      if $4
        sec_fraction = $4.to_i.to_r / (10**$4.size)
      end

      if $5
        hour %= 12
        if $5.downcase == 'p'
          hour += 12
        end
      end

      if $6
        zone = $6
      end
    end

    # eu
    if str.sub!(
                /(\d+)\S*
                 \s+
                 (#{PARSE_MONTHPAT})\S*
                 (?:
                   \s+
                   (-?\d+)
                 )?
                /inox,
                ' ')
      mday = $1.to_i
      mon = ABBR_MONTHS[$2.downcase]

      if $3
        year = $3.to_i
        if $3.size > 2
          comp = false
        end
      end

    # us
    elsif str.sub!(
                   /(#{PARSE_MONTHPAT})\S*
                    \s+
                    (\d+)\S*
                    (?:
                      \s+
                      (-?\d+)
                    )?
                   /inox,
                   ' ')
      mon = ABBR_MONTHS[$1.downcase]
      mday = $2.to_i

      if $3
        year = $3.to_i
        if $3.size > 2
          comp = false
        end
      end

    # iso
    elsif str.sub!(/([-+]?\d+)-(\d+)-(-?\d+)/no, ' ')
      year = $1.to_i
      mon = $2.to_i
      mday = $3.to_i

      if $1.size > 2
        comp = false
      elsif $3.size > 2
        comp = false
        mday, mon, year = year, mon, mday
      end

    # jis
    elsif str.sub!(/([MTSH])(\d+)\.(\d+)\.(\d+)/ino, ' ')
      e = { 'm'=>1867,
            't'=>1911,
            's'=>1925,
            'h'=>1988
          }[$1.downcase]
      year = $2.to_i + e
      mon = $3.to_i
      mday = $4.to_i

    # vms
    elsif str.sub!(/(-?\d+)-(#{PARSE_MONTHPAT})[^-]*-(-?\d+)/ino, ' ')
      mday = $1.to_i
      mon = ABBR_MONTHS[$2.downcase]
      year = $3.to_i

      if $1.size > 2
        comp = false
        year, mon, mday = mday, mon, year
      elsif $3.size > 2
        comp = false
      end

    # sla
    elsif str.sub!(%r|(-?\d+)/(\d+)(?:/(-?\d+))?|no, ' ')
      mon = $1.to_i
      mday = $2.to_i

      if $3
        year = $3.to_i
        if $3.size > 2
          comp = false
        end
      end

      if $3 && $1.size > 2
        comp = false
        year, mon, mday = mon, mday, year
      end

    # ddd
    elsif str.sub!(
                   /([-+]?)(\d{4,14})
                    (?:
                      \s*
                      T?
                      \s*
                      (\d{2,6})(?:[,.](\d*))?
                    )?
                    (?:
                      \s*
                      (
                        Z
                      |
                        [-+]\d{2,4}
                      )
                      \b
                    )?
                   /inox,
                   ' ')
      case $2.size
      when 4
        mon  = $2[ 0, 2].to_i
        mday = $2[ 2, 2].to_i
      when 6
        year = ($1 + $2[ 0, 2]).to_i
        mon  = $2[ 2, 2].to_i
        mday = $2[ 4, 2].to_i
      when 8, 10, 12, 14
        year = ($1 + $2[ 0, 4]).to_i
        mon  = $2[ 4, 2].to_i
        mday = $2[ 6, 2].to_i
        hour = $2[ 8, 2].to_i if $2.size >= 10
        min  = $2[10, 2].to_i if $2.size >= 12
        sec  = $2[12, 2].to_i if $2.size >= 14
        comp = false
      end
      if $3
        case $3.size
        when 2, 4, 6
          hour = $3[ 0, 2].to_i
          min  = $3[ 2, 2].to_i if $3.size >= 4
          sec  = $3[ 4, 2].to_i if $3.size >= 6
        end
      end
      if $4
        sec_fraction = $4.to_i.to_r / (10**$4.size)
      end
      if $5
        zone = $5
      end
    end

    if str.sub!(/\b(bc\b|bce\b|b\.c\.|b\.c\.e\.)/ino, ' ')
      if year
        year = -year + 1
      end
    end

    if comp and year
      if year >= 0 and year <= 99
        if year >= 69
          year += 1900
        else
          year += 2000
        end
      end
    end

    elem = {}
    elem[:year] = year if year
    elem[:mon] = mon if mon
    elem[:mday] = mday if mday
    elem[:hour] = hour if hour
    elem[:min] = min if min
    elem[:sec] = sec if sec
    elem[:sec_fraction] = sec_fraction if sec_fraction
    elem[:zone] = zone if zone
    offset = zone_to_diff(zone) if zone
    elem[:offset] = offset if offset
    elem[:wday] = wday if wday
    elem
  end