/* See LICENSE file for copyright and license details. */
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <time.h>
#include <unistd.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <X11/extensions/Xinerama.h>
#include "draw.h"
#include "hash.h"

#define INTERSECT(x,y,w,h,r) \
    (MAX(0, MIN((x)+(w),(r).x_org+(r).width)  - MAX((x),(r).x_org)) * \
     MAX(0, MIN((y)+(h),(r).y_org+(r).height) - MAX((y),(r).y_org)))
#define INRECT(x,y,rx,ry,rw,rh) \
    ((x) >= (rx) && (x) < (rx)+(rw) && (y) >= (ry) && (y) < (ry)+(rh))
#define MIN(a,b)              ((a) < (b) ? (a) : (b))
#define MAX(a,b)              ((a) > (b) ? (a) : (b))
#define DEFFONT "fixed" /* xft example: "Monospace-11" */
#define TLINE_HEIGHT 1  /* height of the line at the top of the menu*/
#define BLINE_HEIGHT 1  /* height of the line at the bottom of the menu*/

typedef struct Item Item;
struct Item {
	char *text;
	Item *left, *right;
  Bool out;
};

typedef struct Menu Menu;
struct Menu {
  Item *prev;
  Item *next;
  Item *cfirst;   /* current first item of the displayed items */
};

static void appenditem(Item *item, Item **list, Item **last);
static void calcalloffsets(void);
static void calcoffsets(int scrnum);
static void cleanup(void);
static char *cistrstr(const char *s, const char *sub);
static void grabkeyboard(void);
static void insert(const char *str, ssize_t n);
static void keypress(XKeyEvent *ev);
static void match(void);
static void match_fuzzy(void);
static void match_tokens(void);
static char *strchri(const char *s, int c);
static size_t nextrune(int inc);
static void paste(void);
static void readstdin(void);
static void run(void);
static void setup(void);
static void createwindow(Window *window, int scrnum);
static void updatewindows(void);
static void drawmenu(int scrnum);
static void handle_return(char* value);
static int writehistory(char *command);
static void anim(int origin, int target);
static void close_anim(void);
static void usage(void);

static char text[BUFSIZ] = "";
static int barh;
static int inputw, promptw;
static int xoffset = 0;
static int yoffset = 0;
static int width = 0;
static int monitor = -1;
static size_t cursor = 0;
static const char *font = NULL;
static const char *prompt = NULL;
static const char *normbgcolor = "#222222";
static const char *normfgcolor = "#bbbbbb";
static const char *selbgcolor  = "#005577";
static const char *selfgcolor  = "#eeeeee";
static unsigned int lmax = 1;
static int line_height = 0;
static Bool vertical = False;
static ColorSet *normcol;
static ColorSet *selcol;
static Atom clip, utf8;
static Bool topbar = True;
static Bool quiet = False;
static Bool running = True;
static int ret = 0;
static DC *dc;
static Item *items = NULL;
static Item *matches, *matchend;
static Menu *menus;
static Item *sel;
static Window *windows;
static unsigned int last_win_height = 0;
static XIC xic;
static Bool fuzzy;
static Bool returnearly = False;
static char *histfile = NULL;
static size_t histsize = 0;
static int animduration = 0;

static int (*fstrncmp)(const char *, const char *, size_t) = strncmp;
static char *(*fstrstr)(const char *, const char *) = strstr;
static char *(*fstrchr)(const char *, const int) = strchr;

