import streamlit as st
from streamlit_ace import st_ace
from agent import Agent
from example_tube import input_string
from plot import plot
from templates import SYSTEM_1

def page_setup():
    st.set_page_config(layout="wide")

page_setup()

if "agent" not in st.session_state:
    st.session_state.agent = Agent()
    st.session_state.agent.add_system_message(SYSTEM_1)

st.session_state.agent = st.session_state.agent

columns = st.columns([0.3, 0.4, 0.3])


with columns[0]:
    chat_box = st.container(height=730)
    with st.container(height=70):
        usr_msg = st.chat_input("Your message")
        if usr_msg:
            st.session_state.agent.add_user_message(usr_msg)
            st.session_state.agent.run()

    with chat_box:
        for msg in st.session_state.agent.messages:
            if msg['role'] in ['user', 'assistant']:
                with st.chat_message(name=msg['role']):
                    st.write(msg['content'])

with columns[1]:
    with st.container(height=500):
        changed = st_ace(st.session_state.agent.code)
        if changed:
            print("Changed")
    with st.container(height=300):
        if st.button("SIMULATE"):
            st.line_chart(st.session_state.agent.simulate())

with columns[2]:
    icons = st.container(height=400)
    diagram = st.container(height=400)
    icons.write("Icon view")
    icons.pyplot(st.session_state.agent.icon_view)
    diagram.write("Diagram view")
    diagram.pyplot(st.session_state.agent.diagram_view)