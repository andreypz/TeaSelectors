#! /usr/bin/env python

import sys,os
from math import sqrt
from ROOT import *


gROOT.SetBatch()
gStyle.SetOptStat(0)

def handleOverflowBins(hist):
  if hist == None:
    return
  nBins   = hist.GetNbinsX()
  lastBin = hist.GetBinContent(nBins)
  ovflBin = hist.GetBinContent(nBins+1);
  lastBinErr = hist.GetBinError(nBins);
  ovflBinErr = hist.GetBinError(nBins+1);
  firstBin    = hist.GetBinContent(1);
  undflBin    = hist.GetBinContent(0);
  firstBinErr = hist.GetBinError(1);
  undflBinErr = hist.GetBinError(0);
  hist.SetBinError(nBins, sqrt(pow(lastBinErr,2) + pow(ovflBinErr,2)) );
  hist.SetBinContent(1, firstBin+undflBin);
  hist.SetBinError(1, sqrt(pow(firstBinErr,2) + pow(undflBinErr,2)) );
  hist.SetBinContent(0,0);
  hist.SetBinContent(nBins+1,0);
  
if __name__ == "__main__":
  print "This is the __main__ part"

  f = TFile("my_higgsHistograms.root",'OPEN')

  ks = f.Get("AfterCuts")
  names = []
  for key in ks.GetListOfKeys():
    names.append(key.GetName())
    
  print names
  
  h = {}


  primary = "InAPZ"

  for n in ["lep1_pt", "lep2_pt", "gamma_pt",
            "lep1_phi","lep2_phi","gamma_phi",
            "lep1_eta","lep2_eta","gamma_eta",
            "dR_gamma_jet1","dR_gamma_jet2","dR_lep", "dRjj","dR_gamma_dilep",
            "Mllg_full", "Mllg_higg", "Mllg_zed", "Mll_APZ_JPsi","Mll_18",
            "pt_ratio_dilep_gamma",
            "Mgj_full", "Mgj_higg",
            "Mjj_full","Mjj_zoom","Mllgj_full","Mllgj_higg", "Mllgj_x200",
            "jet1_pt","jet1_eta","jet1_phi",
            "jet2_pt","jet2_eta","jet2_phi",
            "met_Et","met_phi","met_dPhi_dilep","met_dPhi_gamma"]:

    
    print "Plotting", n
    m = 0
    for d in [primary, 'AfterCuts', 'InJpsi']:
      h[d] = f.Get(d+'/'+n+'_'+d)
      if h[d] == None:
        print "Not a good histo:", h[d]
        continue
      
      if d==primary:
        opt = "hist"
        h[d].SetLineColor(kGreen+2)
      else:
        opt = "hist same"
        if d=='InJpsi':
          h[d].SetLineColor(kRed+1)
        if d=='AfterCuts':
          h[d].SetLineColor(kBlue+1)
        if d=='M18':
          h[d].SetLineColor(kOrange+1)

        
      norm = h[primary].Integral()
      
      if h[d].Integral()!=0:
        h[d].Scale(norm/h[d].Integral())
      
      if n in ["Mllg_full","gamma_pt","Mjj_full","Mllgj","Mgj_full","pt_ratio_dilep_gamma","met"]:
        handleOverflowBins(h[d])
            
      h[d].Draw(opt)
      m = max(h[d].GetMaximum(), m)
      h[primary].SetMaximum(1.1*m)

    c1.SaveAs("figs/fig_"+n+".png")


  ## < indent of for loop
  evt = f.Get("evt")
  SplusB = evt.GetBinContent(3)
  B = (9./11)*evt.GetBinContent(4)
  significance = 2*(sqrt(SplusB) - sqrt(B))
  print "S+B=%i, S=%.1f, signif=%.3f" %(SplusB, SplusB-B, significance)

  
