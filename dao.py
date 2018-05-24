'''
Created on May 18, 2018

@author: jcorvi
'''
from sqlalchemy import exists
from db_util import getSession
from sqlalchemy import and_
class DAO:
    '''Singleton
    instance = None
    def __init__(self):
        if not DAO.instance:
            DAO.instance = DAO.__DAO()
        DAO.instance
    
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
    ''' 
    def save(self, instance):
        session = getSession()
        try:
            session.add(instance)
            session.commit()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()
          
    def findByName(self, model_class, name):
        session = getSession()
        try:
            ret = session.query(exists().where(model_class.name==name)).all()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()  
            return ret  
    
    def findAllNames(self, model_class):
        session = getSession()
        try:
            ret = session.query(model_class.filename).all()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()  
            return ret 
        
    def findAll(self, model_class):
        session = getSession()
        try:
            ret = session.query(model_class).all()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()  
            return ret   
        
    def findAllForUnzip(self, model_class):
        session = getSession()
        try:
            ret = session.query(model_class).\
            filter(and_(model_class.download == '1', model_class.unzip == '0')).all()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()  
            return ret  
          
    def findAllForStandardization(self, model_class):
        session = getSession()
        try:
            ret = session.query(model_class).\
            filter(and_(model_class.download == '1', model_class.unzip == '1')).all()
        except Exception as inst:
            print inst
            session.rollback()
            raise
        finally:
            session.close()  
            return ret     
        
    def findPubMedArticleByPMID(self, model_class, pmid):
        session = getSession()
        try:
            ret = session.query(model_class).\
            filter(model_class.pmid == pmid).all()
            if(len(ret)==0):
                ret = None
            elif(len(ret)==1): 
                ret = ret[0]
            else:
                raise Exception(model_class, 'more than one record for pmid ' + pmid) 
        finally:
            session.close()  
            return ret  
       
        
           