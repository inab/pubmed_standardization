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
DOCS_FOR_FOLDER=5000
import codecs
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
    standardization2(standardization_input,standardization_output)

def ReadParameters(args):
    parameters_error=False
    parameters_obligation=False
    if(args.p!=None):
        Config = ConfigParser.ConfigParser()
        Config.read(args.p)
        parameters['database_url']=Config.get('DATABASE', 'url')
        parameters['output_directory']=Config.get('MAIN', 'output')
    else:
        parameters_obligation=True
    if(args.u!=None):
        parameters['database_url']=args.u
    elif (parameters_obligation):
        print ("No database url provided")
        parameters_error=True
    if(args.o!=None):
        parameters['output_directory']=args.o
    elif (parameters_obligation):
        print ("No output directory provided")
        parameters_error=False
    if(parameters_error):
        print("Please send the correct parameters.  You can type for --help ")
        sys.exit(1)
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
        if not os.path.exists(workdir_output):
            os.makedirs(workdir_output)
        dirs = os.listdir( workdir_output )
        internal_folder_q = len(dirs)
        '''if(old_unzip_path!=workdir_output):
            internal_folder_q = 0
        old_unzip_path = workdir_output''' 
        file=os.path.join(workdir_input, pubMedRetrieval.filename)
        xml_file_path = file + ".xml" 
        docs_quantity = DOCS_FOR_FOLDER
        if os.path.isfile(xml_file_path):
        #if os.path.isfile("/home/jcorvi/text_mining_data_test/pubmed_data//retrieval//baseline/example_keywords.xml"):
            #with open("/home/jcorvi/text_mining_data_test/pubmed_data//retrieval//baseline/example_keywords.xml",'r') as xml_file:
            with open(xml_file_path,'r') as xml_file:    
                print ("Parsing " + pubMedRetrieval.filename)
                docXml = ET.parse(xml_file)
                for article in docXml.findall("PubmedArticle"):
                    try:
                        pmid = article.find("MedlineCitation").find("PMID").text
                        print ("Processing pmid:" + pmid)
                        article_xml = article.find("MedlineCitation").find("Article")
                        abstract_xml = article_xml.find("Abstract")
                        if(abstract_xml!=None):
                            pubmedArticle = dao.findPubMedArticleByPMID(PubMedArticle,pmid)
                            if(pubmedArticle==None):
                                pubmedArticle = PubMedArticle(pmid,"PMID"+pmid, pubMedRetrieval.filename,'0','null','null','0','null','null')
                                dao.save(pubmedArticle) 
                            if(docs_quantity==DOCS_FOR_FOLDER):
                                internal_folder_q = internal_folder_q + 1
                                internal_folder = workdir_output + "/" + str(internal_folder_q)
                                if not os.path.exists(internal_folder):
                                    os.makedirs(internal_folder)
                            txt_file=codecs.open(internal_folder+"/PMID"+pmid+".txt",'w',encoding='utf8')
                            title_xml=article_xml.find("ArticleTitle")
                            if(title_xml!=None):
                                title = title_xml.text
                                txt_file.write('<TITLE_LIMTOX>.\n'+title+'\n')
                            abstract_xml = article_xml.find("Abstract")
                            if(abstract_xml!=None):
                                abstract_text = abstract_xml.find("AbstractText")
                                if(abstract_text!=None):
                                    abstract=abstract_text.text
                                    txt_file.write('<ABSTRACT_LIMTOX>.\n'+abstract+'\n')
                                    
                            txt_file.write('<KEYWORDS_LIMTOX>.\n')
                            chemicalList = article.find("MedlineCitation").find("ChemicalList")        
                            if(chemicalList!=None):
                                txt_file.write('<KEYWORDS_MESHCHEMICAL_LIMTOX>.\n')
                                for chemical in chemicalList.findall("Chemical"):
                                    name_substance = chemical.find("NameOfSubstance")
                                    if(name_substance!=None):
                                        txt_file.write("<NAME>"+name_substance.text+"</NAME>"+"<UI>"+name_substance.get('UI')+"</UI>."+'\n')
                                    
                            keyWords = article.find("MedlineCitation").find("KeywordList")        
                            if(keyWords!=None):
                                txt_file.write('<KEYWORDS_MANUAL_LIMTOX>.\n')
                                for keyword in keyWords.findall("Keyword"):
                                    txt_file.write("<NAME>"+keyword.text+"</NAME>."+'\n')
                                    
                            meshs = article.find("MedlineCitation").find("MeshHeadingList")        
                            if(meshs!=None):
                                txt_file.write('<KEYWORDS_MESH_LIMTOX>.\n')
                                for mesh in meshs.findall("MeshHeading"):
                                    name_mesh = mesh.find("DescriptorName")
                                    if(name_mesh!=None):
                                        txt_file.write("<NAME>"+name_mesh.text+"</NAME>."+'\n')

                            txt_file.flush()
                            txt_file.close()    
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

