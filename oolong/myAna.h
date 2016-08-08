//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Thu Jun  9 12:00:39 2016 by ROOT version 6.02/13
// from TTree H4treeReco/H4treeReco
// found on file: RECO_3777.root
//////////////////////////////////////////////////////////

#ifndef myAna_h
#define myAna_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TProofOutputFile.h>

#include <stdlib.h>
#include <iostream>
#include "HistManager.h"

#define nC 8


class myAna : public TSelector {

 private:
  UInt_t nEvents[7][nC];
  //map<UInt_t, string> nEvents[nC];

  TProofOutputFile *fProofFile; // For optimized merging of the ntuple

  TFile* histoFile;
  HistManager *hists;


  Char_t TB = 0;
  map<string, UInt_t> PadsMap1;
  map<UInt_t, string> PadsMap2;
  
  UInt_t ped_offset;
  Float_t trig_offset;
  Float_t wc_cut_x[4];
  Float_t wc_cut_y[4];
  UInt_t runs[2];
  map<UInt_t, Float_t> ADCperMIP;

 public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   UInt_t          runNumber;
   UInt_t          spillNumber;
   UInt_t          evtNumber;
   UInt_t          evtTimeDist;
   UInt_t          evtTimeStart;
   UInt_t          nEvtTimes;
   UInt_t          nwc;
   Float_t         wc_recox[2];   //[nwc]
   Float_t         wc_recoy[2];   //[nwc]
   //UInt_t          wc_xl_hits[2];   //[nwc]
   //UInt_t          wc_xr_hits[2];   //[nwc]
   //UInt_t          wc_yu_hits[2];   //[nwc]
   //UInt_t          wc_yd_hits[2];   //[nwc]
   UInt_t          maxch;
   //Float_t         group[7];   //[maxch]
   Float_t         ch[7];   //[maxch]
   Float_t         pedestal[7];   //[maxch]
   Float_t         pedestalRMS[7];   //[maxch]
   //Float_t         pedestalSlope[7];   //[maxch]
   Float_t         wave_max[7];   //[maxch]
   //Float_t         wave_max_aft[7];   //[maxch]
   //Float_t         wave_aroundPed[7][50];   //[maxch]
   //Float_t         time_aroundPed[7][50];   //[maxch]
   Float_t         wave_aroundmax[7][50];   //[maxch]
   Float_t         time_aroundmax[7][50];   //[maxch]
   /*
   Float_t         wave_fit_templ_ampl[7];   //[maxch]
   Float_t         wave_fit_templ_amplerr[7];   //[maxch]
   Float_t         wave_fit_templ_chi2[7];   //[maxch]
   Float_t         wave_fit_templ_ndof[7];   //[maxch]
   Float_t         wave_fit_templ_status[7];   //[maxch]
   Float_t         wave_fit_templ_time[7];   //[maxch]
   Float_t         wave_fit_templ_timeerr[7];   //[maxch]
   Float_t         wave_fit_smallw_ampl[7];   //[maxch]
   Float_t         wave_fit_smallw_amplerr[7];   //[maxch]
   Float_t         wave_fit_smallw_chi2[7];   //[maxch]
   Float_t         wave_fit_smallw_ndof[7];   //[maxch]
   Float_t         wave_fit_largew_ampl[7];   //[maxch]
   Float_t         wave_fit_largew_amplerr[7];   //[maxch]
   Float_t         wave_fit_largew_chi2[7];   //[maxch]
   Float_t         wave_fit_largew_ndof[7];   //[maxch]
   */
   Float_t         charge_integ[7];   //[maxch]
   Float_t         charge_integ_max[7];   //[maxch]
   Float_t         charge_integ_fix[7];   //[maxch]
   /*
   Float_t         charge_integ_smallw[7];   //[maxch]
   Float_t         charge_integ_largew[7];   //[maxch]
   Float_t         charge_integ_smallw_mcp[7];   //[maxch]
   Float_t         charge_integ_largew_mcp[7];   //[maxch]
   Float_t         charge_integ_smallw_noise[7];   //[maxch]
   Float_t         charge_integ_largew_noise[7];   //[maxch]
   Float_t         charge_integ_smallw_rnd[7];   //[maxch]
   Float_t         charge_integ_largew_rnd[7];   //[maxch]
   */
   Float_t         t_max[7];   //[maxch]
   Float_t         t_max_frac30[7];   //[maxch]
   Float_t         t_max_frac50[7];   //[maxch]
   Float_t         t_max_frac10[7];   //[maxch]
   Float_t         t_max_frac90[7];   //[maxch]
   Float_t         t_at_threshold[7];   //[maxch]
   Float_t         t_over_threshold[7];   //[maxch]
   Float_t         t_over_thresholdfrac50[7];   //[maxch]
   
