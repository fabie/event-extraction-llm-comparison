
# Save as gemini_comparison_test.py
!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

""" 

Script Name: “gemini_comparison_test.py" 
Author: Fabienne Van Cappel 
Email: fabienne.vancappel@gmail.com 
Date: 2025
 
""" 


import google.generativeai as genai
import pandas as pd
import json
import time
import os

# Test Google Gemini for comparison
class GeminiEventExtractor:
    
    
    def __init__(self, api_key=None):
        
        # Get free key at: https://makersuite.google.com/app/apikey
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Get free API key at: https://makersuite.google.com/app/apikey")
            self.api_key = input("Enter Gemini API key: ").strip()
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    # Extract using Gemini
    def extract_with_gemini(self, text):
        
        prompt = f"""Extract event information from this text.
Return ONLY a JSON object: {{"event": "name", "venue": "location", "datetime": "date/time"}}
Use empty string if not found.

Text: {text}

JSON:"""
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Remove markdown if present
            result = result.replace("```json", "").replace("```", "").strip()
            
            return json.loads(result)
        except Exception as e:
            print(f"Error: {e}")
            return {"event": "", "venue": "", "datetime": ""}
    
    # Test on sample
    def test_on_sample(self, sample_size=10):
        
        print("="*70)
        print("GEMINI COMPARISON TEST (FREE)")
        print("="*70)
        
        df = pd.read_csv('gold_standard_200_events.csv')
        good_df = df[~df['raw_description'].str.startswith('Action Navigation')]
        
        print(f"\nTesting Gemini Pro on {sample_size} examples...")
        print("Cost: $0.00 (Free tier)")
        
        correct = 0
        total = 0
        
        for idx, row in good_df.head(sample_size).iterrows():
            text = row['raw_description']
            expected = row['verified_event_name']
            
            if pd.isna(expected):
                continue
            
            print(f"\n{total+1}. Testing...")
            extracted = self.extract_with_gemini(text)
            
            print(f"   Text: {text[:60]}...")
            print(f"   Extracted: {extracted.get('event', '')}")
            print(f"   Expected: {expected}")
            
            # Check accuracy
            if extracted.get('event'):
                if any(word.lower() in expected.lower() for word in extracted['event'].split() if len(word) > 3):
                    correct += 1
                    print("   ✅ Correct!")
                else:
                    print("   ❌ Wrong")
            else:
                print("   ❌ No extraction")
            
            total += 1
            time.sleep(1)  # Rate limiting
        
        # Results
        print("\n" + "="*70)
        print("FINAL COMPARISON")
        print("-"*70)
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print(f"\nGoogle Gemini Pro (Cloud /  Free):")
        print(f"  Accuracy: {correct}/{total} = {accuracy:.1f}%")
        print(f"  Cost: $0.00")
        
        print(f"\nYour Hybrid (Local Mixtral):")
        print(f"  Accuracy: 18/20 = 90%")
        print(f"  Cost: $0.00")
        
        print(f"\nOpenAI GPT-3.5 (Cloud, Paid):")
        print(f"  Expected: ~85-90%")
        print(f"  Cost: ~$60/month for 1000 events/day")

# First install the library
print("Install Google Generative AI:")
print("pip install google-generativeai")
print("\nThen get free API key at:")
print("https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    
    # Check if library is installed
    try:
        import google.generativeai
        extractor = GeminiEventExtractor()
        extractor.test_on_sample(10)
    except ImportError:
        print("\n❌ Run: pip install google-generativeai")


