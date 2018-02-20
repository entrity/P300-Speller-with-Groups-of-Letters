# import pygtk
# pygtk.require('2.0')
# import gtk

# class Base:
#   def __init__(self):
#     self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#     self.window.connect("destroy", self.destroy)
#     self.window.show()

#   def main(self):
#     gtk.main()

#   def destroy(self, widget, data=None):
#     gtk.main_quit()


class MyOVBox(OVBox):
	def __init__(self):
		OVBox.__init__(self)
		
	def initialize(self):
		print('Python version:', sys.version)
		# self.gui = new Base()
		return
		
	def process(self):
		pass
		# global count
		# global stimmap
		# count = count + 1
		# for chunkIndex in range( len(self.input[0]) ):
		# 	chunk = self.input[0].pop()
		# 	if(type(chunk) == OVStimulationSet):
		# 		for stimIdx in range(len(chunk)):
		# 			stim=chunk.pop();
		# 			if stim.identifier in stimmap:
		# 				print 'Received stim', stim.identifier, stimmap[stim.identifier], 'stamped at', stim.date
		# 			else:
		# 				print 'Received stim', stim.identifier, 'ERRR', 'stamped at', stim.date

			#else:
			#	print 'Received chunk of type ', type(chunk), " looking for StimulationSet"
		return
		
	def uninitialize(self):
		# nop
		return

box = MyOVBox()
