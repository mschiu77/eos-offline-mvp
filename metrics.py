
import configparser
import os
import subprocess
import re
from distutils.version import StrictVersion

class OfflineMetrics():
    def __init__(self):
        self.metrics_cache_dir = '/var/cache/metrics'
        self.tracking_id_path = '/etc/metrics/tracking-id'
        self.machine_id_path = '/etc/machine-id'
        self.systemd_service = 'eos-metrics-event-recorder.service'
        self.metrics_config_file = '/etc/metrics/eos-metrics-permissions.conf'
        self.metrics_proc_name = 'eos-metrics-event-recorder'
        self.eos_version = None
        self.config = configparser.ConfigParser()
        self.config.read(self.metrics_config_file)

    def get_eos_version(self):
        f = open("/etc/os-release")
        for line in f.readlines():
            if line.startswith("VERSION="):
                fdot = line.find('=')
                major = line[fdot+2:-2]
                self.eos_version = major
                return str(major)

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

    def is_metrics_service_active(self):
        status = os.system('systemctl is-active --quiet ' + self.systemd_service)
        return (status == 0)
