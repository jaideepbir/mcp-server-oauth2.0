# python
import os
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MCP Tools", layout="wide")

# Resolve MCP server URL for both Docker (service DNS) and local dev
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL") or os.environ.get("VITE_MCP_SERVER_URL") or "http://localhost:9000"

st.title("MCP Tools")

with st.sidebar:
    st.markdown("### Auth")
    st.caption("Use 'Bearer admin-key' (rw) or 'Bearer demo-key' (r)")
    bearer = st.text_input("Access Token (include 'Bearer ')", value="Bearer demo-key")

st.header("Excel / CSV Reader")
# Default files list
default_files = [
    "public/sample.csv",
]

mode = st.selectbox("Select source", ["Default", "Upload"], index=0)

# Prepare variables used later
selected_source = None

if mode == "Default":
    cols = st.columns([3,1])
    with cols[0]:
        selected_source = st.selectbox("Default file (DATA_DIR)", default_files, index=0)
    with cols[1]:
        max_rows = st.number_input("Max rows", min_value=1, max_value=5000, value=10)
    if st.button("Read File", type="primary"):
        headers = {"Authorization": bearer} if bearer else {}
        payload = {"source": selected_source, "max_rows": int(max_rows)}
        with st.spinner("Reading file..."):
            try:
                resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/excel_csv_reader", json={**payload}, headers=headers, timeout=30)
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")
                resp = None
        st.divider(); st.subheader("Result")
        if resp and resp.ok:
            data = resp.json(); rows = data.get("rows", [])
            tab_table, tab_json = st.tabs(["Table", "JSON"])
            with tab_table:
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                else:
                    st.info("No rows returned.")
            with tab_json:
                st.code(resp.text)
        elif resp:
            st.error(f"Error {resp.status_code}")
            st.code(resp.text)
        else:
            st.error("No response from server.")
else:
    upcol = st.columns([3,1])
    with upcol[0]:
        uploaded = st.file_uploader("Upload CSV file", type=["csv"]) 
    with upcol[1]:
        max_rows = st.number_input("Max rows", min_value=1, max_value=5000, value=10, key="up_rows")
    if uploaded is not None:
        st.caption("Uploaded file will be read from /data/uploads inside MCP container")
        if st.button("Upload & Read", type="primary"):
            headers = {"Authorization": bearer} if bearer else {}
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "text/csv")}
            with st.spinner("Uploading..."):
                try:
                    up_resp = requests.post(f"{MCP_SERVER_URL}/mcp/upload", files=files, headers=headers, timeout=60)
                except requests.RequestException as e:
                    st.error(f"Upload failed: {e}")
                    up_resp = None
            if up_resp and up_resp.ok:
                up_info = up_resp.json()
                selected_source = up_info.get("relative_path")  # e.g., uploads/<name>
                payload = {"source": selected_source, "max_rows": int(max_rows)}
                with st.spinner("Reading uploaded file..."):
                    try:
                        read_resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/excel_csv_reader", json={**payload}, headers=headers, timeout=30)
                    except requests.RequestException as e:
                        st.error(f"Read failed: {e}")
                        read_resp = None
                st.divider(); st.subheader("Result")
                if read_resp and read_resp.ok:
                    data = read_resp.json(); rows = data.get("rows", [])
                    tab_table, tab_json = st.tabs(["Table", "JSON"])
                    with tab_table:
                        if rows:
                            st.dataframe(pd.DataFrame(rows), use_container_width=True)
                        else:
                            st.info("No rows returned.")
                    with tab_json:
                        st.code(read_resp.text)
                elif read_resp:
                    st.error(f"Read error {read_resp.status_code}")
                    st.code(read_resp.text)
                else:
                    st.error("No response from server for read.")
            elif up_resp:
                st.error(f"Upload error {up_resp.status_code}")
                st.code(up_resp.text)
            else:
                st.error("No response from server for upload.")
    else:
        st.info("Choose a CSV file to enable Upload & Read.")

# OPA Policy Eval section
st.header("OPA Policy Eval")
colsa = st.columns(2)
with colsa[0]:
    action = st.text_input("Action", value="excel.read")
# Determine a safe default resource path
if mode == "Default" and selected_source:
    resource_default = f"/data/{selected_source}"
else:
    # Placeholder for uploads until a file is uploaded
    resource_default = "/data/uploads/<uploaded-file>"
with colsa[1]:
    resource_path = st.text_input("Resource Path", value=resource_default)
if st.button("Evaluate Policy"):
    headers = {"Authorization": bearer} if bearer else {}
    payload = {"action": action, "resource": {"path": resource_path}}
    try:
        resp = requests.post(f"{MCP_SERVER_URL}/mcp/tools/opa_policy_eval", json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        st.error(f"OPA eval failed: {e}")
        resp = None
    st.divider(); st.subheader("Decision")
    data = {}
    if resp and resp.ok:
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
    elif resp:
        data = {"status": resp.status_code, "raw": resp.text}
    else:
        data = {"error": "no response"}
    allow = bool(data.get("allow"))
    role = "admin" if bearer.strip().endswith("admin-key") else "user"
    rights = data.get("rights") or ("rw" if role == "admin" else "r")
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