int
main(int argc, char *argv[]) {
	Bool fast = False;
	int i;

	for(i = 1; i < argc; i++)
		/* these options take no arguments */
		if(!strcmp(argv[i], "-v")) {      /* prints version information */
			puts("dmenu-"VERSION", © 2006-2012 dmenu engineers, 2013 Sylvain Benner, see LICENSE for details");
			exit(EXIT_SUCCESS);
		}
		else if(!strcmp(argv[i], "-b"))   /* appears at the bottom of the screen */
			topbar = False;
		else if(!strcmp(argv[i], "-q"))   /* quiet mode */
			quiet = True;
		else if(!strcmp(argv[i], "-f"))   /* grabs keyboard before reading stdin */
			fast = True;
		else if(!strcmp(argv[i], "-z"))   /* enable fuzzy matching */
			fuzzy = True;
		else if(!strcmp(argv[i], "-lv"))  /* list items verticaly  */
			vertical = True;
		else if(!strcmp(argv[i], "-i")) { /* case-insensitive item matching */
			fstrncmp = strncasecmp;
			fstrstr = cistrstr;
			fstrchr = strchri;
		}
		else if(!strcmp(argv[i], "-r") || !strcmp(argv[i], "--return-early"))
			returnearly = True;
		else if(i+1 == argc)
			usage();
		/* these options take one argument */
		else if(!strcmp(argv[i], "-a"))     /* set animation duration */
			animduration = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-x"))
			xoffset = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-y"))
			yoffset = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-w"))
			width = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-lmax"))  /* maximum number of lines in vertical mode */
			lmax = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-m"))     /* dmenu appears on the given Xinerama screen */
			monitor = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-h"))     /* minimum height of single line */
			line_height = atoi(argv[++i]);
		else if(!strcmp(argv[i], "-p"))     /* adds prompt to left of input field */
			prompt = argv[++i];
		else if(!strcmp(argv[i], "-fn"))    /* font or font set */
			font = argv[++i];
		else if(!strcmp(argv[i], "-nb"))    /* normal background color */
			normbgcolor = argv[++i];
		else if(!strcmp(argv[i], "-nf"))    /* normal foreground color */
			normfgcolor = argv[++i];
		else if(!strcmp(argv[i], "-sb"))    /* selected background color */
			selbgcolor = argv[++i];
		else if(!strcmp(argv[i], "-sf"))    /* selected foreground color */
			selfgcolor = argv[++i];
		else if(!strcmp(argv[i], "-hist"))
			histfile = argv[++i];
		else
			usage();

	dc = initdc();
	initfont(dc, font ? font : DEFFONT);
	normcol = initcolor(dc, normfgcolor, normbgcolor);
	selcol = initcolor(dc, selfgcolor, selbgcolor);
  menus = calloc(dc->scrcount, sizeof(Menu));

	if(fast) {
		grabkeyboard();
		readstdin();
	}
	else {
		readstdin();
		grabkeyboard();
	}
	setup();
	run();
  if(animduration != 0)
    close_anim();
	cleanup();
	return ret;
}

void
appenditem(Item *item, Item **list, Item **last) {
	if(*last)
		(*last)->right = item;
	else
		*list = item;

	item->left = *last;
	item->right = NULL;
	*last = item;
}

void
calcalloffsets(void){
  for(int i=0; i<dc->scrcount; ++i){
    calcoffsets(i);
  }
}

void
calcoffsets(int scrnum) {
  Menu *m = &menus[scrnum];
  DM *dm = &dc->menus[scrnum];
	int i, n;

	if(vertical)
		n = lmax * barh;
	else
		n = dm->width - (promptw + inputw + textw(dc, "<") + textw(dc, ">"));
	/* calculate which items will begin the next page and previous page */
	for(i = 0, m->next = m->cfirst; m->next; m->next = m->next->right)
		if((i += (vertical) ? barh : MIN(textw(dc, m->next->text), n)) > n)
			break;
	for(i = 0, m->prev = m->cfirst; m->prev && m->prev->left; m->prev = m->prev->left)
		if((i += (vertical) ? barh : MIN(textw(dc, m->prev->left->text), n)) > n)
			break;
}

char *
cistrstr(const char *s, const char *sub) {
	size_t len;

	for(len = strlen(sub); *s; s++)
		if(!strncasecmp(s, sub, len))
			return (char *)s;
	return NULL;
}

void
cleanup(void) {
  freecol(dc, normcol);
  freecol(dc, selcol);
  for(int i=0; i<dc->scrcount; ++i){
    XDestroyWindow(dc->dpy, windows[i]);
  }
  XUngrabKeyboard(dc->dpy, CurrentTime);
  freedc(dc);
  free(menus);
}

