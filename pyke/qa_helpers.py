# $Id$
# coding=utf-8
# 
# Copyright © 2007-2008 Bruce Frederiksen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import types
import re
import sys


class regexp(object):
    '''
        >>> m = regexp('(hi)\\s*there', 'the msg', 'the prompt')
        >>> m
        <regexp 'the msg'[the prompt]/(hi)\s*there/>
        >>> m.msg
        'the msg'
        >>> m.prompt
        'the prompt'
        >>> m.match('hithere')
        'hi'
    '''

    def __init__(self, regexp, msg=None, prompt=None):
        self.re = re.compile(regexp, re.UNICODE | re.VERBOSE)
        self.pattern = regexp
        self.msg = msg
        self.prompt = prompt

    def __repr__(self):
        if self.msg:
            if self.prompt:
                return '<regexp %r[%s]/%s/>' % \
                    (self.msg, str(self.prompt), self.pattern)
            return '<regexp %r/%s/>' % (self.msg, self.pattern)
        if self.prompt:
            return '<regexp [%s]/%s/>' % (self.prompt, self.pattern)
        return '<regexp /%s/>' % self.pattern

    def __getstate__(self):
        return self.pattern, self.msg, self.prompt

    def __setstate__(self, args):
        self.pattern, self.msg, self.prompt = args
        self.re = re.compile(self.pattern, re.UNICODE | re.VERBOSE)

    def match(self, string):
        m = self.re.match(string)
        if m and m.end() == len(string):
            if m.lastindex and m.lastindex > 1:
                return m.groups()
            if m.lastindex == 1:
                return m.group(1)
            return string


class qmap(object):
    '''
        >>> m = qmap('y', True)
        >>> m
        <qmap True = 'y'>
        >>> m.test
        'y'
        >>> m.value
        True
    '''

    def __init__(self, test, value):
        self.test = test
        self.value = value

    def __repr__(self):
        return "<qmap %s = %s>" % (repr(self.value), repr(self.test))


if sys.version_info[0] < 3:
    def urepr(x):
        '''
            >>> urepr(44)
            '44'
            >>> tuple(urepr('hi\n'))
            ('"', 'h', 'i', '\\', 'n', '"')
        '''
        if isinstance(x, str):
            return repr(x)
        return unicode(x)
else:
    urepr = repr


def to_int(string):
    '''
        >>> to_int(' -34')
        -34
        >>> to_int(' +43')
        43
        >>> to_int('43x')
        Traceback (most recent call last):
            ...
        ValueError: illegal integer: '43x'
    '''
    try:
        return int(string)
    except ValueError:
        raise ValueError("illegal integer: %s" % urepr(string))


def to_float(string):
    '''
        >>> str(to_float(' -34.444'))
        '-34.444'
        >>> str(to_float(' +43'))
        '43.0'
        >>> to_float('43.3.3')
        Traceback (most recent call last):
            ...
        ValueError: illegal floating point number: '43.3.3'
    '''
    try:
        return float(string)
    except ValueError:
        raise ValueError("illegal floating point number: %s" % urepr(string))


def to_number(string):
    '''
        >>> str(to_number(' -34.444'))
        '-34.444'
        >>> to_number(' +43')
        43
        >>> to_number('43.3.3')
        Traceback (most recent call last):
            ...
        ValueError: illegal number: '43.3.3'
    '''
    try:
        return to_int(string)
    except ValueError:
        try:
            return to_float(string)
        except ValueError:
            raise ValueError("illegal number: %s" % urepr(string))


def to_tuple(string, conv_fn=None, test=None, separator=','):
    '''
        >>> to_tuple('1, 2,3', to_int)
        (1, 2, 3)
        >>> to_tuple('1, 2.5, -7e3', to_number)
        (1, 2.5, -7000.0)
        >>> to_tuple('43', to_number)
        (43,)
        >>> to_tuple('1,43.3.3', to_number)
        Traceback (most recent call last):
            ...
        ValueError: illegal number: '43.3.3'
    '''

    def conv_element(elem):
        elem = elem.strip()
        if conv_fn: elem = conv_fn(elem)
        if test: elem = match(elem, test)
        return elem

    return tuple(conv_element(elem) for elem in string.split(separator))


