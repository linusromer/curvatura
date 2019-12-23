#!/usr/bin/env python

# Curvatura version 20191223

# This is a FontForge plug-in to harmonize or tunnify 
# or add inflection points to the selected parts.
# Installation: FontForge says that you have to copy the file to 
# $(PREFIX)/share/fontforge/python or ~/.FontForge/python
# but for me (on Linux) it works at
# ~/.config/fontforge/python
# and for Windows it might be at
# C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python
# You then will find "Harmonize" and "Tunnify" in the "Tools" menu.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Copyright 2019 by Linus Romer

import fontforge,math,cmath

class Curvatura:
		
	# Returns 1 iff the point p is to the right of the line
	# going from point q through point r,
	# returns -1 iff the point p is to the left of the line,
	# returns 0 iff the point p is to the left of the line
	@staticmethod
	def side(px,py,qx,qy,rx,ry):
		crossproduct = (rx-qx)*(qy-py) - (ry-qy)*(qx-px)
		if crossproduct > 0:
			return 1
		elif crossproduct < 0:
			return -1	
		else:
			return 0
	
	# Returns for a cubic bezier path (a,b), (c,d), (e,f), (g,h)
	# the directions at (a,b) and (g,h). 
	# Other than the derivative, the direction
	# has never length 0 as long as (a,b) != (g,h)
	@staticmethod
	def directions_at_nodes(a,b,c,d,e,f,g,h):
		if (c,d) == (a,b) and (e,f) == (g,h):
			return g-a,h-b,g-a,h-b
		elif (c,d) == (a,b):
			return e-a,f-b,g-e,h-f
		elif (e,f) == (g,h):
			return c-a,d-b,g-c,h-d
		else: # generic case
			return c-a,d-b,g-e,h-f
	
	# Returns the curvature at time t of a cubic bezier segment
	# (a,b), (c,d), (e,f), (g,h).
	# This method is not necessary for the FontForge plugin but may be
	# useful for debugging and documenting.
	@staticmethod
	def curvature_cubic(a,b,c,d,e,f,g,h,t):
		return ((-6*g*t+18*e*t-18*c*t+6*a*t-6*e+12*c-6*a) \
		*(3*h*t**2-9*f*t**2+9*d*t**2-3*b*t**2+6*f*t-12*d*t+6*b*t+3*d-3*b)\
		+(6*h*t-18*f*t+18*d*t-6*b*t+6*f-12*d+6*b) \
		*(3*g*t**2-9*e*t**2+9*c*t**2-3*a*t**2+6*e*t-12*c*t+6*a*t+3*c-3*a)) \
		/(3*((h*t**2-3*f*t**2+3*d*t**2-b*t**2+2*f*t-4*d*t+2*b*t+d-b)**2 \
		+(g*t**2-3*e*t**2+3*c*t**2-a*t**2+2*e*t-4*c*t+2*a*t+c-a)**2)**.5 \
		*((3*h*t**2-9*f*t**2+9*d*t**2-3*b*t**2+6*f*t-12*d*t+6*b*t+3*d-3*b)**2+ \
		(3*g*t**2-9*e*t**2+9*c*t**2-3*a*t**2+6*e*t-12*c*t+6*a*t+3*c-3*a)**2))

	# Returns the curvature at time t of a quadratic bezier segment
	# (a,b), (c,d), (e,f).
	# This method is not necessary for the FontForge plugin but may be
	# useful for debugging and documenting.
	@staticmethod
	def curvature_quadratic(a,b,c,d,e,f,t):	
		return ((-2*e+4*c-2*a)*(2*f*t-4*d*t+2*b*t+2*d-2*b)\
		+(2*f-4*d+2*b)*(2*e*t-4*c*t+2*a*t+2*c-2*a))\
		/(2*((f*t-2*d*t+b*t+d-b)**2+(e*t-2*c*t+a*t+c-a)**2)**.5\
		*((2*f*t-4*d*t+2*b*t+2*d-2*b)**2+(2*e*t-4*c*t+2*a*t+2*c-2*a)**2))
			
	# Splits a contour c after point number i and time 0 < t < 1
	# such that the bezier segment c[i],c[i+1],c[i+2],c[i+3]
	# becomes two segments c[i],q1,q2,q3 and
	# q3,r1,r2,c[i+3].
	@staticmethod
	def split(c,i,t):
		l = len(c)
		if 0 < t < 1 and i % 1 == 0 and 0 <= i < l and c[i].on_curve \
		and not c[i+1].on_curve and not c[i+2].on_curve \
		and c[(i+3)%l].on_curve:
			qx1 = c[i].x + t*(c[i+1].x-c[i].x)
			qy1 = c[i].y + t*(c[i+1].y-c[i].y)
			qx2 = c[i+1].x + t*(c[i+2].x-c[i+1].x)
			qy2 = c[i+1].y + t*(c[i+2].y-c[i+1].y)
			rx2 = c[i+2].x + t*(c[(i+3)%l].x-c[i+2].x)
			ry2 = c[i+2].y + t*(c[(i+3)%l].y-c[i+2].y)
			rx1 = qx2 + t*(rx2-qx2)
			ry1 = qy2 + t*(ry2-qy2)
			qx2 = qx1 + t*(qx2-qx1)
			qy2 = qy1 + t*(qy2-qy1)
			qx3 = qx2 + t*(rx1-qx2)
			qy3 = qy2 + t*(ry1-qy2)     
			doublesegment = fontforge.contour()
			doublesegment.moveTo(c[i].x,c[i].y)
			doublesegment.cubicTo(qx1,qy1,qx2,qy2,qx3,qy3)
			doublesegment.cubicTo(rx1,ry1,rx2,ry2,c[(i+3)%l].x,c[(i+3)%l].y)
			if i+3 == l and c.closed: # end point is starting point 
				c.reverseDirection() # dirty hack because ff2017 is buggy
				doublesegment.reverseDirection()
				c[0:4] = doublesegment
				c.reverseDirection()
			else: # generic case
				c[i:i+4] = doublesegment		


	# Returns the "corner point" of a cubic bezier segment
	# (a,b),(c,d),(e,f),(g,h), which is the intersection of the
	# lines (a,b)--(c,d) and (e,f)--(g,h) in the generic case.
	# If there is no reasonable corner point None,None will be returned.
	@staticmethod
	def corner_point(a,b,c,d,e,f,g,h):
		if (c,d) == (a,b) and (e,f) == (g,h):
			return .5*(a+g),.5*(b+h)
		elif (c,d) == (a,b):
			return e,f
		elif (e,f) == (g,h):
			return c,d
		else: # generic case
			# check if the handles are on the same side 
			# and no inflection occurs and no division by zero
			# will occur:
			if Curvatura.side(c,d,a,b,g,h)*Curvatura.side(e,f,a,b,g,h) \
			< 0 or not Curvatura.inflection(a,b,c,d,e,f,g,h) is None \
			or c*h-a*h-d*g+b*g-c*f+a*f+d*e-b*e == 0 \
			or c*h-a*h-d*g+b*g-c*f+a*f+d*e-b*e == 0:
				return None,None
			else: # generic case
				return a+((c-a)*(e*h-a*h-f*g+b*g+a*f-b*e))\
				/(c*h-a*h-d*g+b*g-c*f+a*f+d*e-b*e),\
				b+((d-b)*(e*h-a*h-f*g+b*g+a*f-b*e))\
				/(c*h-a*h-d*g+b*g-c*f+a*f+d*e-b*e)

	# Returns the inflection point time of a cubic bezier segment
	# (a,b),(c,d),(e,f),(g,h).
	# If there is no inflection point, None is returned.
	@staticmethod
	def inflection(a,b,c,d,e,f,g,h):
		# curvature=0 is an equation aa*t**2+bb*t+c=0 with coefficients: 
		aa = e*h-2*c*h+a*h-f*g+2*d*g-b*g+3*c*f-2*a*f-3*d*e+2*b*e+a*d-b*c
		bb = c*h-a*h-d*g+b*g-3*c*f+3*a*f+3*d*e-3*b*e-2*a*d+2*b*c
		cc = c*f-a*f-d*e+b*e+a*d-b*c
		if aa == 0 and not bb == 0 and 0.001 < -c/bb < 0.999: # lin. eq.
			return -c/bb
		else:
			discriminant = bb**2-4*aa*cc
			if discriminant >= 0 and not aa == 0:
				t1 = (-bb + discriminant**.5)/(2*aa)
				t2 = (-bb - discriminant**.5)/(2*aa)
				if 0.001 < t1 < 0.999: # rounding issues
					return t1
				elif 0.001 < t2 < 0.999:
					return t2
		return None
			
	# Adds missing inflection points to a fontforge contour c.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def inflection_contour(c,is_glyph_variant):
		l = len(c)
		j = 0 # index that will run from 0 to l-1 (may contain jumps)
		while j < l: # going through the points c[j]
			# if a point is selected search for the next on_curve point
			# this must be the overovernext point
			if (c[j].on_curve and not c[(j+1)%l].on_curve \
			and not c[(j+2)%l].on_curve and c[(j+3)%l].on_curve) \
			and (c[j].selected and c[(j+3)%l].selected \
			or c[(j+2)%l].selected or c[(j+1)%l].selected \
			or is_glyph_variant) and (j+3)%l != j:
				t = Curvatura.inflection(c[j].x,c[j].y,c[(j+1)%l].x,c[(j+1)%l].y,
				c[(j+2)%l].x,c[(j+2)%l].y,c[(j+3)%l].x,c[(j+3)%l].y)
				if not t is None:
					Curvatura.split(c,j,t)
					if not is_glyph_variant:
						c[(j+3)%l].selected = True # mark new points
					j += 3 # we just added 3 points...
					l += 3 # we just added 3 points...
				j += 2 # we can jump by 2+1 instead of 1
			j += 1

	# Tunnifies a cubic bezier path (a,b), (c,d), (e,f), (g,h).
	# i.e. moves the handles (c,d) and (e,f) on the lines (a,b)--(c,d) 
	# and (e,f)--(g,h) in order to reach the ideal stated by Eduardo Tunni.
	@staticmethod
	def tunnify(a,b,c,d,e,f,g,h):
		u,v = Curvatura.corner_point(a,b,c,d,e,f,g,h)
		if not u is None and not v is None:
			t = .5*((((c-a)**2+(d-b)**2)/((u-a)**2+(v-b)**2))**.5\
			+(((e-g)**2+(f-h)**2)/((u-g)**2+(v-h)**2))**.5)
			return (1-t)*a+t*u,(1-t)*b+t*v,(1-t)*g+t*u,(1-t)*h+t*v
		return c,d,e,f

	# Tunnifies the handles of a fontforge contour c.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def tunnify_contour(c,is_glyph_variant):
		l = len(c)
		j = 0 # index that will run from 0 to l-1 (may contain jumps)
		while j < l: # going through the points c[j]
			# if a point is selected search for the next on_curve point
			# this must be the overovernext point
			if (c[j].on_curve and not c[(j+1)%l].on_curve \
			and not c[(j+2)%l].on_curve and c[(j+3)%l].on_curve) \
			and (c[j].selected and c[(j+3)%l].selected \
			or c[(j+2)%l].selected or c[(j+1)%l].selected \
			or is_glyph_variant) and (j+3)%l != j:
				c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y = \
				Curvatura.tunnify(c[j].x,c[j].y,c[(j+1)%l].x,c[(j+1)%l].y, 
				c[(j+2)%l].x,c[(j+2)%l].y,c[(j+3)%l].x,c[(j+3)%l].y)
				j += 2 # we can jump by 2+1 instead of 1
			j += 1
			
	# Sets a fixed ratio t for the handles of a cubic bezier path 
	# (a,b), (c,d), (e,f), (g,h) from the nodes to the corner point.
	@staticmethod
	def tunnifix(a,b,c,d,e,f,g,h,t):
		u,v = Curvatura.corner_point(a,b,c,d,e,f,g,h)
		if not u is None and not v is None:
			return (1-t)*a+t*u,(1-t)*b+t*v,(1-t)*g+t*u,(1-t)*h+t*v
		return c,d,e,f
				
	# Applies tunnifix() to a fontforge contour c.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def tunnifix_contour(c,t,is_glyph_variant):
		l = len(c)
		j = 0 # index that will run from 0 to l-1 (may contain jumps)
		while j < l: # going through the points c[j]
			# if a point is selected search for the next on_curve point
			# this must be the overovernext point
			if (c[j].on_curve and not c[(j+1)%l].on_curve \
			and not c[(j+2)%l].on_curve and c[(j+3)%l].on_curve) \
			and (c[j].selected and c[(j+3)%l].selected \
			or c[(j+2)%l].selected or c[(j+1)%l].selected \
			or is_glyph_variant) and (j+3)%l != j:
				c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y = \
				Curvatura.tunnifix(c[j].x,c[j].y,c[(j+1)%l].x,c[(j+1)%l].y, 
				c[(j+2)%l].x,c[(j+2)%l].y,c[(j+3)%l].x,c[(j+3)%l].y,t)
				j += 2 # we can jump by 2+1 instead of 1
			j += 1
	
	# This is the low level harmonize algorithm as described at
	# gist.github.com/simoncozens/3c5d304ae2c14894393c6284df91be5b
	# by Simon Cozens. This is the variant, where the nodes may move
	# but not the handles.
	# Given two adjacent cubic bezier curves (a,b), (c,d), (e,f), (g,h)
	# and (g,h), (i,j), (k,l), (m,n) that are smooth at (g,h)
	# (i.e. (g,h) is approximately on the line (e,f)--(i,j) )
	# we calculate the corner point (u,v)
	# which is the intersection of the lines (a,b)--(c,d) and 
	# (i,j)--(k,l). Then determine the ratio p as below. 
	# Finally, set (g,h) such that it is situated at 
	# t = p / (p+1) of the line (e,f)--(i,j).
	# This method does not check if the necessary conditions are 
	# actually met (such as smoothness).
	@staticmethod
	def harmonize_cubic(c,d,e,f,g,h,i,j,k,l):
		u,v = Curvatura.corner_point(c,d,e,f,i,j,k,l)
		if not u is None and not v is None \
		and not (u,v) == (e,f) and not (i,j) == (k,l):
			p = (((c-e)**2+(d-f)**2)/((u-e)**2+(v-f)**2)\
			*((u-i)**2+(v-j)**2)/((i-k)**2+(j-l)**2) )**.25
			return e+p/(p+1)*(i-e),f+p/(p+1)*(j-f)
		else:
			return g,h
				
	# Harmonizes the nodes of a fontforge contour c.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	# The boolean is_harmonize_variant is true iff we do not move the
	# node but the handles instead (in case of cubic beziers) or
	# put the node in the middle between the handles (in the case of 
	# quadratic beziers).
	@staticmethod
	def harmonize_contour(c,is_glyph_variant,is_harmonize_variant):
		l = len(c)
		for i in range(l): # going through the points c[i]
			if (c[i].selected or is_glyph_variant) \
			and c[i].type in {1,2} and c[i].on_curve:
				if c.is_quadratic:	
					if c.closed and not c[(i+1)%l].on_curve \
					and c[(i+2)%l].on_curve and not c[(i-1)%l].on_curve \
					and c[(i-2)%l].on_curve	\
					or l>= 5 and 2 <= i < l-2 and not c[i+1].on_curve \
					and c[i+2].on_curve and not c[i-1].on_curve \
					and c[i-2].on_curve:
						if is_harmonize_variant: # average of both neighbour handles
							c[i].x, c[i].y = \
							.5*(c[(i-1)%l].x+c[(i+1)%l].x), \
							.5*(c[(i-1)%l].y+c[(i+1)%l].y)
						else: # average of both neighbour handles and node
							c[i].x, c[i].y = \
							1./3*(c[(i-1)%l].x+c[i].x+c[(i+1)%l].x), \
							1./3*(c[(i-1)%l].y+c[i].y+c[(i+1)%l].y)
						i += 2 # makes things a little bit faster
					else:
						i += 1
				else: # c is cubic
					if c.closed and not c[(i+1)%l].on_curve \
					and not c[(i+2)%l].on_curve and c[(i+3)%l].on_curve \
					and not c[(i-1)%l].on_curve and not c[(i-2)%l].on_curve	\
					and c[(i-3)%l].on_curve	\
					or l>= 7 and 3 <= i < l-3 and not c[i+1].on_curve \
					and not c[i+2].on_curve and c[i+3].on_curve \
					and not c[i-1].on_curve and not c[i-2].on_curve	\
					and c[i-3].on_curve:
						if is_harmonize_variant:
							idealx, idealy = Curvatura.harmonize_cubic(c[(i-2)%l].x, 
							c[(i-2)%l].y, c[(i-1)%l].x, c[(i-1)%l].y, c[i].x, c[i].y, 
							c[(i+1)%l].x, c[(i+1)%l].y, c[(i+2)%l].x, c[(i+2)%l].y)
							c[(i-1)%l].x += c[i].x-idealx
							c[(i-1)%l].y += c[i].y-idealy
							c[(i+1)%l].x += c[i].x-idealx
							c[(i+1)%l].y += c[i].y-idealy
						else:
							c[i].x, c[i].y = Curvatura.harmonize_cubic(c[(i-2)%l].x, 
							c[(i-2)%l].y, c[(i-1)%l].x, c[(i-1)%l].y, c[i].x, c[i].y, 
							c[(i+1)%l].x, c[(i+1)%l].y, c[(i+2)%l].x, c[(i+2)%l].y)
						i += 3 # makes things a little bit faster
					else:
						i += 1						

	# Returns the tension ratio f(t,p) as described 
	# at p131 of The METAFONTbook.
	@staticmethod		
	def tension_ratio(t,p):
		return (2+2**.5*(math.sin(t)-.0625*math.sin(p)) \
		*(math.sin(p)-.0625*math.sin(t))*(math.cos(t)-math.cos(p))) \
		/(3*(1+.5*(5**.5-1)*math.cos(t)+.5*(3-5**.5)*math.cos(p)))
	
	# Returns the 4 coordinates of the controls of a cubic bezier path
	# (a,b){k,l} .. tension alpha and beta .. {m,n}(g,h)
	# as described at p131 of The METAFONTbook.
	@staticmethod
	def tension(a,b,i,k,alpha,beta,m,n,g,h):
		z0 = complex(a,b)
		w0 = complex(i,k)
		z1 = complex(g,h)
		w1 = complex(m,n)
		t = cmath.phase(w0/(z1-z0))
		p = cmath.phase((z1-z0)/w1)
		u = z0+cmath.rect(Curvatura.tension_ratio(t,p)/alpha,t)*(z1-z0)
		v = z1-cmath.rect(Curvatura.tension_ratio(p,t)/beta,-p)*(z1-z0)
		return u.real,u.imag,v.real,v.imag
			
	# Sets the tension of a fontforge contour c to 1 by adjusting the
	# controls as described at p131 of The METAFONTbook.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def tension_contour(c,tension,is_glyph_variant):
		l = len(c)
		j = 0 # index that will run from 0 to l-1 (may contain jumps)
		while j < l: # going through the points c[j]
			# if a point is selected search for the next on_curve point
			# this must be the overovernext point
			if (c[j].on_curve and not c[(j+1)%l].on_curve \
			and not c[(j+2)%l].on_curve and c[(j+3)%l].on_curve) \
			and (c[j].selected and c[(j+3)%l].selected \
			or c[(j+2)%l].selected or c[(j+1)%l].selected \
			or is_glyph_variant) and (j+3)%l != j:
				i,k,m,n = Curvatura.directions_at_nodes(c[j].x,c[j].y,
				c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y,
				c[(j+3)%l].x,c[(j+3)%l].y)
				c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y = \
				Curvatura.tension(c[j].x,c[j].y,i,k,tension,tension,m,n, 
				c[(j+3)%l].x,c[(j+3)%l].y)
				j += 2 # we can jump by 2+1 instead of 1
			j += 1
	
	# This is the high level method for using the methods described before.
	# The string action is either "harmonize", "harmonize_variant",
	# "tunnify", "tunnifix", "inflection" or "tension".
	@staticmethod
	def modify_contours(action,glyph):
		glyph.preserveLayerAsUndo()
		layer = glyph.layers[glyph.activeLayer]
		# first, we check, if anything is selected at all
		# because nothing selected means that the whole glyph
		# should be harmonized (at least the author thinks so)
		is_glyph_variant = True # temporary
		for i in range(len(layer)): # going through the contours layer[i]
			for j in range(len(layer[i])):
				if layer[i][j].selected:
					is_glyph_variant = False
					break
		if action == "tension":
			tensionstring = fontforge.askString("Tension","Choose a number greater or equal 0.75.","1")
			try:
				float(tensionstring)
				tension = float(tensionstring)
				if tension < .75:
					tension = 1
					print("Invalid number, I will set tension 1.")
			except ValueError:
				tension = 1
				print("Invalid number, I will set the tension 1.")
		if action == "tunnifix":
			tstring = fontforge.askString("Fixed Tunni ratio","Choose a number (you may prefer a number between 0 and 1).","0.55")
			try:
				float(tstring)
				t = float(tstring)
			except ValueError:
				t = .55 # this is the approximated ratio for the superness 1/sqrt(2) i.e. circle
				# the exact calculation would be (8/sqrt(2)-4)/3
				print("Invalid number, I will set the ratio 0.55.")
		for i in range(len(layer)): # going through the contours layer[i]
			if action == "harmonize":
				Curvatura.harmonize_contour(layer[i],is_glyph_variant,False)
			elif action == "harmonize_variant":
				Curvatura.harmonize_contour(layer[i],is_glyph_variant,True)
			elif action == "tunnify" and not layer[i].is_quadratic:
				Curvatura.tunnify_contour(layer[i],is_glyph_variant)
			elif action == "tunnifix" and not layer[i].is_quadratic:
				Curvatura.tunnifix_contour(layer[i],t,is_glyph_variant)
			elif action == "inflection" and not layer[i].is_quadratic:
				Curvatura.inflection_contour(layer[i],is_glyph_variant)
			elif action == "tension" and not layer[i].is_quadratic:
				Curvatura.tension_contour(layer[i],tension,is_glyph_variant)
		glyph.layers[glyph.activeLayer] = layer
		
	# This is the high level method for using the methods described before.
	# The string action is either "harmonize", "harmonize_variant",
	# "tunnify", "tunnifix", "inflection" or "tension".
	@staticmethod
	def modify_glyphs(action,font):
		if action == "tension":
			tensionstring = fontforge.askString("Tension","Choose a number greater or equal 0.75.","1")
			try:
				float(tensionstring)
				tension = float(tensionstring)
				if tension < 0.75:
					tension = 1
					print("Invalid number, I will take tension 1.")
			except ValueError:
				tension = 1
				print("Invalid number, I will take tension 1.")
		if action == "tunnifix":
			tstring = fontforge.askString("Fixed Tunni ratio","Choose a number (you may prefer a number between 0 and 1).","0.55")
			try:
				float(tstring)
				t = float(tstring)
			except ValueError:
				t = .55 # this is the approximated ratio for the superness 1/sqrt(2) i.e. circle
				# the exact calculation would be (8/sqrt(2)-4)/3
				print("Invalid number, I will set the ratio 0.55.")
		for glyph in font.selection.byGlyphs:
			glyph.preserveLayerAsUndo()
			layer = glyph.layers[glyph.activeLayer]
			for i in range(len(layer)):
				if action == "harmonize":
					Curvatura.harmonize_contour(layer[i],True,False)
				elif action == "harmonize_variant":
					Curvatura.harmonize_contour(layer[i],True,True)
				elif action == "tunnify" and not layer[i].is_quadratic:
					Curvatura.tunnify_contour(layer[i],True)
				elif action == "tunnifix" and not layer[i].is_quadratic:
					Curvatura.tunnifix_contour(layer[i],t,True)
				elif action == "inflection" and not layer[i].is_quadratic:
					Curvatura.inflection_contour(layer[i],True)
				elif action == "tension" and not layer[i].is_quadratic:
					Curvatura.tension_contour(layer[i],tension,True)
			glyph.layers[glyph.activeLayer] = layer
			
	# Returns false iff no glyph is selected 
	# (needed for enabling in tools menu).
	@staticmethod
	def are_glyphs_selected(junk,font):
		font = fontforge.activeFont()
		for glyph in font.selection.byGlyphs:
			return True
		return False

