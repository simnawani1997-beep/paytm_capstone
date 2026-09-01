# debate.py
from stock_universe import STOCK_UNIVERSE


def run_debate(ticker: str = "PAYTECH") -> dict:
  """Executes a deterministic 3-agent debate for a chosen ticker from STOCK_UNIVERSE."""
  if ticker not in STOCK_UNIVERSE:
    raise ValueError(f"Ticker {ticker} not found in STOCK_UNIVERSE.")

  data = STOCK_UNIVERSE[ticker]
  beta = data["beta"]
  exp_return = data["analyst_expected_return"]
  std_dev = data["std_dev"]

  bull_text = (
      f"With an expected return of {exp_return:.1%} against a beta of"
      f" {beta:.2f}, {ticker} offers attractive risk-adjusted upside and strong"
      " capital growth potential."
  )

  bear_text = (
      f"The volatility of {std_dev:.1%} is significantly elevated. With a beta"
      f" of {beta:.2f}, {ticker} carries substantial systemic risk and"
      " downside exposure during market pullbacks."
  )

  synthesizer_text = (
      f"While {ticker} presents an attractive growth profile with a"
      f" {exp_return:.1%} projected return, its high volatility of"
      f" {std_dev:.1%} presents non-trivial downside risk. It is well suited"
      " for aggressive, high-risk portfolios but should be restricted or"
      " hedged for conservative horizons."
  )

  return {
      "ticker": ticker,
      "bull_argument": bull_text,
      "bear_argument": bear_text,
      "synthesizer_summary": synthesizer_text,
  }


if __name__ == "__main__":
  print("--- Running 3-Agent Debate Demo (Mock Baseline) ---")
  result = run_debate("PAYTECH")
  print(f"\n[BULL AGENT]:\n{result['bull_argument']}")
  print(f"\n[BEAR AGENT]:\n{result['bear_argument']}")
  print(f"\n[SYNTHESIZER AGENT]:\n{result['synthesizer_summary']}")
