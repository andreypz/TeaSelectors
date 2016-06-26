#!/usr/bin/env python

import csv, json


import argparse
parser =  argparse.ArgumentParser(description='Making json file', usage="./makeJson.py [--tb apr,june]")
parser.add_argument("--tb", dest="tb", default='apr',  choices=['apr', 'june', 'april'], help="Pick which data to run ober")

opt = parser.parse_args()  

TB_RUNS = {}

if opt.tb in ['apr','april']:
  csvInput = 'H2_HGCAL_April2016_Run_Info.csv'
  spamReader = csv.reader(open(csvInput, 'rb'), delimiter=',', skipinitialspace=True)
  for row in spamReader:
    # print row
    if row[5] in ['RUN','']:
      continue
  
    RUN = int(row[5])
      
    if RUN>=3700 and RUN<=3778:
      BEAM = "ELE"
    else:
      BEAM = "PION"
    if row[0]=='ped':
      BEAM="NOBEAM"
  
    DiodeType = 'N'
    
    TB_RUNS[str(RUN)] = {'BEAM':BEAM, 'ENERGY':row[0], 'SENSOR':DiodeType+row[1], 'HV1':row[2], 'HV2':row[3]}
  

elif opt.tb in ['june']:
  csvInput = 'H2_HGCAL_June2016_Run_Info.csv'
  
  spamReader = csv.reader(open(csvInput, 'rb'), delimiter=',', skipinitialspace=True)
  for row in spamReader:
    #print row[6]
  
    RUN = int(row[6])
      
    if row[3] =='Electrons':
      BEAM = "ELE"
      EN='100'
    else:
      BEAM = "PION"
      EN='150'
  
    DiodeType = 'P'

      
    hv1 = 600
    hv2 = 800
    TB_RUNS[str(RUN)] = {'BEAM':BEAM, 'ENERGY':EN, 'SENSOR':DiodeType+row[5], 'HV1':hv1, 'HV2':hv2}
  
with open('jj.json', 'w') as fp:
  json.dump(TB_RUNS, fp, sort_keys=True, indent=4)

