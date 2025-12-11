"""
FastAPI Application for Recommendation System.
Production-grade API with async endpoints, error handling, and logging.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from app.schemas import (
    CustomerRecommendRequest,
    CustomerRecommendResponse,
    OwnerRecommendRequest,
    OwnerRecommendResponse,
    HealthResponse,
    RetrainResponse,
    ErrorResponse,
)
from models.customer_recommender import CustomerRecommender
from models.owner_recommender import OwnerRecommender
from utils.config import settings, ensure_directories
from utils.logger import app_logger
import pandas as pd


# Global model instances
customer_model = None
owner_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    app_logger.info("Starting Recommendation System API...")
    ensure_directories()
    
    # Load models
    global customer_model, owner_model
    
    try:
        if settings.customer_model_path.exists():
            app_logger.info("Loading customer recommendation model...")
            customer_model = CustomerRecommender.load(settings.customer_model_path)
            app_logger.info("Customer model loaded successfully")
        else:
            app_logger.warning("Customer model not found. Please train the model first.")
    except Exception as e:
        app_logger.error(f"Error loading customer model: {e}")
    
    try:
        if settings.owner_model_path.exists():
            app_logger.info("Loading owner recommendation model...")
            owner_model = OwnerRecommender.load(settings.owner_model_path)
            app_logger.info("Owner model loaded successfully")
        else:
            app_logger.warning("Owner model not found. Please train the model first.")
    except Exception as e:
        app_logger.error(f"Error loading owner model: {e}")
    
    app_logger.info("API startup complete")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down Recommendation System API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Dual recommendation system for customer products and brand owner raw materials",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if settings.static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML testing interface."""
    html_file = settings.static_dir / "index.html"
    
    if html_file.exists():
        return FileResponse(html_file)
    else:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Recommendation System API</title></head>
                <body>
                    <h1>Recommendation System API</h1>
                    <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
                    <p>HTML interface not found. Please create static/index.html</p>
                </body>
            </html>
            """,
            status_code=200
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    app_logger.info("Health check requested")
    
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        models_loaded={
            "customer_model": customer_model is not None and customer_model.is_trained,
            "owner_model": owner_model is not None and owner_model.is_trained,
        }
    )


@app.post("/recommend/customer", response_model=CustomerRecommendResponse)
async def recommend_customer_products(request: CustomerRecommendRequest):
    """
    Recommend products for a customer.
    
    Args:
        request: Customer recommendation request
    
    Returns:
        Product recommendations with scores
    """
    app_logger.info(f"Customer recommendation request: customer_id={request.customer_id}, top_k={request.top_k}")
    
    # Check if model is loaded
    if customer_model is None or not customer_model.is_trained:
        app_logger.error("Customer model not loaded")
        raise HTTPException(
            status_code=503,
            detail="Customer recommendation model not available. Please train the model first."
        )
    
    try:
        # Get recommendations
        recommendations = customer_model.predict(
            customer_id=request.customer_id,
            top_k=request.top_k
        )
        
        app_logger.info(f"Generated {len(recommendations)} recommendations for customer {request.customer_id}")
        
        return CustomerRecommendResponse(
            customer_id=request.customer_id,
            recommendations=recommendations,
            total_recommendations=len(recommendations)
        )
    
    except Exception as e:
        app_logger.error(f"Error generating customer recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.post("/recommend/raw_materials", response_model=OwnerRecommendResponse)
async def recommend_raw_materials(request: OwnerRecommendRequest):
    """
    Recommend raw materials for a brand owner.
    
    Args:
        request: Owner recommendation request
    
    Returns:
        Raw material recommendations with scores and reasons
    """
    app_logger.info(f"Owner recommendation request: owner_id={request.owner_id}, top_k={request.top_k}")
    
    # Check if model is loaded
    if owner_model is None or not owner_model.is_trained:
        app_logger.error("Owner model not loaded")
        raise HTTPException(
            status_code=503,
            detail="Owner recommendation model not available. Please train the model first."
        )
    
    try:
        # Get recommendations
        recommendations = owner_model.predict(
            owner_id=request.owner_id,
            top_k=request.top_k
        )
        
        app_logger.info(f"Generated {len(recommendations)} recommendations for owner {request.owner_id}")
        
        return OwnerRecommendResponse(
            owner_id=request.owner_id,
            recommendations=recommendations,
            total_recommendations=len(recommendations)
        )
    
    except Exception as e:
        app_logger.error(f"Error generating owner recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@app.post("/retrain", response_model=RetrainResponse)
async def retrain_models():
    """
    Retrain both recommendation models.
    
    This endpoint triggers retraining of both models using the latest data.
    """
    app_logger.info("Model retraining requested")
    
    global customer_model, owner_model
    retrained_models = []
    
    try:
        # Load data
        data_dir = settings.data_dir
        
        # Retrain customer model
        app_logger.info("Retraining customer model...")
        transactions_df = pd.read_csv(data_dir / "customer_transactions.csv")
        products_df = pd.read_csv(data_dir / "products.csv")
        customers_df = pd.read_csv(data_dir / "customers.csv")
        
        customer_model = CustomerRecommender()
        customer_model.train(
            transactions_df=transactions_df,
            products_df=products_df,
            customers_df=customers_df,
            epochs=settings.lightfm_epochs,
            num_threads=settings.lightfm_num_threads
        )
        customer_model.save(settings.customer_model_path)
        retrained_models.append("customer_model")
        app_logger.info("Customer model retrained successfully")
        
        # Retrain owner model
        app_logger.info("Retraining owner model...")
        purchase_history_df = pd.read_csv(data_dir / "owner_purchase_history.csv")
        production_df = pd.read_csv(data_dir / "production_data.csv")
        materials_df = pd.read_csv(data_dir / "raw_materials.csv")
        owners_df = pd.read_csv(data_dir / "brand_owners.csv")
        
        owner_model = OwnerRecommender()
        owner_model.train(
            purchase_history_df=purchase_history_df,
            production_df=production_df,
            materials_df=materials_df,
            owners_df=owners_df
        )
        owner_model.save(settings.owner_model_path)
        retrained_models.append("owner_model")
        app_logger.info("Owner model retrained successfully")
        
        return RetrainResponse(
            status="success",
            message="Models retrained successfully",
            models_retrained=retrained_models
        )
    
    except Exception as e:
        app_logger.error(f"Error retraining models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retraining models: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    app_logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal Server Error",
        detail=str(exc)
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
