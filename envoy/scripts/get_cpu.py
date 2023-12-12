import subprocess
import statistics

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


if __name__ == '__main__':
    node_names = ['h2', 'h3']
    print("Collecting CPU usage (vCores):")
    print(get_virtual_cores(node_names, 64, 5))