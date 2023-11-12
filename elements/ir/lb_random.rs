// here we assume Random is global methods
internal {
	addrs: Vec<string> 
}

fn init() {
	addrs.set(addrs.len(), 'server_A');
	addrs.set(addrs.len(), 'server_B');
	addrs.set(addrs.len(), 'server_C');
}

fn req(rpc_req) {
	idx := random(0, len(addrs));
	rpc_req.set('meta_dst', addrs.get(idx));
	send(rpc_req, NET);
}

fn resp(rpc_resp) {
	send(rpc_resp, APP);
}