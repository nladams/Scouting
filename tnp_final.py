import ROOT
import sys
import numpy as np
from array import array

if len(sys.argv) != 3:
    print("USAGE : % <input txt file > <file number"%(sys.argv[0]))
    sys.exit(1)
    
txtFileName = sys.argv[1]
fileNum = int(sys.argv[2])
    
f = open("output"+str(fileNum)+".root","w")
    
outFileName = "output"+str(fileNum)+".root"

print("Reading from ", txtFileName , "using the", fileNum, "th entry and writing to ", outFileName)

with open(txtFileName,"r") as data_files:
    files = data_files.read().splitlines()
#    print("input file", files[fileNum])

#histograms/counters
mijk90 = ROOT.TH1D("mijk_90","m [GeV]", 100,0,500)
mijk80 = ROOT.TH1D("mijk_80","m [GeV]", 100,0,500)
mijk70 = ROOT.TH1D("mijk_70","m [GeV]", 100,0,500)
nobcut = ROOT.TH1D("nobcut","m [Gev]",100,0,500)
bjetbscores = ROOT.TH1D("bjetscores","b score",100,0,1)

count=0
eventcount=0
muonisocount=0

file = files[fileNum]
inFile = ROOT.TFile.Open(file, "READ")
tree = inFile.Get("Events;1")
print("processing", file)

for entryNum in range(0,tree.GetEntries()): # loop through events
    tree.GetEntry(entryNum)
    eventcount +=1

    nMuons = getattr(tree,"nScoutingMuon")
    nJets = getattr(tree,"nScoutingJet") 
    muon_pt = getattr(tree,"ScoutingMuon_pt")
    SingleMu25 = getattr(tree,"L1_SingleMu25")
    
    Jets = np.zeros((nJets,4))
    dRs = np.zeros(nJets)

    
    
    if nMuons == 1  and muon_pt[0] > 20 and nJets == 4: # require 1 muon > 20 GeV and exactly 4 jets
        #print("\nevent no. ", entryNum, "has 4 jets + muon")
        count+=1
            
        jet_pt = getattr(tree,"ScoutingJet_pt") # 1xnJets array of pts
        jet_eta = getattr(tree,"ScoutingJet_eta")
        jet_phi = getattr(tree, "ScoutingJet_phi")
        jet_mass = getattr(tree, "ScoutingJet_mass")
        b_score = getattr(tree, "ScoutingJet_particleNet_prob_b")
        
        muon = ROOT.TLorentzVector()
        muon_eta = getattr(tree, "ScoutingMuon_eta")
        muon_phi = getattr(tree, "ScoutingMuon_phi")
        muon_m = getattr(tree, "ScoutingMuon_m")
        muon.SetPtEtaPhiM(muon_pt[0], muon_eta[0], muon_phi[0], muon_m[0])

        if all(ele >= 30 for ele in jet_pt) and all(eta < 2.4 for eta in jet_eta): # jet pt > 30 GeV and eta cut
            #print("event no.", entryNum, "passed pt and eta requirements")

            for i in range(nJets): # fill jet and dR matrix
                Jets[i][0] = jet_pt[i]
                Jets[i][1] = jet_eta[i] 
                Jets[i][2] = jet_phi[i]
                Jets[i][3] = jet_mass[i]
                
                tempjet = ROOT.TLorentzVector()
                tempjet.SetPtEtaPhiM(Jets[i,0], Jets[i,1], Jets[i,2], Jets[i,3])
                
                dRs[i] = muon.DeltaR(tempjet)

            if any(dR < 0.4 for dR in dRs): # require muon isolation
                dRs = []
                Jets = []
                muonisocount+=1
                #print("event no.", entryNum, "failed muon isolation test")
                    
    if np.any(Jets): # only look at remaining nonzero jet/dR matrices

        #print("\nevent no. ", entryNum)
        #print(np.matrix.round(Jets))
        #print(np.matrix(dRs))
        
        #if nJets > 4: # only keeping top 4 jets
            #n = nJets - 4
            #Jets = Jets[:-n,:]
            #dRs = dRs[:-n]

        bjet_idx = np.argmin(dRs)                                                                                                                                                                                 
        b_jet = ROOT.TLorentzVector()                                                                                                                                                                             
        b_jet.SetPtEtaPhiM(Jets[bjet_idx,0], Jets[bjet_idx,1], Jets[bjet_idx,2], Jets[bjet_idx,3])    
        b_jet_b_score = b_score[bjet_idx]

        print("\nevent no. ", entryNum)
        print(np.matrix.round(Jets))
        print(np.matrix(dRs)) 
        print("b jet index:", bjet_idx, "with b score", b_jet_b_score)
        
        others_idx = [0,1,2,3]
        others_idx.remove(bjet_idx)
        
        jet1 = ROOT.TLorentzVector()
        jet2 = ROOT.TLorentzVector()
        jet3 = ROOT.TLorentzVector()
        
        jet1.SetPtEtaPhiM(Jets[others_idx[0],0], Jets[others_idx[0],1], Jets[others_idx[0],2], Jets[others_idx[0],3])
        jet2.SetPtEtaPhiM(Jets[others_idx[1],0], Jets[others_idx[1],1],Jets[others_idx[1],2], Jets[others_idx[1],3])
        jet3.SetPtEtaPhiM(Jets[others_idx[2],0], Jets[others_idx[2],1],Jets[others_idx[2],2], Jets[others_idx[2],3])

        jet123 = jet1 + jet2 + jet3
        
        nobcut.Fill(jet123.M())
        bjetbscores.Fill(b_jet_b_score)

        
        if b_jet_b_score > .9:
            mijk90.Fill(jet123.M())

        if b_jet_b_score > .8:
            mijk80.Fill(jet123.M())

        if b_jet_b_score > 0.7:
            mijk70.Fill(jet123.M())

            
print("processed", eventcount, "events")
print(count, "4 jet + muon events")
print(muonisocount, "did not have an isolated muon")
print("there are", count - muonisocount, "good events")
   
mijk90.SetDirectory(0)
mijk80.SetDirectory(0)
mijk70.SetDirectory(0)
nobcut.SetDirectory(0)
bjetbscores.SetDirectory(0)

inFile.Close()
outHistFile = ROOT.TFile.Open(outFileName, "RECREATE")
outHistFile.cd()
mijk90.Write()
mijk80.Write()
mijk70.Write()
nobcut.Write()
bjetbscores.Write()
outHistFile.Close()

