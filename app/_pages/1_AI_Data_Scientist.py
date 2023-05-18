import streamlit as st
import os
import traceback
from app.config.content import ai_data_scientist_description
import analytics_bot_langchain


# Display app name
PAGE_NAME = "AI Data Scientist"
st.set_page_config(page_title=PAGE_NAME, page_icon="📈")
st.markdown("# " + PAGE_NAME + " 📈")
st.markdown(ai_data_scientist_description)

# Monkey patching
from plotly.graph_objs._figure import Figure
def st_show(self):
    st.plotly_chart(self, use_container_width=True)
Figure.show = st_show 

st.markdown("### Question")

# Import sample question for project
if os.environ["PROJECT"] == "NFTFI":
    from app.config.nftfi import sample_questions
else:
    from app.config.default import sample_questions

dataset_ids = list(sample_questions.keys())
dataset_id = st.selectbox('Select dataset (optional):', [""] + dataset_ids)

sample_questions_for_dataset = [""]  # Create unselected option
if dataset_id:
    sample_questions_for_dataset.extend(sample_questions[dataset_id])
else:
    sample_questions_for_dataset.extend([item for sublist in sample_questions.values() for item in sublist])

sample_question = st.selectbox('Select sample question (optional):', sample_questions_for_dataset)

if not sample_question:
    question = st.text_input("Enter your question:")
else:
    question = sample_question

# Button for submitting the input
submit_button = st.button("Submit")
st.markdown("### Answer")

# If the button is clicked or the user presses enter
if submit_button:
    st.divider()
    with st.spinner('Thinking...'):
        try:
            # get_agent() is cached by Streamlit, where the cache is invalidated if dataset_ids changes
            agent = analytics_bot_langchain.get_agent(dataset_ids=dataset_ids)
            agent.run(input=question)
            st.success('Analytics complete!')
            st.balloons()
        except Exception as e:
            # For example, catch LangChain OutputParserException:
            st.error("Analytics failed." + "\n\n" + str(e))
            traceback.print_stack()
else:
    st.markdown("...")
