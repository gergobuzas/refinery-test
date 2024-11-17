import websockets
import asyncio
import json
from nanoid import generate as idgen

 # 	   this.resourceName = `${nanoid(7)}.problem`; problem id-ra
 #    const id = nanoid(); sima ID   

class EditorServerConnection:

	def __init__(self, uri) -> None:
		self.uri = uri	

async def on_message(message):
	print(message)

HEADERS = {
    "Sec-WebSocket-Protocol": "tools.refinery.language.web.xtext.v1"
}

async def send_to_server(request: str):
	URI = "ws://localhost:1312/xtext-service"
	async with websockets.connect(URI, additional_headers=HEADERS, subprotocols=["tools.refinery.language.web.xtext.v1"]) as ws:
		resp = await ws.send(request)
		print(resp)
		resp = await ws.recv()
		print(resp)
		resp = await on_message(await ws.recv())
		resp = await on_message(await ws.recv())

if __name__ == "__main__":
	whole_json_request: dict = dict()
	request_dict: dict = dict()

	id = idgen()

	resource =  str(idgen(size=7)) + ".problem"
	service_type = "update"
	full_text = "% Metamodel\n\nabstract class CompositeElement {\n    contains Region[] regions\n}\n\nclass Region {\n    contains Vertex[] vertices opposite region\n}\n\nabstract class Vertex {\n    container Region region opposite vertices\n    contains Transition[] outgoingTransition opposite source\n    Transition[] incomingTransition opposite target\n}\n\nclass Transition {\n    container Vertex source opposite outgoingTransition\n    Vertex[1] target opposite incomingTransition\n}\n\nabstract class Pseudostate extends Vertex.\n\nabstract class RegularState extends Vertex.\n\nclass Entry extends Pseudostate.\n\nclass Exit extends Pseudostate.\n\nclass Choice extends Pseudostate.\n\nclass FinalState extends RegularState.\n\nclass State extends RegularState, CompositeElement.\n\nclass Statechart extends CompositeElement.\n\n% Constraints\n\n%% Entry\n\npred entryInRegion(Region r, Entry e) <->\n    vertices(r, e).\n\nerror noEntryInRegion(Region r) <->\n    !entryInRegion(r, _).\n\nerror multipleEntryInRegion(Region r) <->\n    entryInRegion(r, e1),\n    entryInRegion(r, e2),\n    e1 != e2.\n\nerror incomingToEntry(Transition t, Entry e) <->\n    target(t, e).\n\nerror noOutgoingTransitionFromEntry(Entry e) <->\n    !source(_, e).\n\nerror multipleTransitionFromEntry(Entry e, Transition t1, Transition t2) <->\n    outgoingTransition(e, t1),\n    outgoingTransition(e, t2),\n    t1 != t2.\n\n%% Exit\n\nerror outgoingFromExit(Transition t, Exit e) <->\n    source(t, e).\n\n%% Final\n\nerror outgoingFromFinal(Transition t, FinalState e) <->\n    source(t, e).\n\n%% State vs Region\n\npred stateInRegion(Region r, State s) <->\n    vertices(r, s).\n\nerror noStateInRegion(Region r) <->\n    !stateInRegion(r, _).\n\n%% Choice\n\nerror choiceHasNoOutgoing(Choice c) <->\n    !source(_, c).\n\nerror choiceHasNoIncoming(Choice c) <->\n    !target(_, c).\n\n% Instance model\n\nStatechart(sct).\n\n% Scope\n\nscope node = 20..30, Region = 2..*, Choice = 1..*, Statechart += 0.\n"
	concretize = False
	request_dict['resource'] = resource
	request_dict['serviceType'] = service_type
	request_dict['fullText'] = full_text
	request_dict['concretize'] = concretize
	

	whole_json_request['id'] = id
	whole_json_request['request'] = request_dict

	json_to_send = json.dumps(whole_json_request)
	asyncio.run(send_to_server(json_to_send))
	
