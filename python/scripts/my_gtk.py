import sys
import re
import pygtk
pygtk.require('2.0')
import gtk
import gobject

ROW_CT = 2
COL_CT = 2
NULL_FG = gtk.gdk.Color(20000,20000,20000)
NULL_BG = gtk.gdk.Color(60535,60535,60535)
NULL_BG = gtk.gdk.Color(0,0,0)
FLASH_BG = gtk.gdk.Color(2000,2000,2000)
FLASH_FG = gtk.gdk.Color(60535,60535,60535)
TARGET_FG = gtk.gdk.Color(5000,5000,5000)
TARGET_BG = gtk.gdk.Color(14535,13500,36535) # Purple
WINDOW_DIM = (700,700)
FONT_SIZES = (45000, 55000, 60000, 40000)


CHARS = [ chr(x) for x in range(65,91) ] + [ chr(x) for x in range(48,58) ]

class Cell(gtk.EventBox):
  def __init__(self, i, table):
    gtk.EventBox.__init__(self)
    self.lbl = gtk.Label()
    self.lbl.set_justify(gtk.JUSTIFY_CENTER)
    self.lbl.show()
    self.add(self.lbl)
    self.show()
    self.i = i
    self.r = int(i / COL_CT)
    self.c = i % COL_CT
    self.text = None
    self.size = None
    table.attach(self, self.c, self.c+1, self.r, self.r+1)

  def markup(self, **kwargs):
    if 'text' in kwargs:
      self.text = kwargs['text']
    text = kwargs.get('text', self.text)
    if 'size' in kwargs:
      self.size = kwargs['size']
    size = kwargs.get('size', self.size)
    if 'factor' in kwargs:
      size = int(kwargs['factor'] * size)
    self.lbl.set_markup('<span size="%d">%s</span>' % (size, text))
    if 'fg' in kwargs: self.fg(kwargs.get('fg'))
    if 'bg' in kwargs: self.bg(kwargs.get('bg'))

  def fg(self, fg):
    self.lbl.modify_fg(gtk.STATE_NORMAL, fg)
  
  def bg(self, bg):
    self.modify_bg(gtk.STATE_NORMAL, bg)

class Base:
  def __init__(self):
    # Non-gui attrs
    self.timer = None
    self.target_ct = 0
    # Gui attrs
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    if 'openvibe' not in sys.argv:
      self.window.connect("delete_event", self._delete_event)
      self.window.connect("destroy", self._destroy)
    self.window.connect("key-press-event", self._key_press_event)
    # Table
    self.table = gtk.Table(rows=2, columns=2, homogeneous=True)
    self.cells = [Cell(i, self.table) for i in range(4)]
    self.table.show()
    # Target
    self.target = gtk.Label('Target : ')
    self.target.set_justify(gtk.JUSTIFY_LEFT)
    self.target.show()
    # Main container
    self.vbox = gtk.VBox(False, 0)
    self.vbox.pack_start(self.table, expand=True, fill=True)
    self.vbox.pack_end(self.target, expand=False, fill=True)
    self.vbox.show()
    # Window
    self.window.resize(*WINDOW_DIM)
    self.window.add(self.vbox)
    self.window.show()
    self._set_view(())
    self._restore_bg()
    self.cells[1].lbl.modify_fg(gtk.STATE_NORMAL, NULL_FG)

  def _get_chars(self, selections):
    threes = [CHARS[i:i+3] for i in range(0, len(CHARS), 3)]
    triptrips = [threes[i:i+3] for i in range(0, len(threes), 3)]
    if len(selections) == 0:
      str9s = ['\n'.join(' '.join(x) for x in y) for y in triptrips]
      return str9s
    elif len(selections) == 1:
      return [' '.join(x) for x in triptrips[selections[0]]] + ['back']
    else:
      return triptrips[selections[0]][selections[1]] + ['back']

  def _set_view(self, selections):
    lists = self._get_chars(selections)
    for i in range(4):
      self.cells[i].markup(text=lists[i], size=FONT_SIZES[len(selections)])
    if len(selections) > 0:
      self.cells[i].markup(text='&#8592;back', size=FONT_SIZES[-1])

  def start(self, target_text):
    self.target.set_markup(target_text)

  def restore(self):
    for cell in self.cells:
      cell.markup(bg=NULL_BG, fg=NULL_FG)

  def _restore_bg(self):
    for lbl in self.cells:
      lbl.bg(NULL_BG)
      lbl.fg(NULL_FG)

  def cell(self, row, col):
    return self.cells[COL_CT * row + col]

  def highlight_row(self, row):
    for col in range(COL_CT):
      self.cell(row, col).markup(bg=FLASH_BG, fg=FLASH_FG, factor=1.25)

  def highlight_col(self, col):
    for row in range(ROW_CT):
      self.cell(row, col).markup(bg=FLASH_BG, fg=FLASH_FG, factor=1.25)

  def highlight_target(self, row, col):
    self.target_ct += 1
    self.cell(row, col).markup(bg=TARGET_BG, fg=TARGET_FG) # Leave lit until next thing should be lit
    self.target.set_markup('Target: (%d,%d) [%d]' % (row, col, self.target_ct))

  def _destroy(self, widget, data=None):
    print('quitting')
    gtk.main_quit()

  def _delete_event(self, widget, event, data=None):
    gtk.main_quit()
    return gtk.FALSE

  def _key_press_event(self, widget, event):
    print('key pressed!')
    name = gtk.gdk.keyval_name(event.keyval)
    if name == 'q':
      self._destroy(widget, event)
    elif name == 't':
      self.highlight_row(0)
    elif name == 'b':
      self.highlight_row(1)
    elif name == 'l':
      self.highlight_col(0)
    elif name == 'r':
      self.highlight_col(1)
    elif name == 'w':
      self.highlight_target(0, 0)
    elif name == 'a':
      self.highlight_target(1, 0)
    elif name == 's':
      self.highlight_target(0, 1)
    elif name == 'd':
      self.highlight_target(1, 1)
    elif name == '1':
      self._set_view(())
    elif name == '2':
      self._set_view((1,))
    elif name == '3':
      self._set_view((1,2))
    else:
      print name

  def main(self):
    gtk.main()


if __name__ == "__main__" and 'openvibe' not in sys.argv:
  base = Base()
  base.main()
