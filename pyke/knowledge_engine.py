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

from __future__ import with_statement
import sys
import types
import os
import contextlib
import importlib

import pyke
from pyke import contexts, fact_base

debug = False

Sys_path = tuple(
    os.getcwd() if p == '' else os.path.normpath(os.path.abspath(p))
    for p in sys.path
)


class CanNotProve(Exception):
    pass


class engine(object):
    _Variables = tuple(
        contexts.variable('ans_%d' % i) for i in range(100)
    )

    def __init__(self, *search_paths, **kws):
        # import this stuff here to avoid import cycles...
        global condensedPrint, pattern, goal, rule_base, special, target_pkg
        from pyke import (
            condensedPrint, pattern, goal, rule_base,
            special, target_pkg
        )

        for keyword in kws:
            if keyword not in (
                'load_fc', 'load_bc', 'load_fb', 'load_qb'
            ):
                raise TypeError(
                    "engine.__init__() got an unexpected keyword "
                    "argument %r" % keyword
                )

        self.knowledge_bases = {}
        self.rule_bases = {}
        special.create_for(self)

        if (
            len(search_paths) == 1
            and isinstance(search_paths[0], tuple)
            and search_paths[0][0] == '*direct*'
            and isinstance(search_paths[0][1], types.ModuleType)
        ):
            # secret hook for the compiler to initialize itself
            search_paths[0][1].populate(self)
        else:
            target_pkgs = {}
            for path in search_paths:
                self._create_target_pkg(path, target_pkgs)
            for target_package in target_pkgs.values():
                if debug:
                    print(
                        "target_package:", target_package,
                        file=sys.stderr
                    )
                target_package.compile(self)
                target_package.write()
                target_package.load(self, **kws)

        for kb in self.knowledge_bases.values():
            kb.init2()
        for rb in self.rule_bases.values():
            rb.init2()

    def _create_target_pkg(self, path, target_pkgs):
        if debug:
            print(
                "engine._create_target_pkg:", path,
                file=sys.stderr
            )

        target_package_name = '.compiled_krb'
        if isinstance(path, (tuple, list)):
            path, target_package_name = path
        if isinstance(path, types.ModuleType):
            path = path.__file__
        if not isinstance(path, (str, type(None))):
            raise ValueError(
                "illegal path argument: string expected, got "
                + str(type(path))
            )

        if debug:
            print(
                "_create_target_pkg path:", repr(path),
                file=sys.stderr
            )
            print(
                "_create_target_pkg target_package_name:",
                repr(target_package_name),
                file=sys.stderr
            )

        if path is None:
            # no source files
            assert target_package_name[0] != '.', (
                "engine: relative target, %s, illegal with no source package"
                % target_package_name
            )
            if target_package_name not in target_pkgs:
                tp = _get_target_pkg(
                    target_package_name + '.compiled_pyke_files'
                )
                if tp is None:
                    raise AssertionError(
                        "%s: compiled with different version of Pyke"
                        % target_package_name
                    )
                tp.reset(check_sources=False)
                target_pkgs[target_package_name] = tp
            return

        path = os.path.normpath(os.path.abspath(path))
        path_to_pkg, src_pkg, rem_path, zip_flag = _pythonify_path(path)

        if debug:
            print(
                "_create_target_pkg path to _pythonify_path:",
                repr(path), file=sys.stderr
            )
            print(
                "    path_to_package:", repr(path_to_pkg),
                file=sys.stderr
            )
            print(
                "    source_package_name:", repr(src_pkg),
                file=sys.stderr
            )
            print(
                "    remainder_path:", repr(rem_path),
                file=sys.stderr
            )
            print(
                "    zip_file_flag:", zip_flag,
                file=sys.stderr
            )

        target_filename = None

        if target_package_name[0] == '.':
            num_dots = (
                len(target_package_name)
                - len(target_package_name.lstrip('.'))
            )
            if debug:
                print(
                    "_create_target_pkg num_dots:", num_dots,
                    file=sys.stderr
                )
            if num_dots == 1:
                base_pkg = src_pkg
            else:
                base_pkg = '.'.join(
                    src_pkg.split('.')[:-(num_dots - 1)]
                )
            if base_pkg:
                target_package_name = (
                    base_pkg + '.' + target_package_name[num_dots:]
                )
            else:
                target_package_name = target_package_name[num_dots:]

            target_filename = os.path.join(
                path_to_pkg,
                os.path.join(*target_package_name.split('.')),
                'compiled_pyke_files.py'
            )

            if debug:
                print(
                    "_create_target_pkg absolute "
                    "target_package_name:", target_package_name,
                    file=sys.stderr
                )

        if target_package_name in target_pkgs:
            tp = target_pkgs[target_package_name]
        else:
            tname = target_package_name + '.compiled_pyke_files'
            if debug:
                print(
                    "_create_target_pkg tname:", tname,
                    file=sys.stderr
                )
            tp = None
            try:
                tp = _get_target_pkg(tname)
            except ImportError:
                pass
            if tp is None:
                if debug:
                    print(
                        "_create_target_pkg: no target module",
                        file=sys.stderr
                    )
                tp = target_pkg.target_pkg(tname, target_filename)
            tp.reset()
            target_pkgs[target_package_name] = tp

        src_pkg_dir = os.path.join(
            path_to_pkg,
            os.path.join(*src_pkg.split('.'))
        )
        if not os.path.isdir(src_pkg_dir):
            src_pkg_dir = os.path.dirname(src_pkg_dir)
            rem_path = os.path.dirname(rem_path)
        tp.add_source_package(src_pkg, rem_path, src_pkg_dir)

    def get_ask_module(self):
        if not hasattr(self, 'ask_module'):
            from pyke import ask_tty
            self.ask_module = ask_tty
        return self.ask_module

    def reset(self):
        '''Erases all case-specific facts and deactivates all rule bases.'''
        for rb in self.rule_bases.values():
            rb.reset()
        for kb in self.knowledge_bases.values():
            kb.reset()

    def get_kb(self, kb_name, _new_class=None):
        ans = self.knowledge_bases.get(kb_name)
        if ans is None:
            if _new_class:
                ans = _new_class(self, kb_name)
            else:
                raise KeyError("knowledge_base %s not found" % kb_name)
        return ans

    def get_rb(self, rb_name):
        ans = self.rule_bases.get(rb_name)
        if ans is None:
            raise KeyError("rule_base %s not found" % rb_name)
        return ans

    def get_create(self, rb_name, parent=None, exclude_list=()):
        ans = self.rule_bases.get(rb_name)
        if ans is None:
            from pyke import rule_base
            ans = rule_base.rule_base(self, rb_name, parent, exclude_list)
        elif (
            ans.parent != parent
            or ans.exclude_set != frozenset(exclude_list)
        ):
            raise AssertionError("duplicate rule_base: %s" % rb_name)
        return ans

    def get_ke(self, kb_name, entity_name):
        return self.get_kb(kb_name).get_entity_list(entity_name)

    def add_universal_fact(self, kb_name, fact_name, args):
        '''Universal facts are not deleted by engine.reset.'''
        if isinstance(args, str):
            raise TypeError(
                "engine.add_universal_fact: illegal args type, %s"
                % type(args)
            )
        args = tuple(args)
        return self.get_kb(kb_name, fact_base.fact_base) \
                   .add_universal_fact(fact_name, args)

    def add_case_specific_fact(self, kb_name, fact_name, args):
        '''Case specific facts are deleted by engine.reset.'''
        if isinstance(args, str):
            raise TypeError(
                "engine.add_case_specific_fact: illegal args type, %s"
                % type(args)
            )
        args = tuple(args)
        return self.get_kb(kb_name, fact_base.fact_base) \
                   .add_case_specific_fact(fact_name, args)



    def activate(self, *rb_names):
        '''Activate rule bases.'''
        for rb_name in rb_names:
            self.get_rb(rb_name).activate()

    def lookup(self, kb_name, entity_name, pat_context, patterns):
        return self.get_kb(kb_name).lookup(
            pat_context, pat_context, entity_name, patterns
        )

    def prove_goal(self, goal_str, **args):
        '''Proves goal_str with logic variables set to args.'''
        from pyke import goal
        return goal.compile(goal_str).prove(self, **args)

    def prove_1_goal(self, goal_str, **args):
        '''Returns the first solution or raises CanNotProve.'''
        from pyke import goal
        return goal.compile(goal_str).prove_1(self, **args)

    def prove(self, kb_name, entity_name, pat_context, patterns):
        '''Deprecated. Use engine.prove_goal.'''
        return self.get_kb(kb_name).prove(
            pat_context, pat_context, entity_name, patterns
        )

    def prove_n(self, kb_name, entity_name, fixed_args=(), num_returns=0):
        '''Deprecated. Use engine.prove_goal.'''
        if isinstance(fixed_args, str):
            raise TypeError(
                "engine.prove_n: fixed_args must not be a string"
            )

        def gen():
            from pyke import pattern
            context = contexts.simple_context()
            vars_ = self._Variables[:num_returns]
            try:
                with self.prove(
                    kb_name, entity_name, context,
                    tuple(pattern.pattern_literal(arg)
                          for arg in fixed_args) + vars_
                ) as it:
                    for plan in it:
                        final = {}
                        ans = tuple(
                            context.lookup_data(var.name, final=final)
                            for var in vars_
                        )
                        if plan:
                            plan = plan.create_plan(final)
                        yield ans, plan
            finally:
                context.done()

        return contextlib.closing(gen())

    def prove_1(self, kb_name, entity_name, fixed_args=(), num_returns=0):
        '''Deprecated. Use engine.prove_1_goal.'''
        try:
            with self.prove_n(
                kb_name, entity_name, fixed_args, num_returns
            ) as it:
                return next(iter(it))
        except StopIteration:
            from pyke import condensedPrint
            raise CanNotProve(
                "Can not prove %s.%s%s"
                % (kb_name, entity_name,
                   condensedPrint.cprint(
                       fixed_args + self._Variables[:num_returns]
                   ))
            )

    def print_stats(self, f=sys.stdout):
        for kb in sorted(
            self.knowledge_bases.values(), key=lambda kb: kb.name
        ):
            kb.print_stats(f)

    def trace(self, rb_name, rule_name):
        self.get_rb(rb_name).trace(rule_name)

    def untrace(self, rb_name, rule_name):
        self.get_rb(rb_name).untrace(rule_name)


