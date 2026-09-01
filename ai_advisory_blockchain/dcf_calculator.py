# dcf_calculator.py
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

def run_dcf_valuation():
    # 1. Base FCFF Inputs
    ebit = 500_000_000          # INR 50 Cr
    tax_rate = 0.25             # 25% tax
    dna = 60_000_000            # INR 6 Cr D&A
    capex = 80_000_000          # INR 8 Cr CapEx
    delta_nwc = 20_000_000      # INR 2 Cr Change in NWC

    # FCFF = EBIT * (1 - tax rate) + D&A - CapEx - Delta NWC
    base_fcff = (ebit * (1 - tax_rate)) + dna - capex - delta_nwc
    
    # 2. WACC Calculation using PAYFIN Beta
    beta = STOCK_UNIVERSE["PAYFIN"]["beta"]
    cost_of_equity = RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)
    
    pre_tax_cost_of_debt = 0.09
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
    
    weight_equity = 0.80
    weight_debt = 0.20
    base_wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)
    
    # 3. Growth Rates
    base_terminal_growth = 0.05
    fading_growth_rates = [0.15, 0.12, 0.10, 0.08, 0.06]
    
    def calculate_ev(wacc: float, g: float) -> float:
        cash_flows = []
        cf = base_fcff
        pv_explicit = 0.0
        for year, rate in enumerate(fading_growth_rates, start=1):
            cf *= (1 + rate)
            cash_flows.append(cf)
            pv_explicit += cf / ((1 + wacc) ** year)
        
        terminal_value = (cash_flows[-1] * (1 + g)) / (wacc - g)
        pv_terminal_value = terminal_value / ((1 + wacc) ** len(fading_growth_rates))
        return pv_explicit + pv_terminal_value

    base_ev = calculate_ev(base_wacc, base_terminal_growth)
    
    print("--- DCF VALUATION SUMMARY ---")
    print(f"Base FCFF (Year 0): INR {base_fcff:,.2f}")
    print(f"Cost of Equity: {cost_of_equity:.2%}")
    print(f"Base WACC: {base_wacc:.2%}")
    print(f"Base DCF Enterprise Value: INR {base_ev:,.2f}\n")
    
    # 4. 3x3 Sensitivity Grid
    wacc_grid = [base_wacc - 0.01, base_wacc, base_wacc + 0.01]
    growth_grid = [base_terminal_growth - 0.01, base_terminal_growth, base_terminal_growth + 0.01]
    
    print("--- 3x3 Enterprise Value Sensitivity Table (INR) ---")
    header = f"{'WACC / Terminal g':<20}" + "".join([f"{g:.1%}".center(22) for g in growth_grid])
    print(header)
    print("-" * len(header))
    
    for w in wacc_grid:
        row = f"{w:.2%}".ljust(20)
        for g in growth_grid:
            val = calculate_ev(w, g)
            gap = w - g
            row += f"INR {val/1e7:,.1f}Cr (gap:{gap:.1%})".center(22)
        print(row)
        
    # 5. EV/EBITDA Multiple Cross-Check
    illustrative_ebitda = 600_000_000
    target_multiple = 10.0
    multiple_ev = illustrative_ebitda * target_multiple
    
    print("\n--- EV/EBITDA Valuation Cross-Check ---")
    print(f"EV/EBITDA Valuation ({target_multiple}x on INR {illustrative_ebitda:,.0f}): INR {multiple_ev:,.2f}")
    print("Comparison: The DCF baseline reflects intrinsic cash flow generation discounted at dynamic capital costs, whereas the 10x EV/EBITDA multiple provides a market-comparable heuristic. The minor divergence illustrates that the market multiple implicitly assumes higher medium-term reinvestment efficiency than the fading growth profile.")

if __name__ == "__main__":
    run_dcf_valuation()

