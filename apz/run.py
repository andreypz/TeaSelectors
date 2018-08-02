#!/usr/bin/env python
import sys,os
from math import sqrt
import argparse
parser =  argparse.ArgumentParser(description='Running the tree selection', usage="./run.py")
parser.add_argument("--proof",  dest="proof", action="store_true", default=False,  help="Run this thing with PROOF!")
parser.add_argument("-c",  dest="cuts", type=str, default='default',
                    choices=['default','optimal','scan'],help="Run this thing with PROOF!")

opt = parser.parse_args()

from ROOT import *

workingPath = os.getcwd()
parentDir = os.path.abspath(os.path.join(workingPath, os.pardir))
SandM_path = parentDir+"/sugar-n-milk/"

gSystem.SetBuildDir("buildDir", kTRUE)
gSystem.AddIncludePath(" -I"+SandM_path)
gROOT.LoadMacro(SandM_path+"/HistManager.cc+")

#fChain = TChain("apzTree")
#fChain.Add('APZ_smalltree_25July2018.root')

fChain = TChain("apzTree/apzTree")
fChain.Add('APZ-tree-Data-MuEG-8TeV-2018July25.root')

timer = TStopwatch()
timer.Start()

optima = []

# Default cuts:
gamma_pt_cuts = [25]
gamma_eta_cuts = [1.4442]
lep1_pt_cuts = [23]
lep2_pt_cuts = [4]

if opt.cuts=='scan':
  gamma_pt_cuts = range(26,34)
  gamma_eta_cuts = [1.2, 1.3, 1.4, 1.4442, 1.5, 1.6, 1.8]
  lep1_pt_cuts = range(23,26)
  lep2_pt_cuts = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
if opt.cuts=='optimal':
  # Optimal cuts using 9 bins in signal region:
  gamma_pt_cuts = [30]
  gamma_eta_cuts = [1.5]
  lep1_pt_cuts = [24]
  lep2_pt_cuts = [6]
  # Optimal cuts using 5 bins in signal region:
  #gamma_pt_cuts = [30]
  #gamma_eta_cuts = [1.4442]
  #lep1_pt_cuts = [23]
  #lep2_pt_cuts = [6]

for cut_gamma_pt in gamma_pt_cuts:
  for cut_gamma_eta in gamma_eta_cuts:
    for cut_lep1_pt in lep1_pt_cuts:
      for cut_lep2_pt in lep2_pt_cuts: 
        fChain.Process("smallAna.C+", "%f %f %f %f" % (cut_gamma_pt, cut_gamma_eta, cut_lep1_pt, cut_lep2_pt))
        
        f = TFile("my_higgsHistograms.root",'OPEN')  
        evt = f.Get("evt")
        SplusB = evt.GetBinContent(3)
        B = (9./11)*evt.GetBinContent(4)
        S = SplusB - B;
        significance = 2*(sqrt(SplusB) - sqrt(B))
        print "S+B=%i, S=%.1f, signif=%.3f" %(SplusB, S, significance)
        
        info = [cut_gamma_pt, cut_gamma_eta, cut_lep1_pt, cut_lep2_pt, SplusB, S, significance]
        optima.append(info)

print optima
sort_opt = sorted(optima, key=lambda x: float(x[6]))
print 
print 
for l in sort_opt:
  print l

if opt.cuts!='scan':
  print "Made histos, now let's make the plots"
  execfile('plotit.py')

print sort_opt[-1]
print "Done!", "CPU Time: ", timer.CpuTime(), "RealTime : ", timer.RealTime()



print "End of running"
