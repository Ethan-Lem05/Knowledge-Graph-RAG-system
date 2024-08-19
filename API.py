### API ###
import flask
from flask import request, jsonify
from ds_implementation import knowledge_graph
from functools import wraps
import signal

# Initialize app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Initialize the knowledge graph
kg = knowledge_graph()

def verify_request(func):
    @wraps(func)
    def wrapper(**kwargs):
        if request.json is None:
            return jsonify(error="ERROR! No text provided."), 400
        text = request.json['text']
        return func(text)
    return wrapper

@app.route('/add_node', methods=['POST'])
@verify_request
def add_node(text):
    kg.add_to_ds(text)
    print(kg.graph)
    return jsonify(success=True), 200

@app.route('/similarity_search', methods=['POST'])
@verify_request
def similarity_search(text):
    print(kg.graph)
    similar_nodes = kg.search_ds_by_context(text)
    docs = [n.get_text() for n in similar_nodes]
    return jsonify(docs), 200

@app.route('/remove_node', methods=['DELETE'])
def remove_node():
    if request.json is None:
        return jsonify(error="ERROR! No node_id provided."), 400
    if request.json['node_id'] is None:
        return jsonify(error="ERROR! No node_id provided."), 400
    
    node_id = request.json['node_id']
    kg.remove_from_ds(node_id)

    return jsonify(success=True), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="ERROR! Endpoint does not exist."), 404

@app.before_first_request
def load_graph():
    try:
        kg.load_graph_from_db()
        print("Graph loaded successfully.")
    except Exception as e:
        print(f"Error loading graph: {e}")

@app.teardown_appcontext
def save_graph(exception=None):
    try:
        kg.save_graph_to_db()
        print("Graph saved successfully.")
    except Exception as e:
        print("Error saving graph: {e}")

############################################

#deals with termination signals and unclean exits 
def signal_handler(sig, frame):
    print("Termination signal received. Saving graph...")
    save_graph()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

############################################
if __name__ == '__main__':
    app.run(port=5000, host='localhost')
