import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.run3scouting_cff import *
from FWCore.ParameterSet.VarParsing import VarParsing
import splitter.py as splitter

params = VarParsing('analysis')

params.register('fileNum',
                0,
                VarParsing.multiplicity.singleton,
                VarParsing.varType.int,
                "file number in list of files")

params.register('inputDataset',
    '',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Input dataset")

process = cms.Process("LL")
params.parseArguments()

file_name, parent_files = splitter.get_file_and_parents(params.inputTextFile,params.fileNum)


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
    fileName = cms.string(file_name+".root")
)


# Create SoftDrop pruned GEN jets
process.load('PhysicsTools.NanoAOD.jetMC_cff')
process.genJetSequence = cms.Sequence(
   process.patJetPartonsNano+
   process.genJetFlavourAssociation
)

# Create ParticleNet ntuple
process.tree = cms.EDAnalyzer("AK4JetNtupleProducer",
      isQCD = cms.untracked.bool( '/QCD_' in params.inputDataset ),
      gen_jets = cms.InputTag( "genJetFlavourAssociation" ),
      pf_candidates = cms.InputTag( "hltScoutingPFPacker" ),
)

process.p = cms.Path(process.genJetSequence*process.tree)
