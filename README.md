# Event Extraction from Social Media Posts

A comprehensive comparison of Large Language Model approaches for extracting structured event information (event name, venue, datetime) from Reddit posts about local events in Denver, Austin, and Daytona Beach.

## 🎯 Project Overview

This graduate thesis project evaluates multiple LLM-based approaches for automated event extraction:
- **Local Mixtral** (via Ollama) + Pattern Matching Hybrid
- **OpenAI GPT-3.5-turbo** (Cloud API)
- **Google Gemini Pro** (Cloud API)

**Best Result**: Hybrid approach achieved **90% accuracy** with zero API costs using local Mixtral inference combined with regex patterns.

## Key Findings

| Approach | Accuracy | Cost | Speed |
|----------|----------|------|-------|
| Hybrid (Mixtral + Patterns) | 90% | $0 | ~2-3s/extraction |
| GPT-3.5-turbo | N/A | ~$60/month @ 1k/day | Fast |
| Gemini Pro | N/A | $0 (free tier) | Moderate |

*Estimated based on limited testing

## Architecture

### Hybrid Extraction Pipeline
```python
1. Ollama/Mixtral attempts structured extraction
2. If confidence low → fallback to regex patterns
3. Validate and return structured JSON
```

### Pattern Matching (Fallback)
- Event name: Capitalized phrases + keywords (Festival, Concert, Show, etc.)
- Venue: "at [Location]" or "@[Location]" patterns
- DateTime: Day names + date formats

## Project Structure
```
event-extraction-llm-comparison/
├── **final_hybrid_extraction.py**      # Main hybrid approach (RECOMMENDED)
├── **ollama_event_extraction.py**      # Pure Mixtral extraction
├── **gpt_comparison_test.py**          # OpenAI GPT testing
├── **gemini_comparison_test.py**       # Google Gemini testing
├── debug_ollama.py                 # Mixtral debugging utilities
├── debug_gemini.py                 # Gemini debugging utilities
├── test_openai.py                  # OpenAI API testing
├── **spacy_training_data.json**        # Training examples for NER
└── gold_standard_200_events.csv    # Ground truth dataset (NOT INCLUDED)
```

## Quick Start

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Mixtral model
ollama pull mixtral

# Install Python dependencies
pip install pandas requests google-generativeai openai
```

### Run Hybrid Extraction
```bash
python final_hybrid_extraction.py
```

### Test Individual Models
```bash
# Test Ollama/Mixtral
python ollama_event_extraction.py

# Test OpenAI (requires API key)
python gpt_comparison_test.py

# Test Gemini (requires API key)
python gemini_comparison_test.py
```

## Usage Examples

### Hybrid Extraction
```python
from final_hybrid_extraction import HybridEventExtractor

extractor = HybridEventExtractor()
text = "Concert at Red Rocks on Friday at 7pm"

result = extractor.extract(text)
print(result)
# {'event': 'Concert', 'venue': 'Red Rocks', 'datetime': 'Friday at 7pm'}
```

### OpenAI Extraction
```python
from gpt_comparison_test import GPTEventExtractor

extractor = GPTEventExtractor(api_key="your-key")
result = extractor.extract_with_gpt(text)
```

## Dataset

The evaluation uses 200 manually verified event posts from:
- **Denver** (r/Denver)
- **Austin** (r/Austin)  
- **Daytona Beach** (r/DaytonaBeach)

**Note**: `gold_standard_200_events.csv` is not included in this repository due to privacy/copyright concerns. The file should contain:
- `raw_description`: Original post text
- `verified_event_name`: Ground truth event name
- `verified_venue`: Ground truth venue (optional)
- `datetime`: Ground truth date/time (optional)

## Configuration

### Ollama Settings
- **Model**: mixtral
- **Temperature**: 0 (deterministic)
- **Timeout**: 10s per request

### OpenAI Settings (if testing)
- **Model**: gpt-3.5-turbo
- **Temperature**: 0
- **Max tokens**: 100

### Gemini Settings (if testing)
- **Model**: gemini-1.5-flash (updated from deprecated gemini-pro)
- **Temperature**: 0

## Troubleshooting

### Common Issues

**Ollama not responding**
```bash
# Check Ollama is running
ollama list

# Restart if needed
ollama serve
```

**"Action Navigation" false positives**
- These are scraped artifacts, not real events
- Hybrid approach filters these automatically

**API rate limits**
- Gemini: Free tier has rate limits
- OpenAI: Monitor usage to avoid charges
- Mixtral: No limits (local inference)

## Performance Optimization

1. **Batch Processing**: Process multiple texts in parallel
2. **Caching**: Store Mixtral results to avoid re-inference
3. **Pattern Priority**: Check simple patterns before LLM inference
4. **Timeout Handling**: Set reasonable timeouts for API calls

## Evaluation Methodology

Accuracy calculated as:
```
Correct = (extracted event overlaps with verified event) 
        OR (key words match)
Accuracy = Correct / Total × 100%
```

## Important Notes

### Copyright & Ethics
- This code is part of a graduate thesis project
- Training data scraped from public Reddit posts
- **Never reproduce copyrighted event descriptions verbatim**
- Use for academic/research purposes only

### API Costs
- **OpenAI**: ~$0.002 per 1K tokens
- **Gemini**: Free tier with limits
- **Mixtral**: Free (local)

### Known Limitations
- Mixtral requires 16GB+ RAM
- Abbreviations and slang can confuse models
- Multi-event posts may extract only first event
- Date parsing is basic (no full NLP datetime resolution)

## Citation

If you use this work, please cite:
```
Fabienne Van Cappel (2025). Event Extraction from Social Media Posts: 
A Comparative Analysis of LLM Approaches. Graduate Thesis.
```

## Contact

**Author**: Fabienne Van Cappel  
**Email**: fabienne.vancappel@gmail.com  
**Year**: 2025

## License

Copyright © 2025 Fabienne Van Cappel. All Rights Reserved.

This code is part of a graduate thesis project. Unauthorized use, reproduction, or distribution is prohibited without written permission from the author.

For licensing inquiries, contact: fabienne.vancappel@gmail.com

## Acknowledgments

- **Ollama** for local LLM inference
- **OpenAI** for GPT API access
- **Google** for Gemini API access
- Reddit communities for event data
