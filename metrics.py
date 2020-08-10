
import configparser
import sys
import os
import subprocess
import time
import shutil


class MVPCollector():
    OFFLINE_METRICS_DIR = 'eos-metrics-data-1'
    METRICS_CACHE_DIR = '/var/cache/metrics'
    OFFLINE_METRICS_DEVICE_PATH = None
    OFFLINE_METRICS_DATA_PATH = None
    TRACKING_ID_PATH = '/etc/metrics/tracking-id'
    MACHINE_ID_PATH = '/etc/machine-id'

    def __init__(self, storage_path=None):
        if storage_path is None:
            ''' 
            TODO: Use dialog window instead
            '''
            print('Please assign the metrics data storage path')
        else:
            self.OFFLINE_METRICS_DEVICE_PATH= storage_path

    def check_eos_event_recorder_daemon_version(self):
        print('Not yet implemented')

    def check_available_space(self):
        print('Not yet implemented')

    def check_if_duplicate(self, path = None):
        '''
        Check if directory name (tracking id) is duplicate
        '''
        print('Not yet implemented')

    def create_folder_for_machine(self):
        target_dir = os.path.join(self.OFFLINE_METRICS_DEVICE_PATH, self.OFFLINE_METRICS_DIR)
        if os.path.exists(target_dir) is False:
            os.mkdir(target_dir)

        if os.path.exists(self.TRACKING_ID_PATH) is True:
            f = open(self.TRACKING_ID_PATH)
            self.OFFLINE_METRICS_DATA_PATH = os.path.join(target_dir, f.read(32))
            if os.path.exists(self.OFFLINE_METRICS_DATA_PATH) is False:
                os.mkdir(self.OFFLINE_METRICS_DATA_PATH)
            else:
                subprocess.check_output(['sudo', 'rm', '-rf', self.OFFLINE_METRICS_DATA_PATH])
                os.mkdir(self.OFFLINE_METRICS_DATA_PATH)
            f.close()
        elif os.path.exists(self.MACHINE_ID_PATH) is True:
            f = open(self.MACHINE_ID_PATH)
            self.OFFLINE_METRICS_DATA_PATH = os.path.join(target_dir, f.read(32))
            if os.path.exists(self.OFFLINE_METRICS_DATA_PATH) is False:
                os.mkdir(self.OFFLINE_METRICS_DATA_PATH)
            else:
                subprocess.check_output(['sudo', 'rm', '-rf', self.OFFLINE_METRICS_DATA_PATH])
                os.mkdir(self.OFFLINE_METRICS_DATA_PATH)
            f.close()
        else:
            print('There is no metrics data available')

    def copy_tracking_id(self):
        if os.path.exists(self.TRACKING_ID_PATH) is True:
            # The tracking id file has permission -rwxrwsr-x  which
            # will raise PermissionError for shutil.copy, use copyfile
            # instead
            shutil.copyfile(self.TRACKING_ID_PATH, os.path.join(self.OFFLINE_METRICS_DATA_PATH, os.path.basename(self.TRACKING_ID_PATH)))
        elif os.path.exists(self.MACHINE_ID_PATH) is True:
            shutil.copy(self.MACHINE_ID_PATH, self.OFFLINE_METRICS_DATA_PATH)
        else:
            printf('No tracking ID found')

    def copy_metrics_data(self):
        files = ['boot_offset_metafile', 'network_send_file', 'variants.dat', 'variants.dat.metadata']
        for file in files:
            shutil.copyfile(os.path.join(self.METRICS_CACHE_DIR, file), os.path.join(self.OFFLINE_METRICS_DATA_PATH, os.path.basename(file)))

    def check_disk_usage(self):
        print('Constructing')

    def copy_data(self):
        self.create_folder_for_machine()
        self.copy_tracking_id()
        self.copy_metrics_data()


class MVPUploader():
    OFFLINE_METRICS_DIR = 'eos-metrics-data'
    OFFLINE_TMP_METRICS_DIR = '/var/tmp/metrics'
    OFFLINE_STORAGE_PATH = None

    def __init__(self, storage_path=None):
        if storage_path is None:
            ''' 
            TODO: Use dialog window instead
            '''
            print('Please give the metrics data storage path')
        else:
            self.OFFLINE_STORAGE_PATH = storage_path

    def check_upload_result(self):
        '''
        Check if the upload successful or not
        '''
        print('Constructing')

    def remove_offline_metrics(self):
        '''
        Remove the data after upload done
        '''
        print('Constructing')

    def check_os_version(self):
        '''
        We need the MVP tool run on > eos 3.9 for the upload
        '''
        os_version = configparser.ConfigParser()
        os_version.read('/etc/os-release')
        print(os_version)

    def copy_metrics_data_and_upload(self):
        eos_metrics_data_dir=os.path.join(self.OFFLINE_STORAGE_PATH, self.OFFLINE_METRICS_DIR)
        for target in os.listdir(eos_metrics_data_dir):
            # TODO: only iterates for directories
            print("Directory %s:" % target)
            os.mkdir(self.OFFLINE_TMP_METRICS_DIR)
            target_dir=os.path.join(eos_metrics_data_dir, target)
            for file in os.listdir(os.path.join(eos_metrics_data_dir, target)):
                shutil.copy(os.path.join(target_dir, file), self.OFFLINE_TMP_METRICS_DIR)
            subprocess.Popen(['sudo', 'chown', '-R', 'metrics:metrics', self.OFFLINE_TMP_METRICS_DIR])
            persistent_cache_dir_arg = '--persistent-cache-directory=' + self.OFFLINE_TMP_METRICS_DIR
            tracking_id_path_arg = '--tracking-id-file-path=' + self.OFFLINE_TMP_METRICS_DIR
            #self.daemon = subprocess.Popen(['sudo', '-u', 'metrics', '/lib/eos-event-recorder-daemon/eos-metrics-event-recorder', persistent_cache_dir_arg, tracking_id_path_arg])
            self.daemon = subprocess.Popen(['sudo', '-u', 'metrics', '/lib/eos-event-recorder-daemon/eos-metrics-event-recorder', persistent_cache_dir_arg])
            #self.check_os_version()

            time.sleep(3)
            try: 
                subprocess.check_output(['/usr/bin/eos-upload-metrics'])
            except subprocess.CalledProcessError as e:
                raise RuntimeError ('Upload Fail')
            #self.daemon.kill()
            subprocess.check_output(['sudo', 'killall', '/lib/eos-event-recorder-daemon/eos-metrics-event-recorder'])

            subprocess.check_output(['sudo', 'rm', '-rf', self.OFFLINE_TMP_METRICS_DIR])

    def __del__(self):
        '''
        Remove temporary cache data
        '''
        subprocess.check_output(['sudo', 'rm', '-rf', self.OFFLINE_TMP_METRICS_DIR])

