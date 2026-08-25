PI_HOST ?= telescope.local
PI_USER ?= astro
PI_DIR  ?= /home/astro/telescope
CONFIG_FILE ?= telescope_config.json

RSYNC_EXCLUDES = \
	--exclude=.git/ \
	--exclude=.venv/ \
	--exclude=__pycache__/ \
	--exclude='*.pyc' \
	--exclude=compass_calibration.json \
	--exclude=compass_calibration.csv \
	--exclude=compass_test.csv \
	--exclude=telescope_config.json \
	--exclude=.~ \
	--exclude=.DS_Store

.PHONY: help deploy deploy-config ssh stellarium test \
	service-install service-update service-restart service-stop \
	service-status service-logs calibrate compass-test

help:
	@echo "make deploy   Copy the project to the Raspberry Pi"
	@echo "make deploy-config  Copy the private location configuration"
	@echo "make ssh      Open an SSH session"
	@echo "make stellarium  Run the Stellarium test server on the Raspberry Pi"
	@echo "make service-install  Install and start the automatic service"
	@echo "make service-update  Deploy changes and restart the service"
	@echo "make service-restart  Restart the automatic service"
	@echo "make service-stop  Stop the automatic service"
	@echo "make service-status  Show the automatic service status"
	@echo "make service-logs  Follow the automatic service logs"
	@echo "make calibrate  Stop the service and calibrate the compass"
	@echo "make compass-test  Stop the service and run the compass test"
	@echo "make test     Run the local automated tests"

deploy:
	rsync -av $(RSYNC_EXCLUDES) ./ $(PI_USER)@$(PI_HOST):$(PI_DIR)/

deploy-config:
	rsync -av $(CONFIG_FILE) $(PI_USER)@$(PI_HOST):$(PI_DIR)/telescope_config.json

ssh:
	ssh $(PI_USER)@$(PI_HOST)

stellarium:
	ssh -t $(PI_USER)@$(PI_HOST) 'cd $(PI_DIR) && python3 stellarium_server.py'

service-install: deploy
	ssh -t $(PI_USER)@$(PI_HOST) 'sudo install -m 0644 $(PI_DIR)/telescope.service /etc/systemd/system/telescope.service && sudo systemctl daemon-reload && sudo systemctl enable --now telescope.service'

service-update: deploy
	ssh -t $(PI_USER)@$(PI_HOST) 'sudo systemctl restart telescope.service'

service-restart:
	ssh -t $(PI_USER)@$(PI_HOST) 'sudo systemctl restart telescope.service'

service-stop:
	ssh -t $(PI_USER)@$(PI_HOST) 'sudo systemctl stop telescope.service'

service-status:
	ssh -t $(PI_USER)@$(PI_HOST) 'systemctl status --no-pager telescope.service'

service-logs:
	ssh -t $(PI_USER)@$(PI_HOST) 'sudo journalctl -u telescope.service -f'

calibrate:
	ssh -t $(PI_USER)@$(PI_HOST) 'set -e; sudo systemctl stop telescope.service; trap "sudo systemctl start telescope.service" EXIT; cd $(PI_DIR); python3 calibrate_compass.py'

compass-test:
	ssh -t $(PI_USER)@$(PI_HOST) 'set -e; sudo systemctl stop telescope.service; trap "sudo systemctl start telescope.service" EXIT; cd $(PI_DIR); python3 compass_test.py'

test:
	python3 -m unittest discover -v
