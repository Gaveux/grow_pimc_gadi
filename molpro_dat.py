#!/usr/bin/python2
#=============================================
# molpro data module for Grow2.0 package
#=============================================

#========================
# molpro headers
#========================
# The system specific information, such as basis set and spin 
# multiplicity are read in from the input files, and combined 
# with the magic incantations below to form headers which
# get the coordinates of the particular geometry appended to them
# to form the molecule.inp file which is the input to molpro

#====================================
# adding/modifying ab initio methods
#====================================
# To change an existing method just edit the strings below
# To add a new method, emulate the existing code

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
scf.append('''hf''')

#================================================================
# make a dictionary of methods and availabilities of derivatives
#================================================================
# still need to determine the default behaviour (restricted or unrestricted)
# you really shouldn't be using DFT with molpro, use gaussian for dft
available={}
available['analytic frequencies'] = ['rhf','mcscf']
available['analytic gradients'] = ['hf','rhf','rohf']
available['energies only'] = ['romp2','rmp4','mp4','ccsd','rccsd','ccsd(t)','rccsd(t)','mp2-en']

#================================================================
# make a dictionary of molpro correlated methods and command strings
#================================================================
methods={}
# correlated methods with analytic frequencies
# numerical frequencies...
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
methods['ccsd(t)'] = '''rhf,rccsd(t)'''
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