if __name__ == '__main__':
	if fontforge.hasUserInterface():
		# Register the tools in the tools menu of FontForge:
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"harmonize","Font",
		None,"Curvatura","Harmonize");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"harmonize_variant","Font",
		None,"Curvatura","Harmonize (variant)");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"tunnify","Font",
		None,"Curvatura","Tunnify (balance)");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"tunnifix","Font",
		None,"Curvatura","Set Tunni ratio");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"tension","Font",
		None,"Curvatura","Set tension");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"inflection","Font",
		None,"Curvatura","Add points of inflection");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"harmonize","Glyph",None,"Curvatura","Harmonize");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"harmonize_variant","Glyph",None,"Curvatura","Harmonize (variant)");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"tunnify","Glyph",None,"Curvatura","Tunnify (balance)");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"tunnifix","Glyph",None,"Curvatura","Set Tunni ratio");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"tension","Glyph",None,"Curvatura","Set tension");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"inflection","Glyph",None,"Curvatura","Add points of inflection");
	else:
		import sys
		if len(sys.argv) < 3:
			print("Exactly 2 arguments are needed: input file name"\
			+" and output file name.")
		else:
			if len(sys.argv) > 3:
				print("Exactly 2 arguments are needed: input file name"\
				+" and output file name. I will ignore additional arguments.")
			font = fontforge.open(sys.argv[1])
			for glyph_name in font:
				layer = font[glyph_name].layers[font[glyph_name].activeLayer]
				for j in range(len(layer)):
					Curvatura.harmonize_contour(layer[j],True,False)
			if sys.argv[2][-4:] == ".sfd":
				font.save(sys.argv[2])
			else:
				font.generate(sys.argv[2])
		
