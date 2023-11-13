internal
{
	cache: Map<string, RPC_RESP> 
}

fn init() {
}


fn req(rpc_req) {
	match (cache.get(rpc_req.get('key'))) {
		Some(rpc_resp) => {
			send(rpc_resp, APP);
		}
		None => {
			send(rpc_req, NET);
		}
	};
}

fn resp(rpc_resp) {
	cache.set(rpc_resp.get('key'), rpc_resp);
	send(rpc_resp, APP);
}