class SearchableSelectBox extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.options = [];
    }

    connectedCallback() {
        this.render();
        Streamlit.setComponentReady();
        Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, event => {
            this.options = event.detail.args.options;
            this.renderOptions();
        });
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                /* Include the styles you need for your component here */
            </style>
            <div class="container">
                <input type="text" id="search" placeholder="Search..."/>
                <select id="options" size="5"></select>
            </div>
        `;
        this.shadowRoot.querySelector("#search").addEventListener("keyup", this.filterOptions.bind(this));
        this.shadowRoot.querySelector("#options").addEventListener("change", this.sendValueToStreamlit.bind(this));
    }

    renderOptions() {
        const optionsContainer = this.shadowRoot.querySelector("#options");
        optionsContainer.innerHTML = this.options.map(option => `<option value="${option}">${option}</option>`).join("");
    }

    filterOptions(event) {
        const searchValue = event.target.value.toLowerCase();
        const filteredOptions = this.options.filter(option => option.toLowerCase().includes(searchValue));
        this.shadowRoot.querySelector("#options").innerHTML = filteredOptions.map(option => `<option value="${option}">${option}</option>`).join("");
    }

    sendValueToStreamlit(event) {
        Streamlit.setComponentValue(event.target.value);
    }
}

customElements.define('searchable-selectbox', SearchableSelectBox);

const componentRoot = document.querySelector("#root");
const myComponent = document.createElement("searchable-selectbox");
componentRoot.appendChild(myComponent);
