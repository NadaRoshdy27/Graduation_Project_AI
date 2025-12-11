# 🎯 Recommendation System

A complete end-to-end dual recommendation system built with FastAPI, featuring:
- **Customer Product Recommendations**: Hybrid collaborative + content-based filtering
- **Brand Owner Raw Material Recommendations**: Similarity-based + production trend analysis

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Development](#development)

## ✨ Features

### Customer Product Recommendations
- Hybrid recommendation system combining:
  - **Collaborative Filtering** (LightFM with WARP loss)
  - **Content-Based Filtering** (TF-IDF on product metadata)
- Handles cold-start problem
- Personalized based on customer preferences

### Brand Owner Raw Material Recommendations
- Material similarity based on co-purchase patterns
- Industry-specific recommendations
- Production trend analysis
- Explanations for each recommendation

### API Features
- Production-grade FastAPI server
- Async endpoints for better performance
- Comprehensive error handling and logging
- CORS enabled
- Health check endpoint
- Model retraining endpoint
- Interactive HTML testing interface

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
├─────────────────┤
│  /recommend/    │
│   customer      │◄─── Customer Recommender (LightFM + TF-IDF)
│  /recommend/    │
│  raw_materials  │◄─── Owner Recommender (Similarity + Trends)
│  /retrain       │
│  /health        │
└─────────────────┘
```

## 🚀 Installation

### Option 1: Using Conda (Recommended)

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate recommendation-system
```

### Option 2: Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎬 Quick Start

### 1. Generate Synthetic Data

```bash
python data/generate_data.py
```

This creates 7 datasets:
- `customers.csv` (1,000 rows)
- `products.csv` (500 rows)
- `customer_transactions.csv` (20,000+ rows)
- `brand_owners.csv` (100 rows)
- `raw_materials.csv` (200 rows)
- `owner_purchase_history.csv` (5,000+ rows)
- `production_data.csv` (4,000+ rows)

### 2. Train Models

```bash
# Train customer recommendation model
python models/train_customer_model.py

# Train owner recommendation model
python models/train_owner_model.py
```

### 3. Start the API Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app_name": "Recommendation System API",
  "version": "1.0.0",
  "models_loaded": {
    "customer_model": true,
    "owner_model": true
  }
}
```

### Customer Product Recommendations

```bash
POST /recommend/customer
Content-Type: application/json

{
  "customer_id": 123,
  "top_k": 5
}
```

**Response:**
```json
{
  "customer_id": 123,
  "recommendations": [
    {
      "product_id": 45,
      "name": "Smartphones Product 45",
      "category": "Electronics",
      "subcategory": "Smartphones",
      "price": 899.99,
      "score": 0.8542
    }
  ],
  "total_recommendations": 5
}
```

### Brand Owner Raw Material Recommendations

```bash
POST /recommend/raw_materials
Content-Type: application/json

{
  "owner_id": 55,
  "top_k": 5
}
```

**Response:**
```json
{
  "owner_id": 55,
  "recommendations": [
    {
      "material_id": 12,
      "name": "Cotton Grade 12",
      "category": "Textiles",
      "unit_cost": 15.50,
      "score": 0.7234,
      "reason": "Similar to Polyester Grade 8"
    }
  ],
  "total_recommendations": 5
}
```

### Retrain Models

```bash
POST /retrain
```

**Response:**
```json
{
  "status": "success",
  "message": "Models retrained successfully",
  "models_retrained": ["customer_model", "owner_model"]
}
```

## 🐳 Deployment

### Docker

```bash
# Build image
docker build -t recommendation-system .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/trained_models:/app/trained_models recommendation-system
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables if needed
6. Deploy!

### Deploy to Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

### Deploy to AWS EC2

1. Launch an EC2 instance (Ubuntu 20.04 recommended)
2. SSH into the instance
3. Install Docker:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   ```
4. Clone your repository
5. Run with Docker Compose:
   ```bash
   sudo docker-compose up -d
   ```
6. Configure security groups to allow port 8000

## 📁 Project Structure

```
AI/
├── data/                          # Data directory
│   ├── generate_data.py          # Synthetic data generation
│   └── *.csv                     # Generated datasets
├── models/                        # ML models
│   ├── customer_recommender.py   # Customer recommendation model
│   ├── owner_recommender.py      # Owner recommendation model
│   ├── train_customer_model.py   # Customer model training script
│   └── train_owner_model.py      # Owner model training script
├── app/                           # FastAPI app modules
│   ├── schemas.py                # Pydantic models
│   └── __init__.py
├── utils/                         # Utilities
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging setup
│   └── __init__.py
├── static/                        # Static files
│   └── index.html                # Testing interface
├── notebooks/                     # Jupyter notebooks (optional)
│   ├── customer_eda.ipynb        # Customer data analysis
│   └── owner_eda.ipynb           # Owner data analysis
├── trained_models/                # Saved models
│   ├── customer_recommender.pkl
│   └── owner_recommender.pkl
├── logs/                          # Application logs
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
├── environment.yml                # Conda environment
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose configuration
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .
```

### Adding New Features

1. Create a new branch
2. Implement your feature
3. Add tests
4. Update documentation
5. Submit a pull request

## 📊 Model Details

### Customer Recommendation Model

- **Algorithm**: Hybrid (LightFM + TF-IDF)
- **Collaborative Filtering**: LightFM with WARP loss
- **Content-Based**: TF-IDF on product metadata
- **Weighting**: 70% collaborative, 30% content-based
- **Features**: Handles cold-start, personalized recommendations

### Owner Recommendation Model

- **Algorithm**: Similarity-based + Production trends
- **Similarity**: Cosine similarity on co-purchase patterns
- **Trends**: Industry-specific material recommendations
- **Features**: Explanations, cold-start handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, LightFM, and scikit-learn
