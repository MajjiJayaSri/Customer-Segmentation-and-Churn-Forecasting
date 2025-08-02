import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import os

def segment_customers(df):
    def segments(row):
        f, m, r = row['F'], row['M'], row['R']
        if f <= 2 and m <= 3:
            return 'Frequent Customer'
        elif m == 1 and f >= 4:
            return 'High Spenders'
        elif r == 1 and f >= 3:
            return 'New Customer'
        elif r in [1, 4] and m in [3, 4]:
            return 'Seasonal Buyers'
        else:
            return 'Others'

    df['Customer Segment'] = df.apply(segments, axis=1)
    return df

def churnForecast(dataFrame, segment_name, folder):
    monthly = dataFrame.resample('ME').agg(
        churned=('churn_flag', 'sum'),
        total=('churn_flag', 'count')
    )
    monthly['churn_rate'] = monthly['churned'] / monthly['total']

    model = ARIMA(monthly['churn_rate'], order=(2,1, 2))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=6)
    monthly['forecast'] = model_fit.predict(start=0, end=len(monthly)-1)

    # Plotting
    plt.figure(figsize=(10, 6))
    monthly['churn_rate'].plot(label='Observed')
    monthly['forecast'].plot(label='Forecast')
    forecast.plot(label='Future', style='--', color='orange')
    plt.title(f'Churn Rate Forecast - {segment_name}')
    plt.xlabel('Month')
    plt.ylabel('Churn Rate')
    plt.legend()
    plt.grid()

    plot_path = os.path.join(folder, f"{segment_name}_forecast.png")
    plt.savefig(plot_path)
    plt.close()
    return plot_path
