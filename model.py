import os
from dotenv import load_dotenv

import langid
from deep_translator import GoogleTranslator

import openai
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks import get_openai_callback

from langchain.schema import Document

class Model:
    def __init__(self):
        load_dotenv()
        
        tokens=os.environ.get('TOKENS')
        chunk_path=f"{os.environ.get('CHUNK_PATH')}"
        retrive_code=os.environ.get('RETRIVE_CODE')
        embedding_model=os.environ.get('EMBEDDING_MODEL')
        llm=os.environ.get('GPT_MODEL')
        with open(chunk_path,'r',encoding='UTF-8') as f:
            text_chunks=f.read().split(retrive_code)
        print('Creating Embeddings ...')
        self.embeddings=HuggingFaceEmbeddings(model_name=embedding_model)
        print('Creating LLM model ...')
        self.llm=ChatOpenAI(temperature=0.5,model_name=llm,max_tokens=tokens)
        self.chain=load_qa_chain(self.llm,chain_type='stuff')
        print('Creating Docsearch ...')
        self.docsearch=FAISS.from_texts(text_chunks,self.embeddings)

    def quering(self,query,userdata,appointment=False):
        query_lang,confidence=langid.classify(query)
        docs=[]
        if query_lang!='en':
            query=self.translator(query,query_lang,'en')

        if appointment:
            docs=[]
            docs.append(Document(page_content=userdata))
            response,q_cost=self.Response(docs,query)
            return response
        
        if 'product recommendation' in query.lower():
          prod_rec=True
        else:
            query0=f'''user:{query}
            Does the user needs product recommendations or not ? Just say yes or no
            '''
            prod_rec,q_cost=self.Response(docs,query0)
            print(prod_rec,'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            prod_rec=True if prod_rec.lower()=='yes' else False
        print(prod_rec,'&&&&&&&&&')
        if prod_rec:
          query1=f'''User:"{query}. My baby age is {userdata['ayears']} years {userdata['amonths']} months {userdata['adays']} days"
          Convert this user text to a searchable text of that product.
          '''
          print(query1)
          searchable_que,q_cost=self.Response(docs,query1)
          print(searchable_que)
          if 'The user is searching for '.lower() in searchable_que.lower():
            searchable_que=searchable_que.lower().replace('The user is searching for '.lower(),'').strip()
          if 'The user wants suggestions for'.lower() in searchable_que.lower():
            searchable_que=searchable_que.lower().replace('The user wants suggestions for '.lower(),'').strip()
        
          print(q_cost)
          return prod_rec,searchable_que

        
        #docs=self.search(query)
        usercontent1=f"my baby age is {userdata['ayears']} years {userdata['amonths']} months {userdata['adays']} days"
        usercontent2=f"my name is {userdata['username']} and i'm from {userdata['location']} country"
        usercontent3=f"my baby date of birth is {userdata['babyDOB']}"
        usercontent4=f"Give me the response completely, give me a best refined simple yet to the point response."
        usercontent5=f"if there are any line breaks like when you we have bullet points or steps or any line breaks that you feel to add, then insert \n in that line break place"
        docs.append(Document(page_content=usercontent1))
        docs+=self.search(query)
        docs.append(Document(page_content=usercontent3))
        docs.append(Document(page_content=usercontent2))
        docs.append(Document(page_content=usercontent4))
        docs.append(Document(page_content=usercontent5))
        
        
        response,q_cost=self.Response(docs,query)
        print(f'cost of this question is : {q_cost}$')
        rem_item1='Based on the information you provided, '
        rem_item2='according to the information you provided'
        rem_item3='Based on the information provided, '
        if rem_item1 in response or rem_item2 in response or rem_item3 in response:
            if rem_item2 in response:
                response=response.split(rem_item2)[-1]
                response=response[:0]+response[0]+response[1:]
            elif rem_item1 in response:
                response=response.split(rem_item1)[-1]
                response=response[:0]+response[0].upper()+response[1:]
            elif rem_item3 in response:
                response=response.split(rem_item3)[-1]
                response=response[:0]+response[0].upper()+response[1:]

        #print(q_cost)
        if query_lang!='en':
            response=self.translator(response,'en',query_lang)
        return prod_rec,response


    def translator(self,query,src_lang,target_lang):
        trans=GoogleTranslator(source=src_lang,target=target_lang)
        return trans.translate(query)
        
    def search(self,query):
        docs=self.docsearch.similarity_search(query)
        return docs
    def Response(self,docs,query):
        
        with get_openai_callback() as cb:
            response=self.chain.run(input_documents=docs,question=query)
            q_cost=cb
        return response,q_cost

        
    





