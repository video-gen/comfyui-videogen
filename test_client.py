import json
import os
import unittest
from unittest.mock import patch
import client


class ClientTests(unittest.TestCase):
    def test_default_blocks_credit_use(self):
        with patch.object(client, 'request') as request:
            with self.assertRaises(ValueError):
                client.start_storyboard(['one', 'two'], False)
            request.assert_not_called()

    def test_start_contract(self):
        with patch.object(client, 'request', return_value={'workflowRunId': 'test-run'}) as request:
            self.assertEqual(client.start_storyboard(['one', 'two'], True), 'test-run')
            path, body = request.call_args.args
            self.assertEqual(path, '/v1/workflows/storyboard-to-video')
            self.assertEqual(body['quality'], 'HIGH')
            self.assertTrue(body['autoExport'])
            self.assertEqual(len(body['remixActions']), 2)
            self.assertEqual(body['scenes'], [{'prompt': 'one'}, {'prompt': 'two'}])

    def test_wait_returns_export_and_does_not_start(self):
        with patch.object(client, 'request', return_value={'status': 'succeeded', 'downloadUrl': 'https://example.invalid/video.mp4'}) as request:
            self.assertEqual(client.wait_for_export('test-run', 1, lambda: None), 'https://example.invalid/video.mp4')
            self.assertEqual(request.call_args.args, ('/v1/workflows/runs/test-run',))

    def test_failed_workflow_raises(self):
        with patch.object(client, 'request', return_value={'status': 'failed'}):
            with self.assertRaises(RuntimeError):
                client.wait_for_export('test-run', 1, lambda: None)

    def test_no_credential_in_widget_or_source_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                client.request('/v1/account/me')


if __name__ == '__main__':
    unittest.main()
