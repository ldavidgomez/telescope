PI_HOST ?= telescope.local
PI_USER ?= astro
PI_DIR  ?= /home/astro/telescope

RSYNC_EXCLUDES = \
	--exclude=.git/ \
	--exclude=.venv/ \
	--exclude=__pycache__/ \
	--exclude='*.pyc' \
	--exclude=compass_calibration.json \
	--exclude=compass_test.csv \
	--exclude=.DS_Store

.PHONY: help deploy ssh

help:
	@echo "make deploy   Copy the project to the Raspberry Pi"
	@echo "make ssh      Open an SSH session"

deploy:
	rsync -av $(RSYNC_EXCLUDES) ./ $(PI_USER)@$(PI_HOST):$(PI_DIR)/

ssh:
	ssh $(PI_USER)@$(PI_HOST)
