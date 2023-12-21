import requests
import csv
import datetime
import time


def query_cpu_user(server_host):
    return f"""
    sum by(instance) (irate(node_cpu_seconds_total{{instance="{server_host}:9100",job="node", mode="user"}}[1m])) / 
    on(instance) group_left 
    sum by (instance)(irate(node_cpu_seconds_total{{instance="{server_host}:9100",job="node"}}[1m])) * 100
    """
def query_ram_used(server_host):
    return f"""
        node_memory_MemTotal_bytes{{instance="{server_host}:9100",job="node"}} - node_memory_MemFree_bytes{{instance="{server_host}:9100",job="node"}} - 
        (node_memory_Cached_bytes{{instance="{server_host}:9100",job="node"}} + node_memory_Buffers_bytes{{instance="{server_host}:9100",job="node"}} + 
        node_memory_SReclaimable_bytes{{instance="{server_host}:9100",job="node"}})
        """
def query_disk_used(server_host):
    return f"""
        100 - ((node_filesystem_avail_bytes{{instance="{server_host}:9100",job="node",device!~'rootfs'}} * 100) / 
        node_filesystem_size_bytes{{instance="{server_host}:9100",job="node",device!~'rootfs'}})
        """

# prometheus UTC시간 기준
def to_epoch(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt_utc = dt - datetime.timedelta(hours=9)  # KST -> UTC (한국 기준)
    return int(time.mktime(dt_utc.timetuple()))

filename = ["server_1.csv", "server_2.csv", "server_3.csv", "server_4.csv", "server_5.csv", "server_6.csv", "server_7.csv", "server_8.csv"]

server_list = list(enumerate(server_host_address))
for idx, counter in server_list:
    print(idx, counter)

start_time = "2023-12-16 09:00:00"
end_time = "2023-12-18 09:00:00"


# 에포크 타임스탬프로 변환(이렇게 설정한 시간사이) 즉:-9시간 계산해서 해야함.
start_epoch = to_epoch(start_time)
end_epoch = to_epoch(end_time)

# Prometheus 설정
prometheus_url = "http://10.10.20.138:9001/api/v1/query_range"



# 쿼리 매개변수 설정
def make_params(query):
    return {
        "query": query,
        "start": start_epoch,
        "end": end_epoch,
        "step": "60s"  # 1분 단위
        }

cpu_query = query_cpu_user(server_host_address)
params = make_params(cpu_query)
response = requests.get(prometheus_url, params=params)
data = response.json()

# print(cpu_query)
# print(params)
# print(response)
# print(data)


# # csv 저장 
# for metric_file, server_host in zip(filename, server_host_address):
#     # 데이터 요청
#     cpu_query = query_cpu_user(server_host_address)
#     params = make_params(cpu_query)
#     response = requests.get(prometheus_url, params=params)
#     data = response.json()
#     with open(metric_file, 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(['Metric', 'Timestamp', 'Value'])

#         for result in data['data']['result']:
#             metric = result['metric']
#             for value in result['values']:
#                 timestamp, metric_value = value
#                 writer.writerow([metric, datetime.datetime.fromtimestamp(int(timestamp)), metric_value])