def msg_for(test, type_):
    '''
        >>> msg_for(None, int)
        >>> msg_for(regexp('', 'the msg'), int)
        'the msg'
        >>> msg_for(qmap(44, True), int)
        '44'
        >>> msg_for(slice(3, 55), int)
        'between 3 and 55'
        >>> msg_for(slice(None, 55), int)
        '<= 55'
        >>> msg_for(slice(3, None), int)
        '>= 3'
        >>> msg_for(slice(None, None), int)
        ''
        >>> msg_for(slice(3, 55), str)
        'between 3 and 55 characters'
        >>> msg_for(slice(None, 55), str)
        '<= 55 characters'
        >>> msg_for(slice(3, None), str)
        '>= 3 characters'
        >>> msg_for(slice(None, None), str)
        ''
        >>> msg_for((slice(3, 5), True), str)
        'between 3 and 5 characters or True'
        >>> msg_for(True, str)
        'True'
    '''
    if test is None: return None
    if isinstance(test, regexp): return test.msg
    if isinstance(test, qmap): return msg_for(test.test, type_)
    if isinstance(test, slice):
        if test.start is None:
            ans = "" if test.stop is None else "<= %d" % test.stop
        elif test.stop is None:
            ans = ">= %d" % test.start
        else:
            ans = "between %d and %d" % (test.start, test.stop)
        if issubclass(type_, str) and ans:
            ans += ' characters'
        return ans
    if isinstance(test, (tuple, list)):
        return ' or '.join(filter(None, (msg_for(t, type_) for t in test)))
    return urepr(test)


def match_prompt(test, type_, fmt, default=''):
    '''
        >>> match_prompt(None, int, ' [%s] ')
        ''
        >>> match_prompt(regexp('', '', 'the prompt'), int, ' [%s] ')
        ' [the prompt] '
        >>> match_prompt(qmap(44, True), int, ' [%s] ')
        ' [44] '
        >>> match_prompt(slice(3, 55), int, ' [%s] ')
        ' [3-55] '
        >>> match_prompt(slice(None, 55), int, ' [%s] ')
        ' [max 55] '
        >>> match_prompt(slice(3, None), int, ' [%s] ')
        ' [min 3] '
        >>> match_prompt(slice(None, None), int, ' [%s] ', 'foo')
        'foo'
        >>> match_prompt(slice(3, 55), str, ' [%s] ')
        ' [len: 3-55] '
        >>> match_prompt(slice(None, 55), str, ' [%s] ')
        ' [len <= 55] '
        >>> match_prompt(slice(3, None), str, ' [%s] ')
        ' [len >= 3] '
        >>> match_prompt(slice(None, None), str, ' [%s] ')
        ''
        >>> match_prompt((slice(3, 5), True), str, ' [%s] ')
        ' [len: 3-5 or True] '
        >>> match_prompt(True, str, ' [%s] ')
        ' [True] '
    '''

    def prompt_body(test, type_):
        if test is None: return None
        if isinstance(test, regexp): return test.prompt
        if isinstance(test, qmap): return prompt_body(test.test, type_)
        if isinstance(test, slice):
            if test.start is None:
                if test.stop is not None:
                    return "len <= %d" % test.stop if issubclass(type_, str) else "max %d" % test.stop
                return ""
            if test.stop is None:
                return "len >= %d" % test.start if issubclass(type_, str) else "min %d" % test.start
            return "len: %d-%d" % (test.start, test.stop) if issubclass(type_, str) else "%d-%d" % (
            test.start, test.stop)
        if isinstance(test, (tuple, list)):
            return ' or '.join(filter(None, (prompt_body(t, type_) for t in test)))
        return urepr(test)

    body = prompt_body(test, type_)
    return fmt % body if body else default


def match(ans, test):
    '''
        >>> match('foobar', None)
        'foobar'
        >>> match('hithere', regexp('(hi)\\s*there', 'hi there'))
        'hi'
        >>> match('hi mom', regexp('(hi)\\s*there', 'hi there'))
        Traceback (most recent call last):
            ...
        ValueError: hi there
        >>> match('y', qmap('y', True))
        True
        >>> match(2, qmap(slice(3, 5), True))
        Traceback (most recent call last):
            ...
        ValueError: between 3 and 5
        >>> match(3, slice(3,5))
        3
        >>> match(2, slice(3,5))
        Traceback (most recent call last):
            ...
        ValueError: between 3 and 5
        >>> match(2, (slice(3,5), slice(5,10), 2))
        2
        >>> match(2, 2)
        2
    '''
    if test is None:
        return ans
    if isinstance(test, regexp):
        result = test.match(ans)
        if result is not None:
            return result
    if isinstance(test, qmap):
        match(ans, test.test)  # raises ValueError if it doesn't match
        return test.value
    if isinstance(test, slice):
        value = len(ans) if isinstance(ans, str) else ans
        if (test.start is None or value >= test.start) and (test.stop is None or value <= test.stop):
            return ans
    if isinstance(test, (tuple, list)):
        for t in test:
            try:
                return match(ans, t)
            except ValueError:
                continue
    if test == ans:
        return ans
    raise ValueError(msg_for(test, type(ans)))
