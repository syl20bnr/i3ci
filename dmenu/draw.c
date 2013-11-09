/* See LICENSE file for copyright and license details. */
#include <locale.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <X11/Xlib.h>
#include "draw.h"

#define MAX(a, b)  ((a) > (b) ? (a) : (b))
#define MIN(a, b)  ((a) < (b) ? (a) : (b))

void
drawrect(DC *dc, int scrnum, int x, int y, unsigned int w, unsigned int h, Bool fill, unsigned long color) {
  DM *m = &dc->menus[scrnum];
	XSetForeground(dc->dpy, dc->gc, color);
	if(fill)
		XFillRectangle(dc->dpy, m->canvas, dc->gc, m->cx + x, m->cy + y, w, h);
	else
		XDrawRectangle(dc->dpy, m->canvas, dc->gc, m->cx + x, m->cy + y, w-1, h-1);
}

void
drawtext(DC *dc, int scrnum, const char *text, ColorSet *col) {
	char buf[BUFSIZ];
	size_t mn, n = strlen(text);
  DM *m = &dc->menus[scrnum];
	/* shorten text if necessary */
	for(mn = MIN(n, sizeof buf); textnw(dc, text, mn) + dc->font.height/2 > m->cw; mn--)
		if(mn == 0)
			return;
	memcpy(buf, text, mn);
	if(mn < n)
		for(n = MAX(mn-3, 0); n < mn; buf[n++] = '.');
	drawrect(dc, scrnum, 0, 0, m->cw, m->ch, True, col->BG);
	drawtextn(dc, scrnum, buf, mn, col);
}

void
drawtextn(DC *dc, int scrnum, const char *text, size_t n, ColorSet *col) {
  DM *m = &dc->menus[scrnum];
	int x = m->cx + dc->font.height/2;
	int y = m->cy + dc->font.ascent + (m->ch - dc->font.height)/2;

	XSetForeground(dc->dpy, dc->gc, col->FG);
	if(dc->font.xft_font) {
		if (!m->xftdraw)
			eprintf("error, xft drawable does not exist");
		XftDrawStringUtf8(m->xftdraw, &col->FG_xft,
			dc->font.xft_font, x, y, (unsigned char*)text, n);
	} else if(dc->font.set) {
		XmbDrawString(dc->dpy, m->canvas, dc->font.set, dc->gc, x, y, text, n);
    } else {
		XSetFont(dc->dpy, dc->gc, dc->font.xfont->fid);
		XDrawString(dc->dpy, m->canvas, dc->gc, x, y, text, n);
	}
}

void
eprintf(const char *fmt, ...) {
	va_list ap;

	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);

	if(fmt[0] != '\0' && fmt[strlen(fmt)-1] == ':') {
		fputc(' ', stderr);
		perror(NULL);
	}
	exit(EXIT_FAILURE);
}

void
freecol(DC *dc, ColorSet *col) {
    if(col) {
        if(&col->FG_xft)
            XftColorFree(dc->dpy, DefaultVisual(dc->dpy, DefaultScreen(dc->dpy)),
                DefaultColormap(dc->dpy, DefaultScreen(dc->dpy)), &col->FG_xft);
        free(col); 
    }
}

void
freemenu(DC *dc, DM *dm){
   if(dc->font.xft_font)
     XftDrawDestroy(dm->xftdraw);
  if(dm->canvas)
    XFreePixmap(dc->dpy, dm->canvas);
}

void
freedc(DC *dc) {
  if(dc->info) {
    XFree(dc->info);
  }
  if(dc->font.xft_font)
    XftFontClose(dc->dpy, dc->font.xft_font);
  if(dc->font.set)
    XFreeFontSet(dc->dpy, dc->font.set);
  if(dc->font.xfont)
    XFreeFont(dc->dpy, dc->font.xfont);
  if(dc->menus){
    for(int i=0; i<dc->scrcount; ++i){
      freemenu(dc, &dc->menus[i]);
    }
    free(dc->menus);
  }
  if(dc->gc)
    XFreeGC(dc->dpy, dc->gc);
  if(dc->dpy)
    XCloseDisplay(dc->dpy);
  if(dc)
    free(dc);
}

unsigned long
getcolor(DC *dc, const char *colstr) {
	Colormap cmap = DefaultColormap(dc->dpy, DefaultScreen(dc->dpy));
	XColor color;

	if(!XAllocNamedColor(dc->dpy, cmap, colstr, &color, &color))
		eprintf("cannot allocate color '%s'\n", colstr);
	return color.pixel;
}

