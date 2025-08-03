# python
import os
import streamlit as st
import requests

st.set_page_config(page_title="Chat", layout="wide")

st.title("Chat with LLM (Tool-Calling via MCP — scaffold)")

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:9000")

with st.sidebar:
    bearer = st.text_input("Access Token", type="password")

user_input = st.text_input("Your message")
if st.button("Send") and user_input:
    st.write("This is a placeholder. LLM + tool-calls wiring will be implemented.")
    st.json({"message": user_input})
