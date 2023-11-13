internal {
	last: int
	limit: int
	token: int
	token_per_second: int
}

fn init(lim, token, per_sec) {
	last := current_time();
	limit  := 50;
	token := 500;
	per_sec := 5.0;
}

fn req(rpc_req) {
	token := min(lim, per_sec * (current_time() - last));
	last := current_time();
	match(token > 1) {
		True => {
			token := token - rpc_req.get('meta_size');
			send(rpc_req, NET);
		}
		False => {
			send(err('ratelimit'), APP);
		}
	};
}

fn resp(rpc_resp) {
    send(rpc_resp, APP);
}