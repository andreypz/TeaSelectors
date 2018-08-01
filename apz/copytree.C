void copytree() {
  
  //Get old file, old tree and set top branch address
  //TFile *oldfile = new TFile("APZ-tree-Data-8TeV-Oct27.root");
  TFile *oldfile = new TFile("APZ-tree-Data-MuEG-8TeV-2018July25.root");
  TTree *oldtree = (TTree*)oldfile->Get("apzTree/apzTree");
  //TLorentzVector *lep1   = new TLorentzVector();
  //oldtree->SetBranchAddress("lep1",&lep1);
  oldtree->SetBranchStatus("*",0);
  oldtree->SetBranchStatus("lep1",1);
  oldtree->SetBranchStatus("lep2",1);
  oldtree->SetBranchStatus("gamma",1);
  oldtree->SetBranchStatus("jet1",1);
  oldtree->SetBranchStatus("jet2",1);
  oldtree->SetBranchStatus("met",1);
  oldtree->SetBranchStatus("run",1);
  oldtree->SetBranchStatus("event",1);
  
  //Create a new file + a clone of old tree in new file
  TFile *newfile = new TFile("xsmall.root","recreate");
  TTree *newtree = oldtree->CloneTree();
  
  newtree->Print();
  newfile->Write();
  delete oldfile;
  delete newfile;
}
