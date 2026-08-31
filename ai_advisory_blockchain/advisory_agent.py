import math

# 1. ACT STAGE (Simulated Tool Call)
def get_stock_data(ticker: str) -> dict:
    """Simulates looking up ticker data from an external source."""
    if ticker not in STOCK_UNIVERSE:
        raise ValueError(f"Ticker {ticker} not found in stock universe.")
    return STOCK_UNIVERSE[ticker]

# 2. THINK STAGE (Prescribed Allocation Mapping)
def determine_allocation(risk_tolerance: str) -> list:
    """Maps investor risk tolerance to the exact required 3-stock equal allocation."""
    mapping = {
        "Conservative": ["PAYBOND", "PAYGOLD", "PAYRETAIL"],
        "Moderate": ["PAYRETAIL", "PAYINFRA", "PAYGOLD"],
        "Aggressive": ["PAYTECH", "PAYFIN", "PAYINFRA"]
    }
    return mapping.get(risk_tolerance, [])

# 3. OBSERVE STAGE (CAPM Expected Return & Portfolio Volatility Calculation)
def calculate_portfolio_metrics(tickers: list) -> tuple:
    w = 1.0 / 3.0  # Equal 1/3 weight across the three stocks
    rho = 0.3      # Stated pairwise correlation

    stock_data = [get_stock_data(t) for t in tickers]
    
    # Expected Return per stock via CAPM: E(R) = Rf + beta * (Rm - Rf)
    capm_returns = [
        RISK_FREE_RATE + data["beta"] * (MARKET_RETURN - RISK_FREE_RATE)
        for data in stock_data
    ]
    portfolio_return = sum(w * r for r in capm_returns)

    # Portfolio Variance: Var(Rp) = sum(w_i^2 * sigma_i^2) + 2 * sum(w_i * w_j * rho * sigma_i * sigma_j)
    std_devs = [data["std_dev"] for data in stock_data]
    var_p = sum((w ** 2) * (s ** 2) for s in std_devs)
    
    covariance_term = 0.0
    n = len(tickers)
    for i in range(n):
        for j in range(i + 1, n):
            cov = rho * std_devs[i] * std_devs[j]
            covariance_term += 2 * (w * w * cov)
            
    total_variance = var_p + covariance_term
    portfolio_std_dev = math.sqrt(total_variance)

    return portfolio_return, portfolio_std_dev

# 4. DECISION & HUMAN-IN-THE-LOOP ESCALATION
def run_advisory_agent(investor: dict) -> dict:
    investor_id = investor["investor_id"]
    risk_tolerance = investor["risk_tolerance"]

    tickers = determine_allocation(risk_tolerance)
    port_return, port_std = calculate_portfolio_metrics(tickers)

    # Escalation Rule: Volatility > 20%
    if port_std > 0.20:
        return {
            "investor_id": investor_id,
            "status": "ESCALATED_TO_HUMAN_ADVISOR",
            "risk_tolerance": risk_tolerance,
            "tickers": tickers,
            "expected_return": port_return,
            "volatility": port_std
        }

    # Graded Mock LLM Baseline Narrative
    narrative = (
        f"For {risk_tolerance} investor {investor_id}, we recommend an allocation across "
        f"{', '.join(tickers)} with an expected portfolio return of {port_return:.1%} "
        f"and volatility of {port_std:.1%}."
    )

    return {
        "investor_id": investor_id,
        "status": "FINALIZED",
        "risk_tolerance": risk_tolerance,
        "tickers": tickers,
        "expected_return": port_return,
        "volatility": port_std,
        "narrative": narrative
    }

# Execute for all 5 investor profiles
print("--- Advisory Agent Run Transcripts ---")
for profile in INVESTOR_PROFILES:
    result = run_advisory_agent(profile)
    print(result)
