# $Id$
# coding=utf-8
#
# Copyright © 2008 Bruce Frederiksen
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
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from pyke import knowledge_engine, krb_traceback, pattern, contexts

def parse(s):
    s = s.strip()
    if s[0] == '(':
        return parse_tuple(s[1:])
    if s[0] in "0123456789.-+":
        return parse_number(s)
    if s[0] in "\"'":
        return parse_string(s)
    if s[0].isalpha() or s[0] in "_$*":
        return parse_identifier(s)
    else:
        return parse_symbol(s)

def parse_number(s):
    '''
        >>> parse_number('123abc')
        (123, 'abc')
        >>> parse_number('123e17abc')
        (1.23e+19, 'abc')
        >>> parse_number('-123abc')
        (-123, 'abc')
        >>> parse_number('-1.23e-7abc')
        (-1.23e-07, 'abc')
    '''
    for i in range(1, len(s)):
        if s[i] not in "0123456789.-+e":
            break
    return eval(s[:i]), s[i:]

def parse_string(s):
    '''
        >>> parse_string("'hello' mom")
        ('hello', ' mom')
        >>> parse_string(r'"hello\\" mom"')
        ('hello" mom', '')
    '''
    quote = s[0]
    end = s.index(quote, 1)
    while s[end - 1] == '\\':
        end = s.index(quote, end + 1)
    return eval(s[:end + 1]), s[end + 1:]

def parse_identifier(s):
    '''
        >>> parse_identifier("abc, def")
        ('abc', ', def')
        >>> parse_identifier("$abc, def")
        ('$abc', ', def')
        >>> parse_identifier("*$abc, def")
        ('*$abc', ', def')
        >>> parse_identifier("*")
        ('*', '')
        >>> parse_identifier("True, 0")
        (True, ', 0')
        >>> parse_identifier("False, 0")
        (False, ', 0')
        >>> parse_identifier("None, 0")
        (None, ', 0')
    '''
    if len(s) == 1:
        return s, ''
    start = 2 if s.startswith('*$') else 1
    for i in range(start, len(s)):
        if not s[i].isalnum() and s[i] != '_':
            break
    if s[0] == '*' and (i < 3 or s[1] != '$'):
        return parse_symbol(s)
    if s[0] == '$' and i < 2:
        return parse_symbol(s)
    token = s[:i]
    rest = s[i:]
    if token == 'None':
        return None, rest
    if token == 'True':
        return True, rest
    if token == 'False':
        return False, rest
    return token, rest

def parse_symbol(s):
    '''
        >>> parse_symbol(", def")
        (',', ' def')
        >>> parse_symbol("$+, def")
        ('$+', ', def')
        >>> parse_symbol("+)")
        ('+', ')')
        >>> parse_symbol("+]")
        ('+', ']')
    '''
    if len(s) == 1:
        return s, ''
    for i in range(1, len(s)):
        if s[i].isspace() or s[i].isalnum() or s[i] in "\"'()[]{},;_`":
            break
    return s[:i], s[i:]

def parse_tuple(s):
    '''
        >>> parse_tuple("))")
        ((), ')')
        >>> parse_tuple("a, b), c)")
        (('a', 'b'), ', c)')
        >>> parse_tuple("a, (b), c)")
        (('a', ('b',), 'c'), '')
    '''
    ans = []
    s = s.lstrip()
    while s[0] != ')':
        element, s = parse(s)
        ans.append(element)
        s = s.lstrip()
        if s[0] == ',':
            s = s[1:].lstrip()
    return tuple(ans), s[1:]

def is_pattern(data):
    '''
        >>> is_pattern('abc')
        False
        >>> is_pattern(123)
        False
        >>> is_pattern(())
        False
        >>> is_pattern((1,2,3))
        False
        >>> is_pattern((1,2,'*$_'))
        True
    '''
    if isinstance(data, tuple):
        if data and is_rest_var(data[-1]):
            return True
        return any(is_pattern(elem) for elem in data)
    if isinstance(data, str) and len(data) > 1 and data[0] == '$' \
       and (data[1].isalpha() or data[1] == '_'):
        return True
    return False

def is_rest_var(data):
    '''
    >>> is_rest_var('foo')
    False
    >>> is_rest_var('$foo')
    False
    >>> is_rest_var('*foo')
    False
    >>> is_rest_var('$*foo')
    False
    >>> is_rest_var('*$foo')
    True
    >>> is_rest_var('*$')
    False
    >>> is_rest_var('*')
    False
    >>> is_rest_var('')
    False
    '''
    return isinstance(data, str) and len(data) > 2 \
           and data.startswith('*$') \
           and (data[2].isalpha() or data[2] == '_')

def as_pattern(data):
    if isinstance(data, tuple) and is_pattern(data):
        if is_rest_var(data[-1]):
            name = data[-1][2:]
            if name[0] == '_':
                rest_var = contexts.anonymous(name)
            else:
                rest_var = contexts.variable(name)
            return pattern.pattern_tuple(
                tuple(as_pattern(elem) for elem in data[:-1]),
                rest_var
            )
        return pattern.pattern_tuple(
            tuple(as_pattern(elem) for elem in data)
        )
    if isinstance(data, str) and is_pattern(data):
        name = data[1:]
        if name[0] == '_':
            return contexts.anonymous(name)
        return contexts.variable(name)
    return pattern.pattern_literal(data)

Did_init = False

def init(*args, **kws):
    global Engine, Did_init
    Engine = knowledge_engine.engine(*args, **kws)
    Did_init = True

def eval_plan(globals_, locals_):
    while True:
        print()
        expr = input("run plan: ").strip()
        if not expr:
            break
        ans = eval(expr, globals_.copy(), locals_.copy())
        print("plan returned:", ans)

def run(rule_bases_to_activate,
        default_rb=None, init_fn=None, fn_to_run_plan=eval_plan,
        plan_globals=None):
    if plan_globals is None:
        plan_globals = {}
    if not Did_init:
        init()

    if not isinstance(rule_bases_to_activate, (tuple, list)):
        rule_bases_to_activate = (rule_bases_to_activate,)

    if default_rb is None:
        default_rb = rule_bases_to_activate[0]

    while True:
        print()
        goal_str = input("goal: ")
        if not goal_str:
            break
        goal, args_str = parse(goal_str)
        if goal == "trace":
            args = args_str.split()
            if len(args) == 1:
                Engine.trace(default_rb, args[0])
            else:
                Engine.trace(*args)
            continue
        if goal == "untrace":
            args = args_str.split()
            if len(args) == 1:
                Engine.untrace(default_rb, args[0])
            else:
                Engine.untrace(*args)
            continue
        args_str = args_str.strip()
        rb_name = default_rb
        if args_str and args_str[0] == '.':
            rb_name = goal
            goal, args_str = parse(args_str[1:])
        args = parse(args_str)[0]
        print(f"proving: {rb_name}.{goal}{tuple(args)}")
        goal_args = tuple(as_pattern(arg) for arg in args)
        Engine.reset()
        if init_fn:
            init_fn(Engine)
        context = contexts.simple_context()
        try:
            Engine.activate(*rule_bases_to_activate)
            with Engine.prove(rb_name, goal, context, goal_args) as it:
                for prototype_plan in it:
                    final = {}
                    result = tuple(
                        arg.as_data(context, True, final)
                        for arg in goal_args
                    )
                    print(f"got: {goal}{result}")
                    if not prototype_plan:
                        print("no plan returned")
                    else:
                        plan = prototype_plan.create_plan(final)
                        fn_to_run_plan(plan_globals, locals())
        except Exception:
            krb_traceback.print_exc(100)
