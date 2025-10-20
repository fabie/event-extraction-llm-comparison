# save as ollama_event_extratyion.py
#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

""" 
Script Name: “ollama_event_extratyion.py" 
Author: Fabienne Van Cappel 
Email: fabienne.vancappel@gmail.com 
Date: 2025
 
"""


# Create the script
"""
EVENT EXTRACTION USING OLLAMA MIXTRAL on M3 Max (local machine)
"""

import requests
import json
import pandas as pd
import time

# Extract event info using "local" Mixtral model
def extract_event_with_ollama(text):
    
    prompt = f"""Extract event information from the following text.
    Return ONLY a JSON object with these exact fields:
    {{"event": "name of event or empty string", "venue": "location or empty string", "datetime": "date/time or empty string"}}
    
    Text: {text}
    
    JSON:"""
    
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'mixtral',
            'prompt': prompt,
            'stream': False,
            'temperature': 0.1
        }
    )
    
    try:
        result = response.json()['response']
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*?\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    
    return {"event": "", "venue": "", "datetime": ""}

# Test cases
test_texts = [
    "Concert at Red Rocks on Friday at 7pm",
    "Denver Jazz Festival this weekend at City Park",
    "I Love R&B Party at Your Mom's House Denver",
    "Mixtape Saturdays Live Music @ Punch Bowl Social",
    "Comedy show tonight at Comedy Works Downtown"
]

print("="*60)
print("OLLAMA MIXTRAL EVENT EXTRACTION TEST")
print("="*60)

for text in test_texts:
    print(f"\nText: {text}")
    start = time.time()
    result = extract_event_with_ollama(text)
    elapsed = time.time() - start
    
    print(f"  Event:    '{result.get('event', '')}'")
    print(f"  Venue:    '{result.get('venue', '')}'")
    print(f"  DateTime: '{result.get('datetime', '')}'")
    print(f"  Time:     {elapsed:.1f}s")

print("\n" + "="*60)
print("✅ Ollama extraction test complete!")

# script
# EOF
# Run it
# python3 ollama_event_extraction.py
