import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.run3scouting_cff import *
from FWCore.ParameterSet.VarParsing import VarParsing
from splitter import get_file_and_parents

params = VarParsing('analysis')

# arguments for text file of files and integer number of which file to run on
params.register('fileNum',
                0,
                VarParsing.multiplicity.singleton,
                VarParsing.varType.int,
                "file number in list of files")

params.register('inputTextFile',
    '',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Input text file of files")

process = cms.Process("LL")
params.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5000

# call splitter function to get file name and its corresponding parent files
file_name, parent_files = get_file_and_parents(params.inputTextFile, params.fileNum)


process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10))
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(file_name),
        secondaryFileNames = cms.untracked.vstring(*parent_files)
)
process.TFileService = cms.Service("TFileService",
fileName = cms.string('/cms/nla49/Scouting/CMSSW_13_1_0_pre2/src/Run3ScoutingJetTagging/Analysis/test/QCD_ntuples/ntuple_' + str(params.fileNum) + '.root') # directory to store output
)


# Create SoftDrop pruned GEN jets
process.load('PhysicsTools.NanoAOD.jetMC_cff')
process.genJetSequence = cms.Sequence(
   process.patJetPartonsNano+
   process.genJetFlavourAssociation
)

# Create ParticleNet ntuple
process.tree = cms.EDAnalyzer("AK4JetNtupleProducer",
      isQCD = cms.untracked.bool(True), # change
      gen_jets = cms.InputTag( "genJetFlavourAssociation" ),
      pf_candidates = cms.InputTag( "hltScoutingPFPacker" ),
)

process.p = cms.Path(process.genJetSequence*process.tree)
