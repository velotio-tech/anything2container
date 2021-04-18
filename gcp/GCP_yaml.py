#!/usr/bin/python
# Import System Modules
import yaml

def generate_deployment_yaml(yaml_location, app_name, docker_image, disks, ports):
    data = {}
    data['apiVersion'] = 'extensions/v1beta1'
    data['kind'] = 'Deployment'
    data['metadata'] = {}
    data['metadata']['name'] = app_name
    data['metadata']['labels'] = {}
    data['metadata']['labels']['app'] = app_name
    data['spec'] = {}
    data['spec']['replicas'] = 1
    data['spec']['selector'] = {}
    data['spec']['selector']['matchLabels'] = {}
    data['spec']['selector']['matchLabels']['app'] = app_name
    data['spec']['template'] = {}
    data['spec']['template']['metadata'] = {}
    data['spec']['template']['metadata']['labels'] = {}
    data['spec']['template']['metadata']['labels']['app'] = app_name
    data['spec']['template']['spec'] = {}
    data['spec']['template']['spec']['containers'] = []
    container = {}
    container['image'] = docker_image
    container['name'] = app_name
    container['securityContext'] = {}
    container['securityContext']['privileged'] = True
    container['ports'] = []
    for port in ports:
        container['ports'].append({'containerPort': port})
    container['volumeMounts'] = []
    for volume_path, disk_name in disks.items():
        container['volumeMounts'].append({'name':'%s-%s' % (app_name, volume_path.replace('/', '-')), 'mountPath': "/%s" % volume_path})
    data['spec']['template']['spec']['containers'].append(container)
    data['spec']['template']['spec']['volumes'] = []
    for volume_path, disk_name in disks.items():
        volume = {}
        volume['name'] = '%s-%s' % (app_name, volume_path.replace('/', '-'))
        volume['gcePersistentDisk'] = {}
        volume['gcePersistentDisk']['pdName'] = disk_name
        volume['gcePersistentDisk']['fsType'] = 'ext4'
        data['spec']['template']['spec']['volumes'].append(volume)
        
    with open(yaml_location, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
        
def generate_service_yaml(yaml_location, app_name, ports):
    data = {}
    data['apiVersion'] = 'v1'
    data['kind'] = 'Service'
    data['metadata'] = {}
    data['metadata']['name'] = app_name
    data['metadata']['labels'] = {}
    data['metadata']['labels']['app'] = app_name
    data['spec'] = {}
    data['spec']['type'] = 'LoadBalancer'
    data['spec']['ports'] = []
    for port in ports:
        data['spec']['ports'].append({'port': port, 'name': '%s-%s' % (app_name, str(port))})
    data['spec']['selector'] = {}
    data['spec']['selector']['app'] = app_name
    
    with open(yaml_location, 'w') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
