"""
Math, Calculations, & Unit Conversions Skill for JARVIS / Alexa.
Safely evaluates arithmetic expressions, percentages, and conversions.
"""

import ast
import math
import operator
import re

# Supported safe operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """Safely evaluates an AST node containing mathematical expressions."""
    if isinstance(node, ast.Num):  # Python < 3.8
        return node.n
    elif isinstance(node, ast.Constant):  # Python >= 3.8
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError("Non-numeric constant")
    elif isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    else:
        raise ValueError("Invalid mathematical expression")


def calculate(query: str) -> str:
    """
    Evaluates math expressions or conversions from voice input.
    Examples:
    - 'what is 25 times 4'
    - 'what is 15 percent of 500'
    - 'square root of 144'
    - 'convert 10 miles to kilometers'
    """
    clean = query.lower().strip()

    # 1. Percentage check: "X percent of Y" / "X % of Y"
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:percent|%)\s+of\s+(\d+(?:\.\d+)?)", clean)
    if pct_match:
        pct_val = float(pct_match.group(1))
        total_val = float(pct_match.group(2))
        res = (pct_val / 100.0) * total_val
        formatted = f"{res:.2f}".rstrip("0").rstrip(".")
        return f"{pct_match.group(1)} percent of {pct_match.group(2)} is {formatted}."

    # 2. Square root check: "square root of X"
    sqrt_match = re.search(r"square\s+root\s+of\s+(\d+(?:\.\d+)?)", clean)
    if sqrt_match:
        val = float(sqrt_match.group(1))
        res = math.sqrt(val)
        formatted = f"{res:.2f}".rstrip("0").rstrip(".")
        return f"The square root of {sqrt_match.group(1)} is {formatted}."

    # 3. Unit conversions:
    # Miles <-> Kilometers
    mi_km = re.search(r"(\d+(?:\.\d+)?)\s*(?:miles?|mi)\s+(?:to|in)\s*(?:kilometers?|km)", clean)
    if mi_km:
        val = float(mi_km.group(1))
        res = val * 1.60934
        return f"{val} miles is equal to {res:.2f} kilometers."

    km_mi = re.search(r"(\d+(?:\.\d+)?)\s*(?:kilometers?|km)\s+(?:to|in)\s*(?:miles?|mi)", clean)
    if km_mi:
        val = float(km_mi.group(1))
        res = val / 1.60934
        return f"{val} kilometers is equal to {res:.2f} miles."

    # Celsius <-> Fahrenheit
    c_f = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:celsius|c)\s+(?:to|in)\s*(?:fahrenheit|f)", clean)
    if c_f:
        val = float(c_f.group(1))
        res = (val * 9 / 5) + 32
        return f"{val} degrees Celsius is {res:.1f} degrees Fahrenheit."

    f_c = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:fahrenheit|f)\s+(?:to|in)\s*(?:celsius|c)", clean)
    if f_c:
        val = float(f_c.group(1))
        res = (val - 32) * 5 / 9
        return f"{val} degrees Fahrenheit is {res:.1f} degrees Celsius."

    # Kilograms <-> Pounds
    kg_lbs = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilograms?|kilos?)\s+(?:to|in)\s*(?:pounds?|lbs?)", clean)
    if kg_lbs:
        val = float(kg_lbs.group(1))
        res = val * 2.20462
        return f"{val} kilograms is {res:.2f} pounds."

    lbs_kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:pounds?|lbs?)\s+(?:to|in)\s*(?:kg|kilograms?|kilos?)", clean)
    if lbs_kg:
        val = float(lbs_kg.group(1))
        res = val / 2.20462
        return f"{val} pounds is {res:.2f} kilograms."

    # 4. Standard arithmetic parsing
    expr = clean
    for phrase in ["calculate", "what is", "what's", "how much is", "solve", "math", "evaluate"]:
        expr = expr.replace(phrase, "")

    # Replace word operators with symbols
    expr = expr.replace("plus", "+")
    expr = expr.replace("minus", "-")
    expr = expr.replace("times", "*")
    expr = expr.replace("multiplied by", "*")
    expr = expr.replace("into", "*")
    expr = expr.replace("x", "*")
    expr = expr.replace("divided by", "/")
    expr = expr.replace("over", "/")
    expr = expr.replace("to the power of", "**")
    expr = expr.replace("power", "**")
    expr = expr.replace("^", "**")
    
    # Strip any characters other than numbers and valid math chars
    clean_expr = re.sub(r"[^0-9\+\-\*\/\(\)\.\%]", "", expr)
    
    if not clean_expr:
        return "I couldn't detect a valid mathematical expression."

    try:
        tree = ast.parse(clean_expr, mode='eval')
        result = _safe_eval(tree.body)
        formatted = f"{result:.2f}".rstrip("0").rstrip(".")
        return f"The answer is {formatted}."
    except Exception:
        return "Sorry, I couldn't calculate that."
