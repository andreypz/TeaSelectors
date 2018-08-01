#ifndef smallAna_h
#define smallAna_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <TH1F.h>
// Header file for the classes stored in the TTree if any.
#include "TLorentzVector.h"

#include "HistManager.h"

#define nC 5
class TFile;
class TProofOutputFile;

class smallAna : public TSelector {
 private:

  TFile* histoFile;
  //TFile            *fFile;
  TProofOutputFile *fProofFile; // For optimized merging of the ntuple
  HistManager *hists;
  TH1F* h1;
  UInt_t nEvents[nC];
  UInt_t totEvents;

  Float_t _cut_gamma_pt, _cut_gamma_eta, _cut_lep1_pt, _cut_lep2_pt;

 public :
  TTree          *fChain;   //!pointer to the analyzed TTree or TChain

  // Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   TLorentzVector  *lep1;
   TLorentzVector  *lep2;
   TLorentzVector  *gamma;
   TLorentzVector  *jet1;
   TLorentzVector  *jet2;
   TLorentzVector  *met;
   UInt_t          run;
   ULong64_t       event;

   // List of branches
   TBranch        *b_lep1;   //!
   TBranch        *b_lep2;   //!
   TBranch        *b_gamma;   //!
   TBranch        *b_jet1;   //!
   TBranch        *b_jet2;   //!
   TBranch        *b_met;   //!
   TBranch        *b_run;   //!
   TBranch        *b_event;   //!

 smallAna(TTree * /*tree*/ =0) : fChain(0), fProofFile(0) { }
   virtual ~smallAna() { }
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


   virtual void makeHists(string );

   ClassDef(smallAna,0);
};

#endif

#ifdef smallAna_cxx
void smallAna::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   lep1 = 0;
   lep2 = 0;
   gamma = 0;
   jet1 = 0;
   jet2 = 0;
   met = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("lep1", &lep1, &b_lep1);
   fChain->SetBranchAddress("lep2", &lep2, &b_lep2);
   fChain->SetBranchAddress("gamma", &gamma, &b_gamma);
   fChain->SetBranchAddress("jet1", &jet1, &b_jet1);
   fChain->SetBranchAddress("jet2", &jet2, &b_jet2);
   fChain->SetBranchAddress("met", &met, &b_met);
   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("event", &event, &b_event);
}

Bool_t smallAna::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

#endif // #ifdef smallAna_cxx
