# driver.py

from __future__ import with_statement
import sys
from pyke import knowledge_engine
from pyke import krb_traceback

engine = knowledge_engine.engine(__file__)


def analyze_stocks(stock_data):
    """
    주식 분석 - 간단한 Python 로직으로 처리
    """
    results = {}

    for ticker, data in stock_data['facts_by_ticker'].items():
        print(f"Analyzing {ticker}...")

        # 간단한 규칙 기반 로직
        decision = make_decision(ticker, data, stock_data['overall_facts'])
        results[ticker] = decision
        print(f"{ticker}: {decision}")

    return results


def make_decision(ticker, data, market_facts):
    """
    간단한 if-else 로직으로 투자 결정
    """
    # 펀더멘털 체크
    fund_pros = len(data.get('fundamental', {}).get('pros', []))
    fund_cons = len(data.get('fundamental', {}).get('cons', []))
    fund_good = fund_pros >= 3
    fund_bad = fund_cons >= 2

    # 기술적 지표 체크
    tech = data.get('technical_indicator', '').lower()
    tech_bullish = 'uptrend' in tech or 'positive' in tech or 'strong' in tech
    tech_bearish = 'bearish' in tech or 'decline' in tech or 'weak' in tech

    # 뉴스 체크
    news_pros = data.get('news', {}).get('pros', '').lower()
    news_cons = data.get('news', {}).get('cons', '').lower()
    news_good = 'strong' in news_pros or 'profitable' in news_pros
    news_bad = 'decline' in news_cons or 'concern' in news_cons or 'drop' in news_cons

    # 시장 체크
    market_bad = 'market_cons_recession_fears' in market_facts

    # 결정 로직
    if fund_good and tech_bullish and news_good and not market_bad:
        return 'buy_a_lot'
    elif fund_good and tech_bullish and not market_bad:
        return 'buy'
    elif fund_good and not fund_bad:
        return 'buy_little'
    elif fund_bad and tech_bearish:
        return 'sell'
    elif tech_bearish and news_bad:
        return 'sell_little'
    else:
        return 'hold'


def test_with_sample_data():
    sample_data = {'facts_by_ticker': {'AAPL': {'news': {'pros': 'iPhone demand remains strong despite economic uncertainty.',
                                           'cons': 'Stock underperformed during a weak market session.'},
                                  'fundamental': {'pros': {'solid_fcf_per_share', 'high_roe', 'robust_operating_margin',
                                                           'strong_roa'},
                                                  'cons': {'high_debt_to_equity', 'low_current_ratio',
                                                           'expensive_valuation'}},
                                  'technical_indicator': 'rsi_moderate_macd_positive_offset_by_high_valuation'},
                         'AXP': {'news': {'pros': 'Credit card business remains profitable.',
                                          'cons': 'Stock decline leads Dow drop, raising sentiment concern.'},
                                 'fundamental': {'pros': {'high_fcf_per_share', 'solid_operating_margin'},
                                                 'cons': {'high_total_debt', 'low_quick_ratio', 'low_roa'}},
                                 'technical_indicator': 'bearish_trend_confirmed_by_macd_and_rsi'}, 'JPM': {
            'news': {'pros': 'Stock slightly up in mixed market.', 'cons': 'Facing legal and political controversies.'},
            'fundamental': {'pros': {'reasonable_debt_to_asset', 'low_pe_ratio', 'stable_pb'},
                            'cons': {'low_roa', 'legal_risks'}},
            'technical_indicator': 'neutral_technical_with_low_volatility'}, 'UNH': {
            'news': {'pros': 'Investor attention on strong earnings.',
                     'cons': 'Stock declined in overall weak session.'},
            'fundamental': {'pros': {'high_roe', 'strong_fcf', 'stable_cash_position'},
                            'cons': {'moderate_total_debt', 'low_current_ratio'}},
            'technical_indicator': 'neutral_technical_low_volatility_supported_by_fundamentals'}, 'CVX': {
            'news': {'pros': "Analysts suggest it's a good time to look at energy stocks.",
                     'cons': 'Crude oil prices and energy demand weakening.'},
            'fundamental': {'pros': {'low_debt', 'solid_roic', 'low_pe'},
                            'cons': {'declining_energy_prices', 'sensitive_to_macroeconomic_trends'}},
            'technical_indicator': 'bearish_technical_reflects_macro_pressure'}, 'MSFT': {
            'news': {'pros': 'Canton blockchain initiative boosts innovation profile.',
                     'cons': 'Tech sector facing valuation concerns.'},
            'fundamental': {'pros': {'high_roe', 'strong_cash_position', 'high_operating_margin'},
                            'cons': {'premium_valuation', 'high_pe_ratio'}},
            'technical_indicator': 'strong_uptrend_with_supportive_fundamentals'}},
     'overall_facts': {'market_cons_recession_fears', 'few_holdings', 'market_pros_strong_earnings',
                       'tech_sector_dominant', 'cash_high'}}

    print("Starting stock analysis...")
    results = analyze_stocks(sample_data)

    print("\n=== FINAL RESULTS ===")
    for ticker, decision in results.items():
        print(f"{ticker}: {decision}")

    return results


if __name__ == '__main__':
    test_with_sample_data()