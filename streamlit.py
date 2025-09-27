import uuid

import streamlit as st
import requests

st.title("Luma Agent")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):

    with st.chat_message("user"):
        st.markdown(prompt)

    response = requests.post(
        "http://localhost:8000/",
        json = {
            "input": prompt,
            "session_id": st.session_state.session_id
        }
    )
    answer = response.json()["answer"]

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": answer})

