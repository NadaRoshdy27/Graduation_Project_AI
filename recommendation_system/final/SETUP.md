# Quick Setup Guide

## Prerequisites
- Python 3.10+ installed
- pip or conda package manager

## Setup Steps

### 1. Install Dependencies

**Option A: Using Conda (Recommended)**
```bash
conda env create -f environment.yml
conda activate recommendation-system
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

### 2. Verify Data and Models

The following should already exist:
- ✅ `data/*.csv` - 7 CSV files with synthetic data
- ✅ `trained_models/customer_recommender.pkl` - Customer model
- ✅ `trained_models/owner_recommender.pkl` - Owner model

If missing, regenerate:
```bash
# Generate data
python data/generate_data.py

# Train models
python models/train_customer_model.py
python models/train_owner_model.py
```

### 3. Start the Server

```bash
uvicorn main:app --reload
```

Or with Python:
```bash
python main.py
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Test the API

```bash
python test_api.py
```

## Docker Deployment

### Build and Run
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop
```bash
docker-compose down
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn main:app --port 8001
```

### Models Not Found
```bash
# Retrain models
python models/train_customer_model.py
python models/train_owner_model.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## API Usage Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Customer Recommendations
```bash
curl -X POST http://localhost:8000/recommend/customer \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "top_k": 5}'
```

### Get Owner Recommendations
```bash
curl -X POST http://localhost:8000/recommend/raw_materials \
  -H "Content-Type: application/json" \
  -d '{"owner_id": 1, "top_k": 5}'
```

## Project Status

✅ Data Generated (30K+ rows)
✅ Models Trained (2 models)
✅ API Running (4 endpoints)
✅ HTML Interface Ready
✅ Docker Configuration Complete
✅ Documentation Complete

## Support

For detailed documentation:
- See [README.md](README.md) for full documentation
- See [API_EXAMPLES.md](API_EXAMPLES.md) for API usage examples
- See [walkthrough.md](walkthrough.md) in artifacts for project walkthrough
