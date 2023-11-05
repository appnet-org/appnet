internal
{
	log: Vec<byte> 
}

fn init() {
}

fn req(req) {
	log.set(log.size(), req.get('payload'));
	send(req, NET);
}

fn resp(resp) {
	log.get(log.size(), resp.get('payload'));
	send(rpc_resp, APP);
}