ColorSet *
initcolor(DC *dc, const char * foreground, const char * background) {
	ColorSet * col = (ColorSet *)malloc(sizeof(ColorSet));
	if(!col)
		eprintf("error, cannot allocate memory for color set");
	col->BG = getcolor(dc, background);
	col->FG = getcolor(dc, foreground);
	if(dc->font.xft_font)
		if(!XftColorAllocName(dc->dpy,
                          DefaultVisual(dc->dpy, DefaultScreen(dc->dpy)),
                          DefaultColormap(dc->dpy, DefaultScreen(dc->dpy)),
                          foreground, &col->FG_xft))
			eprintf("error, cannot allocate xft font color '%s'\n", foreground);
	return col;
}

DC *
initdc(void) {
	DC *dc;

	if(!setlocale(LC_CTYPE, "") || !XSupportsLocale())
		fputs("no locale support\n", stderr);
	if(!(dc = calloc(1, sizeof *dc)))
		eprintf("cannot malloc %u bytes:", sizeof *dc);
	if(!(dc->dpy = XOpenDisplay(NULL)))
		eprintf("cannot open display\n");
	if(!(dc->info = XineramaQueryScreens(dc->dpy, &dc->scrcount))){
    dc->scrcount = 1;
  }
  dc->menus = calloc(dc->scrcount, sizeof(DM));
	dc->gc = XCreateGC(dc->dpy, DefaultRootWindow(dc->dpy), 0, NULL);
	XSetLineAttributes(dc->dpy, dc->gc, 1, LineSolid, CapButt, JoinMiter);
	return dc;
}

void
initfont(DC *dc, const char *fontstr) {
	char *def, **missing, **names;
	int i, n;
	XFontStruct **xfonts;

	missing = NULL;
	if((dc->font.xfont = XLoadQueryFont(dc->dpy, fontstr))) {
		dc->font.ascent = dc->font.xfont->ascent;
		dc->font.descent = dc->font.xfont->descent;
		dc->font.width   = dc->font.xfont->max_bounds.width;
	} else if((dc->font.set = XCreateFontSet(dc->dpy, fontstr,
                                           &missing, &n, &def))) {
		n = XFontsOfFontSet(dc->font.set, &xfonts, &names);
		for(i = 0; i < n; i++) {
			dc->font.ascent  = MAX(dc->font.ascent,  xfonts[i]->ascent);
			dc->font.descent = MAX(dc->font.descent, xfonts[i]->descent);
			dc->font.width   = MAX(dc->font.width,   xfonts[i]->max_bounds.width);
		}
	} else if((dc->font.xft_font = XftFontOpenName(dc->dpy,
                                                 DefaultScreen(dc->dpy),
                                                 fontstr))) {
		dc->font.ascent = dc->font.xft_font->ascent;
		dc->font.descent = dc->font.xft_font->descent;
		dc->font.width = dc->font.xft_font->max_advance_width;
	} else {
		eprintf("cannot load font '%s'\n", fontstr);
	}
	if(missing)
		XFreeStringList(missing);
	dc->font.height = dc->font.ascent + dc->font.descent;
	return;
}

void
mapdc(DC *dc, int scrnum, Window win) {
  DM *dm = &dc->menus[scrnum];
	XCopyArea(dc->dpy, dm->canvas, win, dc->gc, 0, 0, dm->width, dm->height, 0, 0);
}

void
resizedc(DC *dc, int scrnum) {
  DM *dm = &dc->menus[scrnum];
	int screen = DefaultScreen(dc->dpy);
  if(dm->canvas)
    XFreePixmap(dc->dpy, dm->canvas);
	dm->canvas = XCreatePixmap(dc->dpy, DefaultRootWindow(dc->dpy),
                             dm->width, dm->height,
                             DefaultDepth(dc->dpy, screen));
	if(dc->font.xft_font && !(dm->xftdraw)) {
    dm->xftdraw = XftDrawCreate(dc->dpy, dm->canvas,
                                DefaultVisual(dc->dpy,screen),
                                DefaultColormap(dc->dpy,screen));
    if(!(dm->xftdraw))
      eprintf("error, cannot create xft drawable\n");
	}
  else {
    XftDrawChange(dm->xftdraw, dm->canvas);
  }
}

int
textnw(DC *dc, const char *text, size_t len) {
	if(dc->font.xft_font) {
		XGlyphInfo gi;
		XftTextExtentsUtf8(dc->dpy, dc->font.xft_font,
                       (const FcChar8*)text, len, &gi);
		return gi.width;
	} else if(dc->font.set) {
		XRectangle r;
		XmbTextExtents(dc->font.set, text, len, NULL, &r);
		return r.width;
	}
	return XTextWidth(dc->font.xfont, text, len);
}

int
textw(DC *dc, const char *text) {
	return textnw(dc, text, strlen(text)) + dc->font.height;
}
