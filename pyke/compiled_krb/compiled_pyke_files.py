# compiled_pyke_files.py

from pyke import target_pkg

pyke_version = '1.1.1'
compiler_version = 1
target_pkg_version = 1

try:
    loader = __loader__
except NameError:
    loader = None

def get_target_pkg():
    return target_pkg.target_pkg(__name__, __file__, pyke_version, loader, {
         ('pyke', '', 'krb_compiler\\compiler.krb'):
           [1749980717.4433594, 'compiler_bc.py'],
         ('pyke', '', 'krb_compiler\\TEST\\kfbparse_test.kfb'):
           [1749980717.448359, 'kfbparse_test.fbc'],
         ('pyke', '', 'krb_compiler\\TEST\\krbparse_test.krb'):
           [1749980717.4513588, 'krbparse_test_fc.py', 'krbparse_test_plans.py', 'krbparse_test_bc.py'],
        },
        compiler_version)

