Configure DAC+:

https://forums.raspberrypi.com/viewtopic.php?t=374279

Summary:

sudo nano /boot/firmware/config.txt

Uncomment: 
# dtparam=i2s=on

Remove:
dtparam=audio=on

Add:
dtoverlay=rpi-dacplus

Add noaudio to:
dtoverlay=vc4-kms-v3d,noaudio