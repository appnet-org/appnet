// here we assume Random is global methods
internal {
	string mirror_address
}

fn init(mirror_address) {
	mirror_address = "xxx"
}

fn req(mirror_address, rpc_req) {
	send(rpc_req, NET)
	rpc_req.meta.dst = mirror_address
	rpc_req.meta.src = "" 
	send(rpc_req, NET)
}

fn resp(rpc_resp) {
	send(rpc_resp, APP)
}