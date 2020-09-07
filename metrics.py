
import configparser
import sys
import os
import subprocess
import time
import shutil
import re

class EOSMetrics():
    def __init__(self):
        self.metrics_cache_dir = '/var/cache/metrics'
        self.tracking_id_path = '/etc/metrics/tracking-id'
        self.machine_id_path = '/etc/machine-id'
        self.systemd_service = 'eos-metrics-event-recorder.service'
        self.metrics_config_file = '/etc/metrics/eos-metrics-permissions.conf'
        self.metrics_proc_name = 'eos-metrics-event-recorder'
        self.eos_version = float(0)
        self.config = configparser.ConfigParser()
        self.config.read(self.metrics_config_file)

    def	get_eos_version(self):
        f = open("/etc/os-release")
        for line in f.readlines():
            if line.startswith("VERSION="):
                fdot = line.find('=')
                ldot = line.rfind('.')
                major = line[fdot+2:ldot]
                self.eos_version = major
                return float(major)

    def get_upload_enable_config(self):
        print(self.config.get("global", "uploading_enabled"))

    def get_environment_config(self):
        print(self.config.get("global", "environment"))

    def metrics_proc_exists(self):
        ps = subprocess.Popen("ps ax -o pid= -o args= ", shell=True, stdout=subprocess.PIPE)
        ps_pid = ps.pid
        output = ps.stdout.read()
        ps.stdout.close()
        ps.wait()

        for line in str(output).split('\n'):
            res = re.findall("(\d+) (.*)", line)
            if res:
                pid = int(res[0][0])
                if self.metrics_proc_name in res[0][1] and pid != os.getpid() and pid != ps_pid:
                    return True
            return False

    def get_service_state(self):
        status = os.system('systemctl is-active --quiet ' + self.systemd_service)
        return (status)
