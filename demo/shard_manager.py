import os
import time, yaml
import requests

key_server_map = {}

def shard_manager():
    with open('shard.yaml', 'r') as file:
        yaml_content = file.read()
        # Load the YAML content
    data = yaml.safe_load(yaml_content)

    # Iterate over the server replicas to populate the map
    lua_script= """
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: echo-lua-extension
spec:
  workloadSelector:
    labels:
      app: frontend
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_OUTBOUND
      listener:
        portNumber: 9000
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
            subFilter:
              name: "envoy.filters.http.router"
    patch:
      operation: INSERT_BEFORE
      value: 
       name: envoy.lua
       typed_config:
          "@type": "type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua"
          inlineCode: |
            function envoy_on_request(handle)
            handle:logWarn(" ============= envoy_on_request ============= ")
            local key = handle:headers():get("key")
            if key then
                local server_name

                -- Assuming 'key' can be converted to a number and determining the server name based on key ranges
                key = tonumber(key)
    """
    for server in data['Sharded-service']['server replicas']:
        server_name = server['Name']
        for shard in server['shards']:
            # Get the range of keys for the shard
            # Map each key in the range to the server name
            key_range_start = shard['range'][0]
            key_range_end = shard['range'][1]

            lua_script += f"""
                if key >= {key_range_start} and key <= {key_range_end} then
                server_name = "{server_name}"
                end
            """
    lua_script += """
                -- Inject a header with the server name into the request
                handle:headers():add("x-server-name", server_name)

                -- Log the server name that was added to the headers
                handle:logWarn("Server name added to header: " .. server_name)
            else
                handle:logWarn("Key not found in request")
            end

            handle:logWarn(" ============================================= ")
            end

            function envoy_on_response(handle)
            handle:logWarn(" ============= envoy_on_response ============= ")
            handle:logWarn(" ============================================= ")
            end
    """
    
    with open('generated_envoy_lua_script.yaml', 'w') as lua_file:
        lua_file.write(lua_script)
    
    import subprocess

    try:
        result = subprocess.run(['kubectl', 'apply', '-f', 'generated_envoy_lua_script.yaml'], 
                        check=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.STDOUT)
        # print(result)
        print("Successfully applied the configuration.")
    except subprocess.CalledProcessError as e:
        print("Failed to apply the configuration:", e)

def watch_file(file_path, interval=1):
    """
    Watches for changes in the file's last modification time.
    :param file_path: Path to the file to be monitored.
    :param interval: Polling interval in seconds.
    """
    last_modified = os.path.getmtime(file_path)

    while True:
        try:
            current_modified = os.path.getmtime(file_path)
            if current_modified != last_modified:
                print(f"File {file_path} has been modified.")
                shard_manager()
                last_modified = current_modified
            else:
                print(f"No change detected in {file_path}.")
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            break  # Exit the loop if the file does not exist

        time.sleep(interval)

# Example usage:
# Replace 'path/to/your/file.txt' with the actual file path you want to monitor
shard_manager()
watch_file('shard.yaml')
