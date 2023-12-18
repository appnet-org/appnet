import subprocess
import random
import statistics
import re

element_pool = ["fault", "cache", "ratelimit", "loadbalance", "logging", "mutation", 
                "accesscontrol", "metrics", "admissioncontrol", "compression", "encryption"]
# TODO: update the configuration dict. Add script to generate random configurations.
element_configs = {
    "fault": "probability=0.2",
    "cache": None,
    "ratelimit": "limit=50, token=5, per_sec=5",
    "loadbalance": None,
    "logging": None,
    "mutation": None,
    "accesscontrol": None,
    "metrics": None,
    "admissioncontrol": None,
    "compression": None,
    "encryption": None
}
position_pool = ["client", "server", "none"]

class Element:
    """Represents an element with a name, position, and optional configuration."""
    def __init__(self, name: str, position: str, config=None):
        self.name = name
        self.position = position
        self.config = config
    
    def add_config(self, config):
        """Adds or updates the configuration for the element."""
        self.config = config
        
    def __repr__(self):
        return f'Element(Name={self.name}, Position={self.position}, Configurations={self.config})'

def select_random_elements(number: int):
    """Selects a random number of elements with random positions."""
    # TODO(xz): also generate random configurations. They can be static for now.
    return [Element(name, position=random.choice(position_pool), config=element_configs[name]) 
            for name in random.sample(element_pool, number)]

def clean_up():
    # Clean up kubernetes deployments and wrks
    subprocess.run(["kubectl", "delete", "all", "--all"], stdout=subprocess.DEVNULL)

    wrk_pid = get_pid("wrk", allow_empty=True)
    if wrk_pid != -1:
        subprocess.run(["kill", "-9", str(wrk_pid)], stdout=subprocess.DEVNULL)

    time.sleep(20)

# Function to convert to microseconds
def convert_to_us(value, unit):
    if unit == 'ms':
        return float(value) * 1000
    elif unit == 's':
        return float(value) * 1000000
    else:  # 'us'
        return float(value)


def run_wrk_and_get_latency(duration=20):
    # TODO: Add script
    # wrk_cmd = ["./wrk/wrk", "-t 1", "-c 1", "-s <script>", "http://10.96.88.88:8080/ping-echo", "-d 800"]
    cmd = ["./wrk/wrk", "-t 1", "-c 1", "http://10.96.88.88:8080/ping-echo", "-d DURATION".replace("DURATION", str(duration)), "-L"]
    proc = subprocess.Popen(" ".join(cmd), shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the command to complete
    stdout_data, stderr_data = proc.communicate()

    # Check if there was an error
    if proc.returncode != 0:
        print("Error executing wrk command:")
        print(stderr_data.decode())
    else:
        # Parse the output
        output = stdout_data.decode()
        print("Command output:")
        print(output)
        
        # Regular expressions to find the results
        latency_50_pattern = r"50%\s+(\d+\.?\d*)(us|ms|s)"
        latency_99_pattern = r"99%\s+(\d+\.?\d*)(us|ms|s)"
        avg_latency_pattern = r"Latency\s+(\d+\.?\d*)(us|ms|s)"
        req_sec_pattern = r"Requests/sec:\s+(\d+\.?\d*)"

        # Search for patterns and convert to microseconds
        latency_50_match = re.search(latency_50_pattern, output)
        latency_50 = convert_to_us(*latency_50_match.groups()) if latency_50_match else "Not found"

        latency_99_match = re.search(latency_99_pattern, output)
        latency_99 = convert_to_us(*latency_99_match.groups()) if latency_99_match else "Not found"

        avg_latency_match = re.search(avg_latency_pattern, output)
        avg_latency = convert_to_us(*avg_latency_match.groups()) if avg_latency_match else "Not found"

        req_sec = re.search(req_sec_pattern, output)
        req_sec = req_sec.group(1) if req_sec else "Not found"

        # Print the extracted and converted data
        print("50% Latency (us):", latency_50)
        print("99% Latency (us):", latency_99)
        print("Average Latency (us):", avg_latency)
        print("Requests per second:", req_sec)


def get_virtual_cores(node_names, core_count, duration):
    print("Running mpstat...")
    total_util = []
    for node_name in node_names:
        cmd = ['ssh', node_name, 'mpstat', '1', str(duration)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        result_average = result.stdout.decode("utf-8").split('\n')[-2].split()
        per_node_util = 100.00 - float(result_average[-1])
        total_util.append(per_node_util)
        
    virtual_cores = sum(total_util)*core_count/100
    return virtual_cores   


def run_wrk2_and_get_cpu(node_names, cores_per_node=64, mpstat_duration=30, wrk2_duration=60, target_rate=2000):
    # cmd = ["./wrk2/wrk", "-t 2", "-c 100", "-s benchmark/wrk_scripts/echo_workload/echo_workload_PROTOCOL_SIZE.lua".replace("PROTOCOL", protocol).replace("SIZE", str(request_size)), "http://10.96.88.88:80", "-d 800", "-R "+str(target_rate)]
    cmd = ["./wrk2/wrk", "-t 10", "-c 100", "http://10.96.88.88:8080/ping-echo", "-d DURATION".replace("DURATION", str(wrk2_duration)), "-R "+str(target_rate)]
    proc = subprocess.Popen(" ".join(cmd), shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("Collecting CPU usage (vCores):")
    print(get_virtual_cores(node_names, cores_per_node, mpstat_duration))
    
    # Terminate the process and wait for the process to actually terminate
    proc.terminate()
    proc.wait()


    

selected_elements = select_random_elements(3)
print(selected_elements)
run_wrk_and_get_latency()
run_wrk2_and_get_cpu(node_names=['h2', 'h3'])
