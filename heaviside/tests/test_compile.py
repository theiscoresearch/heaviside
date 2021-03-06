# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import unittest
from io import StringIO

try:
    from unittest import mock
except ImportError:
    import mock

import heaviside
Path = heaviside.utils.Path

cur_dir = Path(os.path.dirname(os.path.realpath(__file__)))

class TestCompile(unittest.TestCase):
    def execute(self, filename, error_msg):
        filepath = cur_dir / 'sfn' / filename

        try:
            out = heaviside.compile(filepath)
            self.assertFalse(True, "compile() should result in an exception")
        except heaviside.exceptions.CompileError as ex:
            actual = str(ex).split('\n')[-1]
            expected = "Syntax Error: {}".format(error_msg)
            self.assertEqual(actual, expected)

    def test_unterminated_quote(self):
        self.execute('error_unterminated_quote.sfn', 'Unterminated quote')

    def test_unterminated_multiquote(self):
        self.execute('error_unterminated_multiquote.sfn', 'EOF in multi-line string')

    def test_invalid_heartbeat(self):
        self.execute('error_invalid_heartbeat.sfn', "Heartbeat must be less than timeout (defaults to 60)")

    def test_invalid_heartbeat2(self):
        self.execute('error_invalid_heartbeat2.sfn', "'0' is not a positive integer")

    def test_invalid_timeout(self):
        self.execute('error_invalid_timeout.sfn', "'0' is not a positive integer")

    def test_unexpected_catch(self):
        self.execute('error_unexpected_catch.sfn', "Pass state cannot contain a Catch modifier")

    def test_unexpected_data(self):
        self.execute('error_unexpected_data.sfn', "Succeed state cannot contain a Data modifier")

    def test_unexpected_heartbeat(self):
        self.execute('error_unexpected_heartbeat.sfn', "Pass state cannot contain a Heartbeat modifier")

    def test_unexpected_input(self):
        self.execute('error_unexpected_input.sfn', "Fail state cannot contain a Input modifier")

    def test_unexpected_output(self):
        self.execute('error_unexpected_output.sfn', "Fail state cannot contain a Output modifier")

    def test_unexpected_result(self):
        self.execute('error_unexpected_result.sfn', "Fail state cannot contain a Result modifier")

    def test_unexpected_retry(self):
        self.execute('error_unexpected_retry.sfn', "Pass state cannot contain a Retry modifier")

    def test_unexpected_timeout(self):
        self.execute('error_unexpected_timeout.sfn', "Pass state cannot contain a Timeout modifier")

    def test_unexpected_token(self):
        self.execute('error_unexpected_token.sfn', 'Invalid syntax')

    def test_invalid_retry_delay(self):
        self.execute('error_invalid_retry_delay.sfn', "'0' is not a positive integer")

    def test_invalid_retry_backoff(self):
        self.execute('error_invalid_retry_backoff.sfn', "Backoff rate should be >= 1.0")

    def test_invalid_wait_seconds(self):
        self.execute('error_invalid_wait_seconds.sfn', "'0' is not a positive integer")

    def test_invalid_multiple_input(self):
        self.execute('error_invalid_multiple_input.sfn', "Pass state can only contain one Input modifier")

    def test_invalid_state_name(self):
        self.execute('error_invalid_state_name.sfn', "Name exceedes 128 characters")

    def test_duplicate_state_name(self):
        self.execute('error_duplicate_state_name.sfn', "Duplicate state name 'Test'")

class TestTranslate(unittest.TestCase):
    def test_lambda(self):
        expected = 'arn:aws:lambda:region:account:function:Test'
        actual = heaviside.create_translate('region', 'account')('Lambda', 'Test')

        self.assertEqual(actual, expected)

    def test_activity(self):
        expected = 'arn:aws:states:region:account:activity:Test'
        actual = heaviside.create_translate('region', 'account')('Activity', 'Test')

        self.assertEqual(actual, expected)

    def test_invalid_arg(self):
        with self.assertRaises(TypeError):
            heaviside.create_translate(None, None)('Lambda', 'Test')

    def test_none(self):
        expected = 'arn:aws:states:region:account:activity:Test'
        actual = heaviside.create_translate('xxxxxx', 'xxxxxxx')('Activity', expected)

        self.assertEqual(actual, expected)

    def test_partial(self):
        expected = 'arn:aws:states:region:account:activity:Test'
        actual = heaviside.create_translate('region', 'xxxxxxx')('Activity', 'account:activity:Test')

        self.assertEqual(actual, expected)

