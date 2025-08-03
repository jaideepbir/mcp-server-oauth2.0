# python
# To render this diagram: pip install diagrams graphviz && python docs/dataflow.py
# Ensure you have Graphviz installed (brew install graphviz on macOS)

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Nginx
from diagrams.onprem.security import Vault
from diagrams.programming.language import Python
from diagrams.custom import Custom

with Diagram("MCP OAuth2 + OPA + Streamlit", show=False, filename="mcp_oauth2_opa_streamlit", direction="LR"):
    user = Users("User")

    with Cluster("Streamlit UI"):
        streamlit = Python("Streamlit App")

    with Cluster("Auth Server (OIDC)"):
        auth = Server("/authorize\n/token\n/jwks")

    with Cluster("MCP Server"):
        mcp = Python("MCP API")
        excel_tool = Python("excel_csv_reader")
        opa_tool = Python("opa_policy_eval")

    with Cluster("OPA"):
        opa = Server("OPA /v1/data/mcp/authz/allow")

    with Cluster("Data"):
        public = Server("/data/public")
        uploads = Server("/data/uploads")

    llm = Custom("LLM API", "https://raw.githubusercontent.com/mingrammer/diagrams/master/resources/saas/openai/openai.png")

    # Login flow
    user >> streamlit >> Edge(label="/authorize (PKCE)") >> auth
    auth >> Edge(label="code → tokens") >> streamlit

    # Tools invocation
    streamlit >> Edge(label="Bearer access_token") >> mcp
    mcp >> Edge(label="JWKS validate") >> auth
    mcp >> Edge(label="input {sub, action, resource}") >> opa
    opa >> Edge(label="allow/deny") >> mcp

    # Excel/CSV reads
    mcp >> excel_tool
    excel_tool >> public
    excel_tool >> uploads

    # Policy eval tool
    mcp >> opa_tool
    opa_tool >> opa

    # Chat flow
    streamlit >> Edge(label="chat") >> mcp
    mcp >> Edge(label="completion/tool-call") >> llm
