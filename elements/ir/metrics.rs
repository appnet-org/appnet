internal 
{
	map<int, int> record
  vector<int> latency
}

fn init() {
}

fn req() {
	write(record, rpc_req.id, current_timestamp())
	send(rpc_req, NET)
}

fn resp() {
  rpc_id = get(rpc_resp, "id")
  latency = currentimestamp() - get(record, rpc_id)
  write(vector, latency)
}