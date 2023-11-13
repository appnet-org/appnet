internal {
	last: int
	window: int
	failure: int // timestamp here 
	total: int
}

fn init(window) {
	window := 5;
}

fn req(rpc_req) {
	now := current_time();
	match(now - last > window) {
		True => {
			failure := 0;
			total := 0;
			last := now;
		}
		False => {
			// do nothing
		}
	}; 
	match(failure > 0.5 * total) {
		True => {
			send(err('admission_control'), APP);
		}
		False => {
			total := total + 1;
			send(rpc_req, NET);
		}
	};
}

fn resp(resp) {
	match(resp) {
		Some(rpc_resp) => {
			send(rpc_resp, APP);
		}
		Some(err(msg)) => {
			failure := failure + 1;
			send(err(msg), APP);
		}
	};
}