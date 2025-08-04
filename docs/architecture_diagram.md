graph LR
    subgraph "Docker Compose Environment"
        AuthServer[Auth Server (FastAPI)]
        MCPServer[MCP Server (FastAPI)]
        OPA[OPA Policy Engine]
        StreamlitApp[Streamlit Frontend]
    end

    User((User)) --> StreamlitApp
    StreamlitApp --> AuthServer
    StreamlitApp --> MCPServer
    MCPServer --> OPA
