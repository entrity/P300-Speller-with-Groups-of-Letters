import sys
import pygtk
pygtk.require('2.0')
import gtk

ROW_CT = 2
COL_CT = 2
FLASH_COLOR = gtk.gdk.Color(0,65535,65535)
TARGET_COLOR = gtk.gdk.Color(65535,0,65535)
FLASH_DURATION = 1
TARGET_DURATION = 1

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
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    if 'openvibe' not in sys.argv:
      self.window.connect("destroy", self.destroy)
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
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.resize(600,600)
    self.window.add(self.vbox)
    self.window.show()
    self._set_view(())

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

  def _highlight_cell(self, row, col, color, duration):
    i = COL_CT * row + col
    print 'highlight cell'
    self.lbls[i].modify_bg(gtk.STATE_NORMAL, FLASH_COLOR)

  def highlight_row(self, row):
    for col in range(COL_CT):
      self._highlight_cell(row, col, FLASH_COLOR, FLASH_DURATION)

  def highlight_col(self, col):
    for row in range(ROW_CT):
      self._highlight_cell(row, col, FLASH_COLOR, FLASH_DURATION)

  def highlight_target(self, row, col):
    self._highlight_cell(row, col, TARGET_COLOR, TARGET_DURATION)

  def main(self):
    gtk.main()

  def destroy(self, widget, data=None):
    gtk.main_quit()

  def _key_press_event(self, widget, event):
    print('key pressed!')
    name = gtk.gdk.keyval_name(event.keyval)
    if name == 'q':
      self.destroy()
    else:
      print name

if __name__ == "__main__" and 'openvibe' not in sys.argv:
  base = Base()
  base.main()
