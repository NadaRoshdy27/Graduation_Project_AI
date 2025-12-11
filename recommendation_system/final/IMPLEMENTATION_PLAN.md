# Recommendation System Implementation Plan

This plan outlines the complete implementation of a dual recommendation system: one for customer product recommendations and another for brand owner raw material recommendations.

## User Review Required

> [!IMPORTANT]
> **Technology Stack Decisions**
> - Using **LightFM** for collaborative filtering (handles cold-start better than pure matrix factorization)
> - Using **Prophet** for time-series forecasting (easier to use than ARIMA, handles seasonality well)
> - Using **scikit-learn** for content-based filtering and similarity calculations
> - All models will be pre-trained and saved as pickle files for fast API responses

> [!IMPORTANT]
> **Data Generation Approach**
> - Synthetic data will include realistic patterns (seasonal trends, customer preferences, etc.)
> - Customer transactions: 20,000+ rows with temporal patterns
> - Raw material purchases: 5,000+ rows with production correlations
> - Data will be generated with intentional patterns to ensure models can learn meaningful relationships

> [!NOTE]
> **Deployment Options**
> - Primary: Docker container (works on Render, Railway, AWS EC2)
> - Alternative: Direct Python deployment with uvicorn
> - Will include instructions for both approaches

## Proposed Changes

### Data Generation Module

#### [NEW] [generate_data.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/data/generate_data.py)

Generates all 7 synthetic datasets with realistic patterns:
- **Customers**: 1,000 customers with demographics (age, gender, location, preferred_category)
- **Products**: 500 products across multiple categories (Electronics, Fashion, Home, Beauty, Sports)
- **Customer_Transactions**: 20,000+ transactions with temporal patterns and customer preferences
- **Brand_Owners**: 100 brand owners across different industries
- **Raw_Materials**: 200 raw materials across categories (Textiles, Electronics Components, Chemicals, Packaging)
- **Owner_Purchase_History**: 5,000+ purchase records with seasonal patterns
- **Production_Data**: Monthly production volumes with seasonal trends

Uses numpy for random generation with controlled distributions to ensure realistic patterns.

---

### Customer Product Recommendation Model

#### [NEW] [customer_recommender.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/models/customer_recommender.py)

Implements hybrid recommendation system:
- **Collaborative Filtering**: LightFM with WARP loss for implicit feedback
- **Content-Based Filtering**: TF-IDF on product metadata (category, subcategory, name)
- **Hybrid Approach**: Weighted combination (70% collaborative, 30% content-based)
- **Features**:
  - Handles cold-start problem
  - Returns top-K recommendations with scores
  - Includes product metadata in results
  - `.predict(customer_id, top_k)` method

#### [NEW] [train_customer_model.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/models/train_customer_model.py)

Training pipeline for customer recommendation model:
- Loads transaction and product data
- Creates user-item interaction matrix
- Trains LightFM model with hyperparameter tuning
- Trains TF-IDF content model
- Evaluates with precision@k and recall@k
- Saves trained models to disk

---

### Brand Owner Raw Material Recommendation Model

#### [NEW] [owner_recommender.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/models/owner_recommender.py)

Implements time-series + similarity-based recommendation:
- **Time-Series Forecasting**: Prophet for predicting future material needs based on production patterns
- **Item-Based Similarity**: Cosine similarity between materials based on co-purchase patterns
- **Hybrid Approach**: Combines forecasted needs with similar materials
- **Features**:
  - Seasonal trend detection
  - Material substitution suggestions
  - `.predict(owner_id, top_k)` method

#### [NEW] [train_owner_model.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/models/train_owner_model.py)

Training pipeline for brand owner recommendation model:
- Loads purchase history and production data
- Trains Prophet models for each owner's material consumption
- Computes material similarity matrix
- Evaluates forecasting accuracy (MAE, RMSE)
- Saves trained models to disk

---

### FastAPI Backend

#### [NEW] [main.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/main.py)

Production-grade FastAPI application with endpoints:
- `GET /health`: Health check with model status
- `POST /recommend/customer`: Customer product recommendations
- `POST /recommend/raw_materials`: Brand owner raw material recommendations
- `POST /retrain`: Trigger model retraining
- `GET /`: Serves HTML testing interface

