internal
{
	Vec<byte> log
}

fn init() {
}


fn req(req) {
	write(log, log.size(), req.payload)
	send(req, NET)
}

fn resp(resp) {
	write(log, log.size(), resp.payload)
	send(rpc_resp, APP)
}