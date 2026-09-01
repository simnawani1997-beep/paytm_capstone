# extract_disclosure.py
from disclosure_snippets import DISCLOSURE_SNIPPETS


def extract_signals(snippet: str) -> dict:
  """Extracts risk flags, hedging signals, and classifies sentiment using deterministic rules."""
  text = snippet.lower()

  # 1. Risk Flag Detection
  risk_flags = []
  if "litigation" in text:
    risk_flags.append("litigation")
  if "regulatory" in text:
    risk_flags.append("regulatory")
  if "top three customers" in text or "customer concentration" in text:
    risk_flags.append("customer concentration")

  # 2. Hedging Detection
  hedging_terms = ["assuming", "cautiously", "visibility"]
  hedging_detected = any(term in text for term in hedging_terms)

  # 3. Sentiment Classification
  if "confident" in text or "approved" in text:
    sentiment = "confident"
  elif hedging_detected:
    sentiment = "cautious"
  else:
    sentiment = "neutral"

  return {
      "risk_flags": risk_flags,
      "hedging_detected": hedging_detected,
      "sentiment": sentiment,
  }


if __name__ == "__main__":
  print("--- Running Structured Disclosure Extraction ---")
  for snippet in DISCLOSURE_SNIPPETS:
    signals = extract_signals(snippet)
    print(f"\nSnippet: {snippet}")
    print(f"Extracted: {signals}")
