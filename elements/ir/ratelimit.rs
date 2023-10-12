internal {
	last: int
	limit: int
	token: int
	token_per_second: float
}

fn init() {
	last := current_time();
	limit := 50;
	token := 5;
	per_sec := 5.0;
}

fn req(rpc_req) {
	token := min(lim, per_sec * (current_time() - last));
	last := current_time();
    match (token > 1) {
		True => {
			token := token - 1;
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