import re

# Function to convert to microseconds
def convert_to_us(value, unit):
    if unit == 'ms':
        return float(value) * 1000
    elif unit == 's':
        return float(value) * 1000000
    else:  # 'us'
        return float(value)

# Sample output
output = """
Running 20s test @ http://10.96.88.88:8080/ping-echo
  1 threads and 1 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   400.25us   61.65us   1.29ms   77.02%
    Req/Sec     2.50k    28.53     2.60k    66.17%
  Latency Distribution
     50%  384.00ms
     75%  445.00us
     90%  469.00us
     99%  5.00s
  49908 requests in 20.10s, 5.66MB read
Requests/sec:   2482.97
Transfer/sec:    288.55KB
"""

# Regular expressions to find the required data with different units
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
