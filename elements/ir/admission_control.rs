internal {
	int last
	int window
	int failure // timestamp here 
	int total
}

fn init(window) {
	window = 5
}

fn req() {
	now = current_time()
	match(now - last > window) {
		true => {
			failure = 0
			total = 0 
			last = now
		}
		false => {
			// do nothing
		}
	} 
	match(failure > 0.5 * total) {
		true => {
			send(err("admission control"), APP)
		}
		false => {
			total = total + 1
			send(req, NET)
		}
	} 
}

fn resp(resp) {
		match(resp) => {
			Some(rpc_resp) => {
			    send(rpc_resp, APP)
			}
			Some(err(msg)) => {
				failure = failure + 1
				send(err(msg), app)
			}
		}
}