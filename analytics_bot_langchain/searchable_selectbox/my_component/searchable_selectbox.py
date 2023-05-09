from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

# _BUILD_DIR = Path(__file__).parent / "frontend"
_COMPONENT_NAME = "searchable_selectbox"

build_dir = Path(__file__).parent.absolute() / "frontend"

_COMPONENT_FUNC = components.declare_component(
    _COMPONENT_NAME,
    path=str(build_dir)
    # url=f"file://{_BUILD_DIR.resolve()}"
)

def st_searchable_selectbox(
    label: str,
    options: List[str],
    default: Optional[str] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable[[str], None]] = None,
    **kwargs: Any,
) -> str:
    """Create a searchable selectbox widget.

    Parameters
    ----------
    label : str
        A label for the widget.
    options : List[str]
        A list of strings representing the selectable options.
    default : Optional[str], optional
        The default option to select, by default None.
    key : Optional[str], optional
        An optional key to use to identify the widget. If specified,
        the widget state will be persisted across sessions, by default None.
    on_change : Optional[Callable[[str], None]], optional
        An optional callback function that will be called with the new
        selected value whenever the user changes the selection, by default None.
    **kwargs : Any
        Additional keyword arguments to pass to the underlying Streamlit
        selectbox widget.

    Returns
    -------
    str
        The currently selected option.
    """
    print("st_searchable_selectbox called with label={}, options={}".format(label, options))
    if key is None:
        key = label

    selected_value = _COMPONENT_FUNC(
        label=label,
        options=options,
        default=default,
        key=key,
        on_change=on_change,
        **kwargs
    )

    return selected_value