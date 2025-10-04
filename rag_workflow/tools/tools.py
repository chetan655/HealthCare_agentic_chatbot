from langchain_core.tools import tool 



@tool
def calculator(a: float, b: float, operation: str) -> float | str:
    """
    Perform arithmetic operations

    Args: 
        a: float
        b: float
        operation: str (e.g., '+', '-', '*', '/', 'add', 'subtract', 'multiply', 'divide')
    """
    print("Calculator activated")

    print("a", a)
    print("b", b)
    print("operation", operation)
    
    operation = operation.lower()  # normalize input
    
    if operation in ('+', 'add', 'addition'):
        return a + b
    elif operation in ('-', 'sub', 'subtract', 'subtraction'):
        return a - b
    elif operation in ('*', 'mul', 'multiply'):
        return a * b
    elif operation in ('/', 'div', 'divide', 'division'):
        if b == 0:
            return "Error: Division by zero!"
        return a / b
    else:
        return f"Operation '{operation}' not supported."