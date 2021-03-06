#!/usr/bin/env python
import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./plot.py -f inputFileName")
parser.add_argument("-f",  dest="fname", type=str, default='TB_2016_myHistograms.root',
                    help="Filename with histograms")
parser.add_argument("-v", "--verbosity",  dest="verb", action="store_true", default=False,
                    help="Print out more stuff")
parser.add_argument("--fit",  dest="fit", action="store_true", default=False,
                    help="Perform the fits of some distributions")
parser.add_argument("--june",  dest="june", action="store_true", default=False,
                    help="Do plots for June's data (default is April)")
parser.add_argument("--mini",  dest="mini", action="store_true", default=False,
                    help="Only make a few plots for tests, not the whole thing)")
parser.add_argument("--hv",  dest="hv", nargs='+', default=['800','600'],
                    help="Specify which HV2 data we should run")
parser.add_argument("--beam",  dest="beam", nargs='+', default=['ELE','PION'],
                    help="Specify which BEAM data we should run")
parser.add_argument("--allruns",  dest="allruns", action="store_true", default=False,
                    help="Make the plots for each run (they shold be present in the input file)")
parser.add_argument("--syst",  dest="syst", action="store_true", default=False,
                    help="Do systematcis on sigma plots")
parser.add_argument("--gr",  dest="useGraph", action="store_true", default=False,
                    help="Use TGraph to store signa plot and fit it (instead of TH1)")
parser.add_argument("--f3",  dest="f3", action="store_true", default=False,
                    help="Use 3-parameter fit (fefault is 2paramers)")
parser.add_argument("--log",  dest="log", action="store_true", default=False,
                    help="Make some plots in log scale")

opt = parser.parse_args()
#print opt

import sys,os,json
from math import sqrt
from array import array
import numpy as np
from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".L ../sugar-n-milk/tdrstyle.C")
gROOT.LoadMacro("../sugar-n-milk/CMS_lumi.C")
setTDRStyle()
gROOT.ForceStyle()
if not opt.verb:
  gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")


if opt.june:
  outDir = './Plots-TB-June/'
  jsonFile1 = './SiPadsConfig_June2016TB_v1.json'
  jsonFile2 = './RunSummaryTB_June2016.json'
  out = TFile("fJun.root","recreate")
else:
  outDir = './Plots-TB-April/'
  jsonFile1 = './SiPadsConfig_April2016TB_v1.json'
  jsonFile2 = './RunSummaryTB_April2016.json'
  out = TFile("fApr.root","recreate")

with open(jsonFile1, 'r') as fp:
  SiPad_DATA = json.load(fp)

allPads = SiPad_DATA['PADSMAP1']

with open(jsonFile2, 'r') as fp:
  TB_DATA = json.load(fp)

PadsCol = {"SiPad1":1, "SiPad2":47, "SiPad3":8, "SiPad4":9, "SiPad5":41, "SiPad6":46}

c1 = TCanvas("c1","small canvas",600,600);
c2 = TCanvas("c2","small canvas",800,600);

def createDir(myDir):
  if opt.verb: print 'Creating a new directory: ', myDir
  if not os.path.exists(myDir):
    try: os.makedirs(myDir)
    except OSError:
      if os.path.isdir(myDir): pass
      else: raise
  else:
    if opt.verb: print "\t OOps, it already exists"

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


def justPlotAll(myF, inThisDir='Main'):
  if opt.verb: print 'myDir is =', inThisDir
  isDir = None
  if myF!=None and not myF.IsZombie():
    isDir = myF.cd(inThisDir)
    if not isDir: return
  else:
    print "\t Sorry can't draw anything, no files are provided!"
    return

  dirList = gDirectory.GetListOfKeys()
  # dirList.Print()

  path = outDir+inThisDir
  createDir(path)

  c0=c1
  c0.cd()


  histoName = None
  for k in dirList:
    # print '\t Item in the dir: ', k
    mainHist = k.ReadObj()
    histoName = mainHist.GetName()

    if inThisDir!="":
      h1 = myF.Get(inThisDir+"/"+histoName)
    else:
      h1 = myF.Get(histoName)

    handleOverflowBins(h1)

    hmin=0
    hmax=h1.GetMaximum()
    if 'WC_dx' in histoName:
      hmin = -5
      hmax = -1
    if 'WC_dy' in histoName:
      hmin = -3
      hmax = 1
    h1.SetMinimum(hmin)
    h1.SetMaximum(hmax)

    if h1.InheritsFrom("TH2"):
      h1.Draw("col")
    else:
      h1.Draw('e1')

    c0.SaveAs(path+"/"+histoName+'.png')


def onePerTag(myF, hName, tag):
  if opt.verb: print "\t Making plots for ->", hName
  c0=c1
  c0.cd()
  newName = str(hName+tag)

  try:
    h1 = myF.Get(newName).Clone()
  except ReferenceError:
    return

  handleOverflowBins(h1)

  if h1.InheritsFrom("TH2"):
    h1.Draw("col")
  else:
    h1.Draw('e1')

  h1.SetMinimum(0)
  path = outDir+'onePerTag'+tag
  createDir(path)
  split = os.path.split(hName.rstrip("/"))
  c0.SaveAs(path+"/"+split[1]+'.png')

