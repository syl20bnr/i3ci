dmenu - dynamic menu
====================
This is a heavily modified dmenu.

The main differences are:
- by default, draw menu an all monitors
- menu animation with option -a

The following standard patches are applied:
- xft support
- basic history file
- selection for output monitor
- token matching
- fuzzy matching
- custom coordinates
- custom width and height

Requirements
------------
In order to build dmenu you need the Xlib header files.

Installation
------------
Edit config.mk to match your local setup (dmenu is installed into
the /usr/local namespace by default).

Afterwards enter the following command to build and install dmenu
(if necessary as root):

    make clean install

Usage
-----

    Usage: dmenu [OPTION]...
    Display newline-separated input stdin as a menubar
    
      -a            toggle animations on.
    
      -b            dmenu appears at the bottom of the screen.
    
      -f            grab keyboard before reading stdin.
    
      -h N          set dmenu height to N pixels.
    
      -hist FILE    store user choices in the specified file,
                    the value in the file are always displayed
                    first.
    
      -i            dmenu matches menu items case insensitively.
    
      -lmax LINES   maximum number of lines when items are
                    vertically listed.
    
      -lv           dmenu lists items in vertically.
    
      -m MONITOR    dmenu appears only on the given screen. If this
                    agument is not set, dmenu displays the menu on
                    all available monitors.
    
      -p PROMPT     prompt to be displayed to the left of the
                    input field.
    
      -q            quiet mode.
    
      -r            return as soon as a single match is found.
    
      -fn FONT      font or font set to be used.
    
      -nb COLOR     normal background color
                    #RGB, #RRGGBB, and color names supported.
    
      -nf COLOR     normal foreground color.
    
      -sb COLOR     selected background color.
    
      -sf COLOR     selected foreground color.
    
      -v            display version information.
    
      -w N          set dmenu width to N pixels.
    
      -x N          set dmenu x offset to N pixels.
    
      -y N          set dmenu y offset to N pixels.
    
      -z            enable fuzzy matching, if this option is not
                    specified then token matching is used.

Notes
-----

Man pages and tests are not up to date.
It is not well tested outside of my current usage:
- top of the screen
- draw menus on all monitors
- animations enabled
- horizontal and vertical layout
