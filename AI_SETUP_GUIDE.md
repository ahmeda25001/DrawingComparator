# AI-Powered Drawing Comparison Setup Guide

## Overview
Your Drawing Comparator now supports intelligent semantic comparison using OpenAI's GPT models. This provides much more accurate similarity assessment compared to basic text matching.

## Key Improvements

### Before (Basic Text Comparison):
- Simple character-by-character text matching
- No understanding of technical context
- Can't recognize equivalent expressions
- Example: "W14x30" vs "W14 x 30" = low similarity

### After (AI Semantic Comparison):
- Understands engineering terminology and context
- Recognizes equivalent expressions
- Provides detailed technical analysis
- Example: "W14x30 beam" vs "W14 x 30 steel beam" = high similarity

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-`)

### 2. Set Environment Variable

#### For Local Development:
```bash
# Add to your .env file or export in terminal
export OPENAI_API_KEY="sk-your-api-key-here"
```

#### For Vercel Deployment:
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add new variable:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-your-api-key-here`
   - Environment: Production (and Preview if needed)

#### For Other Hosting Platforms:
- **Google Cloud Run**: `gcloud run services update --set-env-vars OPENAI_API_KEY=sk-your-key`
- **Railway**: Add in environment variables section
- **Heroku**: `heroku config:set OPENAI_API_KEY=sk-your-key`

### 3. Configure AI Settings (Optional)

Edit `config.py` to customize AI behavior:

```python
# AI Comparison Settings
USE_AI_COMPARISON = True          # Enable/disable AI
OPENAI_MODEL = "gpt-4"           # Primary model
AI_FALLBACK_MODEL = "gpt-3.5-turbo"  # Fallback model
AI_TEMPERATURE = 0.1             # Consistency (lower = more consistent)
AI_MAX_TOKENS = 2000             # Response length limit
```

## How It Works

### 1. Text Extraction
- Google Vision API extracts text from drawings
- Same as before - no changes needed

### 2. AI Analysis
- Extracted text is sent to OpenAI GPT model
- AI analyzes content in engineering context
- Returns similarity score with reasoning

### 3. Fallback Safety
- If AI fails, automatically falls back to basic comparison
- No interruption to user experience
- Error is logged for debugging

## Features

### Intelligent Similarity Scoring
- **Context-aware**: Understands "W14x30" = "W14 x 30" = "14x30 wide flange"
- **Technical focus**: Weights structural elements more heavily
- **Material recognition**: Knows steel, concrete, wood properties

### Category Analysis
Breaks down similarity by:
- Structural Elements (beams, columns, foundations)
- Dimensions and Measurements
- Materials and Specifications
- Annotations and Labels
- Symbols and Notations
- Layout and Arrangement
- Technical Details
- Calculations and Values

### Detailed Technical Analysis
- **Major Differences**: Significant structural changes
- **Critical Discrepancies**: Safety or code issues
- **Common Elements**: Shared design features
- **Minor Differences**: Non-critical variations

### AI Reasoning
- Explains why drawings are similar/different
- Provides engineering context
- Helps users understand the comparison

## Testing the AI Comparison

### 1. Run Test Script
```bash
cd "/path/to/your/project"
python test_ai_comparison.py
```

### 2. Test with Sample Data
```bash
# Test category analysis
python test_ai_comparison.py --demo-categories
```

### 3. Check AI Status
Visit `/file-limits` endpoint to see if AI is enabled:
```json
{
  "ai_comparison_enabled": true,
  "ai_model": "gpt-4"
}
```

## Cost Considerations

### OpenAI Pricing (as of 2024):
- **GPT-4**: ~$0.03 per 1K tokens (input) + $0.06 per 1K tokens (output)
- **GPT-3.5-turbo**: ~$0.0015 per 1K tokens (much cheaper)

### Typical Usage:
- Average comparison: ~1,000 tokens = $0.03-0.05 per comparison
- Monthly cost for 100 comparisons: ~$3-5

### Cost Optimization:
1. Use GPT-3.5-turbo for routine comparisons
2. Use GPT-4 for critical analyses
3. Set usage limits in OpenAI dashboard
4. Monitor usage in OpenAI account

## Error Handling

### Common Issues:

1. **"AI comparison failed"**
   - Check API key is correct
   - Verify internet connection
   - Check OpenAI account has credits

2. **"Rate limit exceeded"**
   - Wait a moment and retry
   - Consider upgrading OpenAI plan
   - Use GPT-3.5-turbo for higher limits

3. **"Invalid API key"**
   - Regenerate API key
   - Check environment variable is set correctly

### Monitoring:
- Check application logs for AI errors
- Monitor OpenAI usage dashboard
- Set up alerts for high usage

## UI Changes

### New Features in Interface:
1. **Analysis Method Indicator**: Shows if AI or basic comparison was used
2. **AI Confidence Score**: How confident the AI is in its assessment
3. **Category Breakdown**: Visual bars showing similarity by category
4. **AI Reasoning**: Explanation of the analysis
5. **Technical Analysis**: Detailed engineering comparison

### Visual Indicators:
- 🤖 = AI analysis used
- 📊 = Basic text comparison used
- ⚠️ = AI failed, fallback used

## Deployment

### Requirements Update:
The `requirements.txt` already includes:
```
openai==1.3.0
```

### Environment Variables Needed:
```
OPENAI_API_KEY=sk-your-key-here
GOOGLE_CLOUD_VISION_KEY_BASE64=your-existing-key
GOOGLE_CLOUD_STORAGE_BUCKET=your-existing-bucket
```

## Next Steps

1. **Set up OpenAI API key** (required)
2. **Test with sample drawings** to see the difference
3. **Monitor costs** in OpenAI dashboard
4. **Fine-tune settings** in config.py if needed
5. **Consider GPT-4 vs GPT-3.5-turbo** based on accuracy needs

## Support

For issues:
1. Check application logs
2. Verify API key is working: https://platform.openai.com/playground
3. Test with simple text first
4. Review OpenAI status: https://status.openai.com/

The AI comparison makes your Drawing Comparator much more intelligent and useful for engineering applications!
