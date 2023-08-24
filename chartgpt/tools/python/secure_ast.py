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
}

def allowed_node(node, allowed_imports):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        for alias in node.names:
            if alias.name not in allowed_imports:
                raise ValueError(f"Importing '{alias.name}' is not allowed")
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in insecure_functions:
        raise ValueError(f"Function '{node.func.id}' is not allowed")
    if isinstance(node, (ast.Attribute, ast.Name)):
        if (node.attr.startswith('._') or node.attr.startswith('.__')) if hasattr(node, 'attr') else (node.id.startswith('._') or node.id.startswith('.__')):
            raise ValueError(f"Accessing private members is not allowed")

def analyze_ast(node, allowed_imports, max_depth, current_depth=0):
    if current_depth >= max_depth:
        return

    if isinstance(node, ast.AST):
        allowed_node(node, allowed_imports)
        for child in ast.iter_child_nodes(node):
            analyze_ast(child, allowed_imports, max_depth, current_depth + 1)

def secure_exec(code, custom_globals={}, custom_locals={}, max_depth=float("inf")):
    safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}
    custom_globals["__builtins__"] = safe_builtins

    tree = ast.parse(code)
    analyze_ast(tree, allowed_imports, max_depth)

    exec(compile(tree, "<ast>", "exec"), custom_globals, custom_locals)

def secure_eval(expr, custom_globals={}, custom_locals={}, max_depth=float("inf")):
    safe_builtins = {name: getattr(builtins, name) for name in allowed_builtins}
    custom_globals["__builtins__"] = safe_builtins

    tree = ast.parse(expr, mode="eval")
    analyze_ast(tree, allowed_imports, max_depth)

    return eval(compile(tree, "<ast>", "eval"), custom_globals, custom_locals)
