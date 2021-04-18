#!/usr/bin/python
import subprocess
from osinterface import Network

def run_shell_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return p.communicate()

def run_shell_cmd_stdout(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.STDOUT, shell=True)
    return p.communicate()


def network_retrieval_for_cent():
    network_list = []
    (cmd_out, error) = run_shell_cmd(['netstat -ltnp -A inet'])
    if error:
        raise Exception(error)
    records = cmd_out.splitlines()
    for record in records[2:]:
        parts = record.split()
        ip_port = parts[3].split(':')
        network_list.append(Network(parts[0], ip_port[0], ip_port[1], parts[6].split('/')[1]))
    return network_list
    
def convert_list_items_to_string(input_list):
    return_list = []
    for item in input_list:
        return_list.append(item.to_string())
    return return_list
