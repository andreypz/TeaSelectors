#!/usr/bin/env python

# This script will take the TGraphs from the input files and plot them

import argparse
parser =  argparse.ArgumentParser(description='Ploting my plots', usage="./resPlot --fP f1.root --fN f2.root")
parser.add_argument("--fApr",  dest="fApr", type=str, default='fApr.root', help='there is no help')
parser.add_argument("--fJun",  dest="fJun", type=str, default='fJun.root', help='there is no help')
parser.add_argument("--log",  dest="log", action="store_true", default=False , help='Do logX')


opt = parser.parse_args()

from ROOT import *
gROOT.SetBatch()
gROOT.ProcessLine(".L ../sugar-n-milk/tdrstyle.C")
setTDRStyle()
gROOT.ForceStyle()


fApr = TFile(opt.fApr, 'open')
fJun = TFile(opt.fJun, 'open')

# There were two HV setting in the April's data: 600 and 800 V
HV_Apr='800'
g120N = fApr.Get('_GROUP_0_ELE_SENSOR_N120_irrHV_'+HV_Apr)
g200N = fApr.Get('_GROUP_0_ELE_SENSOR_N200_irrHV_'+HV_Apr)
g300N = fApr.Get('_GROUP_0_ELE_SENSOR_N300_irrHV_'+HV_Apr)

g120N.SetMarkerStyle(20)
g120N.SetMarkerColor(kRed+1)
g120N.SetLineStyle(2)
g200N.SetMarkerStyle(21)
g200N.SetMarkerColor(kRed)
g200N.SetLineStyle(3)
g300N.SetMarkerStyle(22)
g300N.SetMarkerColor(kRed+3)
g300N.SetLineStyle(4)

g120P = fJun.Get('_GROUP_0_ELE_SENSOR_P120_irrHV_800')
g200P = fJun.Get('_GROUP_0_ELE_SENSOR_P200_irrHV_800')
g300P = fJun.Get('_GROUP_0_ELE_SENSOR_P300_irrHV_800')

g120P.SetMarkerStyle(20)
g120P.SetMarkerColor(kBlue+1)
g120P.SetLineStyle(2)
g200P.SetMarkerStyle(21)
g200P.SetMarkerColor(kBlue)
g200P.SetLineStyle(3)
g300P.SetMarkerStyle(22)
g300P.SetMarkerColor(kBlue+3)
g300P.SetLineStyle(4)

c1 = TCanvas("c1","small canvas",600,600);
mg = TMultiGraph()
mg.SetTitle('')

drawOpt = 'PL E1'
#if opt.log: 
#    drawOpt = 'P E1'
mg.Add(g120N,drawOpt)
mg.Add(g200N,drawOpt)
mg.Add(g300N,drawOpt)
mg.Add(g120P,drawOpt)
mg.Add(g200P,drawOpt)
mg.Add(g300P,drawOpt)

mg.SetMinimum(0)
mg.SetMaximum(210)

if opt.log:
    lines = []
    for g in mg.GetListOfGraphs():
        x0,y0,x1,y1,x4,y4 = Double(0), Double(0), Double(0), Double(0), Double(0), Double(0)
        g.GetPoint(0,x0,y0)
        g.GetPoint(1,x1,y1)
        g.GetPoint(4,x4,y4)
        lines.append(TLine(x1, y0, x4, y0))
        lines[-1].SetLineColor(g.GetMarkerColor())
        lines[-1].SetLineWidth(2)
        lines[-1].SetLineStyle(9)
        g.RemovePoint(0)
        c1.SetLogx()
        #print g.GetName()
        #g.Print()
      
mg.Draw('A')
mg.GetXaxis().SetTitle('Radiation, n/cm^{2} #times 10^{15}')
mg.GetYaxis().SetTitle('Time resolution, ps')

if opt.log:
    for l in lines:
        l.Draw()

leg = TLegend(0.30,0.68,0.55,0.88)
leg.SetNColumns(2)
leg.AddEntry(g120N, 'N120', 'PL')
leg.AddEntry(g120P, 'P120', 'PL')
leg.AddEntry(g200N, 'N200', 'PL')
leg.AddEntry(g200P, 'P200', 'PL')
leg.AddEntry(g300N, 'N300', 'PL')
leg.AddEntry(g300P, 'P300', 'PL')
leg.SetTextFont(42)
leg.SetTextSize(0.04)
leg.SetFillColor(kWhite)
leg.Draw()

c1.SaveAs('graph.png')
