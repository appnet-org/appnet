internal {
	prob: float
}
fn init(prob) {
	prob := 0.9;
}

fn req(rpc_req) {
	match(randomf(0,1) < prob) {
		True => {
			send(rpc_req, NET);
		}
		False => {
			send(err('fault_injected'), APP);
		}
	};
}

fn resp(rpc_resp) {
    send(rpc_resp, APP);
}