from fastapi import FastAPI, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import create_graph_from_json
from dijkstra import dijkstra
import numpy as np

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None


@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    """
    Upload a graph in JSON format and store it as the active graph.

    If the file is not a JSON file, return an upload error.
    If successful, return the file name.
    """
    global active_graph

    # check that the file has .json extension
    if not file.filename.endswith(".json"):
        # clear any old graph to avoid confusion
        active_graph = None
        return {"Upload Error": "Invalid file type"}

    # build the graph from the uploaded json file
    active_graph = create_graph_from_json(file)

    return {"Upload Success": file.filename}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    """
    Solve the shortest path problem on the active graph.

    If no graph has been uploaded yet, return the "No active graph" error.
    If either start or end node id does not exist, return the invalid id error.
    Otherwise, return the path and its total distance.
    """
    global active_graph

    # case 1: no graph has been uploaded
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    # case 2: invalid node ids
    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}

    start_node = active_graph.nodes[start_node_id]
    end_node = active_graph.nodes[end_node_id]

    # run Dijkstra from the start node
    dijkstra(active_graph, start_node)

    # case 3: no path exists between the nodes
    if np.isinf(end_node.dist):
        return {"shortest_path": None, "total_distance": None}

    # rebuild the path from end node back to start node
    path_nodes = []
    current = end_node
    while current is not None:
        path_nodes.append(current.id)
        current = current.prev

    # reverse to get the path from start to end
    path_nodes.reverse()

    return {
        "shortest_path": path_nodes,
        "total_distance": float(end_node.dist),
    }


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
