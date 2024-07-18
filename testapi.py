# test_api_engine.py
from core.api_engine import APIEngine

def test_api_engine():
    api_engine = APIEngine(engine='openai')  # Adjust the engine as needed
    prompt = {
        "messages": [
            {"role": "user", "content": "Tell me a very random fact, and create a joke about that fact please."}
        ],
        "temperature": 0.8,
        "max_tokens": 100,
        "top_p": 0.9
    }
    response = api_engine.call_api(prompt)
    print(response)

if __name__ == "__main__":
    test_api_engine()
