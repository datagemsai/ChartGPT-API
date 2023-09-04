from RestrictedPython import compile_restricted

from RestrictedPython import safe_builtins

# from RestrictedPython import limited_builtins
# from RestrictedPython import utility_builtins


def secure_exec(code, custom_globals={}, custom_locals={}):
    byte_code = compile_restricted(code, filename="<inline code>", mode="exec")
    _custom_globals = {
        **custom_globals,
        "__builtins__": safe_builtins,
    }

    exec(byte_code, _custom_globals, None)


def secure_eval(expr, custom_globals={}, custom_locals={}):
    byte_code = compile_restricted(expr, filename="<inline code>", mode="eval")
    _custom_globals = {
        **custom_globals,
        "__builtins__": safe_builtins,
    }

    return eval(byte_code, _custom_globals, None)
