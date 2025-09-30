import requests
import json

# Test with a real document ID from the uploads
headers = {
    'Authorization': 'Bearer dev-token',
    'Content-Type': 'application/json'
}

# Use a document ID that we know exists
data = {
    'text': 'What is this document about? Can you summarize the main topic?',
    'document_id': 'eab39c08-0c87-461e-a232-b5975c91efbf'
}

print('Testing chat with real document ID...')
print(f'Document ID: {data["document_id"]}')
print(f'Question: {data["text"]}')

try:
    response = requests.post('http://127.0.0.1:8000/api/chat/query', 
                           json=data, 
                           headers=headers, 
                           timeout=30)
    
    print(f'\nStatus: {response.status_code}')
    
    if response.status_code == 200:
        response_data = response.json()
        print(f'\nAI Response:')
        print(response_data['response'])
        
        if response_data.get('sources'):
            print(f'\nSources found: {len(response_data["sources"])}')
            for i, source in enumerate(response_data['sources'][:2]):
                print(f'Source {i+1}: {source}')
        else:
            print('\nNo sources returned')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Error: {e}')