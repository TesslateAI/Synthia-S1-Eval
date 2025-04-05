import os
import time
import random
import openai
import logging
from packaging.version import parse as parse_version

IS_OPENAI_V1 = parse_version(openai.__version__) >= parse_version('1.0.0')

SYNTHIA_SYS_PROMPT = (
    "Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process "
    "before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, "
    "summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. "
    "Please structure your response into two main sections: Thought and Solution. In the Thought section, detail your reasoning "
    "process using the specified format: <|begin_of_thought|> {thought with steps separated with '\n\n'} <|end_of_thought|> "
    "Each step should include detailed considerations such as analyzing questions, summarizing relevant findings, brainstorming "
    "new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the "
    "Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present "
    "the final solution that you deem correct. The solution should remain a logical, accurate, concise expression style and "
    "detail necessary steps needed to reach the conclusion, formatted as follows: <|begin_of_solution|> {final formatted, "
    "precise, and clear solution} <|end_of_solution|> Now, try to solve the following question through the above guidelines:"
)

class ClientError(RuntimeError):
    pass

def get_content(query, base_url, model_name):
    API_KEY = os.environ.get("OPENAI_API_KEY", "EMPTY")
    API_REQUEST_TIMEOUT = int(os.getenv('OPENAI_API_REQUEST_TIMEOUT', '99999'))
    
    if IS_OPENAI_V1:
        import httpx
        client = openai.OpenAI(
            api_key=API_KEY,
            base_url=base_url,
            timeout=httpx.Timeout(API_REQUEST_TIMEOUT),
        )
        call_func = client.chat.completions.create
        call_args = {
            'model': model_name,
            'messages': [{'role': 'system', 'content': SYNTHIA_SYS_PROMPT}, {'role': 'user', 'content': query}],
            'temperature': 1.0,
            'top_p': 0.95,
            'repetition_penalty': 1.3,
            'min_p': 0.0,
            'max_tokens': 16384,
            'top_k': 64,
            'timeout': API_REQUEST_TIMEOUT,
        }
    else:
        call_func = openai.ChatCompletion.create
        call_args = {
            'model': model_name,
            'messages': [{'role': 'system', 'content': SYNTHIA_SYS_PROMPT}, {'role': 'user', 'content': query}],
            'temperature': 1.0,
            'top_p': 0.95,
            'repetition_penalty': 1.3,
            'min_p': 0.0,
            'max_tokens': 16384,
            'top_k': 64,
            'api_key': API_KEY,
            'api_base': base_url,
            'request_timeout': API_REQUEST_TIMEOUT,
        }
    
    try:
        completion = call_func(**call_args)
        return completion.choices[0].message.content
    except AttributeError as e:
        err_msg = getattr(completion, "message", "")
        time.sleep(random.randint(25, 35))
        raise ClientError(err_msg) from e
    except (APIConnectionError, RateLimitError) as e:
        err_msg = e.message if IS_OPENAI_V1 else e.user_message
        time.sleep(random.randint(25, 35))
        raise ClientError(err_msg) from e
    except APIError as e:
        err_msg = e.message if IS_OPENAI_V1 else e.user_message
        if "maximum context length" in err_msg:
            logging.warning(f"max length exceeded. Error: {err_msg}")
            return {'gen': "", 'end_reason': "max length exceeded"}
        time.sleep(1)
        raise ClientError(err_msg) from e

if __name__ == "__main__":
    conversation_history = []
    user_input = "Hello!"
    try:
        response = get_content(user_input, "http://127.0.0.1:8030/v1", "Tesslate/Synthia-S1-27b")
        print(f"Response: {response}")
    except ClientError as e:
        print(f"Client Error: {e}")