def standardization2(standardization_input, standardization_output):
    dao = DAO()
    old_unzip_path = None
    pubMedRetrievals = dao.findAllForStandardization(PubMedRetrieval)
    for pubMedRetrieval in pubMedRetrievals:
        workdir_input = standardization_input+"/"+pubMedRetrieval.unzip_path
        workdir_output = standardization_output+"/"+pubMedRetrieval.unzip_path
        if not os.path.exists(workdir_output):
            os.makedirs(workdir_output)
        dirs = os.listdir( workdir_output )
        internal_folder_q = len(dirs)
        '''if(old_unzip_path!=workdir_output):
            internal_folder_q = 0
        old_unzip_path = workdir_output''' 
        file=os.path.join(workdir_input, pubMedRetrieval.filename)
        xml_file_path = file + ".xml" 
        docs_quantity = DOCS_FOR_FOLDER
        if os.path.isfile(xml_file_path):
        #if os.path.isfile("/home/jcorvi/text_mining_data_test/pubmed_data//retrieval//baseline/example_keywords.xml"):
            #with open("/home/jcorvi/text_mining_data_test/pubmed_data//retrieval//baseline/example_keywords.xml",'r') as xml_file:
            with open(xml_file_path,'r') as xml_file:    
                print ("Parsing " + pubMedRetrieval.filename)
                docXml = ET.parse(xml_file)
                for article in docXml.findall("PubmedArticle"):
                    try:
                        pmid = article.find("MedlineCitation").find("PMID").text
                        print ("Processing pmid:" + pmid)
                        article_xml = article.find("MedlineCitation").find("Article")
                        abstract_xml = article_xml.find("Abstract")
                        if(abstract_xml!=None):
                            pubmedArticle = dao.findPubMedArticleByPMID(PubMedArticle,pmid)
                            if(pubmedArticle==None):
                                pubmedArticle = PubMedArticle(pmid,"PMID"+pmid, pubMedRetrieval.filename,'0','null','null','0','null','null')
                                dao.save(pubmedArticle) 
                            if(docs_quantity==DOCS_FOR_FOLDER):
                                internal_folder_q = internal_folder_q + 1
                                internal_folder = workdir_output + "/" + str(internal_folder_q)
                                if not os.path.exists(internal_folder):
                                    os.makedirs(internal_folder)
                            txt_file=codecs.open(internal_folder+"/PMID"+pmid+".xml",'w',encoding='utf8')
                            title_xml=article_xml.find("ArticleTitle")
                            
                            txt_file.write('<ARTICLE_LIMTOX>\n')
                            txt_file.write('<SECTIONS_LIMTOX>\n')
                            if(title_xml!=None):
                                title = title_xml.text
                                if(title!=None):
                                    txt_file.write('<TITLE_LIMTOX>'+title+'</TITLE_LIMTOX>\n')
                            abstract_xml = article_xml.find("Abstract")
                            if(abstract_xml!=None):
                                abstract_text = abstract_xml.find("AbstractText")
                                if(abstract_text!=None):
                                    abstract=abstract_text.text
                                    if(abstract!=None):
                                        txt_file.write('<ABSTRACT_LIMTOX>'+abstract+'</ABSTRACT_LIMTOX>\n')
                            txt_file.write('</SECTIONS_LIMTOX>\n')
                            txt_file.write('<KEYWORDS_LIMTOX>\n')
                            chemicalList = article.find("MedlineCitation").find("ChemicalList")        
                            if(chemicalList!=None):
                                txt_file.write('<KEYWORDS_MESHCHEMICAL_LIMTOX>\n')
                                for chemical in chemicalList.findall("Chemical"):
                                    name_substance = chemical.find("NameOfSubstance")
                                    if(name_substance!=None):
                                        txt_file.write("<CHEMICAL><NAME>"+name_substance.text+"</NAME>"+"<UI>"+name_substance.get('UI')+"</UI></CHEMICAL>"+'\n')
                                txt_file.write('</KEYWORDS_MESHCHEMICAL_LIMTOX>\n')    
                            keyWords = article.find("MedlineCitation").find("KeywordList")        
                            if(keyWords!=None):
                                txt_file.write('<KEYWORDS_MANUAL_LIMTOX>')
                                for keyword in keyWords.findall("Keyword"):
                                    txt_file.write("<NAME>"+keyword.text+"</NAME>"+'\n')
                                txt_file.write('</KEYWORDS_MANUAL_LIMTOX>')   
                            meshs = article.find("MedlineCitation").find("MeshHeadingList")        
                            if(meshs!=None):
                                txt_file.write('<KEYWORDS_MESH_LIMTOX>\n')
                                for mesh in meshs.findall("MeshHeading"):
                                    name_mesh = mesh.find("DescriptorName")
                                    if(name_mesh!=None):
                                        txt_file.write("<NAME>"+name_mesh.text+"</NAME>"+'\n')
                                txt_file.write('</KEYWORDS_MESH_LIMTOX>\n')        
                            txt_file.write('</KEYWORDS_LIMTOX>\n')            
                            txt_file.write('</ARTICLE_LIMTOX>\n')
                            
                            txt_file.flush()
                            txt_file.close()    
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

                        
                                