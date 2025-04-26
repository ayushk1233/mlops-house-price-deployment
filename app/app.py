from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import os

app = FastAPI()

# Load the trained model
model_path = 'model/house_price_model.pkl'

if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
else:
    model = None

# Define the structure of input data
class HouseData(BaseModel):
    area: float
    bedrooms: int
    age: float

# When someone sends a POST request to /predict
@app.post('/predict')
def predict_price(house: HouseData):
    if model is None:
        return {"error": "Model not available"}
    data = np.array([[house.area, house.bedrooms, house.age]])
    prediction = model.predict(data)
    return {'predicted_price': prediction[0]}
