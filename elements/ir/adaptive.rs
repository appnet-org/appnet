
// adaptive concurrency

internal {
	outstanding: Vec<RPC_REQ>  	
	window: int
}

fn init() {
	window := 5;
}

fn req(rpc_req) {
	match (outstanding.size() < window) {
		True => {
			set(outstanding, rpc_req.get('meta_id'), current_time());
			send(rpc_req, NET);
		}
		False => {
			send(err('ratelimit'), APP);
		}
	};
}


fn resp(rpc_resp) {
    send_time := outstanding.get(resp.get(id));
    window := update_window(current_time() - send_time);
    outstanding.delete(resp.get(id));
    send(resp, APP);
}