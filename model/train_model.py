import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression

# Load data
data = pd.read_csv('data/house_data.csv')
X = data[['Area', 'Bedrooms', 'Age']]
y = data['Price']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
with open('model/house_price_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Initial model trained and saved!")
