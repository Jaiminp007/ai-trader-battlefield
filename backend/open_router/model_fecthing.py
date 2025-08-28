import os
import requests
import json
from dotenv import load_dotenv
import time

# Load environment variables from a .env file
load_dotenv()

# --- 1. Configuration ---
AGENTS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'ai_agents.json')
API_KEY = os.getenv('OPENROUTER_API_KEY')
CHAT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
TEST_PROMPT = "Hello"
NUM_AGENTS_TO_SELECT = 6

# --- 2. Core Functions ---

def load_all_models(json_path):
    """Loads and cleans all model IDs from the specified JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        model_ids = [model.replace(':free', '') for models in data.values() for model in models]
        print(f"✅ Found {len(model_ids)} models in '{os.path.basename(json_path)}'.")
        return model_ids
    except FileNotFoundError:
        print(f"❌ Error: The file at '{json_path}' was not found.")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error: The file at '{json_path}' is not a valid JSON file.")
        return []

def select_models_for_testing(all_models):
    """Prompts the user to select a specific number of models for testing."""
    print("\n--- Please Select Models to Test ---")
    for i, model in enumerate(all_models):
        print(f"  {i + 1}: {model}")
    while True:
        try:
            prompt = f"\nEnter the numbers for the {NUM_AGENTS_TO_SELECT} models you want to test (e.g., 1 5 8 10 12 13): "
            user_input = input(prompt)
            selected_indices = [int(n.strip()) for n in user_input.replace(',', ' ').split() if n.strip()]

            if len(selected_indices) != NUM_AGENTS_TO_SELECT:
                print(f"❌ Error: Please select exactly {NUM_AGENTS_TO_SELECT} models. You selected {len(selected_indices)}.")
                continue
            if len(set(selected_indices)) != NUM_AGENTS_TO_SELECT:
                 print(f"❌ Error: Please select {NUM_AGENTS_TO_SELECT} unique models. You entered duplicate numbers.")
                 continue

            selected_models = [all_models[index - 1] for index in selected_indices if 1 <= index <= len(all_models)]
            if len(selected_models) != NUM_AGENTS_TO_SELECT:
                print(f"❌ Error: One or more of your selected numbers were out of range.")
                continue
            
            print("\n✅ You have selected the following models for testing and generation:")
            for model in selected_models:
                print(f"  - {model}")
            return selected_models
        except (ValueError, IndexError):
            print("❌ Error: Invalid input. Please enter valid numbers separated by spaces or commas.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

def run_model_test(model_id):
    """Sends the TEST_PROMPT to a specific model and returns its response."""
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": model_id, "messages": [{"role": "user", "content": TEST_PROMPT}]}
    try:
        response = requests.post(CHAT_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()
        return f"✅ SUCCESS\n   Response: {content}"
    except requests.exceptions.RequestException as e:
        return f"❌ FAILED\n   Error: {e}"
    except (KeyError, IndexError):
        return f"❌ FAILED\n   Error: Could not parse a valid response."

def get_models_to_use():
    """
    Main orchestration function for this module. Loads, tests, and returns the
    list of validated models.
    :return: A list of model ID strings, or None if the process fails.
    """
    if not API_KEY:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file.")
        return None

    all_models = load_all_models(AGENTS_JSON_PATH)
    if not all_models:
        return None
        
    models_to_test = select_models_for_testing(all_models)
    if not models_to_test:
        return None
    
    print("\n--- Running Initial Model Tests ---")
    for model in models_to_test:
        print("\n" + "="*50 + f"\nTesting model: {model}\n" + "="*50)
        result = run_model_test(model)
        time.sleep(1)
        print(result)
    
    print("\n--- Model testing complete. ---")
    return models_to_test

if __name__ == "__main__":
    print("--- Running Model Fetching and Testing Standalone ---")
    selected_models = get_models_to_use()
    if selected_models:
        print(f"\n✅ Standalone test complete. The following models were selected: {selected_models}")
    else:
        print("\n--- Standalone test concluded with no models selected. ---")