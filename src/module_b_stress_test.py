import json

def run_stress_test(portfolio_path: str, event_type: str, impact_score: float):
    with open(portfolio_path, 'r') as f:
        portfolio = json.load(f)
        
    # Trigger threshold check
    if impact_score < 7.0:
        return {"status": "NO_STRESS_TRIGGERED", "impact_score": impact_score}

    # Define shock parameters based on event type
    shocks = {
        "Geopolitical": {"equity_shock": -0.15, "rate_shock": 0.015, "credit_spread_bps": 150},
        "Macroeconomic": {"equity_shock": -0.10, "rate_shock": 0.020, "credit_spread_bps": 100},
        "Credit Event": {"equity_shock": -0.20, "rate_shock": -0.005, "credit_spread_bps": 300},
    }.get(event_type, {"equity_shock": -0.05, "rate_shock": 0.005, "credit_spread_bps": 50})

    results = []
    total_pre_val = 0
    total_post_val = 0

    for asset in portfolio:
        notional = asset['notional']
        pre_val = notional
        
        # Apply asset-specific valuation shock formulas
        if asset['asset_type'] in ['Corporate Loan', 'Commercial Real Estate']:
            loss_pct = (shocks['credit_spread_bps'] / 10000) * 5.0 # Duration approx 5
            post_val = pre_val * (1 - loss_pct)
        elif asset['asset_type'] == 'Corporate Bond':
            loss_pct = (shocks['rate_shock'] * 4.0) + (shocks['credit_spread_bps'] / 10000 * 4.0)
            post_val = pre_val * (1 - loss_pct)
        else: # Derivatives / Swaps
            post_val = pre_val * (1 - shocks['rate_shock'] * 2.0)

        total_pre_val += pre_val
        total_post_val += post_val
        results.append({
            "Asset_ID": asset['id'],
            "Type": asset['asset_type'],
            "Pre_Value": pre_val,
            "Post_Value": round(post_val, 2),
            "PnL": round(post_val - pre_val, 2)
        })

    return {
        "status": "STRESS_EXECUTED",
        "event_type": event_type,
        "impact_score": impact_score,
        "pre_stress_total": total_pre_val,
        "post_stress_total": round(total_post_val, 2),
        "total_pnl": round(total_post_val - total_pre_val, 2),
        "pnl_pct": round(((total_post_val - total_pre_val) / total_pre_val) * 100, 2),
        "asset_details": results
    }