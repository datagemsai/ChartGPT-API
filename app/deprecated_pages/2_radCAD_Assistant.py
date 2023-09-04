from typing import Dict
import streamlit as st

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings

from app.config.content import radcad_assistant_description


PAGE_NAME = "radCAD Assistant"
st.set_page_config(page_title=PAGE_NAME, page_icon="⚙️")
st.markdown("# " + PAGE_NAME + " ⚙️")
st.markdown(radcad_assistant_description)

st.warning(
    "This assistant is still in beta and learning from the radCAD knowledge base."
)


@st.cache_resource(show_spinner=False)
def load_model() -> ConversationalRetrievalChain:
    # Load texts from DeepLake vectore store
    embeddings = OpenAIEmbeddings()
    dataset_path = "hub://***REMOVED***/radcad_v3"
    db = DeepLake(
        dataset_path=dataset_path, read_only=True, embedding_function=embeddings
    )

    # Configure retriever search configuration
    retriever = db.as_retriever()
    retriever.search_kwargs["distance_metric"] = "cos"
    retriever.search_kwargs["fetch_k"] = 100
    retriever.search_kwargs["maximal_marginal_relevance"] = True
    retriever.search_kwargs["k"] = 20

    # Create instance of OpenAI GPT model and chain
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)
    return qa


with st.spinner("Loading model..."):
    qa = load_model()

# Create list to store chat history for session
chat_history = []
# Text input for asking a question
question = st.text_input(
    label="Enter your question:",
    label_visibility="hidden",
    placeholder="Enter your question...",
)

# If the button is clicked or the user presses enter
if question:
    with st.spinner("Thinking..."):
        result = qa({"question": question, "chat_history": chat_history})
        answer = result["answer"]
    st.write(answer)

faqs = [
    "What is radCAD?",
    "What is a State Variable?",
    "How do I create a new State Variable?",
    "What Python type is a State Variable?",
    "How can I execute a simulation using multiprocessing?",
]


@st.cache_data(persist=True, show_spinner=False)
def get_faq_answers(_qa_chain, faqs=faqs) -> Dict[str, str]:
    return {
        question: _qa_chain({"question": question, "chat_history": []})["answer"]
        for question in faqs
    }


with st.spinner("Answering FAQs..."):
    faq_answers = get_faq_answers(_qa_chain=qa)

st.markdown("## FAQs")

for question, answer in faq_answers.items():
    st.markdown(f"**{question}**")
    st.markdown(f"{answer}")