Features:
- Async endpoints for better performance
- Pydantic models for request/response validation
- Comprehensive error handling
- Structured logging
- CORS enabled for frontend access
- Model lazy loading

#### [NEW] [schemas.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/app/schemas.py)

Pydantic models for API validation:
- `CustomerRecommendRequest`
- `CustomerRecommendResponse`
- `OwnerRecommendRequest`
- `OwnerRecommendResponse`
- `HealthResponse`
- `RetrainResponse`

---

### Utilities

#### [NEW] [logger.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/utils/logger.py)

Centralized logging configuration with file and console handlers.

#### [NEW] [config.py](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/utils/config.py)

Configuration management for paths, model parameters, and API settings.

---

### Testing Interface

#### [NEW] [index.html](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/static/index.html)

Professional HTML interface with:
- Customer ID dropdown for testing product recommendations
- Owner ID dropdown for testing raw material recommendations
- Results displayed in formatted tables
- Modern, responsive design
- Real-time API calls with fetch
- Error handling and loading states

---

### Exploratory Data Analysis

#### [NEW] [customer_eda.ipynb](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/notebooks/customer_eda.ipynb)

Jupyter notebook analyzing:
- Customer demographics distribution
- Transaction patterns over time
- Popular products and categories
- Customer segmentation
- Purchase frequency analysis

#### [NEW] [owner_eda.ipynb](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/notebooks/owner_eda.ipynb)

Jupyter notebook analyzing:
- Raw material purchase patterns
- Seasonal trends in production
- Material category distributions
- Owner industry analysis
- Production volume trends

---

### Deployment Configuration

#### [NEW] [Dockerfile](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/Dockerfile)

Multi-stage Docker build:
- Python 3.10 slim base image
- Installs all dependencies
- Copies application code
- Exposes port 8000
- Runs uvicorn server

#### [NEW] [docker-compose.yml](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/docker-compose.yml)

Docker Compose configuration for local development and deployment.

#### [NEW] [requirements.txt](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/requirements.txt)

All Python dependencies:
- fastapi, uvicorn (API)
- lightfm, scikit-learn (ML)
- prophet (time-series)
- pandas, numpy (data processing)
- pydantic (validation)
- And more...

#### [NEW] [.env.example](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/.env.example)

Environment variable template for configuration.

---

### Documentation

#### [NEW] [README.md](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/README.md)

Comprehensive documentation including:
- Project overview
- Architecture diagram
- Setup instructions (local & Docker)
- API documentation with examples
- Deployment guide (Render, Railway, AWS)
- Testing instructions
- Troubleshooting

#### [NEW] [API_EXAMPLES.md](file:///d:/Study/Faculity/Graduation%20Project/Graduation-Project/AI/API_EXAMPLES.md)

Detailed API usage examples:
- curl commands for all endpoints
- Postman collection export
- Python requests examples
- Response format documentation

## Verification Plan

### Automated Tests

1. **Data Generation Verification**
   ```bash
   python data/generate_data.py
   # Verify CSV files created with correct row counts
   ```

2. **Model Training Verification**
   ```bash
   python models/train_customer_model.py
   python models/train_owner_model.py
   # Verify models saved and evaluation metrics logged
   ```

3. **API Testing**
   ```bash
   # Start server
   uvicorn main:app --reload
   
   # Test endpoints
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/recommend/customer -H "Content-Type: application/json" -d '{"customer_id": 1, "top_k": 5}'
   curl -X POST http://localhost:8000/recommend/raw_materials -H "Content-Type: application/json" -d '{"owner_id": 1, "top_k": 5}'
   ```

4. **Docker Build Verification**
   ```bash
   docker build -t recommendation-system .
   docker run -p 8000:8000 recommendation-system
   # Test endpoints on http://localhost:8000
   ```

### Manual Verification

1. **HTML Interface Testing**
   - Open http://localhost:8000 in browser
   - Test customer recommendations with different IDs
   - Test owner recommendations with different IDs
   - Verify results display correctly

2. **Recommendation Quality**
   - Review recommended products for sample customers
   - Verify recommendations align with customer preferences
   - Check raw material recommendations make sense for owner's industry
   - Validate seasonal patterns in material recommendations

3. **Deployment Testing**
   - Deploy to chosen platform (Render/Railway/AWS)
   - Test all endpoints on deployed URL
   - Verify HTML interface works on deployed instance
   - Check logs for errors
