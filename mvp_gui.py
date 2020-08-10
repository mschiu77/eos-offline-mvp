#!/usr/bin/python3

import argparse
import configparser
import dbus
import sys
import os
import subprocess
import shutil

from metrics import MVPUploader, MVPCollector

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class OfflineMVPWindow(Gtk.Window):
    def __init__(self, usbpath):
        super().__init__()
        self.init_app_ui()
        self.usbpath = usbpath

    def dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            print("OK")
        widget.destroy()

    def show_message(self, message=None):
        messagedialog = Gtk.MessageDialog(parent=self,
                                modal=True,
                                message_type=Gtk.MessageType.WARNING,
                                buttons=Gtk.ButtonsType.OK,
                                text=message)
        # connect the response (of the button clicked) to the function
        # dialog_response()
        messagedialog.connect("response", self.dialog_response)
        # show the messagedialog
        messagedialog.show()

    def init_app_ui(self):
        grid = Gtk.Grid()
        self.add(grid)

        collectBtn = Gtk.Button(label="Collect")
        collectBtn.set_size_request(120, 50)
        collectBtn.connect("clicked", self.on_collect_clicked)

        uploadBtn = Gtk.Button(label="Upload")
        uploadBtn.set_size_request(120, 50)
        uploadBtn.connect("clicked", self.on_upload_clicked)

        grid.attach(collectBtn, 0, 0, 1, 1)
        grid.attach(uploadBtn, 1, 0, 1, 1)

        self.set_border_width(10)
        self.set_title("Offline MVP tool")
        self.set_default_size(280, 100)
        self.connect("destroy", self.on_destroy)

    def on_destroy(self, widget):
        subprocess.check_output(['/usr/bin/systemctl', 'restart', METRICS_SYSTEMD_SERVICE])
        Gtk.main_quit()

    def on_collect_clicked(self, widget):
        subprocess.check_output(['/usr/bin/systemctl', 'stop', METRICS_SYSTEMD_SERVICE])
        ##location = os.path.dirname(os.path.realpath(sys.argv[0]))
        collector = MVPCollector(self.usbpath)
        disk_usage = shutil.disk_usage(self.usbpath)
        if (disk_usage.free > 10 * 1024 * 1024):
            collector.copy_data()
            self.show_message("Copy Done")
        else:
            self.show_message("Insufficient free space.")

    def on_upload_clicked(self, widget):
        subprocess.check_output(['/usr/bin/systemctl', 'stop', METRICS_SYSTEMD_SERVICE])
        #uploader = MVPUploader('/media/dev/BIOSUP')
        uploader = MVPUploader(self.usbpath)
        try:
            uploader.copy_metrics_data_and_upload()
            self.show_message("Upload Done")
        except:
            self.show_message("Upload Fail. Please check the internet")

METRICS_SYSTEMD_SERVICE = 'eos-metrics-event-recorder.service'

def main():
    '''
    TODO: launch File Manager for users?
    '''
    parser = argparse.ArgumentParser(
    description='The standalone tool to collect and upload metrics data.'
                'Specify the path for the USB storate which users want'
                'to do either collect or upload')
    parser.add_argument('-u', '--usbpath', type=str, required=False,
                        help='Specify the mount point of the USB storage')
    args=parser.parse_args()
    ##location = os.path.dirname(os.path.realpath(sys.argv[0]))
    win = OfflineMVPWindow(args.usbpath)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