def allPadsOnOnePlot(myF, hName, tag, fit=False, overHists=None):
  # print "\t Making plots for ->", hName


  isThisWaveform = 'Waveform' in hName
  isBadSet = ('N200' in tag and not opt.june)

  if 'PER-RUN' in hName: c0 = c2
  else: c0=c1
  c0.cd()

  h = {}
  hmaxima=[]
  for p, ch in allPads.iteritems():
    suffix = '_'+p+'_ch'+str(ch)
    #print 'pad', p,  suffix

    newName = str(hName+suffix+tag)

    try:
      h[p]=myF.Get(newName).Clone()
    except ReferenceError:
      if p=='SiPad1' or (p=='SiPad2' and isBadSet):
        if opt.verb: print '\t Well, this is the front pad Just skip it:', p
        continue
      else:
        print 'Looks like this hist does not exist:', newName
        print '\t *** --> This is no good.. <-- *** \n'
        sys.exit(0)
        #return

    h[p].SetLineColor(PadsCol[p])
    h[p].SetLineWidth(2)
    norm = h[p].Integral()
    if norm!=0 and not h[p].InheritsFrom('TProfile'):
      h[p].Scale(1./norm)
    if not (p=='SiPad2' and isBadSet):
      hmaxima.append(h[p].GetMaximum())

  if h['SiPad3'].InheritsFrom('TProfile'):
    drawOpt = 'e1'
  else:
    drawOpt = 'hist'


  hmin = 0
  hmax = 1.1*max(hmaxima)
  #print hmaxima, hmax

  if isThisWaveform:
    hmin = -0.1
    hmax = 1.1
  if 'Pedestal_PerRun' in hName:
    if opt.june:
      hmin = 3600
      hmax = 3800
    else:
      hmin = 100
      hmax = 300
  if 'PedestalRMS_PerRun' in hName:
    hmax = 50

  leg = TLegend(0.75,0.72,0.92,0.90)

  h['SiPad3'].Draw(drawOpt)
  h['SiPad3'].SetMinimum(hmin)
  h['SiPad3'].SetMaximum(hmax)
  if not isBadSet: # Because in set2 this Pad is bad...
    h["SiPad2"].Draw(drawOpt+' sames')
  h["SiPad4"].Draw(drawOpt+' sames')
  h["SiPad5"].Draw(drawOpt+' sames')
  h["SiPad6"].Draw(drawOpt+' sames')

  try:
    h["SiPad1"].Draw(drawOpt+' sames')
    leg.AddEntry(h["SiPad1"],"SiPad1", "l")
  except:
    if opt.verb: print 'do nothing'

  #c0.Update()
  #gStyle.SetOptStat(1111)
  #gStyle.SetOptFit(1)
  if fit:
    n=0
    print 'Doing gauss fits for:', h
    for p,hi in sorted(h.iteritems()):
      if p=='SiPad2' and isBadSet: continue
      print p, hi
      m = hi.GetMean()
      r = hi.GetRMS()
      hi.Fit('gaus','Q','', m-3*r, m+3*r)
      f = hi.GetFunction('gaus')
      f.SetLineColor(PadsCol[p])
      f.SetLineStyle(kDashed)
      f.Draw('same')
      gPad.Update()
      #print pa, hi.GetListOfFunctions().FindObject("stats")
      st = hi.GetListOfFunctions().FindObject("stats")
      #l = st.GetListOfLines()
      #l.Remove(st.GetLineWith('Mean'))
      #l.Remove(st.GetLineWith('RMS'))
      #l.Remove(st.GetLineWith('Constant'))
      ##l.Remove(st.GetLineWith('Constant'))
      #l.Print()
      #raw_input()
      #st.SetName(pa)
      st.SetY1NDC(0.70-0.115*n)# //new y start position
      st.SetY2NDC(0.60-0.115*n)# //new y end position
      st.SetLineColor(PadsCol[p])
      n+=1

  if not isBadSet:
    leg.AddEntry(h["SiPad2"],"SiPad2", "l")
  leg.AddEntry(h['SiPad3'],"SiPad3", "l")
  leg.AddEntry(h['SiPad4'],"SiPad4", "l")
  leg.AddEntry(h['SiPad5'],"SiPad5", "l")
  leg.AddEntry(h['SiPad6'],"SiPad6", "l")
  leg.SetFillColor(kWhite)
  leg.Draw()

  if tag=='': tag='_PerRun'
  path = outDir+'AllInOne'+tag
  createDir(path)
  split = os.path.split(hName.rstrip("/"))


  drawLabel(tag)

  if isThisWaveform:
    c0.Update()
    l1=TLine(c0.GetUxmin(), 0, c0.GetUxmax(), 0);
    l2=TLine(0, c0.GetUymin(), 0, c0.GetUymax());
    l1.SetLineColor(kBlue)
    l1.SetLineStyle(kDashed)
    l1.Draw()
    l2.SetLineColor(kBlue)
    l2.SetLineStyle(kDashed)
    l2.Draw()


  if overHists!= None:
    # This is written for 'PER-RUN' cases, where I'd like to overlay
    # shade histograms to identofy certain runs: Pedestal Runs, 300 um set, etc
    # print 'Drawing overhists!'
    ovleg = TLegend(0.55,0.72,0.7,0.90)
    for ov in overHists:
      ov.Draw('same hist')
      ov.SetLineStyle(3)
      ov.SetLineWidth(0)
      if ov.GetName()=='300': ovCol = kRed
      if ov.GetName()=='200': ovCol = kOrange
      if ov.GetName()=='120': ovCol = kCyan
      if ov.GetName()=='Ped': ovCol = kBlue
      if ov.GetName()=='Pio': ovCol = kGreen
      # ov.SetFillColorAlpha(ovCol, 0.2)

      ovleg.AddEntry(ov, ov.GetName()+' Runs','f')

    # Re-drawing legend
    leg.SetX1(0.8)
    leg.SetY1(0.64)
    leg.Draw()
    ovleg.Draw()

  c0.SaveAs(path+"/"+split[1]+tag+'.png')

