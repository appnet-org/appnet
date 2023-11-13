internal
{
    config: int
}

fn init() {
}


fn req(rpc_req) {

	match (rpc_req.get('A') == 1) {
		True => {
            alias := rpc_req;
            alias.set('C', '2');
			send(alias, NET);
		}
		False => {
            alias2 := rpc_req;
            temp2 := alias2.get('B');
            send(err(temp), APP);
		}
	};
    match (config == rpc.get('D')) {
		True => {
			send(rpc_req, NET);
		}
		False => {
            rpc_req.set('D', config);
		}
	};
}

fn resp(rpc_resp) {

}