void
updatewindows(void) {
  for(int scrnum=0; scrnum<dc->scrcount; ++scrnum){
    drawmenu(scrnum);
  }
  /* Check for new height on the first window only */
  Item *item;
  unsigned int nh = TLINE_HEIGHT + BLINE_HEIGHT;

  if(vertical){
    for(item = menus[0].cfirst; item != menus[0].next; item = item->right) {
      nh += barh;
    }
  }

  unsigned int new_win_height = nh + barh;
  if(new_win_height != last_win_height){
    for(int scrnum=0; scrnum<dc->scrcount; ++scrnum){
      dc->menus[scrnum].height = new_win_height;
      resizedc(dc, scrnum);
      drawmenu(scrnum);
    }
    if(animduration != 0){
      anim(last_win_height, new_win_height);
    }
    /* ensure that the final window height has been correctly set */
    for(int scrnum=0; scrnum<dc->scrcount; ++scrnum){
      DM *dm = &dc->menus[scrnum];
      XMoveResizeWindow(dc->dpy, windows[scrnum], dm->x, dm->y, dm->width, dm->height);
      drawmenu(scrnum);
    }
    last_win_height = new_win_height;
  }
  for(int scrnum=0; scrnum<dc->scrcount; ++scrnum){
    mapdc(dc, scrnum, windows[scrnum]);
  }
}

void
drawmenu(int scrnum) {
  Menu *m = &menus[scrnum];
  DM *dm = &dc->menus[scrnum];
	int curpos;
	Item *item;

	dm->cx = 0;
	dm->cy = 0;
	dm->ch = barh;

	drawrect(dc, scrnum, 0, 0, dm->width, TLINE_HEIGHT, True, selcol->BG);
	dm->cy = TLINE_HEIGHT;
	drawrect(dc, scrnum, 0, 0, dm->width, dm->height, True, normcol->BG);

	if(prompt) {
		dm->cw = promptw;
		drawtext(dc, scrnum, prompt, selcol);
		dm->cx = dm->cw;
	}
	/* draw input field */
	dm->cw = (vertical || !matches) ? dm->width - dm->cx : inputw;
	drawtext(dc, scrnum, text, normcol);
	if((curpos = textnw(dc, text, cursor) + dc->font.height/2) < dm->cw)
    drawrect(dc, scrnum, curpos, (dm->ch - dc->font.height)/2 + 1, 1,
             dc->font.height - 1, True, normcol->FG);

  if(!quiet || strlen(text) > 0) {
    if(vertical) {
      /* draw vertical list */
      dm->cw = dm->width - dm->cx;
      for(item = m->cfirst; item != m->next; item = item->right) {
        dm->cy += dm->ch;
        drawtext(dc, scrnum, item->text, (item == sel) ? selcol : normcol);
      }
    }
    else if(matches) {
      /* draw horizontal list */
      dm->cx += inputw;
      dm->cw = textw(dc, "<");
      if(m->cfirst->left)
        drawtext(dc, scrnum, "<", normcol);
      for(item = m->cfirst; item != m->next; item = item->right) {
        dm->cx += dm->cw;
        dm->cw = MIN(textw(dc, item->text), dm->width - dm->cx - textw(dc, ">"));
        drawtext(dc, scrnum, item->text, (item == sel) ? selcol : normcol);
      }
      dm->cw = textw(dc, ">");
      dm->cx = dm->width - dm->cw;
      if(m->next)
        drawtext(dc, scrnum, ">", normcol);
    }
  }
  dm->cy += barh;
  dm->cx = 0;
	drawrect(dc, scrnum, 0, 0, dm->width, BLINE_HEIGHT, True, selcol->BG);
}

void
grabkeyboard(void) {
	int i;

	/* try to grab keyboard, we may have to wait for another process to ungrab */
	for(i = 0; i < 1000; i++) {
		if(XGrabKeyboard(dc->dpy, DefaultRootWindow(dc->dpy), True,
		                 GrabModeAsync, GrabModeAsync, CurrentTime) == GrabSuccess)
			return;
		usleep(1000);
	}
	eprintf("cannot grab keyboard\n");
}

