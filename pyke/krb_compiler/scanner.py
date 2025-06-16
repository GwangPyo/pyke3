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

""" See http://www.dabeaz.com/ply/ply.html for syntax of grammer definitions.
"""

import string
import os
import os.path
import sys
from pyke.krb_compiler.ply import lex

debug = 0

kfb_mode = False
goal_mode = False

states = (
    ('indent', 'exclusive'),
    ('code', 'exclusive'),
    ('checknl', 'exclusive'),
)

kfb_keywords = frozenset((
    'False',
    'None',
    'True',
))

keywords = frozenset((
    'as',
    'assert',
    'bc_extras',
    'check',
    'extending',
    'False',
    'fc_extras',
    'first',
    'forall',
    'foreach',
    'in',
    'None',
    'notany',
    'plan_extras',
    'python',
    'require',
    'step',
    'taking',
    'True',
    'use',
    'when',
    'with',
    'without',
))

base_kfb_tokens = (
    'IDENTIFIER_TOK',
    'LP_TOK',
    'NL_TOK',
    'NUMBER_TOK',
    'RP_TOK',
    'STRING_TOK',
)

base_krb_tokens = base_kfb_tokens + (
    'ANONYMOUS_VAR_TOK',
    'CODE_TOK',
    'DEINDENT_TOK',
    'INDENT_TOK',
    'NOT_NL_TOK',
    'PATTERN_VAR_TOK',
)

kfb_tokens = tuple(x.upper() + '_TOK' for x in kfb_keywords) + base_kfb_tokens
tokens = tuple(x.upper() + '_TOK' for x in keywords) + base_krb_tokens

literals = '*:,!.='  # FIX: delete ':'

t_ignore = ' \t'

t_ignore_comment = r'\#.*'


def t_continuation(t):
    r'\\(\r)?\n'
    t.lexer.lineno += 1


def t_NL_TOK(t):
    r'(\r)?\n([ \t]*(\#.*)?(\r)?\n)*'
    t.lexer.lineno += t.value.count('\n')
    if kfb_mode:
        return t
    if nesting_level == 0:
        t.lexer.begin('indent')
        t.lexer.skip(-1)
        return t


indent_levels = []

# prevent warning
t_indent_ignore = ''


def t_indent_sp(t):
    r'\n[ \t]*'
    indent = count_indent(t.value[1:])[0]
    current_indent = indent_levels[-1] if indent_levels else 0
    if debug:
        print(
            "t_indent_sp: indent",
            indent,
            "current_indent",
            current_indent,
            "indent_levels",
            indent_levels,
            file=sys.stderr,
        )
    if indent > current_indent:
        t.type = 'INDENT_TOK'
        indent_levels.append(indent)
        t.lexer.begin('INITIAL')
        if debug:
            print("INDENT_TOK: indent_levels", indent_levels, file=sys.stderr)
        return t
    if indent < current_indent:
        if indent > 0 and indent not in indent_levels:
            raise SyntaxError(
                "deindent doesn't match any previous indent level",
                syntaxerror_params(t.lexpos),
            )
        t.type = 'DEINDENT_TOK'
        del indent_levels[-1]
        if indent < (indent_levels[-1] if indent_levels else 0):
            t.lexer.skip(-len(t.value))
        else:
            t.lexer.begin('INITIAL')
        if debug:
            print("DEINDENT_TOK: indent_levels", indent_levels, file=sys.stderr)
        return t
    t.lexer.begin('INITIAL')
    if debug:
        print("no indent: indent_levels", indent_levels, file=sys.stderr)


t_checknl_ignore = ' \t'


def t_checknl_nl(t):
    r'(\#.*)?(\r)?\n'
    t.lexer.lineno += 1
    t.lexer.begin('indent')
    t.lexer.skip(-1)
    t.type = 'NL_TOK'
    return t


def t_checknl_other(t):
    r'[^\#\r\n]'
    t.lexer.skip(-1)
    t.type = 'NOT_NL_TOK'
    return t


