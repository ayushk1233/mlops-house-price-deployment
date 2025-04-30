import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression

def retrain():
    df = pd.read_csv('data/house_data.csv')
    X = df[['Area', 'Bedrooms', 'Age']]
    y = df['Price']

    model = LinearRegression()
    model.fit(X, y)

    with open('model/house_price_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("✅ Model retrained and saved.")

if __name__ == "__main__":
    retrain()