Compiled_suffix = None


def _get_target_pkg(target_name):
    global Compiled_suffix
    module = target_pkg.import_(target_name)
    path = module.__file__
    do_reload = False
    if path.endswith(('.py', '.pyw')):
        if Compiled_suffix is None:
            do_reload = True
        else:
            source_path = path
            path = path[:-3] + Compiled_suffix
    else:
        assert path.endswith(('.pyc', '.pyo')), (
            'unknown file extension: %r' % path
        )
        Compiled_suffix = path[-4:]
        source_path = path[:-1]

    if not do_reload:
        if not os.path.exists(path) or (
            os.path.exists(source_path)
            and os.path.getmtime(source_path) > os.path.getmtime(path)
        ):
            do_reload = True

    if do_reload:
        module = importlib.reload(module)
        suffix = module.__file__[-4:]
        if suffix in ('.pyc', '.pyo'):
            Compiled_suffix = suffix

    if getattr(module, 'target_pkg_version', None) != pyke.target_pkg_version:
        return None
    return getattr(module, 'get_target_pkg')()


def _pythonify_path(path):
    '''Returns path_to_package, package_name, remainder_path, zip_file_flag.'''
    path = os.path.normpath(os.path.abspath(path))
    if path.endswith(('.py', '.pyw', '.pyc', '.pyo')):
        path = os.path.dirname(path)

    package_name = ''
    remainder_path = ''
    remainder_pkg = ''
    ans = '', '', path, False

    while path:
        if in_sys_path(path):
            if (
                len(remainder_path) < len(ans[2])
                or (
                    len(remainder_path) == len(ans[2])
                    and len(package_name) > len(ans[1])
                )
            ):
                if os.path.isdir(path):
                    ans = path, package_name, remainder_path, False
                else:
                    ans = path, remainder_pkg, '', True
        parent, dir_ = os.path.split(path)
        if parent in ('', path):
            break
        if _is_package_dir(path):
            if package_name:
                package_name = dir_ + '.' + package_name
            else:
                package_name = dir_
        else:
            pkg_path = os.path.join(*package_name.split('.'))
            if remainder_path:
                remainder_path = os.path.join(dir_, pkg_path, remainder_path)
            else:
                remainder_path = os.path.join(dir_, pkg_path)
        if remainder_pkg:
            remainder_pkg = dir_ + '.' + remainder_pkg
        else:
            remainder_pkg = dir_
        path = parent

    return ans


def _is_package_dir(path):
    if not os.path.isdir(path):
        return False
    return any(
        os.path.exists(os.path.join(path, '__init__' + ext))
        for ext in ('.py', '.pyw', '.pyc', '.pyo')
    )


def in_sys_path(path):
    '''Assumes path is a normalized abspath.'''
    return path in Sys_path
