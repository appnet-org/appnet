internal {
	last: int
	window: int
	failure: int // timestamp here 
	total: int
}

fn init(window) {
	window := 5;
}

fn req() {
	now := current_time();
	match(now - last > window) {
		true => {
			failure := 0;
			total := 0;
			last := now;
		}
		false => {
			// do nothing
		}
	}; 
	match(failure > 0.5 * total) {
		true => {
			send(err('admission_control'), APP);
		}
		false => {
			total := total + 1;
			send(req, NET);
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