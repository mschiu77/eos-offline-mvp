#!/bin/bash -e

USB_DISK_NUM=0


prompt_input()
{
    echo "
	 "
    read -p "Please enter the disk number you want to create for metrics? [1] "
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

prompt_input

TARGET_DISK=${DISK[$((USER_CHOICE-1))]}

echo "disk name $TARGET_DISK"
