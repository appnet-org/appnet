// here we assume Random is global methods
internal {
	addrs: Vec<string> 
}

fn init() {
	addrs.set(addrs.len(), 'server A');
	addrs.set(addrs.len(), 'server B');
	addrs.set(addrs.len(), 'server C');
}

fn req(rpc_req) {
	idx := random(0, len(addrs));
	rpc_req.get(meta).get(dst).set(addrs.get(idx));
	send(rpc_req, NET);
}

fn resp(rpc_resp) {
	send(rpc_resp, APP);
}