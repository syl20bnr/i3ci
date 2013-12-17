# i3ci_menu (a fork of dmenu for i3 config improved)
# See LICENSE file for copyright and license details.

include config.mk

SRC = i3ci_menu.c draw.c stest.c hash.c
OBJ = ${SRC:.c=.o}
PROG = i3ci_menu

all: i3ci_menu dmenu_path stest

options:
	@echo i3ci_menu build options:
	@echo "CFLAGS   = ${CFLAGS}"
	@echo "LDFLAGS  = ${LDFLAGS}"
	@echo "CC       = ${CC}"

.c.o:
	@echo CC -c $<
	@${CC} -c $< ${CFLAGS} `freetype-config --cflags --libs`

${OBJ}: config.mk draw.h hash.h

i3ci_menu: i3ci_menu.o draw.o hash.o
	@echo CC -o $@
	@${CC} -o ${PROG} i3ci_menu.o draw.o hash.o ${LDFLAGS} `freetype-config --cflags --libs`

dmenu_path: dmenu_path.o

dmenu_path:
	@echo CC -o $@
	@${CC} -o $@ $+ ${LDFLAGS}

stest: stest.o
	@echo CC -o $@
	@${CC} -o $@ stest.o ${LDFLAGS}

clean:
	@rm -f ${PROG} dmenu_path stest ${OBJ} ${PROG}-${VERSION}.tar.gz

dist: clean
	@echo creating dist tarball
	@mkdir -p ${PROG}-${VERSION}
	@cp LICENSE Makefile README config.mk ${PROG}.c ${PROG}.1 draw.h dmenu_path.c stest.1 ${SRC} ${PROG}-${VERSION}
	@tar -cf ${PROG}-${VERSION}.tar ${PROG}-${VERSION}
	@gzip ${PROG}-${VERSION}.tar
	@rm -rf ${PROG}-${VERSION}

install: all
	@echo installing executables to ${DESTDIR}${PREFIX}/bin
	@mkdir -p ${DESTDIR}${PREFIX}/bin
	@cp -f ${PROG} dmenu_path stest ${DESTDIR}${PREFIX}/bin
	@chmod 755 ${DESTDIR}${PREFIX}/bin/${PROG}
	@chmod 755 ${DESTDIR}${PREFIX}/bin/dmenu_path
	@chmod 755 ${DESTDIR}${PREFIX}/bin/stest
	@echo installing manual pages to ${DESTDIR}${MANPREFIX}/man1
	@mkdir -p ${DESTDIR}${MANPREFIX}/man1
	@sed "s/VERSION/${VERSION}/g" < ${PROG}.1 > ${DESTDIR}${MANPREFIX}/man1/${PROG}.1
	@sed "s/VERSION/${VERSION}/g" < stest.1 > ${DESTDIR}${MANPREFIX}/man1/stest.1
	@chmod 644 ${DESTDIR}${MANPREFIX}/man1/${PROG}.1
	@chmod 644 ${DESTDIR}${MANPREFIX}/man1/stest.1

uninstall:
	@echo removing executables from ${DESTDIR}${PREFIX}/bin
	@rm -f ${DESTDIR}${PREFIX}/bin/${PROG}
	@rm -f ${DESTDIR}${PREFIX}/bin/dmenu_path
	@rm -f ${DESTDIR}${PREFIX}/bin/stest
	@echo removing manual page from ${DESTDIR}${MANPREFIX}/man1
	@rm -f ${DESTDIR}${MANPREFIX}/man1/${PROG}.1
	@rm -f ${DESTDIR}${MANPREFIX}/man1/stest.1

.PHONY: all options clean dist install uninstall
