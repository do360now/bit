pytest --cov=BTC/ --cov-report=term-missing
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/tron/DevOps/projects/bit
plugins: cov-6.0.0
collected 27 items

BTC/test_api_kraken.py .......                                           [ 25%]
BTC/test_indicators.py .......                                           [ 51%]
BTC/test_main.py .sss                                                    [ 66%]
BTC/test_portfolio.py ....                                               [ 81%]
BTC/test_trading_strategy.py .....                                       [100%]

---------- coverage: platform linux, python 3.10.12-final-0 ----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
BTC/api_kraken.py                 91     20    78%   33, 54-55, 58-61, 69, 80, 91, 95, 102, 122-130
BTC/config.py                     12      1    92%   13
BTC/indicators.py                 81     10    88%   42-43, 64-65, 75-76, 94, 100, 107, 114
BTC/logger_config.py              16      0   100%
BTC/main.py                       31      9    71%   18, 21-23, 33-38, 44
BTC/portfolio.py                  16      0   100%
BTC/test_api_kraken.py            57      1    98%   102
BTC/test_indicators.py            45      1    98%   77
BTC/test_main.py                  56     29    48%   19-31, 36-48, 53-66, 84
BTC/test_portfolio.py             35      1    97%   54
BTC/test_trading_strategy.py      62      1    98%   112
BTC/trading_strategy.py           99     34    66%   42, 65-106, 112, 117-118, 142-143
------------------------------------------------------------
TOTAL                            601    107    82%


======================== 24 passed, 3 skipped in 3.98s =========================
