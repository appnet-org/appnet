internal
{
	acl: Map<string, string>
}

fn init() {
}

fn req(rpc_req) {
	match (acl.get(rpc_req.get('name')) == 'Yes') {
		True => {
			send(rpc_req, NET);
		}
		// default includes none or “no”
		False => {
			send(err('acl'), APP);
		}
	}; 
}

fn resp(rpc_resp) {
    send(rpc_resp, APP);	
}