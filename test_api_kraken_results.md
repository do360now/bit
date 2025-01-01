============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-8.3.4, pluggy-1.5.0 -- /home/tron/DevOps/projects/bit/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/tron/DevOps/projects/bit
plugins: cov-6.0.0
collecting ... collected 8 items

BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_execute_trade_invalid_order_book PASSED [ 12%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_btc_order_book_invalid_response PASSED [ 25%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_historical_prices_invalid_data PASSED [ 37%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_market_volume_invalid_response PASSED [ 50%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_market_volume_key_error FAILED [ 62%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_optimal_price_edge_case_buffer PASSED [ 75%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_optimal_price_invalid_side PASSED [ 87%]
BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_make_private_request_error_handling FAILED [100%]

=================================== FAILURES ===================================
____________ TestKrakenAPIEnhanced.test_get_market_volume_key_error ____________

self = <test_api_kraken.TestKrakenAPIEnhanced testMethod=test_get_market_volume_key_error>
mock_get = <MagicMock name='get' id='140448293518784'>

    @patch("api_kraken.requests.get")
    def test_get_market_volume_key_error(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {"XBTUSDT": {"v": []}},
            "error": []
        }
    
>       volume = self.api_kraken.get_market_volume()

BTC/test_api_kraken.py:77: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <api_kraken.KrakenAPI object at 0x7fbcaaa61ea0>, pair = 'XBTUSDT'

    def get_market_volume(self, pair: str = "XBTUSDT") -> Optional[float]:
        """Fetches the 24-hour trading volume for a given pair."""
        result = self._make_request(method="Ticker", path="/0/public/", data={"pair": pair})
        if result:
            try:
>               volume = float(result[pair]['v'][1])  # 'v' represents the volume, and index [1] is the 24-hour volume
E               IndexError: list index out of range

BTC/api_kraken.py:125: IndexError
----------------------------- Captured stderr call -----------------------------
2025-01-01 22:24:49,311 - trading_bot - INFO - Making Ticker request to https://api.kraken.com/0/public/Ticker with data: {'pair': 'XBTUSDT'}
________ TestKrakenAPIEnhanced.test_make_private_request_error_handling ________

self = <Retrying object at 0x7fbcaaad5150 (stop=<tenacity.stop.stop_after_attempt object at 0x7fbcab1e2620>, wait=<tenacity.w...0x7fbcaaa18f70>, before=<function before_nothing at 0x7fbcaaa10790>, after=<function after_nothing at 0x7fbcaaa10a60>)>
fn = <function KrakenAPI._make_request at 0x7fbcaaa13910>
args = (<api_kraken.KrakenAPI object at 0x7fbcaaad5db0>,)
kwargs = {'data': {'nonce': '1735766704426', 'test': 'data'}, 'is_private': True, 'method': 'AddOrder', 'path': '/0/private/'}
retry_state = <RetryCallState 140448294068832: attempt #5; slept for 15.0; last result: failed (Exception Network error)>
do = <tenacity.DoAttempt object at 0x7fbcaaad5360>

    def __call__(
        self,
        fn: t.Callable[..., WrappedFnReturnT],
        *args: t.Any,
        **kwargs: t.Any,
    ) -> WrappedFnReturnT:
        self.begin()
    
        retry_state = RetryCallState(retry_object=self, fn=fn, args=args, kwargs=kwargs)
        while True:
            do = self.iter(retry_state=retry_state)
            if isinstance(do, DoAttempt):
                try:
>                   result = fn(*args, **kwargs)

.venv/lib/python3.10/site-packages/tenacity/__init__.py:478: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
BTC/api_kraken.py:42: in _make_request
    response = requests.post(url, headers=headers, data=data)
/usr/lib/python3.10/unittest/mock.py:1114: in __call__
    return self._mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1118: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1173: in _execute_mock_call
    raise effect
.venv/lib/python3.10/site-packages/tenacity/__init__.py:478: in __call__
    result = fn(*args, **kwargs)
BTC/api_kraken.py:42: in _make_request
    response = requests.post(url, headers=headers, data=data)
/usr/lib/python3.10/unittest/mock.py:1114: in __call__
    return self._mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1118: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1173: in _execute_mock_call
    raise effect
.venv/lib/python3.10/site-packages/tenacity/__init__.py:478: in __call__
    result = fn(*args, **kwargs)
BTC/api_kraken.py:42: in _make_request
    response = requests.post(url, headers=headers, data=data)
/usr/lib/python3.10/unittest/mock.py:1114: in __call__
    return self._mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1118: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1173: in _execute_mock_call
    raise effect
.venv/lib/python3.10/site-packages/tenacity/__init__.py:478: in __call__
    result = fn(*args, **kwargs)
BTC/api_kraken.py:42: in _make_request
    response = requests.post(url, headers=headers, data=data)
/usr/lib/python3.10/unittest/mock.py:1114: in __call__
    return self._mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1118: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1173: in _execute_mock_call
    raise effect
.venv/lib/python3.10/site-packages/tenacity/__init__.py:478: in __call__
    result = fn(*args, **kwargs)
BTC/api_kraken.py:42: in _make_request
    response = requests.post(url, headers=headers, data=data)
/usr/lib/python3.10/unittest/mock.py:1114: in __call__
    return self._mock_call(*args, **kwargs)
/usr/lib/python3.10/unittest/mock.py:1118: in _mock_call
    return self._execute_mock_call(*args, **kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <MagicMock name='post' id='140448294068640'>
args = ('https://api.kraken.com/0/private/AddOrder',)
kwargs = {'data': {'nonce': '1735766704426', 'test': 'data'}, 'headers': {'API-Key': 'test_key', 'API-Sign': 'OSbqezlDPLbeH1Fnq2zB6tO/5jGMz51uP2dUBpwgAM0gfcmt8cE7bnTOV9Vhheq9j9ZUIgletNOROcQliwH0Sw==', 'User-Agent': 'Kraken REST API'}}
effect = Exception('Network error')

    def _execute_mock_call(self, /, *args, **kwargs):
        # separate from _increment_mock_call so that awaited functions are
        # executed separately from their call, also AsyncMock overrides this method
    
        effect = self.side_effect
        if effect is not None:
            if _is_exception(effect):
>               raise effect
E               Exception: Network error

/usr/lib/python3.10/unittest/mock.py:1173: Exception

The above exception was the direct cause of the following exception:

self = <test_api_kraken.TestKrakenAPIEnhanced testMethod=test_make_private_request_error_handling>
mock_post = <MagicMock name='post' id='140448294068640'>

    @patch("api_kraken.requests.post")
    def test_make_private_request_error_handling(self, mock_post):
        mock_post.side_effect = Exception("Network error")
    
>       result = self.api_kraken._make_request(
            method="AddOrder",
            path="/0/private/",
            data={"test": "data"},
            is_private=True
        )

BTC/test_api_kraken.py:16: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.10/site-packages/tenacity/__init__.py:336: in wrapped_f
    return copy(f, *args, **kw)
.venv/lib/python3.10/site-packages/tenacity/__init__.py:475: in __call__
    do = self.iter(retry_state=retry_state)
.venv/lib/python3.10/site-packages/tenacity/__init__.py:376: in iter
    result = action(retry_state)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

rs = <RetryCallState 140448294068832: attempt #5; slept for 15.0; last result: failed (Exception Network error)>

    def exc_check(rs: "RetryCallState") -> None:
        fut = t.cast(Future, rs.outcome)
        retry_exc = self.retry_error_cls(fut)
        if self.reraise:
            raise retry_exc.reraise()
>       raise retry_exc from fut.exception()
E       tenacity.RetryError: RetryError[<Future at 0x7fbcaaad5030 state=finished raised Exception>]

.venv/lib/python3.10/site-packages/tenacity/__init__.py:419: RetryError
----------------------------- Captured stderr call -----------------------------
2025-01-01 22:24:49,397 - trading_bot - INFO - Making AddOrder request to https://api.kraken.com/0/private/AddOrder with data: {'test': 'data', 'nonce': '1735766689397'}
2025-01-01 22:24:50,403 - trading_bot - INFO - Making AddOrder request to https://api.kraken.com/0/private/AddOrder with data: {'test': 'data', 'nonce': '1735766690403'}
2025-01-01 22:24:52,413 - trading_bot - INFO - Making AddOrder request to https://api.kraken.com/0/private/AddOrder with data: {'test': 'data', 'nonce': '1735766692413'}
2025-01-01 22:24:56,420 - trading_bot - INFO - Making AddOrder request to https://api.kraken.com/0/private/AddOrder with data: {'test': 'data', 'nonce': '1735766696420'}
2025-01-01 22:25:04,426 - trading_bot - INFO - Making AddOrder request to https://api.kraken.com/0/private/AddOrder with data: {'test': 'data', 'nonce': '1735766704426'}
=========================== short test summary info ============================
FAILED BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_get_market_volume_key_error
FAILED BTC/test_api_kraken.py::TestKrakenAPIEnhanced::test_make_private_request_error_handling
========================= 2 failed, 6 passed in 16.24s =========================
