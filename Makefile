PLUGIN_DIR := plugins/idmp-plugin
DIST_DIR := dist
PLUGIN_VERSION := $(shell sed -n 's/.*"version": "\([0-9][0-9.]*\)".*/\1/p' $(PLUGIN_DIR)/plugin.json | head -1)
PYTHON ?= python3

.PHONY: codex claude clean

codex:
	$(PYTHON) scripts/package_plugin.py $(PLUGIN_DIR) codex $(DIST_DIR)/idmp-plugin-codex-$(PLUGIN_VERSION).zip

claude:
	$(PYTHON) scripts/package_plugin.py $(PLUGIN_DIR) claude $(DIST_DIR)/idmp-plugin-claude-$(PLUGIN_VERSION).zip

clean:
	rm -rf $(DIST_DIR)