void
insert(const char *str, ssize_t n) {
	if(strlen(text) + n > sizeof text - 1)
		return;
	/* move existing text out of the way, insert new text, and update cursor */
	memmove(&text[cursor + n], &text[cursor], sizeof text - cursor - MAX(n, 0));
	if(n > 0)
		memcpy(&text[cursor], str, n);
	cursor += n;
	match();
}

void
keypress(XKeyEvent *ev) {
	char buf[32];
	int len;
	KeySym ksym = NoSymbol;
	Status status;

	len = XmbLookupString(xic, ev, buf, sizeof buf, &ksym, &status);
	if(status == XBufferOverflow)
		return;
	if(ev->state & ControlMask)
    /* emacs */
		switch(ksym) {
		case XK_a: ksym = XK_Home;      break;
		case XK_b: ksym = XK_Left;      break;
		case XK_c: ksym = XK_Escape;    break;
		case XK_d: ksym = XK_Delete;    break;
		case XK_e: ksym = XK_End;       break;
		case XK_f: ksym = XK_Right;     break;
		case XK_h: ksym = XK_BackSpace; break;
		case XK_i: ksym = XK_Tab;       break;
		case XK_j: ksym = XK_Return;    break;
		case XK_m: ksym = XK_Return;    break;
		case XK_n: ksym = XK_Down;      break;
		case XK_p: ksym = XK_Up;        break;

		case XK_k: /* delete right */
			text[cursor] = '\0';
			match();
			break;
		case XK_u: /* delete left */
			insert(NULL, 0 - cursor);
			break;
		case XK_w: /* delete word */
			while(cursor > 0 && text[nextrune(-1)] == ' ')
				insert(NULL, nextrune(-1) - cursor);
			while(cursor > 0 && text[nextrune(-1)] != ' ')
				insert(NULL, nextrune(-1) - cursor);
			break;
		case XK_y: /* paste selection */
      for(int i=0; i<dc->scrcount; ++i){
        XConvertSelection(dc->dpy, (ev->state & ShiftMask) ? clip : XA_PRIMARY,
                          utf8, utf8, windows[i], CurrentTime);
      }
      return;
    default:
      return;
    }
	else if(ev->state & Mod1Mask)
    /* vi */
		switch(ksym) {
		case XK_g: ksym = XK_Home;  break;
		case XK_G: ksym = XK_End;   break;
		case XK_h: ksym = (vertical ? XK_Prior : XK_Up);    break;
		case XK_j: ksym = (vertical ? XK_Down  : XK_Next);  break;
		case XK_k: ksym = (vertical ? XK_Up    : XK_Prior); break;
		case XK_l: ksym = (vertical ? XK_Next  : XK_Down);  break;
		default:
			return;
		}
	switch(ksym) {
	default:
		if(!iscntrl(*buf))
			insert(buf, len);
		break;
	case XK_Delete:
		if(text[cursor] == '\0')
			return;
		cursor = nextrune(+1);
		/* fallthrough */
	case XK_BackSpace:
		if(cursor == 0)
			return;
		insert(NULL, nextrune(-1) - cursor);
		break;
	case XK_End:
		if(text[cursor] != '\0') {
			cursor = strlen(text);
			break;
		}
    for(int i=0; i<dc->scrcount; ++i){
      Menu *m = &menus[i];
      if(m->next) {
        /* jump to end of list and position items in reverse */
        m->cfirst = matchend;
        calcoffsets(i);
        m->cfirst = m->prev;
        calcoffsets(i);
        while(m->next && (m->cfirst = m->cfirst->right))
          calcalloffsets();
      }
    }
		sel = matchend;
		break;
	case XK_Escape:
        ret = EXIT_FAILURE;
        running = False;
	case XK_Home:
		if(sel == matches) {
			cursor = 0;
			break;
		}
    for(int i=0; i<dc->scrcount; ++i){
      sel = menus[i].cfirst = matches;
      calcoffsets(i);
    }
		break;
	case XK_Left:
		if(cursor > 0 && (!sel || !sel->left || vertical)) {
			cursor = nextrune(-1);
			break;
		}
		if(vertical)
			return;
		/* fallthrough */
	case XK_Up:
    if(sel && sel->left){
      sel = sel->left;
    for(int i=0; i<dc->scrcount; ++i){
      if(sel->right == menus[i].cfirst) {
        menus[i].cfirst = menus[i].prev;
        calcoffsets(i);
      }
    }
    }
		break;
	case XK_Next:
    /* take the default screen's pages */
		if(!menus[0].next)
			return;
    for(int i=0; i<dc->scrcount; ++i){
      sel = menus[i].cfirst = menus[0].next;
    }
    calcalloffsets();
		break;
	case XK_Prior:
    /* take the default screen's pages */
		if(!menus[0].prev)
			return;
    for(int i=0; i<dc->scrcount; ++i){
		  sel = menus[i].cfirst = menus[0].prev;
    }
		calcalloffsets();
		break;
	case XK_Return:
	case XK_KP_Enter:
    handle_return((sel && !(ev->state & ShiftMask)) ? sel->text : text);
		writehistory(sel ? sel->text : text);
	case XK_Right:
		if(text[cursor] != '\0') {
			cursor = nextrune(+1);
			break;
		}
		if(vertical)
			return;
		/* fallthrough */
	case XK_Down:
    if(sel && sel->right){
      sel = sel->right;
      for(int i=0; i<dc->scrcount; ++i){
        if(sel == menus[i].next) {
          menus[i].cfirst = menus[i].next;
          calcoffsets(i);
        }
      }
    }
		break;
	case XK_ISO_Left_Tab:
    if(sel){
      if(sel->left)
        sel = sel->left;
      else
        sel = matchend;
      for(int i=0; i<dc->scrcount; ++i){
        if(sel->right == menus[i].cfirst || sel == matchend) {
          menus[i].cfirst = menus[i].prev;
          calcoffsets(i);
        }
      }
    }
		break;
	case XK_Tab:
    /* cycle to the right or left */
    if(sel){
      if(sel->right)
        sel = sel->right;
      else
        sel = matches;
      for(int i=0; i<dc->scrcount; ++i){
        if(sel == menus[i].next) {
          menus[i].cfirst = menus[i].next;
          calcoffsets(i);
        }
        else if(sel == matches) {
          menus[i].cfirst = sel;
          calcoffsets(i);
        }
      }
    }
		break;
	}
	updatewindows();
}

