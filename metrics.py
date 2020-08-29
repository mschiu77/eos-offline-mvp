
import configparser
import sys
import os
import subprocess
import time
import shutil

class EOSMetrics():
    def __init__(self):
        self.metrics_cache_dir = '/var/cache/metrics'
        self.tracking_id_path = '/etc/metrics/tracking-id'
        self.machine_id_path = '/etc/machine-id'
        self.systemd_service = 'eos-metrics-event-recorder.service'
        self.metrics_config_file = '/etc/metrics/eos-metrics-permissions.conf'
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

    def get_service_state(self):
        status = os.system('systemctl is-active --quiet ' + self.systemd_service)
        return (status)
