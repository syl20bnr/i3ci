# This Makefile builds the dependencies for i3-config and install
# the configuration environment into your ~/.i3 folder

MAKEFLAGS=-s

I3_INSTALL=~/.i3
I3CI_INSTALL=~/.i3ci
BACKUP=.bak

compile: i3ci_menu xcwd
	@echo Backup of current i3 config...
	rm -f $(I3_INSTALL)/config$(BACKUP)
	mv $(I3_INSTALL)/config $(I3_INSTALL)/config$(BACKUP)
	@echo Installing i3 configuration...
	cp i3_config $(I3_INSTALL)/config
	cp i3_i3status.conf ~/.i3status.conf
	@echo Installing i3ci...
	mkdir -p $(I3CI_INSTALL)/bin
	cp i3ci_menu/i3ci_menu $(I3CI_INSTALL)/bin
	cp i3ci_menu/dmenu_path $(I3CI_INSTALL)/bin
	cp -r i3ci_cmd/i3ci $(I3CI_INSTALL)/bin
	cp i3ci_cmd/i3ci_cmd $(I3CI_INSTALL)/bin
	cp i3ci_exit/i3ci_exit $(I3CI_INSTALL)/bin
	cp xcwd/xcwd $(I3CI_INSTALL)/bin

i3ci_menu:
	@echo Compiling i3ci_menu...
	cd i3ci_menu; make

xcwd:
	@echo Compiling xcwd...
	cd xcwd; make

install:
	@echo Symbolic links...
	ln -fs $(I3CI_INSTALL)/bin/i3ci_menu /usr/local/bin/i3ci_menu
	ln -fs $(I3CI_INSTALL)/bin/i3ci_cmd /usr/local/bin/i3ci_cmd
	ln -fs $(I3CI_INSTALL)/bin/i3ci_exit /usr/local/bin/i3ci_exit
	ln -fs $(I3CI_INSTALL)/bin/i3ci_xcwd /usr/local/bin/i3ci_xcwd
	ln -fs $(I3CI_INSTALL)/bin/dmenu_path /usr/local/bin/dmenu_path

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
	cd i3ci_menu; make clean
	cd xcwd; make clean distclean

.PHONY: i3ci_menu xcwd install update revert clean
