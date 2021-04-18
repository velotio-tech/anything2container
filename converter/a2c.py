#!/usr/bin/python
"""
Main utility to do contenarization of vm
"""
# Import local
from metadata import generate_metadata
from util import run_shell_cmd
# Import system
import argparse
import yaml
# import tarfile
import os
import ast
# import stat
from io import BytesIO
# Import 3rd party
from docker import Client

def main():
    ""
    ""
    parser = argparse.ArgumentParser(description='A2C Converter for any given Application')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration file for contenarization')
    parser.add_argument('-d', '--dockerendpoint', required=True,
                        help='Dockerendpoint to be used for image creation')
    parser.add_argument('-i', '--imagename', required=True,
                        help='Name of be assigned to created docekr image')
    parser.add_argument('-p', '--projectname', required=True,
                        help='Name of the GCP Project')
    pargs = parser.parse_args()
    
    config = yaml.load(open(pargs.config, 'r'))
    
    excludes = config['excludes'] + config['volumes']
    print "excluding directories %s" % " ".join(excludes)
    print "creating tar file"
    tarfilepath = os.path.join('/tmp', '%s.tar.gz' % pargs.imagename)
    """
    # Filter out the volume and excludes path from tar
    def filter_files(tarinfo):
        if tarinfo.mode & stat.S_IRUSR == 0:
            print "Cannot read file %s. Ignoring!" % tarinfo.name
            return None
        if tarinfo.name in excludes:
            print "Excluding %s" % tarinfo.name
            return None
        print "Included %s" % tarinfo.name
        return tarinfo
    # Create tar from the given includes list of paths
    tarobject = tarfile.TarFile.gzopen(tarfilepath, 'w', compresslevel=1)
    for path in config['includes']:
        tarobject.add(path, filter=filter_files)
    tarobject.close()
    """
    exclude_cmd = ""
    for path in excludes:
        exclude_cmd = exclude_cmd + " --exclude=%s" % path
        
    run_shell_cmd(['export GZIP=-1; tar -pczf %s --directory=/ %s /' % (tarfilepath, exclude_cmd)])
    print "finished creating tar file"
    print "creating docker image"
    client = Client(base_url=pargs.dockerendpoint, timeout=10000)
    result = client.import_image(src=tarfilepath, repository=pargs.imagename)
    """
    Result comes in the following format
    {"status":"sha256:7cf833972ae093a33e8ec1a14d2669f62574590511087e2fbf64958d6765e80c"}
    """
    result = ast.literal_eval(result)
    imageid = result['status'].rsplit("sha256:")[1]
    print "image created with id %s" % imageid
    print "Collecting metadata for image"
    metadata = generate_metadata(config)
    print metadata
    filecontent = '''
    FROM %s
    CMD ["%s"]
    LABEL %s
    '''
    label = ""
    for key, value in metadata.items():
        label = label + ' %s="%s"' % (key, value)
    filecontent = filecontent % (imageid, metadata['initpath'], label)
    dockerfile = BytesIO(filecontent.encode('utf-8'))
    
    print "Building image from metadata"
    tag = "us.gcr.io/%s/%s" % (pargs.projectname, pargs.imagename)
    response = [line for line in client.build(fileobj=dockerfile, tag=tag, rm=True)]
    print response
    
if __name__ == "__main__":
    main()
