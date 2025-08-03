# python
import os
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MCP Tools", layout="wide")

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:9000")

st.title("MCP Tools")

with st.sidebar:
    st.markdown("### Auth")
    st.caption("Use 'Bearer admin-key' (rw) or 'Bearer demo-key' (r)")
    bearer = st.text_input("Access Token (include 'Bearer ')", value="Bearer demo-key")

st.header("Excel / CSV Reader")
cols = st.columns([3,1])
with cols[0]:
    source = st.text_input("Source path (inside container DATA_DIR)", value="public/sample.csv")
with cols[1]:
    max_rows = st.number_input("Max rows", min_value=1, max_value=5000, value=10)

if st.button("Read File", type="primary"):
    headers = {"Authorization": bearer} if bearer else {}
    payload = {"source": source, "max_rows": int(max_rows)}
    resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/excel_csv_reader", json=payload, headers=headers, timeout=30)
    st.divider()
    st.subheader("Result")
    if resp.ok:
        data = resp.json()
        rows = data.get("rows", [])
        tab_table, tab_json = st.tabs(["Table", "JSON"])
        with tab_table:
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.info("No rows returned.")
        with tab_json:
            st.code(resp.text)
    else:
        st.error(f"Error {resp.status_code}")
        st.code(resp.text)

st.header("OPA Policy Eval")
colsa = st.columns(2)
with colsa[0]:
    action = st.text_input("Action", value="excel.read")
with colsa[1]:
    resource_path = st.text_input("Resource Path", value=f"/data/{source}")
if st.button("Evaluate Policy"):
    headers = {"Authorization": bearer} if bearer else {}
    payload = {"action": action, "resource": {"path": resource_path}}
    resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/opa_policy_eval", json=payload, headers=headers, timeout=30)
    st.divider()
    st.subheader("Decision")
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}
    allow = bool(data.get("allow"))
    role = "admin" if bearer.strip().endswith("admin-key") else "user"
    rights = "rw" if role == "admin" else "r"
    colm = st.columns(3)
    with colm[0]:
        st.metric("Allowed", "YES" if allow else "NO")
    with colm[1]:
        st.metric("Role", role)
    with colm[2]:
        st.metric("Rights", rights)
    tab_json = st.tabs(["JSON"])[0]
    with tab_json:
        st.code(data)
