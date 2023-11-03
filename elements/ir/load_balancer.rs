// here we assume Random is global methods
internal {
	vec<string> addrs
}

fn init() {
	write(addrs, len(addrs), "server A")
	write(addrs, len(addrs), "server B")
	write(addrs, len(addrs), "server C")
}

fn req(addrs, rpc_req) {
	idx = random(0, len(addrs))
	rpc_req.meta.dst = get(addrs, idx)
	send(rpc_req, NET)
}

fn resp(rpc_resp) {
	send(rpc_resp, APP)
}