# app/utils/formula_engine.py
import re

def evaluate_formula(formula_expression: str, context: dict) -> float:
    """
    Evaluates a formula like '(BASIC + HRA)@12%' using the given context.
    Example context: {"GROSS": 30000, "BASIC": 12000, "HRA": 2400}
    """
    expression = formula_expression

    # Replace variable placeholders with actual values
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


def calculate_salary_with_formulas(db, gross_salary: float):
    """
    Dynamically calculates all active formulas using the provided gross salary.
    """
    from app.models.formula_m import Formula

    # Fetch all active formulas from DB
    formulas = db.query(Formula).filter(Formula.is_active == True).all()

    context = {"GROSS": gross_salary}
    unresolved = {f.component_code: f.formula_expression for f in formulas}

    # Run multiple passes to resolve dependencies (nested formulas)
    for _ in range(3):  # Usually enough for interdependent formulas
        for code, text in unresolved.items():
            value = evaluate_formula(text, context)
            if value > 0:
                context[code] = value

    return context
