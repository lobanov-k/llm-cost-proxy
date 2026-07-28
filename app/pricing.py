MODEL_PRICES = {
  ("openai", "gpt-4o-mini"): {
    "input_per_1m": 0.15,
    "output_per_1m": 0.6
  }
}

def calculate_actual_cost(provider, model, output_tokens, input_tokens):
  prices = MODEL_PRICES.get((provider, model))
  if not prices or input_tokens is None or output_tokens is None:
    return None
  
  return (
    input_tokens / 1_000_000 * prices["input_per_1m"] 
    + output_tokens / 1_000_000 * prices["output_per_1m"]
  )