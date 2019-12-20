#!/usr/bin/python2
#===========================================
# Aces2 data module for Grow2.0 package
#===========================================

#========================
# Aces2 command strings
#========================
# The system specific information, such as basis set and spin 
# multiplicity are read in from the input files, and combined 
# with the magic incantations below to form command strings which
# are appended to the coordinates of the particular geometry
# to form the ZMAT file which is needed by aces2

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

# There are three different lists of strings, depending on the scf type 
# that the following job requests.

# rscf is the list of strings which control RHF options. Note that there is
# no stability testing for RHF, since it is only applicable to bound-state
# systems which are unlikely to converge to incorrect scf wavefunctions anyway

rscf=[]
# zeroth attempt (straight scf run)
rscf.append('''
*ACES2(CALC=SCF,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
UNITS=BOHR,
''')
# first attempt (includes damping algorithm of Davidson)
rscf.append('''
*ACES2(CALC=SCF,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
DAMP_TYP=DAVIDSON,
DAMP_TOL=5,
UNITS=BOHR,
''')

# uscf is the list of strings which control UHF options. Here we include
# stability testing right from the start, since UHF is most often used with
# reactive or bond-breaking systems.

uscf=[]
# zeroth attempt (just scf stability test + instability following)
uscf.append('''
*ACES2(CALC=SCF,
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
HFSTABILITY=FOLLOW,
UNITS=BOHR,
''')
# first attempt (also includes damping algorithm)
uscf.append('''
*ACES2(CALC=SCF,
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
DAMP_TYP=DAVIDSON,
DAMP_TOL=5,
HFSTABILITY=FOLLOW,
UNITS=BOHR,
''')

# roscf is the list of strings which control ROHF options. Again, stability
# testing is included from the start, as ROHF is mostly used for open-shell
# systems

roscf=[]
#zeroth attempt (just scf stability test + instability following)
roscf.append('''
*ACES2(CALC=SCF,
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
HFSTABILITY=FOLLOW,
UNITS=BOHR,
''')
# first scf attempt (also includes damping and level-shifting techniques)
roscf.append('''
*ACES2(CALC=SCF,
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
DAMP_TYP=DAVIDSON,
DAMP_TOL=5,
LSHF_A1=20,
LSHF_B1=20,
HFSTABILITY=FOLLOW,
UNITS=BOHR,
''')

#================================================================
# make a dictionary of methods and availabilities of derivatives
#================================================================
# note that in aces you can choose your reference wavefunction
scftype={}
scftype['rscf'] = ['rhf','rmp2','rmp4','rqcisd','rqcisd(t)','rccsd','rccsd(t)','eom-ccsd']
scftype['uscf'] = ['uhf','ump2','ump4','uqcisd','uqcisd(t)','uccsd','uccsd(t)']
scftype['roscf'] = ['rohf','romp2','roccsd','roccsd(t)']
scftype['qscf'] = ['qccsd']

#==================================================================
# make a dictionary of aces2 correlated methods and command strings
#==================================================================
methods={}
# truly analytic frequencies
# rhf
methods['rhf'] = '''
*ACES2(CALC=SCF,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# uhf
methods['uhf'] = '''
*ACES2(CALC=SCF,
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# rohf
methods['rohf'] = '''
*ACES2(CALC=SCF,
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# technically, only some of these are analytic frequencies, but it is more efficient
# calculate numerical derivatives using cfour because of its handling of symmetry. 
# So, we will treat all methods as analytic (i.e. the complete 2nd deriv matrix can 
# be obtained directly from the ab initio package)
# rmp2
methods['rmp2'] = '''
*ACES2(CALC=MBPT(2),
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# ump2
methods['ump2'] = '''
*ACES2(CALC=MBPT(2),
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# romp2
methods['romp2'] = '''
*ACES2(CALC=MBPT(2),
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# rmp4
methods['rmp4'] = '''
*ACES2(CALC=MBPT(4),
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# ump4
methods['ump4'] = '''
*ACES2(CALC=MBPT(4),
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# rqcisd
methods['rqcisd'] = '''
*ACES2(CALC=QCISD,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# uqcisd
methods['uqcisd'] = '''
*ACES2(CALC=QCISD,
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# rqcisd(t)
methods['rqcisd(t)'] = '''
*ACES2(CALC=QCISD(T),
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# uqcisd(t)
methods['uqcisd(t)'] = '''
*ACES2(CALC=QCISD(T),
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# rccsd
methods['rccsd'] = '''
*ACES2(CALC=CCSD,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# uccsd
methods['uccsd'] = '''
*ACES2(CALC=CCSD,
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# roccsd
methods['roccsd'] = '''
*ACES2(CALC=CCSD,
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# rccsd(t)
methods['rccsd(t)'] = '''
*ACES2(CALC=CCSD(T),
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# uccsd(t)
methods['uccsd(t)'] = '''
*ACES2(CALC=CCSD(T),
REF=UHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=EXACT,
RESET=ON,
UNITS=BOHR,
'''
# roccsd(t)
methods['roccsd(t)'] = '''
*ACES2(CALC=CCSD(T),
REF=ROHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# eom-ccsd
methods['eom-ccsd'] = '''
*ACES2(CALC=CCSD,
EXCITE=EOMEE,
REF=RHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
# qccsd
methods['qccsd'] = '''
*ACES2(CALC=CCSD,
REF=QRHF,
COORD=CARTESIAN,
SCF_CONV=10,
VIBRATION=FINDIF,
RESET=ON,
UNITS=BOHR,
'''