def drawLabel(tag):
  label = TText()
  label.SetNDC()
  label.SetTextFont(1)
  label.SetTextColor(kBlue+3)
  label.SetTextSize(0.04)
  label.SetTextAlign(1)
  if 'GROUP_0' in tag:
    if tag[9:12]=="ELE":
      label.DrawText(0.20, 0.95, '  '.join(['Beam:'+tag[9:12],tag[13:24], tag[25:]]).replace('_',':'))
    else:
      label.DrawText(0.20, 0.95, '  '.join(['Beam:'+tag[9:13],tag[14:25], tag[26:]]).replace('_',':'))

  elif 'GROUP_1' in tag:
    label.DrawText(0.15, 0.95, '  '.join(['Beam:'+tag[9:12]+', '+tag[14:20], tag[21:32], tag[33:]]).replace('_',':'))
  else:
    label.DrawText(0.05, 0.95, tag)


def sigmaPlot(myF, hName, tag, sysFiles=[], doSigmaFit=False):
  if opt.verb: print "\t Making Sigma plots for ->", hName
  isBadSet = ('N200' in tag and not opt.june)

  c0=c1
  c0.cd()

  h = {}
  karambaMe, karambaSi = {}, {}
  grafaraSi = {}
  constTerm, noiseTerm, noiseErr, constErr = {}, {}, {}, {}
  for p, ch in allPads.iteritems():
    p=str(p)
    #suffix = p+'_ch'+str(ch)
    suffix = '_'+p+'_ch'+str(ch)
    #print 'pad', p,  suffix
    newName = str(hName+suffix+tag)
    try:
      h[p]=myF.Get(newName).Clone()
    except ReferenceError:
      if p=='SiPad1':
        if opt.verb: print '\t Well, this is the front pad Just skip it:', p
        continue
      else:
        print 'Looks like this hist does not exist:', newName
        print '\t *** --> This is no good.. <-- ***'
        sys.exit(0)
        # return

    path = outDir+'Projects'+tag
    createDir(path)

    if '_VS_nMIPs' in hName:
      varBins = [0,2,3,5,7,9,11,13,15,17,19,21,23,25,27,30,35,40,45,50,60]
      xTitle = ';Number of MiPs'
      figName = '_VS_nMIPs'+tag
    elif '_VS_SigOverNoise' in hName:
      varBins = [2,3,5,7,9,11,13,15,17,19,22,25,28,31,35,40,50,70,140]
      xTitle = ';Signal/Noise'
      figName = '_VS_SigOverNoise'+tag
    elif '_VS_sOvern_Pad1X_nMiPcut' in hName:
      varBins = [2,3,5,7,9,11,13,15,17,19,22,25,28,31,35,40,50,70,140]
      xTitle = ';Effective S/N'
      figName = '_VS_sOvern_Pad1X_nMiPcut'+tag
    elif '_VS_sOvern_Pad1X' in hName:
      #varBins = [3,10,20,30,40,50,60,70,80,90,100,110,120,130,140]
      varBins = [2,3,5,7,9,11,13,15,17,19,22,25,28,31,35,40,50,70,140]
      #lo = '0.3'
      #xTitle = ';(S_{1}/N_{1})#times(S#lower[%s]{#font[12]{i}}/N#lower[%s]{#font[12]{i}}) / #sqrt{(S_{1}/N_{1})^{2} + (S#lower[%s]{#font[12]{i}}/N#lower[%s]{#font[12]{i}})^{2}}' %(lo,lo,lo,lo)
      xTitle = ';(S/N)_{eff}'
      #xTitle = ';(S_{1}/N_{1})\\times(S_{i} /N_{i}) \\sqrt{(S_{1}/N_{1})^{2} + (S_{i} /N_{i})^{2}}'
      #xTitle = ';Effective S/N'
      figName = '_VS_sOvern_Pad1X'+tag

    # xBins are bin-numbers of the varBins (see conversion above)
    # It assumes that the total number of bins on the axis is 400.
    xBins = [int(400.0*(x-varBins[0])/(varBins[-1]-varBins[0]))+1 for x in varBins]
    # print 'varBins:\n \t', varBins
    # print 'xBins:\n \t', xBins

    karambaMe[p] = TH1D('Mean' +p,xTitle+";Mean of (t_{i} - t_{1}), ns", len(varBins)-1,array('d',varBins))
    karambaSi[p] = TH1D('Sigma'+p,xTitle+";#sigma(t_{#font[12]{i}} - t_{1}), ns", len(varBins)-1,array('d',varBins))

    grafaraSi[p] = TGraphAsymmErrors()

    nGr = -1
    for n in range(len(xBins)-1):
      proj = h[p].ProjectionY("", xBins[n], xBins[n+1]-1)

      # print n,'Doing bin:', xBins[n], 'to', xBins[n+1]-1
      # print ' \t which correspond to varBins:\n\t', varBins[n], 'to', varBins[n+1]

      if proj.GetEntries()<200: # Default: 200
        if opt.verb:
          print '\t WARNING: you have too few events to fit for tag:', tag
          print '\t\t nEvents = ',proj.GetEntries(),'  pad = '+p+'  bins:', xBins[n], xBins[n+1]
          print '\t I must continue without this point...'
        continue

      nGr+=1 # This is point counter for TGraph
      
      m = proj.GetMean()
      r = proj.GetRMS()
      FitRangeSigma = 2 # Default: 2
      proj.Fit('gaus','QI','', m-FitRangeSigma*r, m+FitRangeSigma*r)

      # These plots are not really needed, but maybe interesting for debugging:
      # proj.SetTitleOffset(1.0, "X")
      # c0.SaveAs(path+'/Gauss_'+p+figName+'_bin'+str(n)+'.png')


      f = proj.GetFunction('gaus')
      fMean    = f.GetParameter(1)
      fMeanErr = f.GetParError(1)
      fSigma    = f.GetParameter(2)
      fSigmaErr = f.GetParError(2)

      karambaMe[p].SetBinContent(n+1,fMean)
      karambaMe[p].SetBinError(n+1,fMeanErr)

      karambaSi[p].SetBinContent(n+1,fSigma)

      # grafaraSi[p].SetPoint(nGr, 0.5*(varBins[n]+varBins[n+1]), fSigma)
      # Let's set the point at the mean of the bin:
      h[p].GetXaxis().SetRange(xBins[n],  xBins[n+1]-1)
      # print 'Mean in given range:', h[p].GetMean(), 'RMS=', h[p].GetRMS()
      xPos = h[p].GetMean()
      grafaraSi[p].SetPoint(nGr, xPos, fSigma)
      h[p].GetXaxis().SetRange()

      binWidth = (varBins[n+1]-varBins[n])
      if not opt.syst or len(sysFiles)==0:
        karambaSi[p].SetBinError(n+1,fSigmaErr)
        grafaraSi[p].SetPointError(nGr, xPos-varBins[n], varBins[n+1]-xPos, fSigmaErr, fSigmaErr)
        if opt.syst and len(sysFiles)==0:
          print 'No syst files provided to do systematics... Will take the fit uncerrtainty.'
      else:
        fTotErr = 0 # Total error in percent
        if fSigma!=0:
          syst = [fSigmaErr/fSigma]
          for sF in sysFiles:
            # print sF
            hSys = sF.Get(str(p+tag))
            sDiff = fSigma - hSys.GetBinContent(n+1)
            syst.append(sDiff/fSigma)
          s = np.array(syst)

          # print p, n, s
          fTotErr = np.sqrt(np.sum(np.square(s)))
          # print '\t fTotErr=', fTotErr

        karambaSi[p].SetBinError(n+1,fTotErr*fSigma)
        grafaraSi[p].SetPointError(nGr, xPos-varBins[n], varBins[n+1]-xPos, fTotErr*fSigma, fTotErr*fSigma)

      #print '\t My Fit result for mean: ', fMean, fMeanErr
      #print '\t  \t for sigma: ', fSigma, fSigmaErr

    # <-- end of loop over n (xBins and varBbins)

    karambaMe[p].SetLineColor(PadsCol[p])
    karambaMe[p].SetLineWidth(2)
    karambaSi[p].SetLineColor(PadsCol[p])
    karambaSi[p].SetLineWidth(2)
    
    grafaraSi[p].SetLineColor(PadsCol[p])
    grafaraSi[p].SetLineWidth(2)

    if doSigmaFit:
      # print 'Doing sigma fit on ', hName, tag
      # print '\t pad =',p
      c0_2 = c1

      # Two parameters fit

      f2 = TF1 ('f2','sqrt([0]*[0]/(x*x) + [1]*[1])', 5,140.)
      f2.SetParameters(1, 0.03)
      f2.SetParLimits(0, 0, 3)
      f2.SetParLimits(1, 0, 0.2)

      # Three parameters fit:

      f3 = TF1 ('f3','sqrt([0]*[0]/(x*x) + [1]*[1]/x + [2]*[2])', 5.,140.)
      f3.SetParameters(1, 0.3, 0.03)
      f3.SetParLimits(0, 0, 3)
      f3.SetParLimits(1, 0, 1)
      f3.SetParLimits(2, 0., 0.3)

      # For two-parameter fit and const term:
      fToUse = f2
      ConstParInd = 1

      if opt.f3:
        # For three-paremeter fit
        fToUse = f3
        ConstParInd = None


      fitRange = [5,140] # Default range: 5, 70. UPD Apr 2017: extend default to 140

      # A hist to store confidance interval:
      confidInt = TH1D("confidInt", "Fitted func with conf. band", 200, fitRange[0], 110)
      confidInt.SetStats(kFALSE)
      confidInt.SetFillColor(2)

      if not opt.useGraph:
        karambaSi[p].Fit(fToUse,'Q','',fitRange[0],fitRange[1])
        TVirtualFitter.GetFitter().GetConfidenceIntervals(confidInt, 0.68);

        karambaSi[p].Draw()
        karambaSi[p].SetMaximum(0.4)
        karambaSi[p].SetMinimum(0.0)
        karambaSi[p].GetXaxis().SetLimits(0, varBins[-1])
        fToUse.SetRange(fitRange[0], fitRange[1])
        fToUse.Draw("same")
        if opt.log:
          karambaSi[p].SetMinimum(0.01)
          c0_2.SetLogy()

        if opt.f3:
          confidInt.Draw("e3 same")

        c0_2.SaveAs(path+'/SigmaFit_SOverN'+figName+"_"+p+'.png')
        c0_2.SetLogy(0)
        
        noiseTerm[p] = fToUse.GetParameter(0)
        noiseErr[p]  = fToUse.GetParError(0)

      else:
        # ----
        # Fitting the TGraph instead of the TH1:

        grafaraSi[p].Fit(fToUse,'QE','',fitRange[0],fitRange[1])
        TVirtualFitter.GetFitter().GetConfidenceIntervals(confidInt, 0.68);

        grafaraSi[p].Draw("APZ")
        grafaraSi[p].SetMaximum(0.4)
        grafaraSi[p].SetMinimum(0.0)
        grafaraSi[p].GetXaxis().SetLimits(0, varBins[-1])
        fToUse.SetRange(fitRange[0], fitRange[1])
        fToUse.Draw("same")
        if opt.log:
          c0_2.SetLogy()
          grafaraSi[p].SetMinimum(0.01)

        if opt.f3:
          confidInt.Draw("e3 same")

        grafaraSi[p].SetTitle(xTitle+";#sigma(t_{#font[12]{i}} - t_{1}), ns")
        c0_2.SaveAs(path+'/SigmaFit_SOverN_graf'+figName+"_"+p+'.png')
        c0_2.SetLogy(0)

        noiseTerm[p] = fToUse.GetParameter(0)
        noiseErr[p]  = fToUse.GetParError(0)


      if ConstParInd!=None:
        constTerm[p] = fToUse.GetParameter(ConstParInd)
        constErr[p]  = fToUse.GetParError(ConstParInd)
        
      else:
        # When the const term is not reliable, let's just evaluate the function at S/N=100:
        constTerm[p] = fToUse.Eval(100)
        #constTerm[p] = confidInt.GetBinContent(confidInt.FindBin(100))


        # Assign the error from Confidence interval thingy
        constErr[p] = confidInt.GetBinError(confidInt.FindBin(100))

        # If can't be helped, set it to 10% uncertainty:
        #constErr[p]  = 0.10*constTerm[p]


      confidInt.Delete()
    # <-- if dosigmafit indent
  # <-- for p, ch indent

  c0.cd()
  
  drawOpt= 'e1p'
  karambaMe['SiPad3'].Draw(drawOpt)
  if not isBadSet:
    karambaMe['SiPad2'].Draw(drawOpt+' same')
  karambaMe['SiPad4'].Draw(drawOpt+' same')
  karambaMe['SiPad5'].Draw(drawOpt+' same')
  karambaMe['SiPad6'].Draw(drawOpt+' same')
  karambaMe['SiPad3'].SetMinimum(-0.4)
  karambaMe['SiPad3'].SetMaximum(0.6)

  leg = TLegend(0.67,0.62,0.92,0.90)
  if not isBadSet:
    leg.AddEntry(karambaMe["SiPad2"],"SiPad2", "l")
  leg.AddEntry(karambaMe['SiPad3'],"SiPad3", "l")
  leg.AddEntry(karambaMe['SiPad4'],"SiPad4", "l")
  leg.AddEntry(karambaMe['SiPad5'],"SiPad5", "l")
  leg.AddEntry(karambaMe['SiPad6'],"SiPad6", "l")
  leg.SetFillColor(kWhite)
  leg.Draw()

  drawLabel(tag)

  c0.SaveAs(path+'/KarambaMe'+figName+'.png')


  karambaSi['SiPad3'].Draw(drawOpt)
  if not isBadSet:
    karambaSi['SiPad2'].Draw(drawOpt+' same')
  karambaSi['SiPad4'].Draw(drawOpt+' same')
  karambaSi['SiPad5'].Draw(drawOpt+' same')
  karambaSi['SiPad6'].Draw(drawOpt+' same')
  karambaSi['SiPad3'].SetMinimum(0.0)
  karambaSi['SiPad3'].SetMaximum(0.3)

  karambaSi['SiPad3'].SetTitleSize(0.04,"X")
  karambaSi['SiPad3'].SetTitleOffset(1.3, "X")

  leg2 = TLegend(0.67,0.62,0.92,0.90)
  if '120' in tag:
    T = '120'
  elif '200' in tag:
    T = '200'
  elif '300' in tag:
    T = '300'

  leg2.SetHeader('  Fluence:')
  if not isBadSet:
    leg2.AddEntry(karambaSi["SiPad2"],'%1.2E'%(SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T+'um']]['SiPad2']), "l")
  leg2.AddEntry(karambaSi["SiPad3"],'%1.2E'%(SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T+'um']]['SiPad3']), "l")
  leg2.AddEntry(karambaSi["SiPad4"],'%1.2E'%(SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T+'um']]['SiPad4']), "l")
  leg2.AddEntry(karambaSi["SiPad5"],'%1.2E'%(SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T+'um']]['SiPad5']), "l")
  leg2.AddEntry(karambaSi["SiPad6"],'%1.2E'%(SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T+'um']]['SiPad6']), "l")
  leg2.SetFillColor(kWhite)
  leg2.Draw()

  out.cd()
  for p, ch in allPads.iteritems():
    if p=='SiPad1': continue
    if opt.useGraph:
      grafaraSi[p].Write(p+tag)
    else:
      karambaSi[p].Write(p+tag)

  #drawLabel(tag)
  c0.SaveAs(path+'/KarambaSi'+figName+'.png')
  c0.SaveAs(path+'/KarambaSi'+figName+'.pdf')


  drawOpt="PZ"
  grafaraSi['SiPad3'].Draw("A"+drawOpt)
  grafaraSi['SiPad3'].GetXaxis().SetLimits(0, 140)
  grafaraSi['SiPad3'].SetTitle(xTitle+";#sigma(t_{#font[12]{i}} - t_{1}), ns")

  if not isBadSet:
    grafaraSi['SiPad2'].Draw(drawOpt+' same')
  grafaraSi['SiPad4'].Draw(drawOpt+' same')
  grafaraSi['SiPad5'].Draw(drawOpt+' same')
  grafaraSi['SiPad6'].Draw(drawOpt+' same')
  grafaraSi['SiPad3'].SetMinimum(0.0)
  grafaraSi['SiPad3'].SetMaximum(0.3)

  leg2.Draw()
  if opt.log:
    grafaraSi['SiPad3'].SetMinimum(0.010)
    c0.SetLogy()
    logExt= '_Log'
  else:
    logExt=''
  c0.SaveAs(path+'/GrafaraSi'+figName+logExt+'.png')
  c0.SaveAs(path+'/GrafaraSi'+figName+logExt+'.pdf')

  c0.SetLogy(0)

  if doSigmaFit: return noiseTerm, noiseErr, constTerm, constErr
  else: return None


  
