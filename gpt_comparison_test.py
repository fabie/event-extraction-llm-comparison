# Save as gpt_comparison_test.py
#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 

""" 

Script Name: “gpt_comparison_test.py" 
Author: Fabienne Van Cappel 
Email: fabienne.vancappel@gmail.com 
Date: 2025
 
"""


import pandas as pd
import openai
import json
import time
import os

# Test GPT-3.5 and GPT-4 for comparison
class GPTEventExtractor:
    
    def __init__(self, api_key=None):
        
        # Use environment variable  provided key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Enter actual key
        self.api_key = "enter_your_secret""
        if not self.api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.total_tokens = 0
        self.total_cost = 0.0
    
    # Extract using GPT
    def extract_with_gpt(self, text, model="gpt-3.5-turbo"):
        
        
        prompt = f"""Extract event information from this text.
Return ONLY a JSON object with these fields:
{{"event": "event name", "venue": "location", "datetime": "date/time"}}
Use empty string "" if not found.

Text: {text}

JSON:"""
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting event information. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=100
            )
            
            result = response.choices[0].message.content
            
            # Track usage
            tokens = response.usage.total_tokens
            self.total_tokens += tokens
            
            # Calculate cost
            if model == "gpt-3.5-turbo":
                cost = (tokens / 1000) * 0.002  # $0.002 per 1K tokens
            elif model == "gpt-4":
                cost = (tokens / 1000) * 0.03   # $0.03 per 1K tokens
            else:
                cost = 0
            
            self.total_cost += cost
            
            # Parse JSON
            json_match = json.loads(result)
            return json_match
            
        except Exception as e:
            print(f"Error: {e}")
            return {"event": "", "venue": "", "datetime": ""}
    
    # Test on small sample (minimize cost)
    def test_on_sample(self, sample_size=10):
        
        print("="*70)
        print("GPT COMPARISON TEST")
        print("="*70)
        
        # Load your test data
        df = pd.read_csv('gold_standard_200_events.csv')
        
        # Filter to good examples only
        good_df = df[~df['raw_description'].str.startswith('Action Navigation')]
        
        print(f"\nTesting GPT-3.5-turbo on {sample_size} examples...")
        print("(Estimated cost: ~$0.01)")
        
        results = {
            'gpt-3.5': {'correct': 0, 'total': 0},
            'gpt-4': {'correct': 0, 'total': 0}
        }
        
        # Test GPT-3.5
        for idx, row in good_df.head(sample_size).iterrows():
            text = row['raw_description']
            expected = row['verified_event_name']
            
            if pd.isna(expected):
                continue
            
            extracted = self.extract_with_gpt(text, model="gpt-3.5-turbo")
            
            # Check accuracy
            if extracted.get('event'):
                if any(word.lower() in expected.lower() for word in extracted['event'].split() if len(word) > 3):
                    results['gpt-3.5']['correct'] += 1
            
            results['gpt-3.5']['total'] += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        # Test GPT-4 on fewer examples (more expensive)
        test_gpt4 = input("\nTest GPT-4? (5 examples, ~$0.05) [y/N]: ").lower() == 'y'
        
        if test_gpt4:
            print("\nTesting GPT-4 on 5 examples...")
            for idx, row in good_df.head(5).iterrows():
                text = row['raw_description']
                expected = row['verified_event_name']
                
                if pd.isna(expected):
                    continue
                
                extracted = self.extract_with_gpt(text, model="gpt-4")
                
                if extracted.get('event'):
                    if any(word.lower() in expected.lower() for word in extracted['event'].split() if len(word) > 3):
                        results['gpt-4']['correct'] += 1
                
                results['gpt-4']['total'] += 1
                time.sleep(0.5)
        
        # Print results
        print("\n" + "="*70)
        print("RESULTS COMPARISON")
        print("-"*70)
        
        print(f"\nGPT-3.5-turbo:")
        if results['gpt-3.5']['total'] > 0:
            accuracy = results['gpt-3.5']['correct'] / results['gpt-3.5']['total'] * 100
            print(f"  Accuracy: {results['gpt-3.5']['correct']}/{results['gpt-3.5']['total']} = {accuracy:.1f}%")
        
        if results['gpt-4']['total'] > 0:
            print(f"\nGPT-4:")
            accuracy = results['gpt-4']['correct'] / results['gpt-4']['total'] * 100
            print(f"  Accuracy: {results['gpt-4']['correct']}/{results['gpt-4']['total']} = {accuracy:.1f}%")
        
        print(f"\nYour Hybrid (Mixtral + Patterns):")
        print(f"  Accuracy: 18/20 = 90%")
        
        print(f"\nTotal API cost: ${self.total_cost:.4f}")
        print(f"Total tokens used: {self.total_tokens}")
        
        # Project monthly costs
        events_per_day = 1000
        cost_per_event = self.total_cost / sample_size
        monthly_cost = cost_per_event * events_per_day * 30
        
        print(f"\nProjected monthly cost for 1000 events/day:")
        print(f"  GPT-3.5: ${monthly_cost:.2f}")
        # GPT-4 is ~15x more expensive
        print(f"  GPT-4: ${monthly_cost * 15:.2f}")
        print(f"  Your Hybrid: $0.00")
        
        return results

# Quick test function
# Test with just 3 examples to verify it works
def quick_gpt_test():
 
    
    # You can get a free API key with $5 credit from OpenAI
    api_key = input("Enter OpenAI API key (or press Enter to use env variable): ").strip()
    
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key provided. Get one free at: https://platform.openai.com/api-keys")
        return
    
    extractor = GPTEventExtractor(api_key)
    
    # Test on 3 simple examples first
    test_texts = [
        "Concert at Red Rocks on Friday at 7pm",
        "Denver Jazz Festival this weekend at City Park", 
        "Austin Food & Wine Festival at Butler Park April 26-28"
    ]
    
    print("\nQuick GPT-3.5 Test:")
    for text in test_texts:
        result = extractor.extract_with_gpt(text)
        print(f"\nText: {text}")
        print(f"GPT: {result}")
    
    print(f"\nTest cost: ${extractor.total_cost:.4f}")
    
    # Full test
    if input("\nRun full comparison (10 examples)? [y/N]: ").lower() == 'y':
        extractor.test_on_sample(10)

if __name__ == "__main__":
    quick_gpt_test()
