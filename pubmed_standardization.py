import sys
import os
import pandas
from datetime import datetime
import argparse
import gzip
import xml.etree.ElementTree as ET
import json
import xmltodict

DOCS_FOR_FOLDER=1000

parser=argparse.ArgumentParser()
parser.add_argument('-o', help='Output Directory')
parser.add_argument('-r', help='Remove All Before downloading, warning you have to be sure of remove al the PubMed Database')
args=parser.parse_args()

if __name__ == '__main__':
    import pubmed_standardization
    try:
        dest=args.o
        remove=args.r
    except Exception as inst:
        print( "Error: leyendo los parametros.")
        sys.exit(1) 
    if dest==None:
        print( "Error: complete the destination path") 
        sys.exit(1)    
    if not os.path.exists(dest):
        print( "Error: the destination path does not exist.") 
        sys.exit(1) 
    pubmed_standardization.Main(args)
    

def Main(args):
    dest=args.o
    result_file = dest + "/update_history.csv"
    standardization_output = dest + "/standardization/"
    standardization_input = dest + "/retrieval/"
    if not os.path.exists(standardization_output):
        os.makedirs(standardization_output)
    if os.path.isfile(result_file):
        df = pandas.read_csv(result_file, header=0, index_col=0)
    else:
        print ("The update_histroy file is missing.")    
        sys.exit(1) 
    unzip(df,standardization_input,result_file)
    standardization(df,standardization_input,standardization_output,result_file)

def unzip(df,standardization_input,result_file):
    df_=df.loc[df['operation'] == 'download']
    for index, data in df_.iterrows():
        file=os.path.join(standardization_input+"/"+data['folder'], data['name'])
        xml_file_path = file + ".xml"
        if os.path.isfile(file):
            with open(xml_file_path,'w') as xml_file:
                with gzip.open(os.path.join(standardization_input+"/"+data['folder'], data['name']), 'rb') as f:
                    file_content = f.read()
                    xml_file.write(file_content)
                    xml_file.flush()
                    xml_file.close()
                    print data['name'] + " unziped"
                    df.at[index,'unzip']='complete'
                    df.to_csv(result_file)
        else:
            print ("The file " + file + " not exist, please review and download again ")    
            df.at[index,'unzip']='not_tar_file'
            df.to_csv(result_file)
                       
def standardization(df,standardization_input, standardization_output,result_file):
    df_=df.loc[df['unzip'] == 'complete']
    for index, data in df_.iterrows():
        workdir_input = standardization_input+"/"+data['folder']
        workdir_output = standardization_output+"/"+data['folder']
        if not os.path.exists(workdir_output):
            os.makedirs(workdir_output)
        file=os.path.join(workdir_input, data['name'])
        xml_file_path = file + ".xml"
        docs_quantity = DOCS_FOR_FOLDER
        internal_folder_q = 0 
        if os.path.isfile(xml_file_path):
            with open(xml_file_path,'r') as xml_file:
                docXml = ET.parse(xml_file)
                for article in docXml.findall("PubmedArticle"):
                    try:
                        if(docs_quantity==DOCS_FOR_FOLDER):
                            internal_folder_q = internal_folder_q + 1
                            internal_folder = workdir_output + "/" + str(internal_folder_q)
                            if not os.path.exists(internal_folder):
                                os.makedirs(internal_folder)
                        pmid = article.find("MedlineCitation").find("PMID").text
                        print ("Processing pmid:" + pmid)
                        xml_string = ET.tostring(article, encoding='utf-8', method='xml')
                        o = xmltodict.parse(xml_string, encoding='utf-8')
                        jsonString = json.dumps(o, indent=4)
                        json_file=open(internal_folder+"/PMID"+pmid+".json",'w')
                        json_file.write(jsonString)
                        json_file.flush()
                        json_file.close()
                        data['json']='complete'
                        txt = ET.tostring(article, encoding='utf-8', method='text')
                        txt_file=open(internal_folder+"/PMID"+pmid+".txt",'w')
                        txt_file.write(txt)
                        txt_file.flush()
                        txt_file.close()
                        data['txt']='complete'
                        docs_quantity = docs_quantity - 1
                        if(docs_quantity==0):
                            docs_quantity=DOCS_FOR_FOLDER
                    except Exception as inst:
                        data['txt']='complete'
                        data['json']='complete'
                        print "Error Generando el JSON PMID " + pmid
                        print inst
                        x = inst.args
                        print x 
                                