def effPlot(myF, tag):
  if opt.verb: print "\t Making Eff plots for ->"
  isBadSet = ('N200' in tag and not opt.june)

  c0=c1
  c0.cd()

  h = {}

  effPlot1 = TH1F('effPlot1',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot2 = TH1F('effPlot2',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot3 = TH1F('effPlot3',';SiPad Number;Efficiency', 6,0.5,6.5)
  effPlot4 = TH1F('effPlot4',';SiPad Number;Efficiency', 6,0.5,6.5)

  for p, ch in allPads.iteritems():
    suffix = p+'_ch'+str(ch)
    newName = str('Events'+tag+'/nEvents'+suffix+tag)
    try:
      h[p]=(myF.Get(newName).Clone())
    except ReferenceError:
      print 'Looks like this hist does not exist:', newName
      print '\t *** --> This is no good.. <-- ***'
      return

    eff = h[p].GetBinContent(3)/h[p].GetBinContent(1)
    effPlot1.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(7)/h[p].GetBinContent(3)
    effPlot2.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(8)/h[p].GetBinContent(3)
    effPlot3.SetBinContent(int(p[5]),eff)

    eff = h[p].GetBinContent(9)/h[p].GetBinContent(3)
    effPlot4.SetBinContent(int(p[5]),eff)

    if eff==0 and p!='SiPad1':
      print p, 'eff= ', eff, 'Warning'


  path = outDir+'Efficiency'+tag
  createDir(path)

  effPlot1.Draw('p')
  effPlot2.Draw('p same')
  effPlot3.Draw('p same')
  effPlot4.Draw('p same')
  effPlot1.SetMarkerStyle(20)
  effPlot2.SetMarkerStyle(21)
  effPlot3.SetMarkerStyle(22)
  effPlot4.SetMarkerStyle(23)
  effPlot1.SetMarkerColor(kBlue+1)
  effPlot2.SetMarkerColor(kRed+1)
  effPlot3.SetMarkerColor(kGreen+1)
  effPlot4.SetMarkerColor(kCyan+1)

  effPlot1.SetMinimum(0)
  if opt.june:
    effPlot1.SetMaximum(1.0)
  else:
    effPlot1.SetMaximum(1.0)

  leg = TLegend(0.5,0.6,0.92,0.90)
  leg.AddEntry(effPlot1,"0. Pad 1 > 15 MiPs", "p")
  leg.AddEntry(effPlot2,"#0 &&  5 < Pad N < 10 MiPs /#0", "p")
  leg.AddEntry(effPlot3,"#0 && 10 < Pad N < 15 MiPs /#0", "p")
  leg.AddEntry(effPlot4,"#0 &&  Pad N > 15 MiPs /#0", "p")
  leg.SetFillColor(kWhite)
  leg.Draw()

  drawLabel(tag)
  c0.SaveAs(path+'/effPlot.png')


if __name__ == "__main__":
  print "This is the __main__ part"

  f = TFile(opt.fname,'OPEN')

  # Which plots to make:
  tags = []

  print "\t First, let's remove the directory: ", outDir
  import shutil
  try:
    shutil.rmtree(outDir)
  except OSError:
    print outDir, 'probably does not exist. moving on...'


  if opt.allruns:
    for r, param in TB_DATA.iteritems():
      if opt.verb: print r, param
      # if r in ['3777','3778','3776']:
      if param['BEAM'] in opt.beam and param['HV2'] in opt.hv:
        tags.append("_RUN_"+r+"_"+param['BEAM']+"_E"+param['ENERGY']+"GEV_SENSOR_"+param['SENSOR']+"_irrHV_"+param['HV2'])

  for s in ['120','200','300']:
    for b in opt.beam:
      for hv in opt.hv:
        if opt.verb: print s, b, hv
        if opt.june:
          T='P'
        else:
          T='N'

        if opt.june and hv=='600': continue # Only taken with 800V
        tags.append("_GROUP_0_"+b+"_SENSOR_"+T+s+"_irrHV_"+hv)

        continue
        if opt.june: continue
        if b=='ELE': tags.append("_GROUP_1_"+b+"_E150GEV_SENSOR_"+T+s+"_irrHV_"+hv)
        #if b=='PION' and s=='N200' and hv=='600': continue
        if b=='ELE' and s!='300':
          tags.append("_GROUP_1_"+b+"_E100GEV_SENSOR_"+T+s+"_irrHV_"+hv)

        #tags.append("_GROUP_2_SENSOR_"+s+"_irrHV_"+hv)

  for tag in tags:
    if opt.mini: continue

    print '\t -> Making plots for tag:', tag

    #justPlotAll(f,'Main'+tag)
    #justPlotAll(f,'Timing'+tag)
    #justPlotAll(f,'Profiles'+tag)
    #justPlotAll(f,'Other'+tag)

    allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_frac50',tag, fit=opt.fit)
    #allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_frac30',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_peak',tag, fit=opt.fit)
    #allPadsOnOnePlot(f,'Timing'+tag+'/Delay_from_Pad1_threshold',tag)

    allPadsOnOnePlot(f,'Timing'+tag+'/TrigDelay_frac50',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/RisingEdge_30toMax',tag)
    allPadsOnOnePlot(f,'Timing'+tag+'/RisingEdge_10to90',tag)

    for reg in ['3']:
      allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_pulse_MIPrange_'+reg,tag)
      allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_full_MIPrange_'+reg,tag)
      #allPadsOnOnePlot(f,'Pulse'+tag+'/Waveform_DoublePeak_MIPrange_'+reg,tag)


    allPadsOnOnePlot(f,'Other'+tag+'/nMIPs',tag)
    allPadsOnOnePlot(f,'Other'+tag+'/Signal_over_noise',tag)

    allPadsOnOnePlot(f,'Other'+tag+'/Pedestal',tag, fit=opt.fit)
    allPadsOnOnePlot(f,'Other'+tag+'/PedestalRMS',tag, fit=opt.fit)
    allPadsOnOnePlot(f,'Pulse'+tag+'/Charge',tag)

    onePerTag(f, 'Other'+tag+'/WC_dx_dy',tag)
    onePerTag(f, 'Other'+tag+'/WC_dx_dy_sig',tag)
    onePerTag(f, 'Timing'+tag+'/FrontToBackPadsDelay',tag)

    onePerTag(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoiseSiPad3_ch6',tag)
    onePerTag(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_nMIPSSiPad3_ch6',tag)

    # Sigma plots (without fits):
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_nMIPs',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoise',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X',tag)
    sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X_nMiPcut',tag)


    if 'GROUP_0' in tag:
      effPlot(f, tag)


  if not opt.mini:
    justPlotAll(f,'PER-RUN')

    runs = [SiPad_DATA['BeginRun'], SiPad_DATA['EndRun']]
    hPed = TH1F('Ped','Ped', runs[1]-runs[0], runs[0], runs[1])
    hPio = TH1F('Pio','Pio', runs[1]-runs[0], runs[0], runs[1])
    h300 = TH1F('300','300', runs[1]-runs[0], runs[0], runs[1])
    h200 = TH1F('200','200', runs[1]-runs[0], runs[0], runs[1])
    h120 = TH1F('120','120', runs[1]-runs[0], runs[0], runs[1])

    for i in TB_DATA:
      # print i
      if TB_DATA[str(i)]['ENERGY'] == 'ped':
        hPed.Fill(int(i),5000)
      elif TB_DATA[i]['BEAM'] == 'PION':
        hPio.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '300':
        h300.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '200':
        h200.Fill(int(i),5000)
      elif TB_DATA[i]['SENSOR'][1:] == '120':
        h120.Fill(int(i),5000)

    allPadsOnOnePlot(f,'PER-RUN'+'/Pedestal_PerRun','',           overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/PedestalRMS_PerRun','',        overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/Pedestal_PerRun_WithSig','',   overHists=[h300,h200,h120,hPed,hPio])
    allPadsOnOnePlot(f,'PER-RUN'+'/PedestalRMS_PerRun_WithSig','',overHists=[h300,h200,h120,hPed,hPio])


  elif opt.mini:

    # Here, store the graphs of the resolution vs radiation
    b = {}

    for tag in tags:
      print '\t -> Making plots for tag:', tag
      if 'GROUP_0_ELE_' not in tag: continue

      fs = []
      # This one includes systematics:
      if opt.syst:
        Month = 'fApr'
        if opt.june:
          Month = 'fJun'
        if opt.syst:
          #fs.append(TFile(Month+'_default.root','read'))
          fs.append(TFile(Month+'_1p5rms.root','read'))
          fs.append(TFile(Month+'_3rms.root',  'read'))
          fs.append(TFile(Month+'_Nev50.root', 'read'))
          #fs.append(TFile(Month+'_Nev300.root', 'read'))

      # sigmaPlots with fits:
      # sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_SigOverNoise',tag)
      #b[tag] = sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X',tag, fs, doSigmaFit=False)
      b[tag] = sigmaPlot(f, 'Timing'+tag+'/2D_Delay_from_Pad1_frac50_VS_sOvern_Pad1X',tag, fs, doSigmaFit=True)


    for tag in tags:

      if b[tag]==None: continue

      print '\t Fit results for tag:',tag
      #print 0, b[tag]
      #print 1, b[tag][1]
      #print 2, b[tag][2]
      #print 3, b[tag][3]

      for p in ['SiPad2','SiPad3','SiPad4','SiPad5','SiPad6']:
        try:
          print "%s, %.3f +/- %.3f \t %.3f +/- %.3f" % (p, b[tag][0][p], b[tag][1][p], b[tag][2][p], b[tag][3][p])
        except KeyError:
          print 'Key error exception for pad:', p

      isBadSet = ('N200' in tag and not opt.june)

      FluenceArr    = np.zeros(5,dtype = float)
      constTermsArr = np.zeros(5,dtype = float)
      constErrasArr = np.zeros(5,dtype = float)
      xArrZeros     = np.zeros(5,dtype = float)

      # Now, this strange constraction will get us the sensor type (P/N, thickness)
      # and obtaine the fluence number form the JSON data:
      ind = tag.find('SENSOR')
      T = tag[ind+7:ind+11]
      # print T[1:]

      # Here we try to get the per-Pad timing resolutions
      # For the non-irradiated Pads #1 and #2, we can just devide by sqrt(2) to get individual resolution
      # Setting number for SiPad1 and 2 (both non-radiated):
      if isBadSet:
        # Unfortunately the Pad2 of this set was broken. Hence just pick sensible number for this one:
        nonRad = 0.014
        constErrasArr[0] = 0.003
      else:
        nonRad = b[tag][2]['SiPad2']/sqrt(2)
        constErrasArr[0] = b[tag][3]['SiPad2']/sqrt(2)

      constTermsArr[0] = nonRad
      FluenceArr[0] = 0

      for i,p in enumerate(['SiPad3','SiPad4','SiPad5','SiPad6']):

        # Get fluences from the JSON:
        FluenceArr[i+1] = 1E-15*SiPad_DATA['fluence'][SiPad_DATA['SetsMap2'][T[1:]+'um']][p]

        # For the radiated pads we must factor out the resolution of Pad1:
        try:
          constTermsArr[i+1] = sqrt(b[tag][2][p]**2 - nonRad**2)
        except:
          print "\t WARNING: It is negative under the root!", p
          constTermsArr[i+1] = b[tag][2][p]/sqrt(2)

        # Propagate errors:
        S1 = b[tag][2][p]  # Total (convoluted) value
        S2 = nonRad        # Resolution of non-radiated diode
        S1_er = b[tag][3][p]
        S2_er = constErrasArr[0]
        # Error on deconvoluted value of the radiated diode resolution:
        constErrasArr[i+1] = (1./constTermsArr[i+1])*sqrt( (S1*S1_er)**2 + (S2*S2_er)**2)

        if opt.verb:
          print i,p, "%.1f+/-%.1f  %.1f+/-%.1f" %(1000*S1, 1000*S1_er, 1000*S2, 1000*S2_er)
          print "Calc:", "%.1f+/-%.1f" % (1000*constTermsArr[i+1], 1000*constErrasArr[i+1])
                  
      # Get the results in picoseconds:
      constTermsArr = constTermsArr*1000
      constErrasArr = constErrasArr*1000

      if opt.verb:
        print constTermsArr 
        print constErrasArr
          
      g = TGraphErrors(5, FluenceArr, constTermsArr, xArrZeros, constErrasArr)

      out.cd()
      g.Write('Sigma'+tag)
