#!/usr/bin/env python

# Curvatura version 20200612

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

# Copyright 2019-2020 by Linus Romer

import fontforge,math

class Curvatura:
		
	# Returns the signed distance of the point p from the line
	# starting in q and going to r. The value is positive, iff
	# p is right from the line.
	@staticmethod
	def side(px,py,qx,qy,rx,ry):
		a, b = rx-qx, ry-qy
		return ((py-qy)*a-(px-qx)*b)/(a**2+b**2)**.5

	# Returns for a cubic bezier path (a,b), (c,d), (e,f), (g,h)
	# the direction at (a,b). Other than the derivative, the direction
	# has never length 0 as long as (a,b) != (g,h)
	@staticmethod
	def direction_at_start(a,b,c,d,e,f,g,h):
		if (c,d) == (a,b) and (e,f) == (g,h):
			return g-a,h-b
		elif (c,d) == (a,b):
			return e-a,f-b
		else: # generic case
			return c-a,d-b
			
	# Returns for a cubic bezier path (a,b), (c,d), (e,f), (g,h)
	# the curvature at (a,b). 
	@staticmethod
	def curvature_at_start(a,b,c,d,e,f,g,h):
		if b == d and a == c:
			return 0
		return 2./3.*(c*f-a*f-d*e+b*e+a*d-b*c)/((b-d)**2+(a-c)**2)**1.5
	
	# Returns for a cubic bezier path from (0,0) to (1,0) with
	# enclosing angles alpha and beta with the x-axis and 
	# handle lengths a and b
	# the maximal absolute curvature (numerical approximation). 	
	@staticmethod
	def max_curvature(alpha,beta,a,b):
		maximum = 0
		sa = math.sin(alpha)
		sb = math.sin(beta)
		ca = math.cos(alpha)
		cb = math.cos(beta)
		for i in range(0,51):
			t = i/50.
			fxx = 3*b*cb*t**2+3*a*ca*t**2-2*t**2-2*b*cb*t-4*a*ca*t+2*t+a*ca
			fyy = -3*b*sb*t**2+3*a*sa*t**2+2*b*sb*t-4*a*sa*t+a*sa
			fxxx = 3*b*cb*t+3*a*ca*t-2*t-b*cb-2*a*ca+1
			fyyy = -3*b*sb*t+3*a*sa*t+b*sb-2*a*sa
			if not (fxx == 0 and fyy == 0):
				curv = 2*(fxx*fyyy-fxxx*fyy)/(fxx**2+fyy**2)**1.5
				if abs(curv) > maximum:
					maximum = abs(curv)
		return maximum
	
	# Returns the coefficients of the polynomial with the 
	# coefficients coeffs. (The polynomial a*x^2+b*x+c is represented by 
	# the coefficients [a,b,c].)
	@staticmethod
	def derive(coeffs):
		n = len(coeffs)
		derivative = []
		for i in range(0,n-1):
			derivative.append(coeffs[i]*(n-i-1))
		return derivative

	# Divides the polynomial with the coefficients by (x-r) where r is a
	# root of the polynomial (no remainder, Horner)
	@staticmethod
	def polynomial_division(coeffs,r):
		result = [coeffs[0]]
		for i in range(1,len(coeffs)-1): # -1 because of no remainder
			result.append(coeffs[i]+result[-1]*r)
		return result

	# Evaluates a polynomial with coefficients coeffs in x with (Horner)
	@staticmethod
	def evaluate(coeffs,x):
		result = coeffs[0]
		for i in range(1,len(coeffs)):
			result = result*x+coeffs[i]
		return result

	# Newton's algorithm for determing a root of a polynomial with 
	# coefficients coeffs (starting value 0)
	@staticmethod
	def newton_root(coeffs):
		derivative = Curvatura.derive(coeffs)
		x = 0
		for i in range(100):
			if Curvatura.evaluate(derivative,x) == 0:
				x += 1e-9
			d = Curvatura.evaluate(coeffs,x)/Curvatura.evaluate(derivative,x)
			x -= d
			if abs(d) < 1e-9:
				return x
		return None # algorithm did not converge

	# Same as newton_root() but returns ALL real roots
	def newton_roots(coeffs):
		f = coeffs
		while f[0] == 0:
			f.remove(0)
		roots = []
		while len(f) > 1:
			r = Curvatura.newton_root(f)
			if r is None:
				break
			roots.append(r)
			f = Curvatura.polynomial_division(f,r)
		return roots
	
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

	# Returns True iff a cubic bezier segment which lives in 
	# a contour c from c[i] to c[i+3] is selected.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def segment_selected_cubic(c,i,is_glyph_variant):
		l = len(c)
		return not c.is_quadratic \
		and ((c[i].on_curve and not c[(i+1)%l].on_curve \
		and not c[(i+2)%l].on_curve and c[(i+3)%l].on_curve) \
		and (c[i].selected and c[(i+3)%l].selected \
		or c[(i+2)%l].selected or c[(i+1)%l].selected \
		or is_glyph_variant) and (i+3)%l != i)
		
	# Returns True iff at least two smooth adjacent cubic bezier segments
	# which live in a contour c from c[i-3] to c[i+3] are selected.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def segments_selected_cubic(c,i,is_glyph_variant):
		l = len(c)
		return not c.is_quadratic and c[i].type in {1,2} \
		and c[i].on_curve and (c[i].selected or is_glyph_variant) \
		and (c.closed and not c[(i+1)%l].on_curve \
		and not c[(i+2)%l].on_curve and c[(i+3)%l].on_curve \
		and not c[(i-1)%l].on_curve and not c[(i-2)%l].on_curve	\
		and c[(i-3)%l].on_curve	\
		or l>= 7 and 3 <= i < l-3 and not c[i+1].on_curve \
		and not c[i+2].on_curve and c[i+3].on_curve \
		and not c[i-1].on_curve and not c[i-2].on_curve	\
		and c[i-3].on_curve)
		
	# Returns True iff at least two adjacent quadratic bezier segments
	# which live in a contour c from c[i-2] to c[i+2] are selected.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def segments_selected_quadratic(c,i,is_glyph_variant):
		l = len(c)
		return c.is_quadratic and c[i].type in {1,2} \
		and c[i].on_curve and (c[i].selected or is_glyph_variant) \
		and (c.closed and not c[(i+1)%l].on_curve \
		and c[(i+2)%l].on_curve and not c[(i-1)%l].on_curve \
		and c[(i-2)%l].on_curve	\
		or l>= 5 and 2 <= i < l-2 and not c[i+1].on_curve \
		and c[i+2].on_curve and not c[i-1].on_curve \
		and c[i-2].on_curve)
		
	# Returns True iff the curvature sign of two adjacent cubic 
	# bezier segments (a,b), (c,d), (e,f), (g,h)
	# and (g,h) (i,j) (k,l) (m,n) is different at (g,h)
	@staticmethod
	def is_inflection(a,b,c,d,e,f,g,h,i,j,k,l,m,n):
		return ((i-g)*(h-2*j+l)-(j-h)*(g-2*i+k)) \
		* ((e-g)*(h-2*f+d)-(f-h)*(g-2*e)+c) > 0 
		# yes >0 and not <0 because direction is reversed
	
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
			if Curvatura.segment_selected_cubic(c,j,is_glyph_variant):
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
			if Curvatura.segment_selected_cubic(c,j,is_glyph_variant):
				c[(j+1)%l].x,c[(j+1)%l].y,c[(j+2)%l].x,c[(j+2)%l].y = \
				Curvatura.tunnify(c[j].x,c[j].y,c[(j+1)%l].x,c[(j+1)%l].y, 
				c[(j+2)%l].x,c[(j+2)%l].y,c[(j+3)%l].x,c[(j+3)%l].y)
				j += 2 # we can jump by 2+1 instead of 1
			j += 1
			
	# Given two adjacent cubic bezier curves (a,b), (c,d), (e,f), (g,h)
	# and (g,h), (i,j), (k,l), (m,n) that are smooth at (g,h)
	# this method calculates a new point (g,h) such that
	# the curves are G2-continuous in (g,h).
	# This method does not check if the necessary conditions are 
	# actually met (such as smoothness).
	@staticmethod
	def harmonize_cubic(a,b,c,d,e,f,g,h,i,j,k,l,m,n):
		if e==i and f==j:
			return g, h # no changes
		d2 = abs(Curvatura.side(c,d,e,f,i,j))
		l2 = abs(Curvatura.side(k,l,e,f,i,j))
		if d2 == l2: # then (g,h) is in mid between handles
			return .5*(e+i), .5*(f+j) 
		t = (d2-(d2*l2)**.5)/(d2-l2)
		return (1-t)*e+t*i, (1-t)*f+t*j
			
	# Given two adjacent quadratic bezier curves (a,b), (c,d), (e,f), 
	# and (e,f), (g,h), (i,j) that are smooth at (e,f)
	# this method calculates a new point (e,f) such that
	# the curves are G2-continuous in (e,f).
	# This algorithm works actually for two segments only, but the 
	# iteration seems to be stable for more segments.
	# This method does not check if the necessary conditions are 
	# actually met (such as smoothness).
	@staticmethod
	def harmonize_quadratic(a,b,c,d,e,f,g,h,i,j):
		if c==g and d==h:
			return e, f # no changes
		b2 = abs(Curvatura.side(a,b,c,d,g,h))
		j2 = abs(Curvatura.side(i,j,c,d,g,h))
		if b2 == j2: # then (e,f) is in mid between handles
			return .5*(c+g), .5*(d+h) 
		t = (b2-(b2*j2)**.5)/(b2-j2)
		return (1-t)*c+t*g, (1-t)*d+t*h
				
	# Harmonizes the nodes of a fontforge contour c.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def harmonize_contour(c,is_glyph_variant):
		l = len(c)
		if c.is_quadratic:
			# iterate 5 times
			for fivetimes in range(5):
				for i in range(l): # going through the points c[i]
					if Curvatura.segments_selected_quadratic(c,i,is_glyph_variant):
						c[i].x, c[i].y = Curvatura.harmonize_quadratic(
						c[(i-2)%l].x, c[(i-2)%l].y, c[(i-1)%l].x, c[(i-1)%l].y, 
						c[i].x, c[i].y, c[(i+1)%l].x, c[(i+1)%l].y, 
						c[(i+2)%l].x, c[(i+2)%l].y)
						i += 2 # makes things a little bit faster
					else:
						i += 1	
		else:
			for i in range(l): # going through the points c[i]
				if Curvatura.segments_selected_cubic(c,i,is_glyph_variant):
					c[i].x, c[i].y = Curvatura.harmonize_cubic(c[(i-3)%l].x,
					c[(i-3)%l].y, c[(i-2)%l].x, c[(i-2)%l].y, c[(i-1)%l].x, 
					c[(i-1)%l].y, c[i].x, c[i].y, c[(i+1)%l].x, c[(i+1)%l].y, 
					c[(i+2)%l].x, c[(i+2)%l].y, c[(i+3)%l].x, c[(i+3)%l].y)
					i += 3 # makes things a little bit faster
				else:
					i += 1						
	
	# Sets the lengths a and b of the handles of a cubic bezier path 
	# from (0,0) to (1,0) enclosing angles alpha and beta with the x-axis
	# such that the curvature at (0,0) becomes ka and the curvature at
	# (1,0) becomes kb.
	@staticmethod
	def scale_handles(alpha,beta,ka,kb):
		solutions = []
		sa = math.sin(alpha)
		if alpha + beta == 0: # if ka, kb there is no solution (take the best available)
			solutions.append(
			[math.cos(alpha) if ka == 0 else (-2*sa/(3*ka))**.5 ,
			math.cos(beta) if kb == 0 else (2*sa/(3*kb))**.5])
		else:
			sb = math.sin(beta)
			sba = math.sin(alpha+beta)
			b_roots = Curvatura.newton_roots([27*ka*kb**2,0,36*ka*sb*kb,
			-8*sba**3,8*sa*sba**2+12*ka*sb**2])
			for i in b_roots:
				if i > 0:
					a = (sb+1.5*kb*i**2)/sba
					if a > 0:
						solutions.append([a,i])
		if len(solutions) == 0:
			return None, None
		elif len(solutions) == 1:
			return solutions[0][0], solutions[0][1]
		else: # we only take the solution with the smallest max. abs. curvature
			a, b = solutions[0][0], solutions[0][1]
			maxcurv = Curvatura.max_curvature(alpha,beta,a,b)
			for i in range(1,len(solutions)):
				c = Curvatura.max_curvature(alpha,beta,
				solutions[i][0],solutions[i][1])
				if c < maxcurv:
					a, b = solutions[i][0], solutions[i][1]
			return a, b
			
	# Given a cubic bezier path (a,b), (c,d), (e,f), (g,h)
	# and the curvatures ka and kg 
	# we scale the handles (c,d) and (e,f) such that 
	# the at curvatures ka and kg are reached at (a,b) and (g,h) resp.
	@staticmethod
	def adjust_handles(a,b,c,d,e,f,g,h,ka,kg):
		l = ((g-a)**2+(h-b)**2)**.5 # this length will be scaled to 1 for curvature computations
		da,db = Curvatura.direction_at_start(a,b,c,d,e,f,g,h)
		dab = (da**2+db**2)**.5 # this can cause dab = 0 (rounding...)
		if dab == 0: 
			dab = ((g-a)**2+(h-b)**2)**.5
		da,db = da/dab,db/dab # norm length to 1
		alpha = math.asin(((g-a)*db-(h-b)*da)/l) # crossp for direction
		dg,dh = Curvatura.direction_at_start(g,h,e,f,c,d,a,b)
		dgh = (dg**2+dh**2)**.5 # this can cause dgh = 0 (rounding...)
		if dgh == 0: 
			dgh = ((g-a)**2+(h-b)**2)**.5
		dg,dh = dg/dgh,dh/dgh # norm length to 1
		beta = math.asin(((g-a)*dh-(h-b)*dg)/l) # crossp for direction
		t,s = Curvatura.scale_handles(alpha,beta,ka*l,kg*l) 
		if t is None or s is None:
			return c,d,e,f # no changes
		else:
			return a+t*da*l,b+t*db*l,g+s*dg*l,h+s*dh*l # scale back
		
	# This harmonizes the selected paths by moving the handles in
	# order to reach the average curvature at their nodes.
	# The boolean is_glyph_variant is true iff the point selection
	# in the UI does not matter.
	@staticmethod
	def harmonizehandles_contour(c,is_glyph_variant):
		l = len(c)
		# collecting the average curvatures at the moment:
		curvatures = {}
		for fivetimes in range(5): # iterate 5 times to average everything out
			for i in range(l): # going through the points c[i]
				if Curvatura.segments_selected_cubic(c,i,is_glyph_variant):
					postcurvature = Curvatura.curvature_at_start(
					c[i].x, c[i].y,	c[(i+1)%l].x, c[(i+1)%l].y, 
					c[(i+2)%l].x, c[(i+2)%l].y, c[(i+3)%l].x, c[(i+3)%l].y)
					precurvature = -Curvatura.curvature_at_start(
					c[i].x, c[i].y, c[(i-1)%l].x, c[(i-1)%l].y,
					c[(i-2)%l].x, c[(i-2)%l].y, c[(i-3)%l].x, c[(i-3)%l].y)
					if postcurvature*precurvature < 0: # inflection node
						postnew = 0
						prenew = 0
					else:
						postnew = math.copysign(.5*(abs(postcurvature) \
						+ abs(precurvature)),postcurvature)
						prenew = math.copysign(.5*(abs(postcurvature) \
						+ abs(precurvature)),precurvature)
					curvatures[i] = [precurvature,postcurvature,prenew,postnew]
			# adjust the handles to fit the average curvatures:
			# (curvatures at selection ends have not been calculated yet)
			for i in curvatures:
				# looking on the previous segment
				if (i-3)%l in curvatures:
					ka = curvatures[(i-3)%l][3]
				else: 
					ka = Curvatura.curvature_at_start(
					c[(i-3)%l].x, c[(i-3)%l].y, c[(i-2)%l].x, c[(i-2)%l].y,
					c[(i-1)%l].x, c[(i-1)%l].y, c[i].x, c[i].y)
				c[(i-2)%l].x, c[(i-2)%l].y, c[(i-1)%l].x, c[(i-1)%l].y \
				= Curvatura.adjust_handles(c[(i-3)%l].x, c[(i-3)%l].y, 
				c[(i-2)%l].x, c[(i-2)%l].y,	c[(i-1)%l].x, c[(i-1)%l].y, 
				c[i].x, c[i].y, ka, curvatures[i][2])
				if not (i+3)%l in curvatures: # if we are at a selection end
					kg = -Curvatura.curvature_at_start(
					c[(i+3)%l].x, c[(i+3)%l].y, c[(i+2)%l].x, c[(i+2)%l].y,
					c[(i+1)%l].x, c[(i+1)%l].y, c[i].x, c[i].y)
					c[(i+1)%l].x, c[(i+1)%l].y, c[(i+2)%l].x, c[(i+2)%l].y \
					= Curvatura.adjust_handles(c[i].x, c[i].y,
					c[(i+1)%l].x, c[(i+1)%l].y, c[(i+2)%l].x, c[(i+2)%l].y, 
					c[(i+3)%l].x, c[(i+3)%l].y, curvatures[i][3], kg)
				
	# This is the high level method for using the methods described before.
	# The string action is either "harmonize", "harmonizehandles", 
	# "tunnify" or "inflection".
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
		for i in range(len(layer)): # going through the contours layer[i]
			if action == "harmonize":
				Curvatura.harmonize_contour(layer[i],is_glyph_variant)
			elif action == "harmonizehandles":
				Curvatura.harmonizehandles_contour(layer[i],is_glyph_variant)
			elif action == "tunnify" and not layer[i].is_quadratic:
				Curvatura.tunnify_contour(layer[i],is_glyph_variant)
			elif action == "inflection" and not layer[i].is_quadratic:
				Curvatura.inflection_contour(layer[i],is_glyph_variant)	
		glyph.layers[glyph.activeLayer] = layer
		
	# This is the high level method for using the methods described before.
	# The string action is either "harmonize", "harmonizehandles", 
	# "tunnify" or "inflection".
	@staticmethod
	def modify_glyphs(action,font):
		for glyph in font.selection.byGlyphs:
			glyph.preserveLayerAsUndo()
			layer = glyph.layers[glyph.activeLayer]
			for i in range(len(layer)):
				if action == "harmonize":
					Curvatura.harmonize_contour(layer[i],True)
				elif action == "harmonizehandles":
					Curvatura.harmonizehandles_contour(layer[i],True)
				elif action == "tunnify" and not layer[i].is_quadratic:
					Curvatura.tunnify_contour(layer[i],True)
				elif action == "inflection" and not layer[i].is_quadratic:
					Curvatura.inflection_contour(layer[i],True)
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
		Curvatura.are_glyphs_selected,"harmonizehandles","Font",
		None,"Curvatura","Harmonize handles");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"tunnify","Font",
		None,"Curvatura","Tunnify (balance)");
		fontforge.registerMenuItem(Curvatura.modify_glyphs,
		Curvatura.are_glyphs_selected,"inflection","Font",
		None,"Curvatura","Add points of inflection");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"harmonize","Glyph",None,"Curvatura","Harmonize");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"harmonizehandles","Glyph",None,"Curvatura","Harmonize handles");
		fontforge.registerMenuItem(Curvatura.modify_contours,None,
		"tunnify","Glyph",None,"Curvatura","Tunnify (balance)");
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
		
