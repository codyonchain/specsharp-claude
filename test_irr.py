import sys
sys.path.append('backend')
from app.v2.engines.unified_engine import UnifiedEngine

engine = UnifiedEngine()

# Test with restaurant numbers from the actual response
initial_investment = 2013060  # From backend response
annual_cash_flow = 114240     # Net income from backend response
years = 10

print(f"Initial Investment: ${initial_investment:,.0f}")
print(f"Annual Cash Flow: ${annual_cash_flow:,.0f}")
print(f"Years: {years}")

# Try to calculate IRR
irr = engine.calculate_irr(initial_investment, annual_cash_flow, years)
print(f"Calculated IRR: {irr}")
print(f"As percentage: {irr * 100:.1f}%")

# Simple check
total_return = annual_cash_flow * years
print(f"\nTotal 10-year return: ${total_return:,.0f}")
print(f"Investment: ${initial_investment:,.0f}")
print(f"Net gain/loss: ${total_return - initial_investment:,.0f}")
print(f"Simple ROI: {((total_return - initial_investment) / initial_investment) * 100:.1f}%")
