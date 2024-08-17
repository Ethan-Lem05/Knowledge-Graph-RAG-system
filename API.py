### API ###
import flask
from flask import request, jsonify
from ds_implementation import knowledge_graph

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#initialize the knowledge graph
kg = knowledge_graph()

@app.route('/', methods=['GET'])
def home():
    return "<h1>Knowledge Graph API</h1><p>This site is a prototype API for a knowledge graph.</p>"

@app.route('/add_node', methods=['POST'])
def add_node():
    text = request.json['text']
    kg.add_to_ds(text)

@app.route('/similarity_search')
def similarity_search():
    text = request.json['text']
    similar_nodes = kg.search_ds_by_context(text)
    
    docs = [n.get_text() for n in similar_nodes]

    return jsonify(docs), 200

@app.route('/remove_node', methods=['DELETE'])
def remove_node():
    node_id = request.json[node_id];
    kg.remove_from_ds(node_id)

    return jsonify(success=True), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error = "ERROR! Endpoint does not exist."), 404