#define smallAna_cxx

#include "smallAna.h"
#include <TH2.h>
#include <TStyle.h>
#include <iostream>
#include <TFile.h>
#include <TProofOutputFile.h>

void smallAna::Begin(TTree * /*tree*/)
{
   TString option = GetOption();


}

void smallAna::SlaveBegin(TTree * /*tree*/)
{
   TString option = GetOption();
   cout<<"Options are: \n \t "<<option.Data()<<endl;

   TObjArray *args = (TObjArray*)option.Tokenize(" ");
   _cut_gamma_pt  = std::stod((string)((TObjString*)args->At(0))->GetString());
   _cut_gamma_eta = std::stod((string)((TObjString*)args->At(1))->GetString());
   _cut_lep1_pt = std::stod((string)((TObjString*)args->At(2))->GetString());
   _cut_lep2_pt = std::stod((string)((TObjString*)args->At(3))->GetString());
   
   //histoFile = new TFile("my_higgsHistograms.root", "RECREATE");
   //fOutput->Add(histoFile);
   fProofFile = new TProofOutputFile("my_higgsHistograms.root");
   fOutput->Add(fProofFile);
   // Open the file
   histoFile = fProofFile->OpenFile("RECREATE");

   hists    = new HistManager(histoFile);
   for (size_t n=0; n<nC; n++) nEvents[n]=0;

   h1 = new TH1F("evt","evt", 20, 1, 21);
}

Bool_t smallAna::Process(Long64_t entry)
{
  GetEntry(entry);

  nEvents[0]++;
  h1->Fill(0);

  //if (nEvents[0]%10000 == 0){
  //Info("PROC", "Lpt pt = %.2f", lep1->Pt());

  //std::cout<<"lep1 pt = "<<lep1->Pt()<<std::endl;
  //std::cout<<"\t lep2 pt = "<<lep2->Pt()<<std::endl;
  //std::cout<<"\t\t gamma pt = "<<gamma->Pt()<<std::endl;
  //}

  //makeHists("Init", *lep1, *lep2, *gamma);
  //makeHists("Init");

  if (lep1->Pt() < _cut_lep1_pt) return kTRUE; // Original cut is 23
  if (lep2->Pt() < _cut_lep2_pt) return kTRUE; // Original cut is 4
  if (gamma->Pt() < _cut_gamma_pt) return kTRUE; // Original cut is 25
  if (abs(gamma->Eta()) > _cut_gamma_eta) return kTRUE; // Original cut is 1.4442
  //if (Mtri<110 || Mtri>170) return kTRUE;
  if (lep1->DeltaR(*gamma)<1 || lep2->DeltaR(*gamma)<1) return kTRUE; // Original cut is 1.0

  //hists->fill1DHist(lep1->Pt(), "lep1_pt_test",";p_T(l1)",  100, 0,100, 1,"DIR");

  if (!trig1) return kTRUE;

  h1->Fill(1);

  nEvents[1]++;
  makeHists("AfterCuts");

  Float_t mll  = (*lep1+*lep2).M();
  Float_t mllg = (*lep1+*lep2+*gamma).M();
  if (mll>3.0 && mll<3.2) {
    nEvents[2]++;
    makeHists("InJpsi");
    h1->Fill(2);
  }

  if (mll>=2.76 && mll<=2.85) {
    nEvents[3]++;
    makeHists("InAPZ");
    h1->Fill(3);
  }

  if (  ( mll>2.70 && mll<2.76) || (mll>2.85 && mll<2.9 ) ) {
    nEvents[4]++;
    makeHists("InSideBand");
    h1->Fill(4);
  }

  const Float_t Mllg = (*lep1+*lep2+*gamma).M();

  //if ( gamma->Pt()/Mllg > 0.35 && (*lep1+*lep2).Pt()/Mllg > 0.35
  //   && Mllg>100 && Mllg<150) { // Optimal?
  if ( gamma->Pt()/Mllg > 0.3 && (*lep1+*lep2).Pt()/Mllg > 0.30
       && Mllg>110 && Mllg<170) { // PAS
    nEvents[5]++;
    makeHists("M18");
    h1->Fill(5);
  }
  
  h1->Fill(6);

  return kTRUE;
}

