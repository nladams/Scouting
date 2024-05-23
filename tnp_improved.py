import ROOT
import sys
import numpy as np

if len(sys.argv) != 3:
    print("USAGE : % <input file > <output file >"%(sys.argv[0]))
    sys.exit(1)
inFileName = sys.argv[1]
outFileName = sys.argv[2]

print("Reading from ", inFileName , "and writing to ", outFileName, "looking for single isolated muon + jets")

inFile = ROOT.TFile.Open(inFileName, "READ")
tree = inFile.Get("Events;1")

#some histogram
mijk = ROOT.TH1D("data","m_{ijk}, data", 100,0,500) #0 to 500 GeV

count=0 # keep track of "good" events

for entryNum in range(0,tree.GetEntries()): # loop through events
    tree.GetEntry(entryNum)
    
    nMuons = getattr(tree,"nScoutingMuon")
    nJets = getattr(tree,"nScoutingJet") 
    muon_pt = getattr(tree,"ScoutingMuon_pt")
    
    Jets = np.zeros((nJets,4))
    dRs = np.zeros(nJets)

    if nMuons == 1  and muon_pt[0] > 20 and nJets >=4: # require 1 muon > 20 GeV and at least 4 jets
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

        if all(ele >= 20 for ele in jet_pt): # jet pt > 20 GeV
            count += 1
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
            count -= 1
        
    if np.any(Jets): # only look at remaining nonzero jet/dR matrices

        #print("\nevent no. ", entryNum)
        #print(np.matrix.round(Jets))
        #print(np.matrix(dRs))

        if nJets > 4: # only keeping top 4 jets
            n = nJets - 4
            Jets = Jets[:-n,:]
            dRs = dRs[:-n]

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

        if b_jet_b_score > .9:
            triquark_mass = jet1.M() + jet2.M() + jet3.M()
            mijk.Fill(triquark_mass)

print("found", count, "good events")   
mijk.SetDirectory(0)
inFile.Close()
outHistFile = ROOT.TFile.Open(outFileName, "RECREATE")
outHistFile.cd()
mijk.Write()
outHistFile.Close()