char *
strchri(const char *s, int c) {
	char *u, *l;
	if(!isalpha(c)) return strchr(s, c);
	if(isupper(c)) {
		u = strchr(s, c);
		l = strchr(s, tolower(c));
	}
	else {
		l = strchr(s, c);
		u = strchr(s, toupper(c));
	}

	if(u && l) return u < l ? u : l;
	return u == NULL ? l : u;
}

void
match(void) {
	if(fuzzy) match_fuzzy();
	else match_tokens();
}

void
match_fuzzy(void) {
	size_t i;
	size_t len;
	Item *item;

	char *pos;

	len = strlen(text);

	matches = matchend = NULL;
	for(item = items; item && item->text; item++) {
		i = 0;
		for(pos = fstrchr(item->text, text[i]); pos && text[i]; i++, pos = fstrchr(pos+1, text[i]));
		if(i == len) appenditem(item, &matches, &matchend);
	}

  sel = matches;
  for(int i=0; i<dc->scrcount; ++i){
	  menus[i].cfirst = sel;
  }
	calcalloffsets();

  if(returnearly && menus[0].cfirst && !menus[0].cfirst->right) {
    handle_return(menus[0].cfirst->text);
  }
}

void
match_tokens(void) {
	static char **tokv = NULL;
	static int tokn = 0;

	char buf[sizeof text], *s;
	int i, tokc = 0;
	size_t len;
	Item *item, *lprefix, *lsubstr, *prefixend, *substrend;

	strcpy(buf, text);
	/* separate input text into tokens to be matched individually */
	for(s = strtok(buf, " "); s; tokv[tokc-1] = s, s = strtok(NULL, " "))
		if(++tokc > tokn && !(tokv = realloc(tokv, ++tokn * sizeof *tokv)))
			eprintf("cannot realloc %u bytes\n", tokn * sizeof *tokv);
	len = tokc ? strlen(tokv[0]) : 0;

	matches = lprefix = lsubstr = matchend = prefixend = substrend = NULL;
	for(item = items; item && item->text; item++) {
		for(i = 0; i < tokc; i++)
			if(!fstrstr(item->text, tokv[i]))
				break;
		if(i != tokc) /* not all tokens match */
			continue;
		/* exact matches go first, then prefixes, then substrings */
		if(!tokc || !fstrncmp(tokv[0], item->text, len+1))
			appenditem(item, &matches, &matchend);
		else if(!fstrncmp(tokv[0], item->text, len))
			appenditem(item, &lprefix, &prefixend);
		else
			appenditem(item, &lsubstr, &substrend);
	}
	if(lprefix) {
		if(matches) {
			matchend->right = lprefix;
			lprefix->left = matchend;
		}
		else
			matches = lprefix;
		matchend = prefixend;
	}
	if(lsubstr) {
		if(matches) {
			matchend->right = lsubstr;
			lsubstr->left = matchend;
		}
		else
			matches = lsubstr;
		matchend = substrend;
	}
  sel = matches;
  for(int i=0; i<dc->scrcount; ++i){
	  menus[i].cfirst = sel;
  }
	calcalloffsets();

  if(returnearly && menus[0].cfirst && !menus[0].cfirst->right) {
    handle_return(menus[0].cfirst->text);
  }
}

