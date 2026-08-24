PI_HOST ?= telescope.local
PI_USER ?= astro
PI_DIR  ?= /home/astro/telescope

RSYNC_EXCLUDES = \
	--exclude=.git/ \
	--exclude=.venv/ \
	--exclude=__pycache__/ \
	--exclude='*.pyc' \
	--exclude=.DS_Store

.PHONY: help deploy ssh

help:
	@echo "make deploy   Copia el proyecto a la Raspberry"
	@echo "make ssh      Abre una sesión SSH"

deploy:
	rsync -av $(RSYNC_EXCLUDES) ./ $(PI_USER)@$(PI_HOST):$(PI_DIR)/

ssh:
	ssh $(PI_USER)@$(PI_HOST)
