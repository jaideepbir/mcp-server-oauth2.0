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
            opa_docker = Node("OPA Policy Engine")  # Using generic Node for OPA
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

# Legend and combined image generation
try:
    from PIL import Image, ImageDraw, ImageFont
    import os, sys

    legend_data = [
        "1. User sends HTTP/S request to Cloud Run service",
        "2. Cloud Run routes HTTPS traffic to Streamlit Frontend",
        "3. Streamlit initiates OAuth2 authentication request to Auth Server",
        "4. Auth Server returns ID and Access Tokens (JWT) to Streamlit",
        "5. Streamlit makes tool call to MCP Server with Bearer Token",
        "6. MCP Server queries OPA Policy Engine for authorization",
        "7. OPA returns policy decision (Allow/Deny) to MCP Server",
        "8. MCP Server reads/writes data from/to GCS based on policy",
    ]

    # Legend image sizing
    width = 880
    line_height = 28
    padding_top = 16
    padding_bottom = 16
    height = padding_top + len(legend_data) * line_height + padding_bottom

    img = Image.new("RGB", (width, height), color="white")
    d = ImageDraw.Draw(img)

    # font fallback
    try:
        font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    # draw legend
    x = 12
    y = padding_top
    for line in legend_data:
        d.text((x, y), line, fill=(0, 0, 0), font=font)
        y += line_height

    # Save legend alongside diagram outputs (repo root or current working dir)
    legend_path = os.path.join(os.getcwd(), "architecture_legend.png")
    img.save(legend_path)

    # Combine base diagram with legend, with reduced gap
    base_path = os.path.join(os.getcwd(), "mcp_server_architecture.png")
    if os.path.exists(base_path):
        img1 = Image.open(base_path).convert("RGB")
        img2 = Image.open(legend_path).convert("RGB")

        new_width = max(img1.width, img2.width)
        # Bring legend up by an additional 15 lines (total ~20 lines up)
        # Negative spacing overlaps legend upward relative to diagram.
        spacing = -5 * line_height
        new_height = img1.height + max(0, spacing) + img2.height

        new_im = Image.new("RGB", (new_width, new_height), (255, 255, 255))
        new_im.paste(img1, (0, 0))
        legend_x = max(0, (new_width - img2.width)//2 + int(0.15 * new_width))
        new_im.paste(img2, (legend_x, img1.height + spacing))
        out_path = os.path.join(os.getcwd(), "mcp_server_architecture_with_legend.png")
        new_im.save(out_path, "PNG")
except Exception as e:
    # Soft-fail so diagram still generates even if PIL/graphviz not available
    sys.stderr.write(f"[legend-combine] Skipped due to error: {e}\n")