void smallAna::makeHists(string tag){
  //void smallAna::makeHists(string tag, const TLorentzVector& l1, const TLorentzVector& l2, const TLorentzVector& g){
  const TLorentzVector diLep = (*lep1+*lep2);
  const TLorentzVector tri   = (*lep1+*lep2+*gamma);
  const Float_t Mll  = diLep.M();
  const Float_t Mjj = (*jet1+*jet2).M();
  const Float_t Mllg = tri.M();
  const Float_t Mllgj = (*lep1+*lep2+*gamma+*jet1).M();
  const Float_t Mgj = (*gamma+*jet1).M();

  //const TVector2 diLep2(diLep.X(), diLep.Y());
  //const TVector2 gamma2(gamma->X(), gamma->Y());
  
  hists->fill1DHist(lep1->Pt(), "lep1_pt_"+tag,";p_{T}(l1)",  60, 20,80, 1,tag);
  hists->fill1DHist(lep2->Pt(), "lep2_pt_"+tag,";p_{T}(l2)",  50, 0,50, 1,tag);
  hists->fill1DHist(gamma->Pt(),"gamma_pt_"+tag,";p_{T}(#gamma)",  100, 20,100, 1,tag);


  hists->fill1DHist(lep1->Phi(), "lep1_phi_"+tag,";#phi(l1)",  50, -3.2, 3.2, 1,tag);
  hists->fill1DHist(lep2->Phi(), "lep2_phi_"+tag,";#phi(l2)",  50, -3.2, 3.2, 1,tag);
  hists->fill1DHist(gamma->Phi(), "gamma_phi_"+tag,";#phi(#gamma)",  50, -3.2, 3.2, 1,tag);


  hists->fill1DHist(lep1->Eta(), "lep1_eta_"+tag,";#eta(l1)",  50, -2.4,2.4, 1,tag);
  hists->fill1DHist(lep2->Eta(), "lep2_eta_"+tag,";#eta(l2)",  50, -2.4,2.4, 1,tag);
  hists->fill1DHist(gamma->Eta(), "gamma_eta_"+tag,";#eta(#gamma)", 50, -2.4,2.4, 1,tag);


  hists->fill1DHist(Mll, "Mll_50_"+tag,";m_{#mu#mu}",  100, 0,50, 1,tag);
  hists->fill1DHist(Mll, "Mll_20_"+tag,";m_{#mu#mu}",  100, 0,20, 1,tag);
  hists->fill1DHist(Mll, "Mll_20_to_50_"+tag,";m_{#mu#mu}", 50, 20,50, 1,tag);
  hists->fill1DHist(Mll, "Mll_18_"+tag,";m_{#mu#mu}",  50, 10,30, 1,tag);
  hists->fill1DHist(Mll, "Mll_Ups_"+tag,";m_{#mu#mu}", 60, 9,12, 1,tag);
  hists->fill1DHist(Mll, "Mll_JPsi_"+tag,";m_{#mu#mu}",  50, 2,4, 1,tag);
  hists->fill1DHist(Mll, "Mll_APZ_JPsi_"+tag,";m_{#mu#mu}", 70, 2.7, 3.4, 1,tag);
  hists->fill1DHist(Mll, "Mll_APZ_"+tag,";m_{#mu#mu}",  30, 2.7,3.0, 1,tag);

  hists->fill1DHist(Mllg, "Mllg_full_"+tag,";m_{#mu#mu#gamma}",  100, 0,300,   1,tag);
  hists->fill1DHist(Mllg, "Mllg_higg_"+tag,";m_{#mu#mu#gamma}",  50, 100,150, 1,tag);
  hists->fill1DHist(Mllg, "Mllg_zed_"+tag,";m_{#mu#mu#gamma}",   40, 50,90, 1,tag);


  hists->fill1DHist(lep1->DeltaR(*lep2), "dR_lep_"+tag,";#DeltaR(l1,l2)",  100, 0,1.5, 1,tag);
  hists->fill1DHist(gamma->DeltaR(*lep1+*lep2), "dR_gamma_dilep_"+tag,";#DeltaR(#gamma,#mu#mu)",  50, 1, 4.5, 1,tag);

  hists->fill1DHist(diLep.Pt()/gamma->Pt(),"pt_ratio_dilep_gamma_"+tag,";p_{T}(#mu#mu)/p_{T}(#gamma)",  50, 0,2, 1,tag);

  hists->fill1DHist(met->Pt(), "met_Et_"+tag,";MET", 50, 0, 100, 1,tag);
  hists->fill1DHist(met->Phi(), "met_phi_"+tag,";#phi(MET)",  50, -3.2, 3.2, 1,tag);
  hists->fill1DHist(met->DeltaPhi(diLep), "met_dPhi_dilep_"+tag,";#Delta#phi(MET,#mu#mu)",  50, 0, 3.2, 1,tag);
  hists->fill1DHist(met->DeltaPhi(*gamma), "met_dPhi_gamma_"+tag,";#Delta#phi(MET,#gamma)",  50, 0, 3.2, 1,tag);

  if (jet1->Pt()>0){
    hists->fill1DHist(jet1->Pt(),  "jet1_pt_"+tag, ";p_{T}(j1)", 50, 20, 120, 1,tag);
    hists->fill1DHist(jet1->Eta(), "jet1_eta_"+tag,";#eta(j1)",  50, -2.4, 2.4, 1,tag);
    hists->fill1DHist(jet1->Phi(), "jet1_phi_"+tag,";#phi(j1)",  50, -3.2, 3.2, 1,tag);

    hists->fill1DHist(Mllgj, "Mllgj_full_"+tag,";m_{#mu#mu#gammaj}",  100, 50,500,   1,tag);
    hists->fill1DHist(Mllgj, "Mllgj_higg_"+tag,";m_{#mu#mu#gammaj}",  20, 100,200, 1,tag);
    hists->fill1DHist(Mllgj, "Mllgj_x200_"+tag,";m_{#mu#mu#gammaj}",  25, 180,230, 1,tag);

    hists->fill1DHist(Mgj, "Mgj_full_"+tag,";m_{#gammaj}",  50, 0,500, 1,tag);
    hists->fill1DHist(Mgj, "Mgj_higg_"+tag,";m_{#gammaj}",  50, 100,200, 1,tag);

    hists->fill1DHist(gamma->DeltaR(*jet1), "dR_gamma_jet1_"+tag,";#DeltaR(#gamma,jet1)",  50, 0,5, 1,tag);
  
    if (jet2->Pt()>0){
      hists->fill1DHist(jet2->Pt(),  "jet2_pt_"+tag, ";p_{T}(j2)", 50, 20, 100, 1,tag);
      hists->fill1DHist(jet2->Eta(), "jet2_eta_"+tag,";#eta(j2)",  50, -2.4, 2.4, 1,tag);
      hists->fill1DHist(jet2->Phi(), "jet2_phi_"+tag,";#phi(j2)",  50, -3.2, 3.2, 1,tag);
      
      hists->fill1DHist(Mjj, "Mjj_full_"+tag,";m_{jj}",  50, 0, 600, 1,tag);
      hists->fill1DHist(Mjj, "Mjj_zoom_"+tag,";m_{jj}",  50, 100, 400, 1,tag);

      hists->fill1DHist(gamma->DeltaR(*jet2), "dR_gamma_jet2_"+tag,";#DeltaR(#gamma,jet2)",  50, 0,5, 1,tag);

      hists->fill1DHist(jet1->DeltaR(*jet2), "dRjj_"+tag,";#DeltaR(jj)",  50, 0,5, 1,tag);
    }
  }

}

void smallAna::SlaveTerminate()
{
  histoFile->cd();
  histoFile->Write();
  histoFile->Close();
      
  cout<<" ** Slave is terminating, my master ...bow x3... **"<<endl;

}

void smallAna::Terminate()
{
  cout<<" ** End of Analyzer **"<<endl;
}
