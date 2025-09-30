#!/usr/bin/env python3

import os
import sys
sys.path.append('./backend')

# Simulate what happens in chat.py
def test_path_resolution():
    print("Testing path resolution...")
    
    # This is what happens in chat.py
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"current_dir (from test script): {current_dir}")
    
    # This is the actual location
    document_id = 'eab39c08-0c87-461e-a232-b5975c91efbf'
    mock_file_calculated = os.path.join(current_dir, "data", "mock_embeddings", f"doc_{document_id}.json")
    print(f"Calculated mock file path: {mock_file_calculated}")
    print(f"File exists: {os.path.exists(mock_file_calculated)}")
    
    # The actual file location
    actual_mock_file = f"./backend/data/mock_embeddings/doc_{document_id}.json"
    print(f"Actual mock file path: {actual_mock_file}")
    print(f"Actual file exists: {os.path.exists(actual_mock_file)}")
    
    # What would chat.py see?
    # Simulate being in backend/app/chat.py
    chat_file_path = "./backend/app/chat.py"
    if os.path.exists(chat_file_path):
        chat_dir = os.path.dirname(os.path.dirname(os.path.abspath(chat_file_path)))
        print(f"chat.py directory calculation: {chat_dir}")
        chat_mock_file = os.path.join(chat_dir, "data", "mock_embeddings", f"doc_{document_id}.json")
        print(f"chat.py mock file path: {chat_mock_file}")
        print(f"chat.py file exists: {os.path.exists(chat_mock_file)}")
    
    # List all files in mock_embeddings
    mock_dir = "./backend/data/mock_embeddings"
    if os.path.exists(mock_dir):
        files = os.listdir(mock_dir)
        print(f"\nFiles in mock_embeddings directory: {files}")

if __name__ == "__main__":
    test_path_resolution()