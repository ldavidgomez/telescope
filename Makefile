PI_HOST ?= telescope.local
PI_USER ?= astro
PI_DIR  ?= /home/astro/telescope
SSH_KEY ?= $(HOME)/.ssh/telescope_ed25519
CONFIG_FILE ?= telescope_config.json
RECORD_SECONDS ?= 30
RECORD_RATE ?= 100

SSH_OPTIONS = -o BatchMode=yes -o IdentitiesOnly=yes -i $(SSH_KEY)
SSH = ssh $(SSH_OPTIONS)
RSYNC = rsync -e 'ssh $(SSH_OPTIONS)'

RSYNC_EXCLUDES = \
	--exclude=.git/ \
	--exclude=.venv/ \
	--exclude=__pycache__/ \
	--exclude='*.pyc' \
	--exclude=compass_calibration.json \
	--exclude=compass_calibration.csv \
	--exclude=compass_test.csv \
	--exclude=imu_recording.csv \
	--exclude=imu_recording.json \
	--exclude=imu_replay.csv \
	--exclude=telescope_config.json \
	--exclude=.~ \
	--exclude=.DS_Store

.PHONY: help deploy deploy-config ssh stellarium test replay-imu \
	service-install service-permissions service-update service-restart service-stop \
	service-status service-logs bluetooth-install bluetooth-status bluetooth-logs \
	wifi-watchdog-install wifi-watchdog-status wifi-watchdog-logs \
	calibrate compass-test record-imu fetch-imu

help:
	@echo "make deploy   Copy the project to the Raspberry Pi"
	@echo "make deploy-config  Copy the private location configuration"
	@echo "make ssh      Open an SSH session"
	@echo "make stellarium  Run the Stellarium test server on the Raspberry Pi"
	@echo "make service-install  Install and start the automatic service"
	@echo "make service-permissions  Allow service management without a password"
	@echo "make service-update  Deploy changes and restart the service"
	@echo "make service-restart  Restart the automatic service"
	@echo "make service-stop  Stop the automatic service"
	@echo "make service-status  Show the automatic service status"
	@echo "make service-logs  Follow the automatic service logs"
	@echo "make bluetooth-install  Install the Bluetooth LX200 serial bridge"
	@echo "make bluetooth-status  Show the Bluetooth bridge status"
	@echo "make bluetooth-logs  Follow the Bluetooth bridge logs"
	@echo "make wifi-watchdog-install  Install the Wi-Fi recovery watchdog"
	@echo "make wifi-watchdog-status  Show the Wi-Fi watchdog status"
	@echo "make wifi-watchdog-logs  Follow the Wi-Fi watchdog logs"
	@echo "make calibrate  Stop the service and calibrate the compass"
	@echo "make compass-test  Stop the service and run the compass test"
	@echo "make record-imu  Record synchronized 9-axis IMU data"
	@echo "make fetch-imu  Copy the latest IMU recording to the Mac"
	@echo "make replay-imu  Test sensor fusion against the latest recording"
	@echo "make test     Run the local automated tests"

deploy:
	$(RSYNC) -av $(RSYNC_EXCLUDES) ./ $(PI_USER)@$(PI_HOST):$(PI_DIR)/

deploy-config:
	$(RSYNC) -av $(CONFIG_FILE) $(PI_USER)@$(PI_HOST):$(PI_DIR)/telescope_config.json

ssh:
	$(SSH) $(PI_USER)@$(PI_HOST)

stellarium:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'cd $(PI_DIR) && python3 stellarium_server.py'

service-install: deploy
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo install -m 0644 $(PI_DIR)/telescope.service /etc/systemd/system/telescope.service && sudo systemctl daemon-reload && sudo systemctl enable --now telescope.service'

service-permissions: deploy
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo visudo -cf $(PI_DIR)/telescope-sudoers && sudo install -o root -g root -m 0440 $(PI_DIR)/telescope-sudoers /etc/sudoers.d/telescope && sudo visudo -cf /etc/sudoers.d/telescope'

service-update: deploy
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo -n systemctl restart telescope.service'

service-restart:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo -n systemctl restart telescope.service'

service-stop:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo -n systemctl stop telescope.service'

service-status:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'systemctl status --no-pager telescope.service'

service-logs:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo -n journalctl -u telescope.service -f'

bluetooth-install: deploy
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo install -d -m 0755 /etc/systemd/system/bluetooth.service.d && sudo install -m 0644 $(PI_DIR)/bluetooth-compat.conf /etc/systemd/system/bluetooth.service.d/compat.conf && sudo install -m 0644 $(PI_DIR)/telescope-bluetooth.service /etc/systemd/system/telescope-bluetooth.service && sudo systemctl daemon-reload && sudo systemctl restart bluetooth.service && sudo systemctl enable --now telescope-bluetooth.service'

bluetooth-status:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'systemctl status --no-pager telescope-bluetooth.service'

bluetooth-logs:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'journalctl -u telescope-bluetooth.service -f'

wifi-watchdog-install: deploy
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'sudo install -m 0644 $(PI_DIR)/telescope-wifi-watchdog.service /etc/systemd/system/telescope-wifi-watchdog.service && sudo systemctl daemon-reload && sudo systemctl enable telescope-wifi-watchdog.service && sudo systemctl restart telescope-wifi-watchdog.service'

wifi-watchdog-status:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'systemctl status --no-pager telescope-wifi-watchdog.service'

wifi-watchdog-logs:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'journalctl -u telescope-wifi-watchdog.service -f'

calibrate:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'set -e; sudo -n systemctl stop telescope.service; trap "sudo -n systemctl start telescope.service" EXIT; cd $(PI_DIR); python3 calibrate_compass.py'

compass-test:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'set -e; sudo -n systemctl stop telescope.service; trap "sudo -n systemctl start telescope.service" EXIT; cd $(PI_DIR); python3 compass_test.py'

record-imu:
	$(SSH) -t $(PI_USER)@$(PI_HOST) 'set -e; sudo -n systemctl stop telescope.service; trap "sudo -n systemctl start telescope.service" EXIT; cd $(PI_DIR); python3 record_imu.py --duration $(RECORD_SECONDS) --sample-rate $(RECORD_RATE)'

fetch-imu:
	$(RSYNC) -av $(PI_USER)@$(PI_HOST):$(PI_DIR)/imu_recording.csv ./
	$(RSYNC) -av $(PI_USER)@$(PI_HOST):$(PI_DIR)/imu_recording.json ./

replay-imu:
	python3 replay_imu.py

test:
	python3 -m unittest discover -v