   // List of branches
   TBranch        *b_runNumber;   //!
   TBranch        *b_spillNumber;   //!
   TBranch        *b_evtNumber;   //!
   TBranch        *b_evtTimeDist;   //!
   TBranch        *b_evtTimeStart;   //!
   TBranch        *b_nEvtTimes;   //!
   TBranch        *b_nwc;   //!
   TBranch        *b_wc_recox;   //!
   TBranch        *b_wc_recoy;   //!
   //TBranch        *b_wc_xl_hits;   //!
   //TBranch        *b_wc_xr_hits;   //!
   //TBranch        *b_wc_yu_hits;   //!
   // TBranch        *b_wc_yd_hits;   //!
   TBranch        *b_maxch;   //!
   //TBranch        *b_group;   //!
   TBranch        *b_ch;   //!
   TBranch        *b_pedestal;   //!
   TBranch        *b_pedestalRMS;   //!
   //TBranch        *b_pedestalSlope;   //!
   TBranch        *b_wave_max;   //!
   //TBranch        *b_wave_max_aft;   //!
   //TBranch        *b_wave_aroundPed;   //!
   //TBranch        *b_time_aroundPed;   //!
   TBranch        *b_wave_aroundmax;   //!
   TBranch        *b_time_aroundmax;   //!
   /*
   TBranch        *b_wave_fit_templ_ampl;   //!
   TBranch        *b_wave_fit_templ_amplerr;   //!
   TBranch        *b_wave_fit_templ_chi2;   //!
   TBranch        *b_wave_fit_templ_ndof;   //!
   TBranch        *b_wave_fit_templ_status;   //!
   TBranch        *b_wave_fit_templ_time;   //!
   TBranch        *b_wave_fit_templ_timeerr;   //!
   TBranch        *b_wave_fit_smallw_ampl;   //!
   TBranch        *b_wave_fit_smallw_amplerr;   //!
   TBranch        *b_wave_fit_smallw_chi2;   //!
   TBranch        *b_wave_fit_smallw_ndof;   //!
   TBranch        *b_wave_fit_largew_ampl;   //!
   TBranch        *b_wave_fit_largew_amplerr;   //!
   TBranch        *b_wave_fit_largew_chi2;   //!
   TBranch        *b_wave_fit_largew_ndof;   //!
   */
   TBranch        *b_charge_integ;   //!
   TBranch        *b_charge_integ_max;   //!
   TBranch        *b_charge_integ_fix;   //!
   /*
   TBranch        *b_charge_integ_smallw;   //!
   TBranch        *b_charge_integ_largew;   //!
   TBranch        *b_charge_integ_smallw_mcp;   //!
   TBranch        *b_charge_integ_largew_mcp;   //!
   TBranch        *b_charge_integ_smallw_noise;   //!
   TBranch        *b_charge_integ_largew_noise;   //!
   TBranch        *b_charge_integ_smallw_rnd;   //!
   TBranch        *b_charge_integ_largew_rnd;   //!
   */
   TBranch        *b_t_max;   //!
   TBranch        *b_t_max_frac30;   //!
   TBranch        *b_t_max_frac50;   //!
   TBranch        *b_t_max_frac10;   //!
   TBranch        *b_t_max_frac90;   //!
   TBranch        *b_t_at_threshold;   //!
   TBranch        *b_t_over_threshold;   //!
   TBranch        *b_t_over_thresholdfrac50;   //!
   
 myAna(TTree * /*tree*/ =0) : fChain(0), fProofFile(0) { }
   virtual ~myAna() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   void FillHistoCounts(UInt_t num, string suff, string tag);

   ClassDef(myAna,0);
};

#endif

