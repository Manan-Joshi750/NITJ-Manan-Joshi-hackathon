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

def format_rebalance_df(df: pd.DataFrame) -> pd.DataFrame:
    """Formats raw numerical weights into clean percentages and formatted signs for UI presentation."""
    formatted = df.copy()
    formatted['Base Weight'] = formatted['Base_Weight'].apply(lambda x: f"{x * 100:.2f}%")
    formatted['Sentiment Score'] = formatted['Sentiment'].apply(lambda x: f"{x:+.2f}")
    formatted['New Weight'] = formatted['New_Weight'].apply(lambda x: f"{x * 100:.2f}%")
    formatted['Weight Change'] = formatted['Weight_Change'].apply(lambda x: f"{x * 100:+.2f}%")
    return formatted[['Ticker', 'Base Weight', 'Sentiment Score', 'New Weight', 'Weight Change']]