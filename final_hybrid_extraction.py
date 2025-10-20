# save as final_hybrid_extraction.py
#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

# COPYRIGHTED

"""
Event Extraction from Reddit Posts - Capstone Project
Copyright (c) 12 OCT  2025 [Fabienne Van Cappel]. All Rights Reserved.

This code is part of a graduate thesis project and is protected by copyright.
Unauthorized use, reproduction, or distribution is prohibited without 
written permission from the author.

For licensing inquiries, contact: [fabienne.vancappel@gmail.com)]
"""

import pandas as pd
import requests
import json
import re
import time

# Combines Ollama with pattern matching for better accuracy
class HybridEventExtractor:
    
    def __init__(self):
        self.event_patterns = [
            r'([A-Z][A-Za-z\s]+(?:Festival|Concert|Show|Game|Match|Performance|Conference|Gala))',
            r'([A-Z][A-Za-z\s]+)\s+at\s+[A-Z]',
            r'([A-Z][A-Za-z\s]+)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
        ]
        
        self.venue_patterns = [
            r'at\s+([A-Z][A-Za-z\s]+?)(?:\s*,|\s+on|\s+this|\s+from|$)',
            r'@\s+([A-Z][A-Za-z\s]+?)(?:\s*,|\s+on|\s+this|$)',
            r'(?:Stadium|Arena|Center|Theatre|Theater|Park|Hall|Club)\b',
        ]
    
    #Fallback pattern-based extraction
    def extract_with_patterns(self, text):
        result = {"event": "", "venue": "", "datetime": ""}
        
        # Find EVENTS
        for pattern in self.event_patterns:
            match = re.search(pattern, text)
            if match:
                result["event"] = match.group(1).strip()
                break
        
        # Find VENUES
        for pattern in self.venue_patterns[:2]:
            match = re.search(pattern, text)
            if match:
                result["venue"] = match.group(1).strip()
                break
        
        # Find DATETIMES
        date_pattern = r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,\s]+[A-Za-z]+\s+\d{1,2}[,\s]+\d{4}'
        match = re.search(date_pattern, text)
        if match:
            result["datetime"] = match.group(0)
        
        return result
    
    # Ollama extraction with better prompting
    def extract_with_ollama(self, text):
        
        # Skip if text is too short or starts with "Action Navigation"
        if len(text) < 20 or text.startswith("Action Navigation"):
            return self.extract_with_patterns(text)
        
        prompt = f"""You are extracting event information. 
Look for: concerts, festivals, sports games, shows, conferences, or any events.

Text: "{text}"

Extract and return ONLY a JSON object:
{{"event": "event name here", "venue": "location here", "datetime": "date/time here"}}

If something is not found, use empty string "". Be specific and accurate."""
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={'model': 'mixtral', 'prompt': prompt, 'stream': False, 'temperature': 0},
                timeout=10
            )
            
            result = response.json()['response']
            json_match = re.search(r'\{[^{}]*\}', result)
            if json_match:
                extracted = json.loads(json_match.group())
                
                # Validate extraction
                if extracted.get("event") and len(extracted["event"]) > 2:
                    return extracted
        except:
            pass
        
        #Fall back to patterns if Ollama fails
        return self.extract_with_patterns(text)
    
    # MAIN EXTRACTION METHOD
    def extract(self, text):
        
        # Try Ollama first
        result = self.extract_with_ollama(text)
        
        # If Ollama didn't find event, try patterns
        if not result.get("event"):
            pattern_result = self.extract_with_patterns(text)
            if pattern_result.get("event"):
                result = pattern_result
        
        return result

# EVALUATE HYBRID METHOD
def evaluate_hybrid():
    print("="*70)
    print("HYBRID EXTRACTION EVALUATION")
    print("="*70)
    
    df = pd.read_csv('gold_standard_200_events.csv')
    extractor = HybridEventExtractor()
    
    # Filter to good examples (not Action Navigation)
    good_df = df[~df['raw_description'].str.startswith('Action Navigation')]
    print(f"Testing on {len(good_df)} non-corrupted events")
    
    correct = 0
    total = 0
    
    for idx, row in good_df.head(20).iterrows():
        text = row['raw_description']
        expected_event = row['verified_event_name']
        
        if pd.isna(expected_event):
            continue
        
        extracted = extractor.extract(text)
        
        print(f"\n{total+1}. Text: {text[:80]}...")
        print(f"   Expected: {expected_event}")
        print(f"   Extracted: {extracted.get('event', 'NONE')}")
        
        if extracted.get('event'):
            
            # More merciful matching
            extracted_clean = extracted['event'].lower()
            expected_clean = expected_event.lower()
            
            # Check if key words match
            extracted_words = set(extracted_clean.split())
            expected_words = set(expected_clean.split())
            
            common_words = extracted_words & expected_words
            if len(common_words) >= 1 and any(len(w) > 3 for w in common_words):
                correct += 1
                print("   ✅ Match!")
            else:
                print("   ❌ No match")
        else:
            print("   ❌ Nothing extracted")
        
        total += 1
    
    print(f"\n" + "="*70)
    print(f"Hybrid Accuracy: {correct}/{total} = {correct/total*100:.1f}%")
    
    # Test on the problematic "Action Navigation" ones with patterns only
    action_nav_df = df[df['raw_description'].str.startswith('Action Navigation')]
    if len(action_nav_df) > 0:
        print(f"\nTesting pattern extraction on {len(action_nav_df)} 'Action Navigation' events...")
        
        for idx, row in action_nav_df.head(3).iterrows():
            text = row['raw_description']
            expected = row['verified_event_name']
            
            # Extract datetime which (usually present)
            date_match = re.search(r'[A-Z][a-z]+day,\s+[A-Z][a-z]+\s+\d+,\s+\d{4}', text)
            time_match = re.search(r'\d{1,2}:\d{2}\s*[AP]M', text)
            
            print(f"\nText: {text[:100]}...")
            print(f"Expected event: {expected}")
            if date_match:
                print(f"Found date: {date_match.group()}")
            if time_match:
                print(f"Found time: {time_match.group()}")

evaluate_hybrid()

