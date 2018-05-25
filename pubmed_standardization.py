import sys
import os
import pandas
from datetime import datetime
import argparse
import gzip
import xml.etree.ElementTree as ET
import json
import xmltodict 
from db_util import InitDataBase
import ConfigParser
from dao import DAO
from model import PubMedRetrieval
from model import PubMedArticle
DOCS_FOR_FOLDER=1000

parser=argparse.ArgumentParser()
parser.add_argument('-o', help='Output Directory')
parser.add_argument('-u', help='SQLITE Database URL')
parser.add_argument('-p', help='Path Parameters')
args=parser.parse_args()
parameters={}
if __name__ == '__main__':
    import pubmed_standardization
    parameters = pubmed_standardization.ReadParameters(args)     
    InitDataBase(parameters)
    pubmed_standardization.Main(parameters)

def Main(parameters):
    dest=parameters['output_directory']
    standardization_output = dest + "/standardization/"
    standardization_input = dest + "/retrieval/"
    if not os.path.exists(standardization_output):
        os.makedirs(standardization_output)
    unzip(standardization_input)
    standardization(standardization_input,standardization_output)

def ReadParameters(args):
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['database_url']=Config.get('DATABASE', 'url')
        parameters['output_directory']=Config.get('MAIN', 'output')
    if(args.u!=None):
        parameters['database_url']=args.u
    if(args.o!=None):
        parameters['output_directory']=args.o
    return parameters

def unzip(standardization_input):
    dao = DAO()
    pubMedRetrievals = dao.findAllForUnzip(PubMedRetrieval)
    for pubMedRetrieval in pubMedRetrievals:
        print pubMedRetrieval.filename
        file=os.path.join(standardization_input+"/"+pubMedRetrieval.download_path, pubMedRetrieval.filename)
        xml_file_path = file + ".xml"
        if os.path.isfile(file):
            with open(xml_file_path,'w') as xml_file:
                with gzip.open(os.path.join(standardization_input+"/"+pubMedRetrieval.download_path, pubMedRetrieval.filename), 'rb') as f:
                    file_content = f.read()
                    xml_file.write(file_content)
                    xml_file.flush()
                    xml_file.close()
                    print pubMedRetrieval.filename + " unzip"
                    pubMedRetrieval.unzip=1
                    pubMedRetrieval.unzip_datetime=datetime.now()
                    pubMedRetrieval.unzip_path=pubMedRetrieval.download_path
                    dao.save(pubMedRetrieval)
        else:
            print ("The file " + file + " not exist, please review and download again ")    
           
                       
def standardization(standardization_input, standardization_output):
    dao = DAO()
    old_unzip_path = None
    pubMedRetrievals = dao.findAllForStandardization(PubMedRetrieval)
    for pubMedRetrieval in pubMedRetrievals:
        workdir_input = standardization_input+"/"+pubMedRetrieval.unzip_path
        workdir_output = standardization_output+"/"+pubMedRetrieval.unzip_path
        if(old_unzip_path!=workdir_output):
            internal_folder_q = 0
        old_unzip_path = workdir_output 
        if not os.path.exists(workdir_output):
            os.makedirs(workdir_output)
        file=os.path.join(workdir_input, pubMedRetrieval.filename)
        xml_file_path = file + ".xml"
        docs_quantity = DOCS_FOR_FOLDER
        if os.path.isfile(xml_file_path):
            with open(xml_file_path,'r') as xml_file:
                print ("Parsing " + pubMedRetrieval.filename)
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
                        pubmedArticle = dao.findPubMedArticleByPMID(PubMedArticle,pmid)
                        if(pubmedArticle==None):
                            pubmedArticle = PubMedArticle(pmid,"PMID"+pmid, pubMedRetrieval.filename,'0','null','null','0','null','null')
                            dao.save(pubmedArticle) 
                        '''xml_string = ET.tostring(article, encoding='utf-8', method='xml')
                        o = xmltodict.parse(xml_string, encoding='utf-8')
                        jsonString = json.dumps(o, indent=4)
                        json_file=open(internal_folder+"/PMID"+pmid+".json",'w')
                        json_file.write(jsonString)
                        json_file.flush()
                        json_file.close()'''
                        pubmedArticle.json=1
                        pubmedArticle.json_path=pubMedRetrieval.unzip_path + "/" + str(internal_folder_q)
                        pubmedArticle.json_datetime=datetime.now()
                        dao.save(pubmedArticle) 
                        '''txt = ET.tostring(article, encoding='utf-8', method='text')
                        txt_file=open(internal_folder+"/PMID"+pmid+".txt",'w')
                        txt_file.write(txt)
                        txt_file.flush()
                        txt_file.close()'''
                        pubmedArticle.txt=1
                        pubmedArticle.txt_path=pubMedRetrieval.unzip_path + "/" + str(internal_folder_q)
                        pubmedArticle.txt_datetime=datetime.now()
                        dao.save(pubmedArticle) 
                        docs_quantity = docs_quantity - 1
                        if(docs_quantity==0):
                            docs_quantity=DOCS_FOR_FOLDER
                    except Exception as inst:
                        print "Error Generando el JSON/TXT PMID " + pmid
                        print inst
                        x = inst.args
                        print x 
                        
                                