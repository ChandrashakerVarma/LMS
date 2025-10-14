# app/utils/formula_engine.py
import re

def evaluate_formula(formula_text: str, context: dict) -> float:
    """
    Evaluates a formula like '(BASIC + HRA)@12%' using the given context.
    Example context: {"GROSS": 30000, "BASIC": 12000, "HRA": 2400}
    """
    expression = formula_text

    # Replace @VAR@ placeholders with their values
    for key, value in context.items():
        expression = re.sub(rf"\b{key}\b", str(value), expression)

    # Replace @12% patterns with *12/100
    expression = re.sub(r"@(\d+)%", r"*\1/100", expression)

    # Replace remaining '@' symbols if any
    expression = expression.replace("@", "")

    try:
        result = eval(expression)
        return round(result, 2)
    except Exception:
        return 0.0
