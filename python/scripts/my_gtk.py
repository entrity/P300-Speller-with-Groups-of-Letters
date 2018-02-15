import pygtk
pygtk.require('2.0')
import gtk

class Base:
  def __init__(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.connect("destroy", self.destroy)
    self.window.show()

  def main(self):
    gtk.main()

  def destroy(self, widget, data=None):
    gtk.main_quit()

if __name__ == "__main__":
  base = Base()
  base.main()
