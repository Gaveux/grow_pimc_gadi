#!/usr/bin/python2
#=============================================
# Gaussian03 data module for Grow2.2 package
# modified by Meredith Jordan March 2006
# g03 -> g16 Keiran Rowell August 2017
#=============================================

#========================
# Gaussian16 headers
#========================
# The system specific information, such as basis set and spin 
# multiplicity are read in from the input files, and combined 
# with the magic incantations below to form headers which
# get the coordinates of the particular geometry appended to them
# to form the molecule.com file which is the input to g16
# these haven't need to change since g03

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
# NB scf is assumed to be "uhf"
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
# note that the default in g16 is for unrestricted methods
available={}
available['analytic frequencies'] = ['hf','rhf','rohf','b3lyp','m052x','m052xscf','um052x','um052xscf''pw91','mp2', 'rmp2','ump2','m06','m06scf','um06','um06scf','m062x','m062xscf','um062x','um062xscf']                                                      
available['analytic gradients'] = ['mp4(sdq)', 'ccd','rccd','mp2-force']
available['energies only'] = ['romp2','rmp4','mp4','ccsd','rccsd','ccsd(t)','rccsd(t)','mp2-en']

#================================================================
# make a dictionary of g16 correlated methods and command strings
#================================================================
methods={}
# uhf  NB hf is assumed to be "uhf", rhf must be specified explicitly
methods['hf'] = '''
#p uhf
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen 
'''
# uhf  NB hf is assumed to be "uhf", rhf must be specified explicitly
methods['uhf'] = '''
#p uhf
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen 
'''
# rhf  NB hf is assumed to be "uhf", rhf must be specified explicitly
methods['rhf'] = '''
#p rhf
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen 
'''
# hf - energy only, NB assumed to be "uhf"
methods['hfscf'] = '''
#p uhf
gen  
'''
# single point energies using RMP2 method
methods['sp'] = '''
#p rmp2
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
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
# ub3lyp
methods['ub3lyp'] = '''
#p ub3lyp
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
int=ultrafine
formcheck=all
punch=(coord,derivatives)
gen  
'''
# b3lyp - energy only; assumed to be ub3lyp
methods['b3lypscf'] = '''
#p ub3lyp
gen  
'''
# ub3lyp - energy only; 
methods['ub3lypscf'] = '''
#p ub3lyp
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
# UM05-2X
methods['um052x'] = '''
#p um052x
scf=(tight,conver=10)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
formcheck=all
punch=(coord,derivatives)
gen  
'''
# m052x - energy only
methods['m052xscf'] = '''
#p m052x
gen 
'''
# um052x - energy only
methods['um052xscf'] = '''
#p um052x
gen 
'''
# M06
methods['m06'] = '''
#p m06
scf=(tight,conver=10)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
FChk=all
punch=(coord,derivatives)
gen  
'''
# UM06
methods['um06'] = '''
#p um06
scf=(tight,conver=10,maxcycle=100)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
FChk=all
punch=(coord,derivatives)
gen  
'''
# M06-2X
methods['m062x'] = '''
#p m062x
scf=(tight,conver=10,maxcycle=100)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
FChk=all
punch=(coord,derivatives)
gen 
'''
# UM06-2X
methods['um062x'] = '''
#p um062x
scf=(tight,conver=10,maxcycle=100)
freq=noraman
int=ultrafine
iop(2/12=1)
nosymm
FChk=all
punch=(coord,derivatives)
gen 
'''
# M06 - energy only
methods['m06scf'] = '''
#p m06
gen 
'''
# UM06 - energy only
methods['um06scf'] = '''
#p um06
gen 
'''
# M06-2X - energy only
methods['m062xscf'] = '''
#p m062x
gen 
'''
# UM06-2X - energy only
methods['um062xscf'] = '''
#p um062x
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
# upw91
methods['upw91'] = '''
#p upw91pw91
scf=(tight,conver=10)
guess=read
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen  
'''
# pw91 - energy only
methods['pw91scf'] = '''
#p pw91pw9
gen 
'''
# upw91 - energy only
methods['upw91scf'] = '''
#p upw91pw91
gen 
'''
# mp2 NB assumed to be RMP2 with guess recalculated
methods['mp2'] = '''
#p mp2
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen  
'''
# rmp2 
methods['rmp2'] = '''
#p rmp2
scf=(tight,conver=10)
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen  
'''
# ump2
methods['ump2'] = '''
#p ump2
scf=(tight,conver=10)
guess=read
freq=noraman
iop(2/12=1)
formcheck=all
punch=(coord,derivatives)
gen  
'''
# mp2 - crude energy only
methods['mp2scf'] = '''
#p rmp2
gen  
'''
# ump2 - crude energy only
methods['ump2scf'] = '''
#p ump2
gen  
'''
# correlated methods with analytic gradients
# mp2 analytic gradients - debug only
# assumed to be RMP2 so recalculated guess
methods['mp2-force'] = '''
#p rmp2
scf=(tight,conver=10)
force
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
# ump4(sdq)
methods['mp4(sdq)'] = '''
#p ump4(sdq)
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
# uccd
methods['uccd'] = '''
#p uccd=(conver=10,maxcyc=100)
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
# assumed to be RMP2 so recalculate guess
methods['mp2-en'] = '''
#p rmp2
scf=(tight,conver=10)
iop(2/12=1)
formcheck=all
gen
'''
# romp2
methods['romp2'] = '''
#p romp2
scf=(tight,conver=10)
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
# ump4
methods['ump4'] = '''
#p ump4
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
# uccsd
methods['uccsd'] = '''
#p uccsd=(conver=10,maxcyc=100)
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
#p ccsd=(t,conver=10,maxcyc=200)
scf=(tight,conver=10)
guess=read
iop(2/12=1)
formcheck=all
gen  
'''
# ccsd(t) - crude energy
methods['ccsd(t)scf'] = '''
#p ccsd=(t)
gen  
'''
# uccsd(t) - crude energy
methods['uccsd(t)scf'] = '''
#p uccsd=(t)
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
#guess=read
iop(2/12=1)
formcheck=all
gen
'''
# mp4
methods['mp4_numfreq'] = '''
#p mp4
scf=(tight,conver=10)
freq=noraman
#guess=read
iop(2/12=1)
formcheck=all
gen
'''
# ump4
methods['ump4_numfreq'] = '''
#p ump4
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
# uccsd
methods['uccsd_numfreq'] = '''
#p uccsd=(conver=10,maxcyc=100)
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
# uccsd(t)
methods['uccsdt_numfreq'] = '''
#p uccsd=(t,conver=10,maxcyc=100)
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