def start_code(plan_name=None, multiline=False, var_format="(context['%s'])"):
    global current_line, code, current_plan_name, pattern_var_format
    global plan_vars_needed, code_nesting_level, code_lineno, code_lexpos
    global code_indent_level
    pattern_var_format = var_format
    plan_vars_needed = []
    current_line = ''
    code = []
    code_indent_level = indent_levels[-1] if multiline else 1000000000
    current_plan_name = plan_name
    code_nesting_level = 0
    code_lineno = code_lexpos = None
    lexer.begin('code')


def mark(t):
    global code_lineno, code_lexpos
    if code_lineno is None:
        code_lineno = t.lexer.lineno
        code_lexpos = t.lexpos


t_code_ignore = ''


def t_code_string(t):
    r"'''([^\\]|\\.)*?'''|" \
    r'"""([^\\]|\\.)*?"""|' \
    r"'([^'\\\n\r]|\\.|\\(\r)?\n)*?'|" \
    r'"([^"\\\n\r]|\\.|\\(\r)?\n)*?"'
    global current_line
    current_line += t.value
    mark(t)
    if debug:
        print("scanner saw string:", t.value, file=sys.stderr)
    t.lexer.lineno += t.value.count('\n')


def t_code_comment(t):
    r'[ \t\f\r]*\#.*'
    if debug:
        print("scanner saw comment:", t.value, file=sys.stderr)


def t_code_plan(t):
    r'\$\$'
    global current_line
    mark(t)
    if debug:
        print("scanner saw '$$', current_plan_name is", current_plan_name, file=sys.stderr)
    if not current_plan_name:
        raise SyntaxError("'$$' only allowed in plan_specs within the 'when' clause",
                          syntaxerror_params(t.lexpos))
    current_line += pattern_var_format % current_plan_name
    plan_vars_needed.append(current_plan_name)


def t_code_pattern_var(t):
    r'\$[a-zA-Z_][a-zA-Z0-9_]*\b'
    global current_line
    mark(t)
    if not pattern_var_format:
        raise SyntaxError("$<name> only allowed in backward chaining rules",
                          syntaxerror_params(t.lexpos))
    current_line += pattern_var_format % t.value[1:]
    plan_vars_needed.append(t.value[1:])
    if debug:
        print("scanner saw pattern_var:", t.value, file=sys.stderr)


def t_code_continuation(t):
    r'\\(\r)?\n'
    global current_line
    t.lexer.lineno += 1
    current_line += '\\'
    code.append(current_line)
    current_line = ''
    if debug:
        print("scanner saw continuation:", t.value, file=sys.stderr)


def t_code_open(t):
    r'[{([]'
    global current_line, code_nesting_level
    mark(t)
    code_nesting_level += 1
    current_line += t.value


def t_code_close(t):
    r'[]})]'
    global current_line, code_nesting_level
    mark(t)
    if code_nesting_level <= 0:
        raise SyntaxError("unmatched %s" % repr(t.value),
                          syntaxerror_params(t.lexpos))
    code_nesting_level -= 1
    current_line += t.value


def t_code_symbol(t):
    r'[0-9a-zA-Z_]+'
    global current_line
    mark(t)
    current_line += t.value
    if debug:
        print("scanner saw symbol:", t.value, file=sys.stderr)


def t_code_space(t):
    r'[ \t]+'
    global current_line
    current_line += t.value


def t_code_other(t):
    r'[^][(){}$\\\'"\r\n0-9a-zA-Z_ \t]+'
    global current_line
    mark(t)
    current_line += t.value


def t_code_NL_TOK(t):
    r'(\r)?\n([ \t]*(\#.*)?(\r)?\n)*[ \t]*'
    global current_line
    if current_line:
        code.append(current_line)
        current_line = ''
    indent = count_indent(t.value[t.value.rindex('\n') + 1:])[0]
    if indent < code_indent_level and code_nesting_level == 0:
        t.lexer.skip(-len(t.value))
        t.type = 'CODE_TOK'
        t.value = tuple(code), tuple(plan_vars_needed), code_lineno, code_lexpos
        t.lexer.begin('INITIAL')
        return t
    t.lexer.lineno += t.value.count('\n')
    current_line = ' ' * (indent - code_indent_level)


