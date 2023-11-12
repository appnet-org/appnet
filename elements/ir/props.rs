internal
{
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
            temp := alias2.get('B');
            send(err(temp), APP);
		}
	};
}

fn resp(rpc_resp) {

}