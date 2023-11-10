internal
{
	log: Vec<byte> 
}

fn init() {
}

fn req(rpc_req) {
	log.set(log.size(), rpc_req.get('payload'));
	send(rpc_req, NET);
}

fn resp(rpc_resp) {
	log.get(log.size(), rpc_resp.get('payload'));
	send(rpc_resp, APP);
}