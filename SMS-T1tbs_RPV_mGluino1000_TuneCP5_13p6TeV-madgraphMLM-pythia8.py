import FWCore.ParameterSet.Config as cms  # Load CMSSW Python configuration tools

from Configuration.Generator.Pythia8CommonSettings_cfi import *  # Load general Pythia8 settings
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *  # Load Run3 CP5 tune

import math  # For mathematical calculations used in matching

mglu = 1000  # Set gluino mass (GeV)

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",  # Load external LHE events via gridpack
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/SUSY_SMS/SMS-GlGl/SMS-GlGl_mGl-1000_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz'),
    nEvents = cms.untracked.uint32(5000),  # Number of events to generate from the gridpack
    numberOfParameters = cms.uint32(1),  # Only one argument (gridpack path)
    outputFile = cms.string('cmsgrid_final.lhe'),  # Output LHE file name
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')  # Standard gridpack execution script
)

# Minimal SLHA table just to assign mass and decay mode of gluino (t b s)
baseSLHATable=""" 
BLOCK MASS  # Mass Spectrum
# PDG code           mass       particle
        25     1.00000000E+03
        35     1.00000000E+03
        36     1.00000000E+03
        37     1.00000000E+03
        6      1.72500000E+02
   1000001     100000.0          # ~d_L
   2000001     1.00000000E+05   # ~d_R
   1000002     100000.0          # ~u_L
   2000002     1.00000000E+05   # ~u_R
   1000003     100000.0          # ~s_L
   2000003     1.00000000E+05   # ~s_R
   1000004     100000.0         # ~c_L
   2000004     1.00000000E+05   # ~c_R
   1000005     1.00000000E+05   # ~b_1
   2000005     1.10000000E+05   # ~b_2
   1000006     1.10000000E+05   # ~t_1
   2000006     1.10000000E+05   # ~t_2
   1000011     1.00000000E+04   # ~e_L
   2000011     1.00000000E+04   # ~e_R
   1000012     1.00000000E+04   # ~nu_eL
   1000013     1.00000000E+04   # ~mu_L
   2000013     1.00000000E+04   # ~mu_R
   1000014     1.00000000E+04   # ~nu_muL
   1000015     1.00000000E+04   # ~tau_1
   2000015     1.00000000E+04   # ~tau_2
   1000016     1.00000000E+04   # ~nu_tauL
   1000021     %MGLU%              # ~g
   1000022     1.00000000E+05   # ~chi_10
   1000023     1.00000000E+04   # ~chi_20
   1000025     1.00000000E+04   # ~chi_30
   1000035     1.00000000E+04   # ~chi_40
   1000024     1.00000000E+05   # ~chi_1+
   1000037     1.00000000E+04   # ~chi_2+
# DECAY TABLE
#         PDG            Width
DECAY         6     1.134E+00        # top decays
DECAY   1000006     0.00000000E+00   # stop2 decays
DECAY   2000006     0.00000000E+00   # stop2 decays
DECAY   1000005     0.00000000E+00   # sbottom1 decays
DECAY   2000005     0.00000000E+00   # sbottom2 decays
#         PDG            Width
DECAY   1000011     0.00000000E+00   # selectron_L decays
DECAY   2000011     0.00000000E+00   # selectron_R decays
DECAY   1000013     0.00000000E+00   # smuon_L decays
DECAY   2000013     0.00000000E+00   # smuon_R decays
DECAY   1000015     0.00000000E+00   # stau_1 decays
DECAY   2000015     0.00000000E+00   # stau_2 decays
#         PDG            Width
DECAY   1000012     0.00000000E+00   # snu_elL decays
DECAY   1000014     0.00000000E+00   # snu_muL decays
DECAY   1000016     0.00000000E+00   # snu_tauL decays
DECAY   1000021     1.0000000E+00   # gluino decays
#          BR         NDA      ID1       ID2
     1.00000000E+00    3       6         5     3     # ~g -> t b s
DECAY   1000024     0.0000000E+00   # chargino1 decays
DECAY   1000022     0.00000000E+00   # neutralino1 decays
"""

model = "T1tbs"
# weighted average of matching efficiencies for the full scan
# must equal the number entered in McM generator params
mcm_eff = 0.235


# Parameters that define the grid in the bulk and diagonal
# Fit to gluino cross-section in fb
def xsec(mass):
    return 4.563e+17*math.pow(mass, -4.761*math.exp(5.848e-05*mass))


# Matching parameters depend on gluino mass
def matchParams(mass):
    if   mass < 799: return 118., 0.235
    elif mass < 999: return 128., 0.235
    elif mass < 1199: return 140., 0.235
    elif mass < 1399: return 143., 0.245
    elif mass < 1499: return 147., 0.255
    elif mass < 1799: return 150., 0.267
    elif mass < 2099: return 156., 0.290
    else: return 160., 0.315

qcut, matcheff = matchParams(mglu)  # Extract appropriate matching scale and efficiency
baseSLHA = baseSLHATable.replace('%MGLU%', '%e' % mglu)  # Replace gluino mass in SLHA

generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",  # Run3-compatible Pythia8 hadronizer
  maxEventsToPrint = cms.untracked.int32(1),  # Print 1 event
  pythiaPylistVerbosity = cms.untracked.int32(1),  # Print Pythia event info
  filterEfficiency = cms.untracked.double(1.0),  # Matching efficiency
  pythiaHepMCVerbosity = cms.untracked.bool(False),
  comEnergy = cms.double(13600.),  # Run3 center-of-mass energy: 13.6 TeV
  PythiaParameters = cms.PSet(
    pythia8CommonSettingsBlock,  # Common settings
    pythia8CP5SettingsBlock,  # Run3 CP5 tune
    JetMatchingParameters = cms.vstring(  # MLM jet-parton matching
      'JetMatching:setMad = off',
      'JetMatching:scheme = 1',
      'JetMatching:merge = on',
      'JetMatching:jetAlgorithm = 2',
      'JetMatching:etaJetMax = 5.',
      'JetMatching:coneRadius = 1.',
      'JetMatching:slowJetPower = 1',
      'JetMatching:qCut = %e' % qcut,  # Merging scale
      'JetMatching:nQmatch = 5',  # 5-flavor scheme (matching includes b-quarks)
      'JetMatching:nJetMax = 2',  # Number of partons in ME
      'JetMatching:doShowerKt = off'
    ),
    parameterSets = cms.vstring('pythia8CommonSettings',
                                'pythia8CP5Settings',
                                'JetMatchingParameters')
  ),
  SLHATableForPythia8 = cms.string(baseSLHA)  # Inject SLHA block
)