def t_tsqstring(t):
    r"[uU]?[rR]?'''([^\\]|\\.)*?'''"
    t.type = 'STRING_TOK'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_tdqstring(t):
    r'[uU]?[rR]?"""([^\\]|\\.)*?"""'
    t.type = 'STRING_TOK'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_sqstring(t):
    r"[uU]?[rR]?'([^'\\\n\r]|\\.|\\(\r)?\n)*?'"
    t.lexer.lineno += t.value.count('\n')
    t.type = 'STRING_TOK'
    return t


def t_dqstring(t):
    r'[uU]?[rR]?"([^"\\\n\r]|\\.|\\(\r)?\n)*?"'
    t.type = 'STRING_TOK'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_ANONYMOUS_VAR_TOK(t):
    r'\$_([a-zA-Z_][a-zA-Z0-9_]*)?'
    if kfb_mode:
        t_ANY_error(t)
    t.value = t.value[1:] if goal_mode else "'" + t.value[1:] + "'"
    return t


def t_PATTERN_VAR_TOK(t):
    r'\$[a-zA-Z][a-zA-Z0-9_]*'
    if kfb_mode:
        t_ANY_error(t)
    t.value = t.value[1:] if goal_mode else "'" + t.value[1:] + "'"
    return t


def t_IDENTIFIER_TOK(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if kfb_mode and t.value in kfb_keywords or not kfb_mode and t.value in keywords:
        t.type = t.value.upper() + '_TOK'
    return t


def t_float(t):
    r'[-+]?([0-9]+(\.[0-9]*([eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)|\.[0-9]+([eE][-+]?[0-9]+)?)'
    t.value = float(t.value)
    t.type = 'NUMBER_TOK'
    return t


def t_hexint(t):
    r'[-+]?0[xX][0-9a-fA-F]+'
    t.value = int(t.value, 16)
    t.type = 'NUMBER_TOK'
    return t


def t_octalint(t):
    r'[-+]?0[0-7]*'
    t.value = int(t.value, 8)
    t.type = 'NUMBER_TOK'
    return t


def t_int(t):
    r'[-+]?[1-9][0-9]*'
    t.value = int(t.value)
    t.type = 'NUMBER_TOK'
    return t


nesting_level = 0


def t_LB_TOK(t):
    r'\['
    global nesting_level
    nesting_level += 1


def t_LC_TOK(t):
    r'\{'
    global nesting_level
    nesting_level += 1


def t_LP_TOK(t):
    r'\('
    global nesting_level
    nesting_level += 1
    return t


def t_RB_TOK(t):
    r'\]'
    global nesting_level
    nesting_level -= 1


def t_RC_TOK(t):
    r'\}'
    global nesting_level
    nesting_level -= 1


def t_RP_TOK(t):
    r'\)'
    global nesting_level
    nesting_level -= 1
    return t


def t_ANY_error(t):
    raise SyntaxError(
        "illegal character %s" % repr(t.value[0]),
        syntaxerror_params(t.lexpos),
    )


def count_indent(s, count_all=False):
    indent = 0
    chars = 0
    for c in s:
        if c == '\t':
            indent = (indent + 8) & ~7
        elif c == ' ' or count_all:
            indent += 1
        else:
            break
        chars += 1
    return indent, chars


escapes = {
    'a': '\a',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
    'v': '\v',
    '\\': '\\',
    '\'': '\'',
    '\"': '\"',
}


def unescape(s):
    start = 0
    ans = []
    i = s.find('\\', start)
    while i >= 0:
        ans.append(s[start:i])
        e = escapes.get(s[i + 1])
        if e:
            ans.append(e)
            start = i + 2
        elif s[i + 1] == '\n':
            start = i + 2
        elif s[i + 1] == '\r':
            start = i + 3 if s[i + 2] == '\n' else i + 2
        elif s[i + 1:i + 3] == 'N{':
            end = s.index('}', i + 3)
            import unicodedata
            ans.append(unicodedata.lookup(s[i + 3:end]))
            start = end + 1
        elif s[i + 1] == 'u':
            ans.append(chr(int(s[i + 2:i + 6], 16)))
            start = i + 6
        elif s[i + 1] == 'U':
            ans.append(chr(int(s[i + 2:i + 10], 16)))
            start = i + 10
        elif s[i + 1] in string.octdigits:
            if s[i + 2] not in string.octdigits:
                ans.append(chr(int(s[i + 2:i + 3], 8)))
                start = i + 3
            elif s[i + 3] not in string.octdigits:
                ans.append(chr(int(s[i + 2:i + 4], 8)))
                start = i + 4
            else:
                ans.append(chr(int(s[i + 2:i + 5], 8)))
                start = i + 5
        elif s[i + 1] == 'x':
            if s[i + 3] not in string.hexdigits:
                ans.append(chr(int(s[i + 2:i + 3], 16)))
                start = i + 3
            else:
                ans.append(chr(int(s[i + 2:i + 4], 16)))
                start = i + 4
        else:
            ans.append(s[i])
            start = i + 1
        i = s.find('\\', start)
    ans.append(s[start:])
    return ''.join(ans)


class token_iterator(object):
    def __init__(self, input_):
        lexer.lineno = 1
        lexer.input(input_)

    def __iter__(self):
        return self

    def __next__(self):
        t = lex.token()
        if t:
            return t
        raise StopIteration

    next = __next__  # for compatibility


def tokenize(s):
    for t in token_iterator(s):
        print(t)


def tokenize_file(filename='TEST/scan_test'):
    with open(filename) as f:
        tokenize(f.read())


def syntaxerror_params(pos=None, lineno=None):
    if pos is None:
        pos = lexer.lexpos
    if pos > len(lexer.lexdata):
        pos = len(lexer.lexdata)
    end = pos
    if lineno is None:
        lineno = lexer.lineno
    while end > 0 and (end >= len(lexer.lexdata) or lexer.lexdata[end] in '\r\n'):
        end -= 1
    start = max(lexer.lexdata.rfind('\r', 0, end),
                lexer.lexdata.rfind('\n', 0, end)) + 1
    column = pos - start + 1
    end1 = lexer.lexdata.find('\r', end)
    end2 = lexer.lexdata.find('\n', end)
    if end1 < 0:
        end = len(lexer.lexdata) if end2 < 0 else end2
    elif end2 < 0:
        end = end1
    else:
        end = min(end1, end2)
    if goal_mode and start == 0 and lexer.lexdata.startswith('check ', start):
        start += 6
        column -= 6
    return lexer.filename, lineno, column, lexer.lexdata[start:end]


lexer = None


def init(this_module, debug_param, check_tables=False, kfb=False):
    global indent_levels, nesting_level, kfb_mode, lexer, debug
    indent_levels = []
    nesting_level = 0
    kfb_mode = kfb
    debug = debug_param
    if lexer is None:
        if debug_param:
            lexer = lex.lex(module=this_module, debug=1)
        else:
            if check_tables:
                scanner_mtime = os.path.getmtime(this_module.__file__)
                tables_name = os.path.join(os.path.dirname(this_module.__file__),
                                           'scanner_tables.py')
                try:
                    ok = os.path.getmtime(tables_name) >= scanner_mtime
                except OSError:
                    ok = False
                if not ok:
                    try:
                        os.remove(tables_name)
                    except OSError:
                        pass
                    try:
                        os.remove(tables_name + 'c')
                    except OSError:
                        pass
                    try:
                        os.remove(tables_name + 'o')
                    except OSError:
                        pass
            lexer = lex.lex(module=this_module,
                            optimize=1,
                            lextab='pyke.krb_compiler.scanner_tables',
                            outputdir=os.path.dirname(this_module.__file__))
