function onKeyUp(event) {
  Streamlit.setComponentValue(event.target.value)
}

const debounce = (callback, wait) => {
  let timeoutId = null;
  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      callback.apply(null, args);
    }, wait);
  };
}

/**
 * The component's render function. This will be called immediately after
 * the component is initially loaded, and then again every time the
 * component gets new data from Python.
 */
function onRender(event) {
  // Get the RenderData from the event
  if (!window.rendered) {
    const {
      label,
      value,
      debounce: debounce_time,
      options,
      disabled,
      label_visibility
    } = event.detail.args;

    const input = document.getElementById("input_box");
    const label_el = document.getElementById("label")
    const root = document.getElementById("root")
    const optionsContainer = document.getElementById("options-container")

    if (label_el) {
      label_el.innerText = label
    }

    if (value && !input.value) {
      input.value = value
    }

    if (disabled) {
      input.disabled = true
      label.disabled = true
      // Add "disabled" class to root element
      root.classList.add("disabled")
    }

    if (label_visibility == "hidden") {
      root.classList.add("label-hidden")
    }
    else if (label_visibility == "collapsed") {
      root.classList.add("label-collapsed")
      Streamlit.setFrameHeight(45)
    }

    if (debounce_time > 0) { // is false if debounce_time is 0 or undefined
      input.onkeyup = debounce(onKeyUp, debounce_time)
    }
    else {
      input.onkeyup = onKeyUp
    }

    // Add default options to container
    options.forEach((option) => {
      const optionEl = document.createElement("div")
      optionEl.className = "option"
      optionEl.innerText = option
      optionsContainer.appendChild(optionEl)
    })

    window.rendered = true
  }
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)
Streamlit.setComponentReady()
// Render with the correct height
Streamlit.setFrameHeight(73)
