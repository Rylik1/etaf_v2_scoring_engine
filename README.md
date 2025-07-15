# ETAF v2 Microservice

Enhanced Threat Assessment Framework v2 for Arabic and Farsi text analysis using Spark NLP.

## Overview

This microservice provides REST API endpoints for scoring threat levels in Arabic and Farsi text using advanced NLP models and rule-based analysis.

## Features

- **Multi-language Support**: Arabic and Farsi text analysis
- **ETAF v2 Scoring**: 4-component threat assessment framework
- **Spark NLP Integration**: Advanced NLP processing with pre-trained models
- **Railway Compatible**: Optimized for Railway.app deployment
- **Comprehensive API**: RESTful endpoints with detailed responses

## ETAF Components

1. **Temporal** (0-100): Future-oriented threats and temporal indicators
2. **Operational** (0-100): Military language, commands, and operational terms
3. **Specificity** (0-100): Concrete details, locations, people, quantities
4. **Source Intent** (0-100): Channel credibility and historical accuracy

## API Endpoints

### POST /score

Score a message using ETAF v2 framework.

**Request:**
```json
{
  "message_text": "Text to analyze",
  "lang": "ar",
  "channel_metadata": {
    "source": "Channel name",
    "verified": true,
    "follower_count": 50000,
    "historical_accuracy": 0.8
  }
}
```

**Response:**
```json
{
  "etaf_score": 327,
  "level": "High", 
  "components": {
    "temporal": 90,
    "operational": 80,
    "specificity": 70,
    "source_intent": 87
  },
  "rationale": "Forward-looking threat with operational instructions and credible source"
}
```

### GET /health

Health check endpoint for monitoring.

## Local Development

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Locally:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Test the API:**
   ```bash
   curl -X POST http://localhost:8000/score \
     -H "Content-Type: application/json" \
     -d @test_payload.json
   ```

## Railway Deployment

1. **Connect Repository** to Railway.app
2. **Environment Variables**: None required (auto-configured)
3. **Deploy**: Railway will automatically use `railway.json` configuration

## Spark NLP Setup

The service automatically downloads and configures required Spark NLP models:

- **Multilingual Models**: For cross-language compatibility
- **Arabic Specific**: Enhanced Arabic NLP processing
- **Farsi Specific**: Enhanced Farsi NLP processing

**Note**: First startup may take 2-3 minutes while models download.

## Environment Variables

- `PORT`: Server port (auto-set by Railway)
- `PYTHONUNBUFFERED`: Python output buffering (optional)
- `SPARK_LOCAL_IP`: Spark cluster IP (set to 0.0.0.0 for Railway)

## Performance Notes

- **Memory Usage**: ~2-4GB recommended for Spark NLP models
- **Startup Time**: 60-180 seconds for model initialization
- **Concurrent Requests**: Supports multiple simultaneous scoring requests

## Error Handling

The service includes comprehensive error handling:

- **Model Loading Failures**: Graceful fallback to basic NLP
- **Scoring Errors**: Returns minimum viable scores
- **Request Validation**: Detailed error messages for invalid inputs

## Monitoring

Use the `/health` endpoint to monitor service status:

```bash
curl http://your-railway-app.railway.app/health
```

## License

ThreatVista ETAF v2 Microservice - Internal Use Only