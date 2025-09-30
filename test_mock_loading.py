import os
import json

# Test if we can load the mock embeddings directly
document_id = 'eab39c08-0c87-461e-a232-b5975c91efbf'
mock_file = f"./backend/data/mock_embeddings/doc_{document_id}.json"

print(f"Testing mock embeddings loading...")
print(f"Looking for file: {mock_file}")
print(f"File exists: {os.path.exists(mock_file)}")

if os.path.exists(mock_file):
    with open(mock_file, 'r', encoding='utf-8') as f:
        mock_data = json.load(f)
    
    print(f"Document ID: {mock_data['document_id']}")
    print(f"Number of chunks: {len(mock_data['chunks'])}")
    print(f"First chunk preview: {mock_data['chunks'][0][:200]}...")
    
    # Test keyword matching
    question = "What is this document about? Can you summarize the main topic?"
    question_words = question.lower().split()
    
    print(f"\nTesting keyword matching...")
    print(f"Question words: {question_words}")
    
    relevant_chunks = []
    for i, chunk in enumerate(mock_data['chunks']):
        chunk_words = chunk.lower().split()
        matches = sum(1 for word in question_words if word in chunk_words)
        if matches > 0:
            relevant_chunks.append((chunk, matches))
            print(f"Chunk {i}: {matches} matches")
    
    print(f"Found {len(relevant_chunks)} chunks with matches")
    
    if relevant_chunks:
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunk = relevant_chunks[0]
        print(f"Top matching chunk: {top_chunk[0][:200]}...")
    else:
        print("No keyword matches - would use fallback chunks")
        print(f"Fallback chunk 0: {mock_data['chunks'][0][:200]}...")
        
else:
    print("Mock embeddings file not found!")
    mock_dir = "./backend/data/mock_embeddings"
    if os.path.exists(mock_dir):
        files = os.listdir(mock_dir)
        print(f"Available files: {files}")
    else:
        print("Mock embeddings directory doesn't exist!")