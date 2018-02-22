import sys
import pygtk
pygtk.require('2.0')
import gtk
import gobject

ROW_CT = 2
COL_CT = 2
NULL_FG = gtk.gdk.Color(20000,20000,20000)
NULL_BG = gtk.gdk.Color(60535,60535,60535)
FLASH_BG = gtk.gdk.Color(0,0,0)
FLASH_FG = gtk.gdk.Color(60535,60535,60535)
TARGET_BG = gtk.gdk.Color(25535,0,25535)
FLASH_DURATION = 250
TARGET_DURATION = 250

CHARS = [ chr(x) for x in range(65,91) ] + [ chr(x) for x in range(48,58) ]

def make_label():
  eb = gtk.EventBox()
  l = gtk.Label()
  l.set_justify(gtk.JUSTIFY_CENTER)
  l.show()
  eb.add(l)
  eb.show()
  return eb

class Base:
  def __init__(self):
    # Non-gui attrs
    self.timer = None
    # Gui attrs
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    if 'openvibe' not in sys.argv:
      self.window.connect("delete_event", self._delete_event)
      self.window.connect("destroy", self._destroy)
    self.window.connect("key-press-event", self._key_press_event)
    self.lbls = [make_label() for i in range(4)]
    # Table
    self.table = gtk.Table(rows=2, columns=2, homogeneous=True)
    self.table.attach(self.lbls[0], 0, 1, 0, 1)
    self.table.attach(self.lbls[1], 1, 2, 0, 1)
    self.table.attach(self.lbls[2], 0, 1, 1, 2)
    self.table.attach(self.lbls[3], 1, 2, 1, 2)
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
    self.window.resize(600,600)
    self.window.add(self.vbox)
    self.window.show()
    self._set_view(())
    self._restore_bg()
    self.lbls[1].get_children()[0].modify_fg(gtk.STATE_NORMAL, NULL_FG)

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
    print(lists)
    for i in range(4):
      size = 50000 if len(selections) == 0 else 100000
      self.lbls[i].get_children()[0].set_markup(('<span size="%d">' % size)+lists[i]+'</span>')
    if len(selections) > 0:
      self.lbls[3].get_children()[0].set_markup('<span size="40000">&#8592;back</span>')

  def start(self, target_text):
    self.target_text = target_text

  def _restore_bg(self):
    for lbl in self.lbls:
      lbl.modify_bg(gtk.STATE_NORMAL, NULL_BG)
      lbl.get_children()[0].modify_fg(gtk.STATE_NORMAL, NULL_FG)


  def _highlight_cell(self, row, col, bg_color, fg_color=None):
    i = COL_CT * row + col
    self.lbls[i].modify_bg(gtk.STATE_NORMAL, bg_color)
    if fg_color != None:
      self.lbls[i].get_children()[0].modify_fg(gtk.STATE_NORMAL, fg_color)

  def highlight_row(self, row):
    for col in range(COL_CT):
      self._highlight_cell(row, col, FLASH_BG, FLASH_FG)
    gobject.timeout_add(FLASH_DURATION, self._restore_bg)

  def highlight_col(self, col):
    for row in range(ROW_CT):
      self._highlight_cell(row, col, FLASH_BG, FLASH_FG)
    gobject.timeout_add(FLASH_DURATION, self._restore_bg)

  def highlight_target(self, row, col):
    self._highlight_cell(row, col, TARGET_BG)
    gobject.timeout_add(TARGET_DURATION, self._restore_bg)

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

  print('end')