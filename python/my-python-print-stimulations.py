
class MyOVBox(OVBox):
	def __init__(self):
		OVBox.__init__(self)
		
	def initialize(self):
		# nop
		return
		
	def process(self):
		for chunkIndex in range( len(self.input[0]) ):
			chunk = self.input[0].pop()
			if(type(chunk) == OVStimulationSet):
				for stimIdx in range(len(chunk)):
					stim=chunk.pop();
					print 'Received stim', stim.identifier, 'stamped at', stim.date, 's'
			#else:
			#	print 'Received chunk of type ', type(chunk), " looking for StimulationSet"
		return
		
	def uninitialize(self):
		# nop
		return

box = MyOVBox()
