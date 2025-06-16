# stock_analysis_bc.py

from __future__ import with_statement
import itertools
from pyke import contexts, pattern, bc_rule

pyke_version = '1.1.1'
compiler_version = 1

def is_fundamental_good(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'fundamental_positive', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_fundamental_good: got unexpected plan from when clause 1"
            with engine.prove('stock_analysis', 'fundamental_positive', context,
                              (rule.pattern(0),
                               rule.pattern(2),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.is_fundamental_good: got unexpected plan from when clause 2"
                with engine.prove('stock_analysis', 'fundamental_positive', context,
                                  (rule.pattern(0),
                                   rule.pattern(3),)) \
                  as gen_3:
                  for x_3 in gen_3:
                    assert x_3 is None, \
                      "stock_analysis.is_fundamental_good: got unexpected plan from when clause 3"
                    if context.lookup_data('pos1') != context.lookup_data('pos2'):
                      if context.lookup_data('pos2') != context.lookup_data('pos3'):
                        rule.rule_base.num_bc_rule_successes += 1
                        yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_fundamental_bad(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'fundamental_negative', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_fundamental_bad: got unexpected plan from when clause 1"
            with engine.prove('stock_analysis', 'fundamental_negative', context,
                              (rule.pattern(0),
                               rule.pattern(2),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.is_fundamental_bad: got unexpected plan from when clause 2"
                if context.lookup_data('neg1') != context.lookup_data('neg2'):
                  rule.rule_base.num_bc_rule_successes += 1
                  yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_technical_bullish(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'technical_indicator', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_technical_bullish: got unexpected plan from when clause 1"
            'uptrend' in context.lookup_data('indicator').lower() or 'positive' in context.lookup_data('indicator').lower() or 'strong' in context.lookup_data('indicator').lower()
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_technical_bearish(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'technical_indicator', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_technical_bearish: got unexpected plan from when clause 1"
            'bearish' in context.lookup_data('indicator').lower() or 'decline' in context.lookup_data('indicator').lower() or 'weak' in context.lookup_data('indicator').lower()
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_news_positive(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'news_positive', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_news_positive: got unexpected plan from when clause 1"
            'strong' in context.lookup_data('news').lower() or 'profitable' in context.lookup_data('news').lower()
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_news_negative(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'news_negative', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_news_negative: got unexpected plan from when clause 1"
            'decline' in context.lookup_data('news').lower() or 'concern' in context.lookup_data('news').lower() or 'drop' in context.lookup_data('news').lower()
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def is_market_bad(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'market_condition', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.is_market_bad: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def buy_a_lot_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_fundamental_good', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.buy_a_lot_rule: got unexpected plan from when clause 1"
            with engine.prove(rule.rule_base.root_name, 'is_technical_bullish', context,
                              (rule.pattern(0),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.buy_a_lot_rule: got unexpected plan from when clause 2"
                with engine.prove(rule.rule_base.root_name, 'is_news_positive', context,
                                  (rule.pattern(0),)) \
                  as gen_3:
                  for x_3 in gen_3:
                    assert x_3 is None, \
                      "stock_analysis.buy_a_lot_rule: got unexpected plan from when clause 3"
                    rule.rule_base.num_bc_rule_successes += 1
                    yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def buy_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_fundamental_good', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.buy_rule: got unexpected plan from when clause 1"
            with engine.prove(rule.rule_base.root_name, 'is_technical_bullish', context,
                              (rule.pattern(0),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.buy_rule: got unexpected plan from when clause 2"
                rule.rule_base.num_bc_rule_successes += 1
                yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def buy_little_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_fundamental_good', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.buy_little_rule: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def sell_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_fundamental_bad', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.sell_rule: got unexpected plan from when clause 1"
            with engine.prove(rule.rule_base.root_name, 'is_technical_bearish', context,
                              (rule.pattern(0),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.sell_rule: got unexpected plan from when clause 2"
                rule.rule_base.num_bc_rule_successes += 1
                yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def sell_little_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_technical_bearish', context,
                          (rule.pattern(0),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.sell_little_rule: got unexpected plan from when clause 1"
            with engine.prove(rule.rule_base.root_name, 'is_news_negative', context,
                              (rule.pattern(0),)) \
              as gen_2:
              for x_2 in gen_2:
                assert x_2 is None, \
                  "stock_analysis.sell_little_rule: got unexpected plan from when clause 2"
                rule.rule_base.num_bc_rule_successes += 1
                yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def hold_market_bad_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove(rule.rule_base.root_name, 'is_market_bad', context,
                          ()) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.hold_market_bad_rule: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def hold_default_rule(rule, arg_patterns, arg_context):
  engine = rule.rule_base.engine
  patterns = rule.goal_arg_patterns()
  if len(arg_patterns) == len(patterns):
    context = contexts.bc_context(rule)
    try:
      if all(map(lambda pat, arg:
                              pat.match_pattern(context, context,
                                                arg, arg_context),
                            patterns,
                            arg_patterns)):
        rule.rule_base.num_bc_rules_matched += 1
        with engine.prove('stock_analysis', 'technical_indicator', context,
                          (rule.pattern(0),
                           rule.pattern(1),)) \
          as gen_1:
          for x_1 in gen_1:
            assert x_1 is None, \
              "stock_analysis.hold_default_rule: got unexpected plan from when clause 1"
            rule.rule_base.num_bc_rule_successes += 1
            yield
        rule.rule_base.num_bc_rule_failures += 1
    finally:
      context.done()

def populate(engine):
  This_rule_base = engine.get_create('stock_analysis')
  
  bc_rule.bc_rule('is_fundamental_good', This_rule_base, 'is_fundamental_good',
                  is_fundamental_good, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('pos1'),
                   contexts.variable('pos2'),
                   contexts.variable('pos3'),))
  
  bc_rule.bc_rule('is_fundamental_bad', This_rule_base, 'is_fundamental_bad',
                  is_fundamental_bad, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('neg1'),
                   contexts.variable('neg2'),))
  
  bc_rule.bc_rule('is_technical_bullish', This_rule_base, 'is_technical_bullish',
                  is_technical_bullish, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('indicator'),))
  
  bc_rule.bc_rule('is_technical_bearish', This_rule_base, 'is_technical_bearish',
                  is_technical_bearish, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('indicator'),))
  
  bc_rule.bc_rule('is_news_positive', This_rule_base, 'is_news_positive',
                  is_news_positive, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('news'),))
  
  bc_rule.bc_rule('is_news_negative', This_rule_base, 'is_news_negative',
                  is_news_negative, None,
                  (contexts.variable('ticker'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('news'),))
  
  bc_rule.bc_rule('is_market_bad', This_rule_base, 'is_market_bad',
                  is_market_bad, None,
                  (),
                  (),
                  (pattern.pattern_literal('market_cons_recession_fears'),))
  
  bc_rule.bc_rule('buy_a_lot_rule', This_rule_base, 'investment_decision',
                  buy_a_lot_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('buy_a_lot'),),
                  (),
                  (contexts.variable('ticker'),))
  
  bc_rule.bc_rule('buy_rule', This_rule_base, 'investment_decision',
                  buy_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('buy'),),
                  (),
                  (contexts.variable('ticker'),))
  
  bc_rule.bc_rule('buy_little_rule', This_rule_base, 'investment_decision',
                  buy_little_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('buy_little'),),
                  (),
                  (contexts.variable('ticker'),))
  
  bc_rule.bc_rule('sell_rule', This_rule_base, 'investment_decision',
                  sell_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('sell'),),
                  (),
                  (contexts.variable('ticker'),))
  
  bc_rule.bc_rule('sell_little_rule', This_rule_base, 'investment_decision',
                  sell_little_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('sell_little'),),
                  (),
                  (contexts.variable('ticker'),))
  
  bc_rule.bc_rule('hold_market_bad_rule', This_rule_base, 'investment_decision',
                  hold_market_bad_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('hold'),),
                  (),
                  ())
  
  bc_rule.bc_rule('hold_default_rule', This_rule_base, 'investment_decision',
                  hold_default_rule, None,
                  (contexts.variable('ticker'),
                   pattern.pattern_literal('hold'),),
                  (),
                  (contexts.variable('ticker'),
                   contexts.variable('any_indicator'),))


Krb_filename = '..\\stock_analysis.krb'
Krb_lineno_map = (
    ((16, 20), (2, 2)),
    ((22, 28), (4, 4)),
    ((29, 35), (5, 5)),
    ((36, 42), (6, 6)),
    ((43, 43), (7, 7)),
    ((44, 44), (8, 8)),
    ((57, 61), (11, 11)),
    ((63, 69), (13, 13)),
    ((70, 76), (14, 14)),
    ((77, 77), (15, 15)),
    ((90, 94), (18, 18)),
    ((96, 102), (20, 20)),
    ((103, 103), (21, 21)),
    ((116, 120), (24, 24)),
    ((122, 128), (26, 26)),
    ((129, 129), (27, 27)),
    ((142, 146), (30, 30)),
    ((148, 154), (32, 32)),
    ((155, 155), (33, 33)),
    ((168, 172), (36, 36)),
    ((174, 180), (38, 38)),
    ((181, 181), (39, 39)),
    ((194, 198), (42, 42)),
    ((200, 205), (44, 44)),
    ((218, 222), (47, 47)),
    ((224, 229), (49, 49)),
    ((230, 235), (50, 50)),
    ((236, 241), (51, 51)),
    ((254, 258), (54, 54)),
    ((260, 265), (56, 56)),
    ((266, 271), (57, 57)),
    ((284, 288), (60, 60)),
    ((290, 295), (62, 62)),
    ((308, 312), (65, 65)),
    ((314, 319), (67, 67)),
    ((320, 325), (68, 68)),
    ((338, 342), (71, 71)),
    ((344, 349), (73, 73)),
    ((350, 355), (74, 74)),
    ((368, 372), (77, 77)),
    ((374, 379), (79, 79)),
    ((392, 396), (82, 82)),
    ((398, 404), (84, 84)),
)
