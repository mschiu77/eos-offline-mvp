#!/bin/bash -e

USB_DISK_NUM=0


prompt_input()
{
    echo "
	 "
    read -p "Please enter the disk number you want to create for metrics? [] "
    response="${REPLY,,}" # to lower
    if [[ ! "$response" =~ ^[1-9]$ ]]; then
        echo " Please re-input your selection "
        prompt_input
    fi 
    if [ $((response)) -gt $((USB_DISK_NUM)) ]; then
        echo " Please re-input your selection "
        prompt_input
    fi

    USER_CHOICE=$response
}

for device in /sys/block/*
do
    if udevadm info --query=property --path=$device | grep -q ^ID_BUS=usb
    then
        DISK[$USB_DISK_NUM]="/dev/${device##*/}"
        ((USB_DISK_NUM=USB_DISK_NUM+1)) 
        echo "$USB_DISK_NUM) / ${DISK[$((USB_DISK_NUM-1))]}"
        echo "`lsblk -o name,label /dev/${device##*/}`"
    fi
done

if [ $USB_DISK_NUM -eq 0 ]; then
    echo "Please plug in the USB storage device."
    exit 1
fi

prompt_input

TARGET_DISK=${DISK[$((USER_CHOICE-1))]}

echo "disk name $TARGET_DISK"
MOUNTPOINT=$(grep "$TARGET_DISK" /proc/mounts | cut -f1 -d' ' | tr '\n' ' ')
if test -n "$MOUNTPOINT" -a -d "$MOUNTPOINT"
then
	umount -f -q $MOUNTPOINT
fi

TABLE=$(sfdisk -d "$TARGET_DISK")
HEADER=$(echo "$TABLE" | grep -v '^/')
# Remove the last-lba line so that we fill the disk
HEADER=$(echo "$HEADER" | sed -e '/^last-lba:/d')

# Prepend our partition
PARTS="start=2048, name=EOSMETRICS, type=EBD0A0A2-B9E5-4433-87C0-68B6B72699C7
$PARTS"

echo $HEADER

echo $PARTS
# Reconstruct the table
TABLE="$HEADER
$PARTS"

echo "$TABLE" | sfdisk --force --no-reread "$TARGET_DISK"
PART=$(sfdisk -d "$TARGET_DISK" | grep 'EOSMETRICS' | cut -f1 -d' ')

mkfs.vfat -n EOSMETRICS "$PART"

# Give udisks a chance to notice the new partition
partprobe "$TARGET_DISK"
udevadm settle

# Try to mount the fat32 partition
udisksctl mount -b "$PART" --no-user-interaction || exit 1
# Grab the mount point
TARGET_MOUNTPOINT=$(grep "$PART" /proc/mounts | cut -f2 -d' ')
if test -n "$TARGET_MOUNTPOINT" -a -d "$TARGET_MOUNTPOINT"
then
  # Copy the script files here.
  cp /usr/bin/eos-metrics-collector "$TARGET_MOUNTPOINT"/
  cp /usr/bin/eos-metrics-uploader "$TARGET_MOUNTPOINT"/
fi
udisksctl unmount -b "$PART" --no-user-interaction
sync
