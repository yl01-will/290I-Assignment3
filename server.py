from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    #TODO: implement this function
    global active_graph
    filename = file.filename or ""
    if not filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": filename}
    except Exception:
        return {"Upload Error": "Invalid JSON content"}
    raise NotImplementedError("/upload_graph_json not yet implemented.")


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
        global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}

    start_node = active_graph.nodes[start_node_id]
    end_node = active_graph.nodes[end_node_id]

    # run dijkstra
    dijkstra(active_graph, start_node)

    # unreachable?
    if np.isinf(end_node.dist):
        return {"shortest_path": None, "total_distance": None}

    # reconstruct path
    path = []
    cur = end_node
    while cur is not None:
        path.append(cur.id)
        cur = cur.prev
    path.reverse()

    return {"shortest_path": path, "total_distance": float(end_node.dist)}
    raise NotImplementedError("/solve_shortest_path not yet implemented.")

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
