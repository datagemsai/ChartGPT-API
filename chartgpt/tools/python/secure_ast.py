from sentry_sdk import capture_exception
import ast
import builtins


allowed_builtins = {
    "abs",
    "bool",
    "callable",
    "chr",
    "complex",
    "divmod",
    "float",
    "hex",
    "int",
    "isinstance",
    "len",
    "max",
    "min",
    "oct",
    "ord",
    "pow",
    "range",
    "repr",
    "round",
    "sorted",
    "str",
    "sum",
    "tuple",
    "type",
    "zip",
    "__import__",
    "print",
    "list",
    "dict",
    "set",
}

insecure_functions = {
    "open",
    "exec",
    "eval",
    "compile",
    "globals",
    "locals",
    "vars",
    "dir",
    "importlib",
}

disallowed_attributes = {
    # Builtins
    "os",
    "sys",
    "__import__",
    # Streamlit
    "session_state",
    "secrets",
}

allowed_imports = {
    "dataclass",
    "pandas",
    "streamlit",
    "bigquery",
    "plotly",
    "plotly.express",
    "plotly.graph_objs",
    "plotly.graph_objects",
    "plotly.io",
    "numpy",
    "math",
    "Figure",
    "make_subplots",
    "datetime",
    "timedelta",
    # GPT suggested:
    "google.cloud.bigquery",
    "numpy",
    "math",
    "plotly.subplots",
    # "matplotlib",
    # "matplotlib.pyplot",
    # "seaborn",
    "scipy",
    "scipy.stats",
    "scipy.optimize",
    "scikit-learn",
    "sklearn",
    "sklearn.preprocessing",
    "sklearn.metrics",
    "sklearn.model_selection",
    "sklearn.linear_model",
    "sklearn.tree",
    "sklearn.ensemble",
    "sklearn.cluster",
    "sklearn.decomposition",
    "statsmodels",
    "statsmodels.api",
    "statsmodels.formula.api",
    "statsmodels.tsa.api",
    "statsmodels.stats.api",
    # "tensorflow",
    # "tensorflow.keras",
    # "keras",
    # "keras.models",
    # "keras.layers",
    # "keras.optimizers",
    # "keras.preprocessing",
    # "keras.callbacks",
    # "keras.utils",
    # "keras.datasets",
    # "pytorch",
    # "torch",
    # "torch.nn",
    # "torch.optim",
    # "torch.utils.data",
    # "torchvision",
    # "torchvision.transforms",
    # "torchvision.datasets",
    # "torchtext",
    # "nltk",
    "spacy",
    "gensim",
    "psycopg2",
    "dash",
    "dash_core_components",
    "dash_html_components",
    "dash.dependencies",
    "dash_table",
    "lxml",
    "geopandas",
    "shapely",
    "networkx",
    "bokeh",
    "holoviews",
    "altair",
    "time",
    "pyarrow",
    "dask",
    "dask.dataframe",
    "h5py",
    "json",
    "pickle",
    "csv",
    "re",
    # Types
    "typing",
    "Optional",
}


def allowed_node(node):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        for alias in node.names:
            if alias.name not in allowed_imports:
                raise ValueError(f"Importing '{alias.name}' is not allowed")

    if isinstance(node, ast.Call):
        # Check for the '__import__' function
        if isinstance(node.func, ast.Name) and node.func.id == "__import__":
            if isinstance(node.args[0], ast.Str):
                if node.args[0].s not in allowed_imports:
                    raise ValueError(
                        f"Dynamic importing '{node.args[0].s}' is not allowed"
                    )
        # Check for other insecure functions
        elif isinstance(node.func, ast.Name) and node.func.id in insecure_functions:
            raise ValueError(f"Function '{node.func.id}' is not allowed")

    if isinstance(node, ast.Attribute):
        full_name = []
        n = node
        while isinstance(n, ast.Attribute):
            full_name.insert(0, n.attr)
            n = n.value
        if isinstance(n, ast.Name):
            full_name.insert(0, n.id)
        full_attr_name = ".".join(full_name)
        if full_attr_name in disallowed_attributes:
            raise ValueError(f"Accessing '{full_attr_name}' is not allowed")

    if isinstance(node, (ast.Attribute, ast.Name)):
        if (
            (node.attr.startswith("._") or node.attr.startswith(".__"))
            if hasattr(node, "attr")
            else (node.id.startswith("._") or node.id.startswith(".__"))
        ):
            raise ValueError(f"Accessing private members is not allowed")


def analyze_ast(node, max_depth, current_depth=0):
    if current_depth >= max_depth:
        return

    try:
        if isinstance(node, ast.AST):
            allowed_node(node)
            for child in ast.iter_child_nodes(node):
                analyze_ast(child, max_depth, current_depth + 1)
    except Exception as e:
        capture_exception(e)
        raise e


def secure_exec(code, custom_globals={}, custom_locals={}, max_depth=float("inf")):
    safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}
    custom_globals["__builtins__"] = safe_builtins

    tree = ast.parse(code)
    analyze_ast(tree, max_depth)

    exec(compile(tree, "<ast>", "exec"), custom_globals, custom_locals)


def secure_eval(expr, custom_globals={}, custom_locals={}, max_depth=float("inf")):
    safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}
    custom_globals["__builtins__"] = safe_builtins

    tree = ast.parse(expr, mode="eval")
    analyze_ast(tree, max_depth)

    return eval(compile(tree, "<ast>", "eval"), custom_globals, custom_locals)
