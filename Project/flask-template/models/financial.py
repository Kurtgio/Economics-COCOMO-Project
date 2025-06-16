def calculate_roi(cost, benefit, years):
    """Calculate Return on Investment"""
    total_benefit = benefit * years
    if cost == 0:
        return 0  # Return 0% ROI or handle specially
    roi = ((total_benefit - cost) / cost) * 100
    return round(roi, 2)

def calculate_npv(cost, annual_benefit, discount_rate, years):
    """Calculate Net Present Value"""
    npv = -cost
    for year in range(1, years + 1):
        npv += annual_benefit / ((1 + discount_rate) ** year)
    return round(npv, 2)

def calculate_payback_period(cost, annual_benefit):
    """Calculate Payback Period in years"""
    if annual_benefit <= 0:
        return float('inf')  # Infinite payback period
    return round(cost / annual_benefit, 2)