size_t
nextrune(int inc) {
	ssize_t n;

	/* return location of next utf8 rune in the given direction (+1 or -1) */
	for(n = cursor + inc; n + inc >= 0 && (text[n] & 0xc0) == 0x80; n += inc);
	return n;
}

void
paste(void) {
	/* we have been given the current selection, now insert it into input */
  for(int i=0; i<dc->scrcount; ++i){
    char *p, *q;
    int di;
    unsigned long dl;
    Atom da;
    XGetWindowProperty(dc->dpy, windows[i], utf8, 0, (sizeof text / 4) + 1, False,
                       utf8, &da, &di, &dl, &dl, (unsigned char **)&p);
    insert(p, (q = strchr(p, '\n')) ? q-p : (ssize_t)strlen(p));
    XFree(p);
  }
	updatewindows();
}

void
readstdin(void) {
	char buf[sizeof text], *p, *maxstr = NULL;
	size_t i = 0, max = 0, size = 0;
#define readstdin_internals(the_input_file) \
	for(; fgets(buf, sizeof buf, the_input_file); i++) {\
		if(i+1 >= size / sizeof *items)\
			if(!(items = realloc(items, (size += BUFSIZ))))\
				eprintf("cannot realloc %u bytes:", size);\
		if((p = strchr(buf, '\n')))\
			*p = '\0';\
		if(!(items[i].text = strdup(buf)))\
			eprintf("cannot strdup %u bytes:", strlen(buf)+1);\
		if(strlen(items[i].text) > max)\
			max = strlen(maxstr = items[i].text);\
	}\
	/* lines from the history file must appear first in menu */
	FILE *f;
  /* hash_t *hitems = hash_new(); */
  /* hash_set(hitems, "item1", (void *)1); */
  /* hash_each(hitems, {printf("%s: %p\n", key, val);}); */
  /* hash_free(hitems); */
	if(histfile && (f = fopen(histfile, "r"))) {
		readstdin_internals(f);
		histsize = i;
		fclose(f);
	}
	/* read each line from stdin and add it to the item list */
	readstdin_internals(stdin);
	if(items)
		items[i].text = NULL;
	inputw = maxstr ? textw(dc, maxstr) : 0;
}

