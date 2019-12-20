#!/usr/bin/python2
#=============================================
# Gaussian03 data module for Grow2.2 package
# modified by Meredith Jordan March 2006
#=============================================

#========================
# Gaussian03 headers
#========================
# The system specific information, such as basis set and spin 
# multiplicity are read in from the input files, and combined 
# with the magic incantations below to form headers which
# get the coordinates of the particular geometry appended to them
# to form the molecule.com file which is the input to g03

#====================================
# adding/modifying ab initio methods
#====================================
# To change an existing method just edit the strings below
# To add a new method, eg DFT, emulate the existing code

#===========
# SCF jobs
#===========
# At the time of writing these are our favourite options for getting
# SCF calculations at arbitrary molecular geometries to converge.
# These strings are inserted into the appropriate headers and
# the jobs attempted in sequence... if all four fail then we
# discard that particular geometry and move on

# scf is a list of strings
scf=[]
# zeroth attempt
scf.append('''
#p uhf 
scf=(tight,conver=10)
iop(2/12=1)
gen
''')
# first scf attempt 
scf.append('''
#p uhf 
scf=(tight,conver=10)
stable=opt
iop(2/12=1)
gen
''')
# second scf attempt
scf.append('''
#p uhf 
scf=(qc,conver=10)
stable=opt
iop(2/12=1)
gen
''') 
# third scf attempt  
scf.append('''
#p uhf 
scf=(tight,conver=10)
guess=mix
stable=opt
iop(2/12=1)
gen
''')
# fourth scf attempt
scf.append('''
#p uhf 
scf=(qc,conver=10)
guess=read
stable=opt
iop(2/12=1)
gen
''')

#================================================================
# make a dictionary of methods and availabilities of derivatives
#================================================================
# note that the default in g03 is for unrestricted methods
available={}
available['analytic frequencies'] = ['hf','rhf','rohf','b3lyp','m052x','pw91','mp2','rmp2']
available['analytic gradients'] = ['mp4(sdq)', 'ccd','rccd','mp2-force']
available['energies only'] = ['romp2','rmp4','mp4','ccsd','rccsd','ccsd(t)','rccsd(t)','mp2-en']

#================================================================
# make a dictionary of g03 correlated methods and command strings
#================================================================
methods={}
# hf
methods['hf'] = '''
#p hf
scf=(tight,conver=10)
guess=read
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen
'''
# correlated methods with analytic frequencies
# b3lyp
methods['b3lyp'] = '''
#p b3lyp
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
int=ultrafine
formcheck=all
punch=(coord,derivatives)
gen
'''
# M05-2X
methods['m052x'] = '''
#p m052x
scf=(tight,conver=10)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
formcheck=all
punch=(coord,derivatives)
gen
'''
# pw91
methods['pw91'] = '''
#p pw91pw91
scf=(tight,conver=10)
guess=read
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen
'''
# mp2
methods['mp2'] = '''
#p mp2
scf=(tight,conver=10)
guess=read
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen 
'''
# correlated methods with analytic gradients
# mp2 analytic gradients - debug only
methods['mp2-force'] = '''
#p mp2
scf=(tight,conver=10)
force
guess=read
iop(2/12=1)
iop(7/32=2)
formcheck=all
gen
'''
# mp4(sdq)
methods['mp4(sdq)'] = '''
#p mp4(sdq)
scf=(tight,conver=10)
force
guess=read
iop(2/12=1)
iop(7/32=2)
formcheck=all
gen
'''
# ccd
methods['ccd'] = '''
#p ccd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
force
guess=read
iop(2/12=1)
iop(7/32=2)
formcheck=all
gen
'''
# rccd
methods['rccd'] = '''
#p rccd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
force
guess=read
iop(2/12=1)
iop(7/32=2)
formcheck=all
gen
'''
# correlated methods without any analytic derivatives
# mp2 energies - debug only
methods['mp2-en'] = '''
#p mp2
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# romp2
methods['romp2'] = '''
#p romp2
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# mp4
methods['mp4'] = '''
#p mp4
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# ccsd
methods['ccsd'] = '''
#p ccsd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# rccsd
methods['rccsd'] = '''
#p rccsd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# ccsd(t)
methods['ccsd(t)'] = '''
#p ccsd=(t,conver=10,maxcyc=100)
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# rccsd(t)
methods['rccsd(t)'] = '''
#p rccsd=(t,conver=10,maxcyc=100)
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# numerical frequencies...
# Incredibly, Gaussian does its displacements in cartesian
# coordinates, thereby using 6 extra force calculations if
# differentiating gradients and a larger number if using
# energies only.  We provide these for convenience only...
# romp2
methods['romp2_numfreq'] = '''
#p romp2
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# mp4
methods['mp4_numfreq'] = '''
#p mp4
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# ccsd
methods['ccsd_numfreq'] = '''
#p ccsd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# rccsd
methods['rccsd_numfreq'] = '''
#p rccsd=(conver=10,maxcyc=100)
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# ccsd(t)
methods['ccsdt_numfreq'] = '''
#p ccsd=(t,conver=10,maxcyc=100)
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''
# rccsd(t)
methods['rccsdt_numfreq'] = '''
#p rccsd=(t,conver=10,maxcyc=100)
scf=(tight,conver=10)
freq=noraman
guess=read
iop(2/12=1)
formcheck=all
gen
'''


