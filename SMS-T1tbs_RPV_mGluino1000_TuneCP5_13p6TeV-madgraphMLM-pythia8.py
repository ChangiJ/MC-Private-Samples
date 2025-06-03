import FWCore.ParameterSet.Config as cms  # Load CMSSW Python configuration tools

from Configuration.Generator.Pythia8CommonSettings_cfi import *  # Load general Pythia8 settings
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *  # Load Run3 CP5 tune

import math  # For mathematical calculations used in matching

mglu = 1000  # Set gluino mass (GeV)

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",  # Load external LHE events via gridpack
    args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/RunIII/13p6TeV/slc7_amd64_gcc10/MadGraph5_aMCatNLO/SUSY_SMS/SMS-GlGl/SMS-GlGl_mGl-1000_slc7_amd64_gcc10_CMSSW_12_4_8_tarball.tar.xz' % mglu),
    nEvents = cms.untracked.uint32(5000),  # Number of events to generate from the gridpack
    numberOfParameters = cms.uint32(1),  # Only one argument (gridpack path)
    outputFile = cms.string('cmsgrid_final.lhe'),  # Output LHE file name
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')  # Standard gridpack execution script
)

# Minimal SLHA table just to assign mass and decay mode of gluino (t b s)
baseSLHATable = """
BLOCK MASS  # Mass Spectrum
   1000021     %MGLU%  # ~g gluino
DECAY   1000021     1.0  # gluino width (arbitrary)
  1.00000000E+00    3       6         5     3     # ~g -> t b s
"""

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
  filterEfficiency = cms.untracked.double(matcheff),  # Matching efficiency
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
