from diagrams import Diagram, Cluster, Node, Edge
from diagrams.gcp.compute import Run
from diagrams.gcp.storage import GCS
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker

with Diagram("MCP Server Architecture on GCP Cloud Run", show=False, filename="mcp_server_architecture", direction="LR"):
    user = User("User")

    with Cluster("GCP Cloud Run Deployment"):
        cloud_run = Run("Cloud Run Service")
        
        with Cluster("Docker Containers"):
            auth_server_docker = Docker("Auth Server")
            mcp_server_docker = Docker("MCP Server")
            opa_docker = Node("OPA Policy Engine") # Using generic Node for OPA
            streamlit_app_docker = Docker("Streamlit Frontend")

        storage = GCS("Data Storage (GCS)")

    # User to Cloud Run
    user >> Edge(label="1") >> cloud_run
    cloud_run >> Edge(label="2") >> streamlit_app_docker

    # Authentication Flow
    streamlit_app_docker >> Edge(label="3") >> auth_server_docker
    auth_server_docker << Edge(label="4") << streamlit_app_docker

    # Tool Invocation Flow
    streamlit_app_docker >> Edge(label="5") >> mcp_server_docker
    mcp_server_docker >> Edge(label="6") >> opa_docker
    opa_docker >> Edge(label="7") >> mcp_server_docker
    mcp_server_docker >> Edge(label="8") >> storage
