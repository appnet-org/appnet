internal {
	int last
	int limit
	int token
	float token_per_second
}

fn init(lim, token, per_sec) {
	last = current_time()
	limit  = 50
	token = 500
	per_sec = 5.0
}

fn req(rpc_req) {
	token = min(lim, per_sec * (current_time() - last)
	last = current_time()
	Match(token > 1) {
		true => {
			token = token - rpc_req.meta.size
			send(rpc_req, NET)
		
		false => {
			send(err("ratelimit"), APP)
		}
	}
}

fn resp(rpc_resp) {
    send(rpc_resp, APP)
}