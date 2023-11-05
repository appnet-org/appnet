internal 
{
	record: map<int, int>
  latency: vec<int>
}

fn init() {
}

fn req(rpc_req) {
	record.set(rpc_req.get('meta').get('id'), current_timestamp());
	send(rpc_req, NET);
}

fn resp(rpc_resp) {
  rpc_id := rpc_resp.get('id')
  lat := curren_time() - rec_record.get(rpc_id)
  latency.set(latency.size(), lat);
}