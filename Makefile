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

.PHONY: help deploy deploy-config ssh stellarium test

help:
	@echo "make deploy   Copy the project to the Raspberry Pi"
	@echo "make deploy-config  Copy the private location configuration"
	@echo "make ssh      Open an SSH session"
	@echo "make stellarium  Run the Stellarium test server on the Raspberry Pi"
	@echo "make test     Run the local automated tests"

deploy:
	rsync -av $(RSYNC_EXCLUDES) ./ $(PI_USER)@$(PI_HOST):$(PI_DIR)/

deploy-config:
	rsync -av $(CONFIG_FILE) $(PI_USER)@$(PI_HOST):$(PI_DIR)/telescope_config.json

ssh:
	ssh $(PI_USER)@$(PI_HOST)

stellarium:
	ssh -t $(PI_USER)@$(PI_HOST) 'cd $(PI_DIR) && python3 stellarium_server.py'

test:
	python3 -m unittest discover -v