int
writehistory(char *command) {
	size_t i = 0;
	FILE *f;
	if(!histfile || strlen(command) <= 0)
		return 0;
	if((f = fopen(histfile, "w"))) {
		fputs(command, f);
		fputc('\n', f);
		for(; i < histsize; i++) {
			if(strcmp(command, items[i].text) != 0) {
				fputs(items[i].text, f);
				fputc('\n', f);
			}
		}
		fclose(f);
		return 1;
	}
	return 0;
}

void
run(void) {
	XEvent ev;

	while(running && !XNextEvent(dc->dpy, &ev)) {
    Bool filter = True;
    for(int i=0; i<dc->scrcount; ++i){
      if(!XFilterEvent(&ev, windows[i]))
        filter = False;
    }
    if(filter){
      continue;
    }
		switch(ev.type) {
		case Expose:
			if(ev.xexpose.count == 0)
        for(int i=0; i<dc->scrcount; ++i){
          mapdc(dc, i, windows[i]);
        }
			break;
		case KeyPress:
			keypress(&ev.xkey);
			break;
		case SelectionNotify:
			if(ev.xselection.property == utf8)
				paste();
			break;
		case VisibilityNotify:
			if(ev.xvisibility.state != VisibilityUnobscured)
        for(int i=0; i<dc->scrcount; ++i){
          XRaiseWindow(dc->dpy, windows[i]);
        }
			break;
		}
	}
}

void
setup(void) {
	int screen = DefaultScreen(dc->dpy);

	clip = XInternAtom(dc->dpy, "CLIPBOARD",   False);
	utf8 = XInternAtom(dc->dpy, "UTF8_STRING", False);

	/* calculate menu geometry */
	barh = (line_height > dc->font.height + 2) ? line_height : dc->font.height + 2;
	lmax = MAX(lmax, 0);
  windows = (Window *)calloc(dc->scrcount, sizeof(Window));
  if(dc->info){
    for(int i=0; i<dc->scrcount; ++i) {
      DM *dm = &dc->menus[i];
      dm->width = dc->info[i].width;
      dm->height = barh + TLINE_HEIGHT + BLINE_HEIGHT;
      dm->x = dc->info[i].x_org;
      dm->y = dc->info[i].y_org +
        (topbar ? yoffset : dc->info[i].height - dm->height - yoffset);
      createwindow(&windows[i], i);
    }
	}
	else
	{
    DM *dm = &dc->menus[0];
		dm->x = 0;
		dm->width = DisplayWidth(dc->dpy, screen);
      dm->height = barh + TLINE_HEIGHT + BLINE_HEIGHT;
		dm->y = topbar ? yoffset : DisplayHeight(dc->dpy, screen) - dm->width - yoffset;
    createwindow(&windows[0], 0);
	}
  updatewindows();
}

void
createwindow(Window *window, int scrnum) {
  DM *dm = &dc->menus[scrnum];
	int screen = DefaultScreen(dc->dpy);
	Window root = RootWindow(dc->dpy, screen);
	XSetWindowAttributes swa;
	XIM xim;

  dm->x += xoffset;
  dm->width = width ? width : dm->width;

	promptw = prompt ? textw(dc, prompt) : 0;
	inputw = MIN(inputw, dm->width/3);
	match();

	/* create menu window */
	swa.override_redirect = True;
	swa.event_mask = ExposureMask | KeyPressMask | VisibilityChangeMask;
	*window = XCreateWindow(dc->dpy, root, dm->x, dm->y, dm->width, dm->height, 0,
	                       DefaultDepth(dc->dpy, screen), CopyFromParent,
	                       DefaultVisual(dc->dpy, screen),
	                       CWOverrideRedirect | CWEventMask, &swa);

	/* open input methods */
  xim = XOpenIM(dc->dpy, NULL, NULL, NULL);
	xic = XCreateIC(xim, XNInputStyle, XIMPreeditNothing | XIMStatusNothing,
	                XNClientWindow, *window, XNFocusWindow, *window, NULL);

  if(monitor == -1 || monitor == scrnum){
    XMapRaised(dc->dpy, *window);
  }
	resizedc(dc, scrnum);
}

