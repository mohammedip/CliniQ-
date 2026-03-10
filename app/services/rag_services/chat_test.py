import requests
import json

def ask_bot():
    base_url = "http://localhost:8000"
    
    print("--- CliniQ Chatbot (Type 'exit' to quit) ---")
    
    while True:
        question = input("\nYou: ")
        if question.lower() == 'exit':
            break
        
        if not question.strip():
            continue
            
        try:
            # Send question to /queries/ask endpoint with JSON body (no auth)
            url = f"{base_url}/queries/ask"
            payload = {
                "question": question,
                "top_k": 5
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nBot: {data.get('answer', 'No answer provided')}")
                if data.get('sources'):
                    print(f"Sources: {data['sources']}")
                
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    ask_bot()