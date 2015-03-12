'''
VOLUME CALCULATION STL binary MODELS
Author: Mar Canet (mar.canet@gmail.com) - september 2012
Description: useful to calculate cost in a 3D printing ABS or PLA usage
'''
import struct
import sys

class STLUtils:
	def resetVariables(self):
		self.normals = []
		self.points = []
		self.triangles = []
		self.bytecount = []
		self.fb = [] # debug list
		self.min_x = float("inf")
		self.min_y = float("inf")
		self.min_z = float("inf")
		self.max_x = float("-inf")
		self.max_y = float("-inf")
		self.max_z = float("-inf")
		
	# Calculate volume fo the 3D mesh using Tetrahedron volume
	# based in: http://stackoverflow.com/questions/1406029/how-to-calculate-the-volume-of-a-3d-mesh-object-the-surface-of-which-is-made-up
	def signedVolumeOfTriangle(self,p1, p2, p3):
		v321 = p3[0]*p2[1]*p1[2]
		v231 = p2[0]*p3[1]*p1[2]
		v312 = p3[0]*p1[1]*p2[2]
		v132 = p1[0]*p3[1]*p2[2]
		v213 = p2[0]*p1[1]*p3[2]
		v123 = p1[0]*p2[1]*p3[2]
		return (1.0/6.0)*(-v321 + v231 + v312 - v132 - v213 + v123)

	def unpack(self, sig, l):
		s = self.f.read(l)
		self.fb.append(s)
		return struct.unpack(sig, s)

	def read_triangle(self):
		n  = self.unpack("<3f", 12)
		p1 = self.unpack("<3f", 12)
		p2 = self.unpack("<3f", 12)
		p3 = self.unpack("<3f", 12)
		b  = self.unpack("<h", 2)
		
		self.normals.append(n)
		l = len(self.points)
		self.points.append(p1)
		self.min_x = min(self.min_x, p1[0], p2[0], p3[0])
		self.max_x = max(self.max_x, p1[0], p2[0], p3[0])
		self.points.append(p2)
		self.min_y = min(self.min_y, p1[1], p2[1], p3[1])
		self.max_y = max(self.max_y, p1[1], p2[1], p3[1])
		self.points.append(p3)
		self.min_z = min(self.min_z, p1[2], p2[2], p3[2])
		self.max_z = max(self.max_z, p1[2], p2[2], p3[2])
		self.triangles.append((l, l+1, l+2))
		self.bytecount.append(b[0])
		return self.signedVolumeOfTriangle(p1,p2,p3)

	def read_length(self):
   		length = struct.unpack("@i", self.f.read(4))
   		return length[0]

	def read_header(self):
		self.f.seek(self.f.tell()+80)
		
	def cm3_To_inch3Transform(self, v):
		return v*0.0610237441
		
	def calculateWeight(self,volumeIn_cm):
		return volumeIn_cm*1.04
	
	def calculateVolume(self,infilename, unit):
		print infilename
		self.resetVariables()
		totalVolume = 0
		try:
			self.f = open( infilename, "rb")
			self.read_header()
			l = self.read_length()
			print "total triangles:",l
			try:
				while True:
					totalVolume +=self.read_triangle()
			except Exception, e:
				#print e
				print "End calculate triangles volume"
			#print len(self.normals), len(self.points), len(self.triangles), l, 
			if unit=="cm":
				totalVolume = (totalVolume/1000)
				print "Total volume:", totalVolume,"cm"
			else:
				totalVolume = self.cm3_To_inch3Transform(totalVolume/1000)
				print "Total volume:", totalVolume,"inch"
			print "min_x: ", self.min_x
			print "min_y: ", self.min_y
			print "min_z: ", self.min_z
			print "max_x: ", self.max_x
			print "max_y: ", self.max_y
			print "max_z: ", self.max_z

		except Exception, e:
			print e
		return totalVolume

if __name__ == '__main__':
	if len(sys.argv)==1:
		print "Define model to calculate volume ej: python mesure_volume.py torus.stl"
	else:
		mySTLUtils = STLUtils()
		if(len(sys.argv)>2 and sys.argv[2]=="inch"):
			mySTLUtils.calculateVolume(sys.argv[1],"inch")
		else:
			mySTLUtils.calculateVolume(sys.argv[1],"cm")
