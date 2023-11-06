// here we assume Random is global methods
internal {
	mirror_address: string
}

fn init(mirror_address) {
	mirror_address := 'xxx';
}

fn req(mirror_address, rpc_req) {
	send(rpc_req, NET);
	rpc_req.get('meta').get('dst').set(mirror_address);
	rpc_req.get('meta').get('src').set('');
	// todo! how to deal with rpc_id
	send(rpc_req, NET);
}

fn resp(rpc_resp) {
	send(rpc_resp, APP);
}