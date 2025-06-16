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
         ('', '', 'investment_rules.krb'):
           [1749982010.7378237, 'investment_rules_bc.py'],
         ('', '', 'stock_analysis.krb'):
           [1749982010.745824, 'stock_analysis_bc.py'],
        },
        compiler_version)

