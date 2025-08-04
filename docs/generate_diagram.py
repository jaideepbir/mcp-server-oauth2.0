from diagrams import Diagram, Cluster, Node, Edge
from diagrams.gcp.compute import Run
from diagrams.gcp.storage import GCS
from diagrams.gcp.network import VirtualPrivateCloud
from diagrams.onprem.client import User
from PIL import Image, ImageDraw, ImageFont
import os

with Diagram("MCP Server Architecture on GCP Cloud Run", show=False, filename="mcp_server_architecture", direction="LR"):
    user = User("User")
    vpc = VirtualPrivateCloud("VPC Network")
    
    with Cluster("GCP Services"):
        auth_server = Run("Auth Server")
        mcp_server = Run("MCP Server")
        opa = Node("OPA Policy Engine")
        streamlit_app = Run("Streamlit Frontend")
        storage = GCS("Data Storage (GCS)")

        # User to Streamlit Frontend
        user >> Edge(label="1") >> streamlit_app

        # Authentication Flow
        streamlit_app >> Edge(label="2") >> auth_server
        auth_server << Edge(label="3") << streamlit_app

        # Tool Invocation Flow
        streamlit_app >> Edge(label="4") >> mcp_server
        mcp_server >> Edge(label="5") >> opa
        opa >> Edge(label="6") >> mcp_server
        mcp_server >> Edge(label="7") >> storage

# Create Legend Image
legend_data = [
    "1. User sends HTTP/S request to Cloud Run service",
    "2. Cloud Run routes HTTPS traffic to Streamlit Frontend",
    "3. Streamlit initiates OAuth2 authentication request to Auth Server",
    "4. Auth Server returns ID and Access Tokens (JWT) to Streamlit",
    "5. Streamlit makes tool call to MCP Server with Bearer Token",
    "6. MCP Server queries OPA Policy Engine for authorization",
    "7. OPA returns policy decision (Allow/Deny) to MCP Server",
    "8. MCP Server reads/writes data from/to GCS based on policy"
]

# Define image size and font
# Increase legend overall scale slightly (font size + leading) and adjust width accordingly
width = 600
line_height = 20  # original
height = len(legend_data) * 20 + 20  # Adjust height based on number of lines
img = Image.new('RGB', (width, height), color = 'white')
d = ImageDraw.Draw(img)
font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 14) # Replace with a valid font path

# Draw the text
y_offset = 10
for i, line in enumerate(legend_data):
    d.text((10, y_offset), line, fill=(0, 0, 0), font=font)
    y_offset += 20

img.save(os.path.join(os.getcwd(), "architecture_legend.png"))

# Combine Images
import os
img1 = Image.open(os.path.join(os.getcwd(), "mcp_server_architecture.png"))
img2 = Image.open(os.path.join(os.getcwd(), "architecture_legend.png"))
img1_size = img1.size
img2_size = img2.size
new_width = max(img1_size[0], img2_size[0])
# Reduce spacing so legend sits 10px closer (lift legend up by 10px)
new_height = img1_size[1] + img2_size[1] + 6  # was +20
new_im = Image.new('RGB', (new_width, new_height), (255,255,255))

# Paste the images, bringing legend up by 10px
new_im.paste(img1, (0,0))
new_im.paste(img2, (0, img1_size[1] + 6))

new_im.save(os.path.join(os.getcwd(), "mcp_server_architecture_with_legend.png"), "PNG")
