# Add LangGraph Node

Guide for adding a new node to the LangGraph issue agent.

## Steps
1. Create the node function in `agent/nodes/<name>.py`
   - Function signature: `def <name>(state: IssueState) -> dict`
   - Return only the fields being updated
2. If the node needs a prompt, create it in `agent/prompts/<name>.py`
3. Register the node in `agent/graph.py`:
   - Add node: `graph.add_node("<name>", <name>_node)`
   - Add edges: connect to/from other nodes
   - Update conditional edges if needed
4. Update `agent/state.py` if new state fields are needed
5. Write tests in `tests/agent/nodes/test_<name>.py`
