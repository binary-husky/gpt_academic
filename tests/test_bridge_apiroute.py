import unittest
import os
import sys

def validate_path():
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)

validate_path()

from request_llms.bridge_apiroute import decode_chunk, generate_payload, verify_endpoint

class TestBridgeApiRoute(unittest.TestCase):
    def test_decode_chunk_content(self):
        raw_chunk = b'data: {"choices": [{"delta": {"content": "Hello", "role": "assistant"}}]}'
        chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_reasoning, has_role = decode_chunk(raw_chunk)
        self.assertTrue(has_choices)
        self.assertTrue(choice_valid)
        self.assertTrue(has_content)
        self.assertFalse(has_reasoning)
        self.assertTrue(has_role)
        self.assertEqual(chunkjson["choices"][0]["delta"]["content"], "Hello")

    def test_decode_chunk_reasoning(self):
        raw_chunk = b'data: {"choices": [{"delta": {"reasoning_content": "Thinking step 1"}}]}'
        chunk_decoded, chunkjson, has_choices, choice_valid, has_content, has_reasoning, has_role = decode_chunk(raw_chunk)
        self.assertTrue(has_choices)
        self.assertTrue(choice_valid)
        self.assertFalse(has_content)
        self.assertTrue(has_reasoning)
        self.assertEqual(chunkjson["choices"][0]["delta"]["reasoning_content"], "Thinking step 1")

    def test_verify_endpoint(self):
        endpoint = "https://www.api-route.com/v1/chat/completions"
        self.assertEqual(verify_endpoint(endpoint), endpoint)

    def test_generate_payload_prefix_stripping(self):
        llm_kwargs = {
            "api_key": "sk-test12345678901234567890",
            "llm_model": "api-route-gpt-4o",
            "temperature": 0.7,
            "top_p": 0.9,
        }
        headers, payload = generate_payload(
            inputs="Hello API Route",
            llm_kwargs=llm_kwargs,
            history=[],
            system_prompt="You are a helpful assistant.",
            stream=True
        )
        self.assertEqual(payload["model"], "gpt-4o")
        self.assertEqual(headers["Authorization"], "Bearer sk-test12345678901234567890")
        self.assertEqual(payload["messages"][-1]["content"], "Hello API Route")
        self.assertEqual(payload["temperature"], 0.7)

    def test_generate_payload_with_apiroute_and_token_override(self):
        llm_kwargs = {
            "api_key": "sk-dist-test12345678901234567890",
            "llm_model": "apiroute-claude-3-7-sonnet-20250219(max_token=64000)",
            "temperature": 1.0,
            "top_p": 1.0,
        }
        headers, payload = generate_payload(
            inputs="Explain quantum computing",
            llm_kwargs=llm_kwargs,
            history=[],
            system_prompt="You are a scientist.",
            stream=True
        )
        self.assertEqual(payload["model"], "claude-3-7-sonnet-20250219")
        self.assertEqual(headers["Authorization"], "Bearer sk-dist-test12345678901234567890")
        self.assertEqual(payload["messages"][-1]["content"], "Explain quantum computing")

if __name__ == '__main__':
    unittest.main()
