'''
Created on May 18, 2018

@author: jcorvi
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence

Base = declarative_base()

class PubMedRetrieval(Base):
    __tablename__ = 'pubmed_retrieval'
    id = Column(Integer, Sequence('id'), primary_key=True)
    filename = Column(String(250))
    download = Column(Integer)
    download_datetime = Column(String(250))
    download_path = Column(String(400))
    unzip = Column(Integer)
    unzip_datetime = Column(String(250))
    unzip_path = Column(String(400))
    def __repr__(self):
        return "<PubMedRetrieval(filename='%s', download='%s', download_datetime='%s',download_path='%s', unzip='%s', unzip_datetime='%s', unzip_path='%s')>" % (
                                self.filename, self.download, self.download_datetime, self.download_path, self.unzip, self.unzip_datetime, self.unzip_path)
    
    """Consctructor"""
    def __init__(self, filename, download,download_datetime,download_path,unzip, unzip_datetime,unzip_path):
        self.filename = filename
        self.download = download
        self.download_datetime = download_datetime
        self.download_path = download_path
        self.unzip = unzip
        self.unzip_datetime = unzip_datetime
        self.unzip_path = unzip_path
        
        
class PubMedArticle(Base):
    __tablename__ = 'pubmed_articles'
    id = Column(Integer, Sequence('id'), primary_key=True)
    pmid = Column(String(100))
    filename = Column(String(250))
    parent_filename = Column(String(250))
    json = Column(Integer)
    json_datetime = Column(String(250))
    json_path = Column(String(400))
    txt = Column(Integer)
    txt_datetime = Column(String(250))
    txt_path = Column(String(400))
    def __repr__(self):
        return "<PubMedArticle(pmid='%s', filename='%s',parent_filename='%s', download='%s', download_datetime='%s',download_path='%s', txt='%s', txt_datetime='%s', txt_path='%s')>" % (
                                self.pmid, self.filename, self.parent_filename, self.json, self.json_datetime, self.json_path, self.txt, self.txt_datetime, self.txt_path)
    
    """Consctructor"""
    def __init__(self,pmid,filename, parent_filename, json,json_datetime,json_path,txt, txt_datetime,txt_path):
        self.pmid = pmid
        self.filename = filename
        self.parent_filename = parent_filename
        self.json = json
        self.json_datetime = json_datetime
        self.json_path = json_path
        self.txt = txt
        self.txt_datetime = txt_datetime
        self.txt_path = txt_path