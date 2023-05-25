import base64
import io
import json
import os
import pickle
import zlib

import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

import matplotlib.pyplot as plt
import networkx as nx

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the routes through which requests can be made
@app.get("/")
async def read_root():
    return {"Hello": "World"}


supported_diagrams = [
    "blockdiag",
    "seqdiag",
    "actdiag",
    "nwdiag",
    "packetdiag",
    "rackdiag",
    "c4plantuml",
    "ditaa",
    "erd",
    "graphviz",
    "mermaid",
    "nomnoml",
    "plantuml",
    "svgbob",
    "umlet",
    "vega",
    "vegalite",
    "wavedrom",
    "network"
]


class Diagram(BaseModel):
    diagram_type: str
    diagram_source: str


def render_kroki(diagram):
    # Encode the text to base64
    encoded_text = base64.urlsafe_b64encode(zlib.compress(diagram.diagram_source.encode("utf-8"), 9))

    # Define the URL for the Kroki API
    return f"https://kroki.io/{diagram.diagram_type}/svg/" + encoded_text.decode("utf-8")


def render_network(diagram):
    base_url = base_url_from_env()
    encoded_text = base64.urlsafe_b64encode(zlib.compress(diagram.diagram_source.encode("utf-8"), 9))
    return f"{base_url}/network/" + encoded_text.decode("utf-8")


def base_url_from_env():
    return os.environ.get("BASE_URL", "http://localhost:5003")


@app.post("/diagram")
def render_diagram(diagram: Diagram):
    if diagram.diagram_type == "network":
        url = render_network(diagram)
    else: #default kroki.io
        url = render_kroki(diagram)

    # We don't need to render the image since ChatGPT will do it automatically from the link
    return url

@app.get("/network/{encoded_graph}")
async def graph(encoded_graph: str):
    # Decode and decompress the diagram source
    diagram_source = zlib.decompress(base64.urlsafe_b64decode(encoded_graph)).decode("utf-8")

    # Load the diagram source as JSON
    data = json.loads(diagram_source)

    # Convert the dictionary to a graph
    G = nx.node_link_graph(data)

    # Render the graph
    plt.figure(figsize=(10, 10))  # Increase figure size for better visibility
    pos = nx.spring_layout(G)  # Use spring layout for better node distribution

    # Draw nodes with larger size
    nx.draw_networkx_nodes(G, pos, node_size=1000)

    # Draw edges
    nx.draw_networkx_edges(G, pos)

    # Draw labels outside node centers
    label_pos = {node: (coords[0], coords[1] + 0.09) for node, coords in pos.items()}
    nx.draw_networkx_labels(G, label_pos)

    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='svg')

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the SVG data
    return Response(buffer.read(), media_type="image/svg+xml")


def media_type(filepath):
    if filepath.endswith(".yaml"):
        return "application/x-yaml"
    elif filepath.endswith(".json"):
        return "application/json"
    else: #default
        return "application/text"


from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))


@app.get("/.well-known/ai-plugin.json")
# @app.get("/static/openapi.yaml")
async def static(request: Request):
    context = {
        "base_url": base_url_from_env(),
    }

    filepath = request.url.path.lstrip("/")

    # add prompt.txt contents if ai-plugin.json is being requested
    if filepath.endswith("ai-plugin.json"):
        with open("prompt.txt", "r") as f:
            context["prompt"] = json.dumps(f.read())[1:-1] # remove extra double quotes

    try:
        template = env.get_template(filepath)
    except FileNotFoundError:
        return PlainTextResponse(f"File not found: {filepath}", status_code=404)

    content = template.render(context)

    return PlainTextResponse(content, media_type=media_type(filepath))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5003)
