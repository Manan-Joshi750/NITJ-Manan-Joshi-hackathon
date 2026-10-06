import numpy as np
import pandas as pd

def calculate_rebalanced_weights(base_weights: dict, sentiment_scores: dict, tilt_factor: float = 0.2) -> pd.DataFrame:
    tickers = list(base_weights.keys())
    df = pd.DataFrame({'Ticker': tickers, 'Base_Weight': [base_weights[t] for t in tickers]})
    
    # Calculate sentiment tilt
    df['Sentiment'] = df['Ticker'].map(lambda x: sentiment_scores.get(x, 0.0))
    df['Adjusted_Weight'] = df['Base_Weight'] * (1 + tilt_factor * df['Sentiment'])
    
    # Normalize weights so they sum to 1.0 (100%)
    df['New_Weight'] = df['Adjusted_Weight'] / df['Adjusted_Weight'].sum()
    df['Weight_Change'] = df['New_Weight'] - df['Base_Weight']
    return df