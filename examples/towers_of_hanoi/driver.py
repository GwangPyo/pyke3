# driver.py

from __future__ import with_statement
import sys
from pyke import knowledge_engine
from pyke import krb_traceback

engine = knowledge_engine.engine(__file__)
from math import inf

def test(num_disks):
    engine.reset()
    optimal_length = inf
    optimal = None
    arg_opt = -1
    try:
        engine.activate('towers_of_hanoi')

        with engine.prove_goal('towers_of_hanoi.solve($num_disks, $moves)',
                               num_disks=num_disks) \
                as gen:

            for i, (vars, no_plan) in enumerate(gen):
                if len(vars['moves']) < optimal_length:
                    optimal = vars['moves']
                    optimal_length = len(optimal)
                    arg_opt = i + 1
                print("got %d:" % (i + 1), vars['moves'])
        print("Optimal Solution", arg_opt, optimal, optimal_length)
    except:
        krb_traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    test(4)