#ifdef myAna_cxx
void myAna::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("runNumber", &runNumber, &b_runNumber);
   fChain->SetBranchAddress("spillNumber", &spillNumber, &b_spillNumber);
   fChain->SetBranchAddress("evtNumber", &evtNumber, &b_evtNumber);
   fChain->SetBranchAddress("evtTimeDist", &evtTimeDist, &b_evtTimeDist);
   fChain->SetBranchAddress("evtTimeStart", &evtTimeStart, &b_evtTimeStart);
   fChain->SetBranchAddress("nEvtTimes", &nEvtTimes, &b_nEvtTimes);
   fChain->SetBranchAddress("nwc", &nwc, &b_nwc);
   fChain->SetBranchAddress("wc_recox", wc_recox, &b_wc_recox);
   fChain->SetBranchAddress("wc_recoy", wc_recoy, &b_wc_recoy);
   //fChain->SetBranchAddress("wc_xl_hits", wc_xl_hits, &b_wc_xl_hits);
   //fChain->SetBranchAddress("wc_xr_hits", wc_xr_hits, &b_wc_xr_hits);
   //fChain->SetBranchAddress("wc_yu_hits", wc_yu_hits, &b_wc_yu_hits);
   //fChain->SetBranchAddress("wc_yd_hits", wc_yd_hits, &b_wc_yd_hits);
   fChain->SetBranchAddress("maxch", &maxch, &b_maxch);
   //fChain->SetBranchAddress("group", group, &b_group);
   fChain->SetBranchAddress("ch", ch, &b_ch);
   fChain->SetBranchAddress("pedestal", pedestal, &b_pedestal);
   fChain->SetBranchAddress("pedestalRMS", pedestalRMS, &b_pedestalRMS);
   //fChain->SetBranchAddress("pedestalSlope", pedestalSlope, &b_pedestalSlope);
   fChain->SetBranchAddress("wave_max", wave_max, &b_wave_max);
   //fChain->SetBranchAddress("wave_max_aft", wave_max_aft, &b_wave_max_aft);
   //fChain->SetBranchAddress("wave_aroundPed", wave_aroundPed, &b_wave_aroundPed);
   //fChain->SetBranchAddress("time_aroundPed", time_aroundPed, &b_time_aroundPed);
   fChain->SetBranchAddress("wave_aroundmax", wave_aroundmax, &b_wave_aroundmax);
   fChain->SetBranchAddress("time_aroundmax", time_aroundmax, &b_time_aroundmax);
   /*
   fChain->SetBranchAddress("wave_fit_templ_ampl", wave_fit_templ_ampl, &b_wave_fit_templ_ampl);
   fChain->SetBranchAddress("wave_fit_templ_amplerr", wave_fit_templ_amplerr, &b_wave_fit_templ_amplerr);
   fChain->SetBranchAddress("wave_fit_templ_chi2", wave_fit_templ_chi2, &b_wave_fit_templ_chi2);
   fChain->SetBranchAddress("wave_fit_templ_ndof", wave_fit_templ_ndof, &b_wave_fit_templ_ndof);
   fChain->SetBranchAddress("wave_fit_templ_status", wave_fit_templ_status, &b_wave_fit_templ_status);
   fChain->SetBranchAddress("wave_fit_templ_time", wave_fit_templ_time, &b_wave_fit_templ_time);
   fChain->SetBranchAddress("wave_fit_templ_timeerr", wave_fit_templ_timeerr, &b_wave_fit_templ_timeerr);
   fChain->SetBranchAddress("wave_fit_smallw_ampl", wave_fit_smallw_ampl, &b_wave_fit_smallw_ampl);
   fChain->SetBranchAddress("wave_fit_smallw_amplerr", wave_fit_smallw_amplerr, &b_wave_fit_smallw_amplerr);
   fChain->SetBranchAddress("wave_fit_smallw_chi2", wave_fit_smallw_chi2, &b_wave_fit_smallw_chi2);
   fChain->SetBranchAddress("wave_fit_smallw_ndof", wave_fit_smallw_ndof, &b_wave_fit_smallw_ndof);
   fChain->SetBranchAddress("wave_fit_largew_ampl", wave_fit_largew_ampl, &b_wave_fit_largew_ampl);
   fChain->SetBranchAddress("wave_fit_largew_amplerr", wave_fit_largew_amplerr, &b_wave_fit_largew_amplerr);
   fChain->SetBranchAddress("wave_fit_largew_chi2", wave_fit_largew_chi2, &b_wave_fit_largew_chi2);
   fChain->SetBranchAddress("wave_fit_largew_ndof", wave_fit_largew_ndof, &b_wave_fit_largew_ndof);
   */
   fChain->SetBranchAddress("charge_integ", charge_integ, &b_charge_integ);
   fChain->SetBranchAddress("charge_integ_max", charge_integ_max, &b_charge_integ_max);
   fChain->SetBranchAddress("charge_integ_fix", charge_integ_fix, &b_charge_integ_fix);
   /*
   fChain->SetBranchAddress("charge_integ_smallw", charge_integ_smallw, &b_charge_integ_smallw);
   fChain->SetBranchAddress("charge_integ_largew", charge_integ_largew, &b_charge_integ_largew);
   fChain->SetBranchAddress("charge_integ_smallw_mcp", charge_integ_smallw_mcp, &b_charge_integ_smallw_mcp);
   fChain->SetBranchAddress("charge_integ_largew_mcp", charge_integ_largew_mcp, &b_charge_integ_largew_mcp);
   fChain->SetBranchAddress("charge_integ_smallw_noise", charge_integ_smallw_noise, &b_charge_integ_smallw_noise);
   fChain->SetBranchAddress("charge_integ_largew_noise", charge_integ_largew_noise, &b_charge_integ_largew_noise);
   fChain->SetBranchAddress("charge_integ_smallw_rnd", charge_integ_smallw_rnd, &b_charge_integ_smallw_rnd);
   fChain->SetBranchAddress("charge_integ_largew_rnd", charge_integ_largew_rnd, &b_charge_integ_largew_rnd);
   */
   fChain->SetBranchAddress("t_max", t_max, &b_t_max);
   fChain->SetBranchAddress("t_max_frac30", t_max_frac30, &b_t_max_frac30);
   fChain->SetBranchAddress("t_max_frac50", t_max_frac50, &b_t_max_frac50);
   fChain->SetBranchAddress("t_max_frac10", t_max_frac10, &b_t_max_frac10);
   fChain->SetBranchAddress("t_max_frac90", t_max_frac90, &b_t_max_frac90);
   fChain->SetBranchAddress("t_at_threshold", t_at_threshold, &b_t_at_threshold);
   fChain->SetBranchAddress("t_over_threshold", t_over_threshold, &b_t_over_threshold);
   fChain->SetBranchAddress("t_over_thresholdfrac50", t_over_thresholdfrac50, &b_t_over_thresholdfrac50);
}

Bool_t myAna::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

#endif // #ifdef myAna_cxx
