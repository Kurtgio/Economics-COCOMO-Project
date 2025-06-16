def calculate_risk_score(probability, impact):
    """
    Calculate risk score from probability and impact
    Both inputs should be 1-5 scale
    """
    return probability * impact

def risk_category(score):
    """Categorize risk based on score"""
    if score <= 5:
        return "Low"
    elif score <= 15:
        return "Medium"
    else:
        return "High"