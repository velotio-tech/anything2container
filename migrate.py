#!/usr/bin/python
# Import system
import argparse
import yaml
# Import Local
from utils.remote_connection import RemoteConnection
from converter import util
from gcp.GCPClient import volume_data_copy
from gcp.GCP_yaml import  generate_deployment_yaml
from gcp.GCP_yaml import generate_service_yaml
from utils.docker_client import get_port_list


def main():
    ""
    ""
    parser = argparse.ArgumentParser(description='A2C Converter for any given Application')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file for contenarization')
    parser.add_argument('-d', '--dockerremote', required=True,
                        help='Remote docker endpoint to be used for image creation')
    parser.add_argument('-i', '--imagename', required=True,
                        help='Name of be assigned to created docekr image')
    parser.add_argument('-p', '--projectname', required=True,
                        help='Name of the GCP Project')
    parser.add_argument("source",
                        help='Host Application IP to be containerized')
    parser.add_argument('-u', '--user', required=True,
                        help='Host Application user name with sudo access')
    parser.add_argument('-k', '--keyfile', required=True,
                        help='Host application key for given user name')
    parser.add_argument('-l', '--localhostname', required=False,
                        help='HostName of GCP server running this code')
    parser.add_argument('--gcecluster', required=True,
                        help='Name of the container cluster in GCE to be used for deployment')
    parser.add_argument('--gcezone', required=True,
                        help='Name of the Google Cloud Zone to be used for creating resources. Should match zone of container cluster')
    pargs = parser.parse_args()

    if pargs.localhostname is None:
        pargs.localhostname = 'a2chost'    
    config = yaml.load(open(pargs.config, 'r'))
    docker_tag = 'us.gcr.io/%s/%s' % (pargs.projectname, pargs.imagename)
    
    remote_conn = get_remote_connection(pargs.source, pargs.user, pargs.keyfile)
    print "Pushing converter binary to target machine"
    push_converter_to_remote(remote_conn)
 
    print "Pushing data config to target machine"
    push_config_to_remote(remote_conn, pargs.config)
 
    print "Pushing installer script to target machine"
    run_installer_on_remote(remote_conn)
 
    print "Running converter binary on target machine"
    run_converter_on_remote(remote_conn, pargs.dockerremote, pargs.imagename, pargs.projectname)
 
    print "Pushing the docker image to GCP container registry"    
    util.run_shell_cmd('gcloud docker -- push %s' % docker_tag)
 
    print "Initiate remote data copy"
    disks = {}
    if config['volumes']:
        disks = volume_data_copy(pargs.user, pargs.keyfile, pargs.source, pargs.imagename, config['volumes'], pargs.localhostname, pargs.projectname, pargs.gcezone) 
    service_file_location = '/tmp/gcp-service.yaml'
    deployment_file_location = '/tmp/gcp-deployment.yaml'
    ports = get_port_list(pargs.dockerremote, docker_tag)
    generate_deployment_yaml(deployment_file_location, pargs.imagename, docker_tag, disks, ports)
    generate_service_yaml(service_file_location, pargs.imagename, ports)
    
    print "Connecting to GCP cluster for deployment"
    util.run_shell_cmd("gcloud container clusters get-credentials %s --zone %s --project %s" % (pargs.gcecluster,
                                                                pargs.gcezone, pargs.projectname))
    print "Creating deployment on container cluster"
    util.run_shell_cmd('kubectl create -f %s' % deployment_file_location)
 
    print "Creating service on container cluster"
    util.run_shell_cmd('kubectl create -f %s' % service_file_location)
 
    print "Printing list of running pods"
    (response, _) = util.run_shell_cmd('kubectl get pod')
    print response
 
    print "Printing list of deployments"
    (response, _) = util.run_shell_cmd('kubectl get deployment')
    print response
 
    print "Printing list of services"
    (response, _) = util.run_shell_cmd('kubectl get service')
    print response
 
    print "All Done! Please check your container cluster for more details"
    
    
if __name__ == "__main__":
    main()


def get_remote_connection(hostname, user, keyfile):
    conn_config = {}
    conn_config['system_username'] = user
    conn_config['system_use_sudo'] = True
    conn_config['key_file'] = keyfile
    rc = RemoteConnection(hostname, conn_config)
    return rc

def push_converter_to_remote(remote_conn):
    remote_conn.send_file('converter', '/tmp')
    
def push_config_to_remote(remote_conn, config):
    remote_conn.send_file(config, '/tmp/data_handler.yml')
    
def run_installer_on_remote(remote_conn):
    cmd = "/tmp/converter/remote_install.sh"
    remote_conn.exec_command(cmd)
    
def run_converter_on_remote(remote_conn, dockerremote, image_name, project_name):
    cmd = "/tmp/converter/a2c.py -c /tmp/data_handler.yml -d %s -i %s -p %s" % (dockerremote, image_name, project_name)
    remote_conn.exec_command(cmd)
