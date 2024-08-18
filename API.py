### API ###
import flask
from flask import request, jsonify
from ds_implementation import knowledge_graph
from functools import wraps

#initialize app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

#initialize the knowledge graph
kg = knowledge_graph()

def verify_request(func):
    @wraps(func)
    def wrapper(**kwargs):
        if request.json is None:
            return jsonify(error = "ERROR! No text provided."), 400
        text = request.json['text']
        return func(text)
    return wrapper

@app.route('/add_node', methods=['POST'])
@verify_request
def add_node(text):
    kg.add_to_ds(text)
    return jsonify(success=True), 200

@app.route('/similarity_search', methods=['POST'])
@verify_request
def similarity_search(text):
    similar_nodes = kg.search_ds_by_context(text)
    docs = [n.get_text() for n in similar_nodes]
    return jsonify(docs), 200

@app.route('/remove_node', methods=['DELETE'])
def remove_node():
    if request.json is None:
        return jsonify(error = "ERROR! No node_id provided."), 400
    if request.json['node_id'] is None:
        return jsonify(error = "ERROR! No node_id provided."), 400
    
    node_id = request.json['node_id']
    kg.remove_from_ds(node_id)

    return jsonify(success=True), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error = "ERROR! Endpoint does not exist."), 404

############################################
if __name__ == '__main__':
    kg.load_graph_from_db()
    app.run(port=5000, host='localhost')
    kg.save_graph_to_db()