import websockets
import asyncio
import json
import time
from nanoid import generate as idgen

HEADERS = {
    "Sec-WebSocket-Protocol": "tools.refinery.language.web.xtext.v1"
}

class EditorServerConnection:

	def __init__(self, uri) -> None:
		self.uri = uri	
		self.ws = None
		self.initialized = False
		self.problem = None
		self.current_state_id = ""
		self.caret_offset = 0
	
	async def connect(self):
		self.ws = await websockets.connect(self.uri, additional_headers=HEADERS, subprotocols=["tools.refinery.language.web.xtext.v1"])

	async def on_message(self, message):
		dict_of_message: dict = json.loads(message)
		print(dict_of_message)
		# Setting the expected id
		if 'response' in dict_of_message.keys():
			response = dict_of_message["response"]
			self.current_state_id = response["stateId"]
	
	def create_init_update(self):
		'''Init of the problem. Sent as an update'''
		whole_json_request: dict = dict()
		request_dict: dict = dict()

		id_of_msg = idgen()

		self.resource =  str(idgen(size=7)) + ".problem"
		service_type = "update"
		full_text = "% Metamodel\n\nabstract class CompositeElement {\n    contains Region[] regions\n}\n\nclass Region {\n    contains Vertex[] vertices opposite region\n}\n\nabstract class Vertex {\n    container Region region opposite vertices\n    contains Transition[] outgoingTransition opposite source\n    Transition[] incomingTransition opposite target\n}\n\nclass Transition {\n    container Vertex source opposite outgoingTransition\n    Vertex[1] target opposite incomingTransition\n}\n\nabstract class Pseudostate extends Vertex.\n\nabstract class RegularState extends Vertex.\n\nclass Entry extends Pseudostate.\n\nclass Exit extends Pseudostate.\n\nclass Choice extends Pseudostate.\n\nclass FinalState extends RegularState.\n\nclass State extends RegularState, CompositeElement.\n\nclass Statechart extends CompositeElement.\n\n% Constraints\n\n%% Entry\n\npred entryInRegion(Region r, Entry e) <->\n    vertices(r, e).\n\nerror noEntryInRegion(Region r) <->\n    !entryInRegion(r, _).\n\nerror multipleEntryInRegion(Region r) <->\n    entryInRegion(r, e1),\n    entryInRegion(r, e2),\n    e1 != e2.\n\nerror incomingToEntry(Transition t, Entry e) <->\n    target(t, e).\n\nerror noOutgoingTransitionFromEntry(Entry e) <->\n    !source(_, e).\n\nerror multipleTransitionFromEntry(Entry e, Transition t1, Transition t2) <->\n    outgoingTransition(e, t1),\n    outgoingTransition(e, t2),\n    t1 != t2.\n\n%% Exit\n\nerror outgoingFromExit(Transition t, Exit e) <->\n    source(t, e).\n\n%% Final\n\nerror outgoingFromFinal(Transition t, FinalState e) <->\n    source(t, e).\n\n%% State vs Region\n\npred stateInRegion(Region r, State s) <->\n    vertices(r, s).\n\nerror noStateInRegion(Region r) <->\n    !stateInRegion(r, _).\n\n%% Choice\n\nerror choiceHasNoOutgoing(Choice c) <->\n    !source(_, c).\n\nerror choiceHasNoIncoming(Choice c) <->\n    !target(_, c).\n\n% Instance model\n\nStatechart(sct).\n\n% Scope\n\nscope node = 20..30, Region = 2..*, Choice = 1..*, Statechart += 0.\n"
		concretize = False
		request_dict['resource'] = self.resource
		request_dict['serviceType'] = service_type
		request_dict['fullText'] = full_text
		request_dict['concretize'] = concretize

		whole_json_request['id'] = id_of_msg
		whole_json_request['request'] = request_dict
		whole_json_request = json.dumps(whole_json_request)
		return whole_json_request

	def create_occurences(self):
		whole_json_request: dict = dict()
		request_dict: dict = dict()

		id_of_msg = idgen()

		request_dict['resource'] = self.resource
		request_dict['serviceType'] = "occurrences"
		request_dict['caretOffset'] = self.caret_offset
		request_dict['expectedStateId'] = self.current_state_id

		whole_json_request['id'] = id_of_msg
		whole_json_request['request'] = request_dict
		whole_json_request = json.dumps(whole_json_request)
		return whole_json_request

	def create_assist_add_text(self):
		whole_json_request: dict = dict()
		request_dict: dict = dict()

		id_of_msg = idgen()

		self.caret_offset = 4
		request_dict['caretOffset'] = self.caret_offset
		request_dict['proposalsLimit'] = 1000
		request_dict['resource'] = self.resource
		request_dict['serviceType'] = "assist"
		request_dict['requiredStateId'] = self.current_state_id
		request_dict['deltaOffset'] = 0
		request_dict['deltaReplaceLength'] = 0
		request_dict['deltaText'] = "asdf"

		whole_json_request['id'] = id_of_msg
		whole_json_request['request'] = request_dict
		whole_json_request = json.dumps(whole_json_request)
		return whole_json_request

	def create_update_remove_text(self):
		whole_json_request: dict = dict()
		request_dict: dict = dict()

		id_of_msg = idgen()

		request_dict['resource'] = self.resource
		request_dict['serviceType'] = "update"
		request_dict['requiredStateId'] = self.current_state_id
		request_dict['deltaOffset'] = 0
		request_dict['deltaReplaceLength'] = 4 # Because I only add "asdf" to the text
		request_dict['deltaText'] = ""
		self.caret_offset = 0

		whole_json_request['id'] = id_of_msg
		whole_json_request['request'] = request_dict
		whole_json_request = json.dumps(whole_json_request)
		return whole_json_request

	async def send_init_messages(self, request):
		await self.connect()
		await self.ws.send(request)
		# Waiting for the initial connection messages
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		self.initialized = True
		print('Update fullText responses received!... (4)')
		print('')

	async def send_occurences_message(self, request):
		await self.ws.send(request)
		await self.on_message(await self.ws.recv())
		print('Occurences response received!...')
		print('')
	
	async def send_assist_message(self, request):
		await self.ws.send(request)
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		print('Assist (add "asdf") responses received...! (3)')
		print('')

	async def send_update_message(self, request):
		await self.ws.send(request)
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		await self.on_message(await self.ws.recv())
		print('Update (remove "asdf") responses received...! (3)')
		print('')

	async def send_to_server(self, type: str):
		if str.lower(type) == 'init':
				if not self.initialized:
					request = self.create_init_update()
					await self.send_init_messages(request)
					await self.send_to_server('occurrences')
				else:
					raise RuntimeError("Already initialized the connection")

		elif str.lower(type) == 'occurrences':
			# Can be a click in the editor or the 
			occ_req = self.create_occurences()
			await self.send_occurences_message(occ_req)

		elif str.lower(type) == 'assist':
			await self.send_to_server('occurrences') # Simulating clicking on the editor field
			request = self.create_assist_add_text()
			time.sleep(1)	# Artificial delay, as if the person was writing
			await self.send_assist_message(request)
			await self.send_to_server('occurrences')

		elif str.lower(type) == 'update':
			await self.send_to_server('occurrences') # Simulating clicking on the editor field
			request = self.create_update_remove_text()
			time.sleep(1)	# Artificial delay, as if the person was writing
			await self.send_update_message(request)
			await self.send_to_server('occurrences')

	async def run_test(self):
		await self.send_to_server('init')
		time.sleep(1)
		await self.send_to_server('assist')
		time.sleep(1)
		await self.send_to_server('update')

     
 
if __name__ == "__main__":
	conn = EditorServerConnection("ws://localhost:1312/xtext-service")
	asyncio.run(conn.run_test())

	
