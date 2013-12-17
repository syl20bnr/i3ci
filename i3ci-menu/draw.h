/* See LICENSE file for copyright and license details. */

#include <X11/Xft/Xft.h>
#include <X11/extensions/Xinerama.h>

typedef struct {
	int cx, cy, cw, ch;
	int x, y;
  int width, height;
	Pixmap canvas;
	XftDraw *xftdraw;
} DM; /* draw menu */

typedef struct {
	Bool invert;
	GC gc;
  DM *menus;
	Display *dpy;
  int scrcount;
  XineramaScreenInfo *info;
	struct {
		int ascent;
		int descent;
		int height;
		int width;
		XFontSet set;
		XFontStruct *xfont;
		XftFont *xft_font;
	} font;
} DC;  /* draw context */

typedef struct {
	unsigned long FG;
	XftColor FG_xft;
	unsigned long BG;
} ColorSet;

void drawrect(DC *dc, int scrnum, int x, int y, unsigned int w, unsigned int h,
              Bool fill, unsigned long color);
void drawtext(DC *dc, int scrnum, const char *text, ColorSet *col);
void drawtextn(DC *dc, int scrnum, const char *text, size_t n, ColorSet *col);
void freecol(DC *dc, ColorSet *col);
void eprintf(const char *fmt, ...);
void freedc(DC *dc);
unsigned long getcolor(DC *dc, const char *colstr);
ColorSet *initcolor(DC *dc, const char *foreground, const char *background);
DC *initdc(void);
void initfont(DC *dc, const char *fontstr);
void mapdc(DC *dc, int scrnum, Window win);
void resizedc(DC *dc, int scrnum);
int textnw(DC *dc, const char *text, size_t len);
int textw(DC *dc, const char *text);
