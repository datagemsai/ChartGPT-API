from copy import copy
import streamlit as st
from PIL import Image
import os
import traceback
from app.config.content import chartgpt_description
import analytics_bot_langchain
from plotly.graph_objs._figure import Figure
import base64


# Display app name
PAGE_NAME = "ChartGPT"
st.set_page_config(page_title=PAGE_NAME, page_icon="📈")

cadlabs_logo = Image.open('logo.png')
st.image(cadlabs_logo)

st.markdown("# " + PAGE_NAME + " 📈")
st.markdown(chartgpt_description)

# Monkey patching
def st_show(self):
    st.plotly_chart(self, use_container_width=True)
Figure.show = st_show 

# Import sample question for project
if os.environ["PROJECT"] == "NFTFI":
    from app.config.nftfi import datasets
else:
    from app.config.default import datasets

dataset_ids = list(datasets.keys())

# TODO In future we can add cards to present datasets more visually:
# from streamlit_card import card
# for dataset_id, sample_questions in datasets.items():
#     hasClicked = card(
#         title=dataset_id,
#         text=f"\"{sample_questions[0]}\"",
#         # image="http://placekitten.com/200/300",
#         # url="https://github.com/gamcoh/st-card"
#     )

st.markdown("### Question")

# dataset_id = st.selectbox('Select dataset (optional):', [""] + dataset_ids)
dataset_id = st.selectbox('Select dataset:', dataset_ids, index=0)

sample_questions_for_dataset = [""]  # Create unselected option
if dataset_id:
    sample_questions_for_dataset.extend(datasets[dataset_id])
else:
    sample_questions_for_dataset.extend([item for sublist in datasets.values() for item in sublist])

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

# if 'answers' not in st.session_state:
#     st.session_state['answers'] = {}

# if submit_button:
#     st.session_state.answers[copy(current_question)] = False

# st.write(st.session_state)

# for question, answer in st.session_state.answers.items():
#     with st.expander(label=question, expanded=(not answer)):
#         # If the button is clicked or the user presses enter
#         if not answer:
#             with st.spinner('Thinking...'):
#                 try:
#                     # get_agent() is cached by Streamlit, where the cache is invalidated if dataset_ids changes
#                     agent = analytics_bot_langchain.get_agent(dataset_ids=dataset_ids)
#                     st.session_state.answers[question] = agent.run(input=question)
#                     st.success('Analytics complete!')
#                     st.balloons()
#                     st.write(st.session_state)
#                 except Exception as e:
#                     # For example, catch LangChain OutputParserException:
#                     st.error("Analytics failed." + "\n\n" + str(e))
#                     traceback.print_stack()
#                     st.write(st.session_state)
