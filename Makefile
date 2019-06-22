setup:
	sudo apt-get update
	sudo apt-get install -y bluez minicom python-serial pass rng-tools
	mkdir -p /tmp/bt-config
	cp /etc/systemd/system/dbus-org.bluez.service /tmp/bt-config/dbus-org.bluez.service.old
	sed '/ExecStartPost/d' /tmp/bt-config/dbus-org.bluez.service.old > /tmp/bt-config/dbus-org.bluez.service
	sed -i 's/ExecStart=\/usr\/lib\/bluetooth\/bluetoothd.*/ExecStart=\/usr\/lib\/bluetooth\/bluetoothd -C\nExecStartPost=\/usr\/bin\/sdptool add SP/' /tmp/bt-config/dbus-org.bluez.service
	sudo cp /tmp/bt-config/dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service
	mkdir -p /home/pi/.password-store
	-sudo rngd
	gpg --batch --generate-key src/gpg/gen-key-conf
	/usr/bin/pass init OwnVoiceAssistant
	echo -e "pi\nraspberry" | /usr/bin/pass insert Bluetooth/Admin
	sudo sed -i -e '$i \echo "discoverable on" | sudo /usr/bin/bluetoothctl\n' /etc/rc.local

install:
	mkdir -p ${HOME}/script
	mkdir -p ${HOME}/bin
	cp src/*.py ${HOME}/script
	cp src/bin/* ${HOME}/bin
	sudo cp rfcomm.service /etc/systemd/system
	sudo systemctl enable rfcomm
