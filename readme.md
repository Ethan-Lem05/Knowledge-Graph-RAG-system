# Ada Nomad AI Backend Engineer project 

## Initial planning

### Knowledge graph:

* Start by developing a knowledge graph data structure so that data can start to be added to it 
* Assign IDs to different documents uploaded by the user --> should be parsed into a high-dimensional dense context vector

### API
* Allow for things such as GET, POST, UPDATE, DELETE functionality 
    * GET by ID or get by context 
    * POST will always do the same 
    * DELETE will remove the node by ID and all relevant edges 
* NOTE: all edges will by bidirectional

### RAG implementation
* Build upon langchain to introduce our knowledge graph for RAG functionality, use TOOLs to add functions for RAG     functionality


