# This Makefile builds the dependencies for i3-config and install
# the configuration environment into your ~/.i3 folder

MAKEFLAGS=-s

INSTALL=~/.i3
BACKUP=$(INSTALL).bak

all:
	@echo Compiling dmenu...
	cd dmenu; make

install: all
	@echo Making a backup of current i3 config in $(BACKUP)...
	rm -rf $(BACKUP)
	mv $(INSTALL) $(BACKUP)
	@echo Installing i3 configuration...
	cp -r i3/ $(INSTALL)
	mkdir -p $(INSTALL)/bin
	cp dmenu/dmenu $(INSTALL)/bin

update: install
	@echo Restarting i3 config...
  # Redirect error since i3-msg will crash when i3 restarts
	i3-msg restart > /dev/null 2>&1 || true

# TODO: check if there is a backup
revert:
	@echo Reverting i3 config...
	rm -rf $(INSTALL)
	mv $(BACKUP) $(INSTALL)

clean:
	@echo Cleaning...
	cd dmenu; make clean