# Change a existing header and add a new one

internal{}

fn init() {}

fn req(rpc_req) {
	write(rpc_req, "language", "english")
  write(rpc_req, "location", "seattle")
}

fn resp(rpc_resp) {
	send(rpc_resp, APP)
}