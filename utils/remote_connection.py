
from __future__ import with_statement

# from fabric.api import *
from fabric.api import hide
from fabric.api import run
from fabric.api import settings
from fabric.api import sudo
from fabric.api import put
from fabric.api import get
from fabric.state import connections


class RemoteConnection(object):
    def __init__(self, hostname, conn_config):
        self.hostname = hostname
        self.username = conn_config['system_username']
        self.use_sudo = conn_config['system_use_sudo']
        self.key_file = conn_config['key_file']


    # Do not print the command as it may have the secret stuff like password
    # or keys which we do not want in the logs
    def exec_secret_command(self, cmd, close_conn=True):
        with hide('running'):
            result = self.exec_command(cmd, close_conn)
            return result


    def exec_command(self, cmd, close_conn=True):
        try:
            if self.use_sudo:
                with settings(host_string=self.hostname, user=self.username, \
                         key_filename=self.key_file, warn_only=True):
                    result = sudo(cmd)
            else:
                with settings(host_string=self.hostname, user=self.username, \
                       key_filename=self.key_file, warn_only=True):
                    result = run(cmd)
        finally:
            if close_conn:
                self.close_connection()

        if result.return_code:
            print "Running command '" + cmd + "' failed with error '" + \
                str(result.return_code) + "' Stdout: " + result.stdout + \
                "\n Stderr: " + result.stderr
            raise Exception(result.stderr + result.stdout)
        return result

    def exec_batch(self, cmd_list, exit_on_fail=True):
        try:
            for cmd in cmd_list:
                self.exec_command(cmd, close_conn=False)
                # TODO : Check exit code and exit on failure
        finally:
            self.close_connection()

    def send_file(self, source_path, dest_path):
        try:
            with settings(host_string=self.hostname, user=self.username, key_filename=self.key_file):
                return put(source_path, dest_path, mirror_local_mode=True, use_sudo=self.use_sudo)
        finally:
            self.close_connection()

    def get_file(self, source_path, local_path):
        try:
            with settings(host_string=self.hostname, user=self.username, key_filename=self.key_file):
                return get(source_path, local_path)
        finally:
            self.close_connection()

    def close_connection(self):
        for key in connections.keys():
            if self.hostname in key:
                connections[key].close()
                del connections[key]
                break
