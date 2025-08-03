# python
import os
import requests
import streamlit as st

st.set_page_config(page_title="MCP Tools", layout="wide")

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:9000")

st.title("MCP Tools")

with st.sidebar:
    st.markdown("### Auth")
    bearer = st.text_input("Access Token", type="password")

st.header("Excel / CSV Reader")
source = st.text_input("Source path (inside container DATA_DIR)", value="public/sample.csv")
max_rows = st.number_input("Max rows", min_value=1, max_value=5000, value=10)
if st.button("Read File"):
    headers = {"Authorization": f"Bearer {bearer}"} if bearer else {}
    payload = {"source": source, "max_rows": max_rows}
    resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/excel_csv_reader", json=payload, headers=headers, timeout=30)
    st.code(resp.text)

st.header("OPA Policy Eval")
action = st.text_input("Action", value="excel.read")
resource_path = st.text_input("Resource Path", value=f"/data/{source}")
if st.button("Evaluate Policy"):
    headers = {"Authorization": f"Bearer {bearer}"} if bearer else {}
    payload = {"action": action, "resource": {"path": resource_path}}
    resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/opa_policy_eval", json=payload, headers=headers, timeout=30)
    st.code(resp.text)
