from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import pickle
import numpy as np
from pathlib import Path  # Use pathlib for cleaner path handling

app = FastAPI(title="House Price Prediction API")

# --- Define Pydantic Model ---
class HouseData(BaseModel):
    area: float
    bedrooms: int
    age: float

# --- Load the Model ---
# Use pathlib.Path for robust path management
model_path = Path('model/house_price_model.pkl')
model = None

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded successfully from {model_path}")
except FileNotFoundError:
    print(f"WARNING: Model file not found at {model_path}")
    model = None
except Exception as e:
    print(f"ERROR: An error occurred loading model: {e}")
    model = None

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the House Price Prediction API. Go to /docs for API documentation."}

# --- NEW: Health Check Endpoint ---
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Simple health check.
    Returns '{"status": "ok"}' if the app is running.
    Nagios and other tools will hit this endpoint.
    """
    return {"status": "ok"}

# --- Prediction Endpoint ---
@app.post('/predict', tags=["Prediction"])
async def predict_price(house: HouseData):
    """
    Predicts the price of a house based on its features.
    """
    if model is None:
        # Return a 503 Service Unavailable if the model isn't loaded
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded or available. Please train the model first."
        )
    
    try:
        data = np.array([[house.area, house.bedrooms, house.age]])
        prediction = model.predict(data)
        return {'predicted_price': prediction[0]}
    except Exception as e:
        # Catch potential errors during prediction
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during prediction: {str(e)}"
        )