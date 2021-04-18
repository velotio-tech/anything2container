#!/usr/bin/python
from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import subprocess
import time

def create_new_disk(disk_name, disk_size, zone):
    """
    credentials = GoogleCredentials.get_application_default()

    print("Credentials:", credentials)
    service = discovery.build('compute', 'v1', credentials=credentials)

    # Project ID for this request.
    project = project_name
    
    # The name of the zone for this request.
    zone = zone

    disk_body = {
        "sizeGb":disk_size,
        "name":disk_name

    }

    request = service.disks().insert(project=project, zone=zone, body=disk_body)
    response = request.execute()
    pprint(response)
    time.sleep(20)
    """
    cmd = "gcloud compute disks create %s --size=%sGB --zone=%s" % (disk_name, disk_size, zone)
    result = subprocess.Popen(cmd, shell=True)
    result.communicate()
    if(result.returncode == 0):
        print("Disk Created Succesfully")
        time.sleep(20)
        return True
    else:
        return False
    

def authorize_gcloud(json_file_path="/tmp/Velotio-d5a284fc39a2.json"):
    activate_account_cmd = "gcloud auth activate-service-account --key-file=%s" % json_file_path
    activate = subprocess.Popen(activate_account_cmd, shell=True)
    activate.communicate()
    if(activate.returncode == 0):
        return True
    else:
        raise Exception("gcloud authentication failed")


def attach_disk(instance, disk_name, zone):
    
    cmd = "gcloud compute instances attach-disk %s --disk=%s --zone=%s" % (instance, disk_name, zone)
    result = subprocess.Popen(cmd, shell=True)
    result.communicate()
    if(result.returncode == 0):
        print("Disk Attached Succesfully")
        return True
    else:
        return False

def get_unmounted_disk():
    res = subprocess.check_output("lsblk" " -l --nodeps -n --include 8,65,66,67,68,69,70,71,128,129,130,131,132,133,134,135,202,253 "
                             "| grep -v 'SWAP' | awk '{if($6==\"disk\"){print $1}}'", shell=True)
    # disk_mounted = subprocess.check_output("mount | awk '{print $1}' | sort | uniq", shell=True)
    sdisk = res.strip()
    vdisk = sdisk.split()
    for disk in vdisk:
        cmd = "mount | awk '{print $1}' | sort | uniq | grep %s" % disk
        disk_mounted = subprocess.Popen(cmd, shell=True)
        disk_mounted.communicate()
        if disk_mounted.returncode == 0:
            continue
        else:
            return disk

def mount_disk(device_id, mount_point="/tmp/test_data"):
    cmd = "sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/%s" % device_id
    result = subprocess.Popen(cmd, shell=True)
    result.communicate()
    if(result.returncode == 0):
        print "success"
        cmd = "mkdir -p %s" % mount_point
        subprocess.Popen(cmd, shell=True)
        cmd = "mount -o discard,defaults /dev/%s %s" % (device_id, mount_point)
        mount = subprocess.Popen(cmd, shell=True)
        mount.communicate()
        if(mount.returncode == 0):
            print("Mount Completed Suucessfully")
            subprocess.Popen("sudo chmod a+w %s" % mount_point, shell=True)
            return True
        else:
            print("Some Error!!")
            return False

    else:
        print False

def unmount_disk(mount_path):
    cmd = "sudo umount -l %s" % mount_path
    unmount = subprocess.Popen(cmd, shell=True)
    unmount.communicate()
    if(unmount.returncode == 0):
        print"Unmounted!!"
        return True
    else:
        print("Error in unmount disk!!")
        return False

def detach_disk(hostname, disk_name, zone):
    cmd = "gcloud compute instances detach-disk %s --disk=%s --zone=%s" % (hostname, disk_name, zone)
    detached = subprocess.Popen(cmd, shell=True)
    detached.communicate()
    if(detached.returncode == 0):
        print "Detached"
        return True
    else:
        print "Error"
        return False

def volume_data_copy(user, key, target_ip, image_name, volumes, hostname, project_name, zone, size=10):
    created_disks = {}
    i = 0
    authorize_gcloud()
    for volume in volumes:
        disk_name = "%s-" % image_name + str(i)
        print "for volume %s" % volume
        print "Creating disk %s" % disk_name
        create_new_disk(disk_name, size, zone)
        print "Attaching disk"
        disk_attached = attach_disk(hostname, disk_name, zone)
        if(disk_attached):
            mount_point = '/tmp/test_data'
            print "Mounting disk"
            unmounted_disk = get_unmounted_disk()
            disk_mounted = mount_disk(unmounted_disk, mount_point)
            if(disk_mounted):
                print "transferring data from source"
                cmd = "rsync -a -e 'ssh -i %s' %s@%s:/%s/ %s/" % (key, user, target_ip, volume, mount_point)
                # remote_conn.get_file("/%s/*" % volume, mount_point)
                copied = subprocess.Popen(cmd, shell=True)
                copied.communicate()
                if(copied.returncode == 0):
                    print "Detached"
                created_disks[volume] = disk_name
                i = i + 1
                print "unmounting disk"
                if(unmount_disk(mount_point)):
                    print "detaching disk"
                    detach_disk(hostname, disk_name, zone)


    return created_disks