int msleep(unsigned long milisec)
{
  struct timespec req={0, 0};
  time_t sec=(int)(milisec/1000);
  milisec=milisec-(sec*1000);
  req.tv_sec=sec;
  req.tv_nsec=milisec*1000000L;
  while(nanosleep(&req,&req)==-1)
    continue;
  return 1;
}

void
anim(int origin, int target){
  int frequency = 60;
  int steps = frequency*animduration/1000;
  float interval = animduration/steps;
  float current = origin;
  float increment = (target - origin) / steps;
  for (int i=0; i<steps; ++i){
    current += increment;
    if((increment >= 0 && current > target) ||
       (increment < 0 && current < target))
      break;
    for(int scrnum=0; scrnum<dc->scrcount; ++scrnum){
      DM *dm = &dc->menus[scrnum];
      XMoveResizeWindow(dc->dpy, windows[scrnum], dm->x, dm->y, dm->width, current);
      mapdc(dc, scrnum, windows[scrnum]);
    }
    msleep(interval);
    XFlush(dc->dpy);
  }
}

void
close_anim(void){
  anim(dc->menus[0].height, 1);
}

void handle_return(char* value) {
  fputs(value, stdout);
  fflush(stdout);
  ret = EXIT_SUCCESS;
  running = False;
}

void
usage(void) {
    printf("Usage: i3ci-menu [OPTION]...\n");
    printf("Display newline-separated input stdin as a menubar.\n");
    printf("\n");
    printf("  -a N          Set the approximate duration of the animations.\n");
    printf("                If 0 the animations are disabled.\n");
    printf("                Default value is 0.\n");
    printf("\n");
    printf("  -b            i3ci-menu appears at the bottom of the screen.\n");
    printf("\n");
    printf("  -f            grab keyboard before reading stdin.\n");
    printf("\n");
    printf("  -h N          set i3ci-menu height to N pixels.\n");
    printf("\n");
    printf("  -hist FILE    store user choices in the specified file,\n");
    printf("                the value in the file are always displayed\n");
    printf("                first.\n");
    printf("\n");
    printf("  -i            i3ci-menu matches menu items case insensitively.\n");
    printf("\n");
    printf("  -lmax LINES   maximum number of lines when items are\n");
    printf("                vertically listed.\n");
    printf("\n");
    printf("  -lv           i3ci-menu lists items vertically.\n");
    printf("\n");
    printf("  -m MONITOR    i3ci-menu appears only on the given screen. If this\n");
    printf("                agument is not set, i3ci-menu displays the menu on\n");
    printf("                all available monitors.\n");
    printf("\n");
    printf("  -p PROMPT     prompt to be displayed to the left of the\n");
    printf("                input field.\n");
    printf("\n");
    printf("  -q            quiet mode.\n");
    printf("\n");
    printf("  -r            return as soon as a single match is found.\n");
    printf("\n");
    printf("  -fn FONT      font or font set to be used.\n");
    printf("\n");
    printf("  -nb COLOR     normal background color\n");
    printf("                #RGB, #RRGGBB, and color names supported.\n");
    printf("\n");
    printf("  -nf COLOR     normal foreground color.\n");
    printf("\n");
    printf("  -sb COLOR     selected background color.\n");
    printf("\n");
    printf("  -sf COLOR     selected foreground color.\n");
    printf("\n");
    printf("  -v            display version information.\n");
    printf("\n");
    printf("  -w N          set i3ci-menu width to N pixels.\n");
    printf("\n");
    printf("  -x N          set i3ci-menu x offset to N pixels.\n");
    printf("\n");
    printf("  -y N          set i3ci-menu y offset to N pixels.\n");
    printf("\n");
    printf("  -z            enable fuzzy matching, if this option is not\n");
    printf("                specified then token matching is used.");

	exit(EXIT_FAILURE);
}
