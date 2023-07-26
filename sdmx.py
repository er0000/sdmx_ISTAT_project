#!/usr/bin/env python
from conf import conf
from Common import *
from models import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import *    
from peewee import *
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import time

#TODO: riscaricare i file mensili fino ad ora in db (-> modificato il paramentro END: inserendo solo l'anno scarica solo gennaio)
# TODO: modificare logica nomenclatura e salvataggio file mensili. (va fatto un update sullo stesso file per essere coerenti con i file a frequenza annuale che hanno nel nome solo l'anno)

#now = datetime.now()                     ##### ELIMINATO nella richiesta delle query mensili richiediamo sempre anno-12
#current_month = now.month

s=Service(ChromeDriverManager(version="114.0.5735.90").install())

logger = get_logger(path = conf['db'][conf['env']]['logger_path'])

logger.info('**** START ****')
driver = webdriver.Chrome(service=s)
url = 'https://www.istat.it/it/metodi-e-strumenti/web-service-sdmx#Aggiornamentodeidataseterelativequery-2'
driver.get(url )

down_dir=conf['db'][conf['env']]['download_directory']

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "rsssep"))
    )
    page_source = driver.page_source

finally:
    driver.quit()

from bs4 import BeautifulSoup
import lxml
soup = BeautifulSoup(page_source,'html.parser')


try:

    l=soup.find(class_='simplePagerNav')
    result=[]
    ndt=0
    len(l)
    logger.debug('Casistica multi pagina')
    info_list=[]
    for i in list(range(1, len(l)+1)):
        cl='simplePagerPage'+str(i)
        page=soup.find_all(class_=cl)
        for box in page:
                    print('______________ box numero', i, '_______________')
                    Info=Get_box_info(box)
                    print(Info['titolo'])
                    print('aggiornato il ' + Info['data_aggiornamento'])
                    print('info per query -> ',  Info['flow'],  Info['start_periodo'], Info['end_periodo'])
                    print(' ')
                    i=i+1
                    time.sleep(1)
                    ndt=ndt+1 
                    info_list.append(Info)
    logger.info(f'Identificate {len(l)} pagine di aggiornamenti per un totale di {ndt} dataset')
    time.sleep(3)
    
except TypeError as e :   
    logger.error(e)
    logger.debug('Except - casistica unica pagina')
    cl='simplePagerPage1'
    page=soup.find_all(class_=cl)
    i=1
    info_list=[]
    for box in page:
        print('______________ box numero', i, '_______________')
        Info=Get_box_info(box)
        print(Info['titolo'])
        print('aggiornato il ' + Info['data_aggiornamento'])
        print('info per query -> ',  Info['flow'], '-' ,Info['start_periodo'], '-' ,Info['end_periodo'])
        print(' ')
        time.sleep(1)
        i=i+1
        info_list.append(Info)

    logger.info(f'Identificata 1 pagina di aggiornamenti per un totale di {len(page)} dataset ')
    time.sleep(3)
      
n=0
for row in info_list:

    try:

        n=n+1
        flow=row['flow']
        titolo=row['titolo']
        data_aggiornamento=row['data_aggiornamento']
        cur=db.cursor()
        cur.execute(f'select count(*) from monitor where flow="{flow}" and data_aggiornamento="{data_aggiornamento}"')
        res=cur.fetchall()[0][0]

        if res==0:
            
            logger.info(f'inserisco riga {n} - {flow} in db')

            Monitor.create(**row)
        
        else:

            logger.info(f'Aggiornamento flow {flow} già presente in db')
            
    except Exception as e:
    
        logger.error(e)

db.close()


import time
######### leggo i risultati dello scraping e seleziono le nuove osservazioni da scaricare
    ######### Aggiunto scarico + parsing delle constraint + individuazione livello geografico 
        ######### aggiunta modifica dei campi Download e Volume post scarico
            ###### gestito parametro frequenza in base alle constraint(si provano tutte), **ELIMINATO** frequenza=annuale
                ######## TODO: gestire scarichi multipli in base ai livelli geografici minimi disponibili
                                # Al momento scarica al livello geo minimo disponibile
                    ###### Aggiunto controllo sulla pre-esistenza del file constraint.xml


logger.info('**** FASE DOWNLOAD ****')

   
try:
    cur=db.cursor()
    cur.execute('select * from monitor where download=False')
    result=cur.fetchall()
    db.close()

    for flow in result:
        
        flowRef=flow[3]
        start=flow[5]
        end=flow[6]+1
        titolo=flow[2]
        data_agg=flow[4]
        anni=range(start,end)


        logger.info(f' **  {flow[2]}  ** ')
        logger.info('___________________________________________________________________________')
        logger.info('Controllo constraint in corso')
        
        exist=os.path.isfile(f'./constraint/constraint_{flowRef}.xml') 
        
        if exist:

            constraint=parse_constraint(flowRef)

        else:
            
            get_constraint(flowRef) 
        
            constraint=parse_constraint(flowRef)
              

        geo=get_geo_level(constraint) 
        
        if min_geo_level(geo):

            
            logger.info(f'livello geografico minimo: {geo}. \b download in corso  ')

            cont=len(anni)

            #for fr in constraint['FREQ']:
            for a in anni:

                cont=cont-1

                try:
                    
                    cmd=f'Rscript get_data.R -r {flowRef} -f A -s {a} -e {a} -g {geo} -d {down_dir}'

                    result=subprocess.run(cmd, stderr=subprocess.PIPE,stdout=subprocess.PIPE, text=True)
                    volume,note= get_cmd_info(result)
                    logger.info(f'scaricati {volume} in {note}')
                    cur=db.cursor()
                    
                    query=f'insert INTO Download (titolo,flow,data_aggiornamento,anno,volume,note,livello_geografico)values ("{titolo}","{flowRef}","{data_agg}","{a}","{volume}","{note}","{geo}");'
                    cur.execute(query)  
                    logger.info(f'Aggiornata osservazione in db')
                    db.close()

                    if cont<=2: ### Scarico i mensili solo se degli ultimi due anni 
                        cmd=f'Rscript get_data.R -r {flowRef} -f M -s {a} -e {a}-12 -g {geo} -d {down_dir}'

                        result=subprocess.run(cmd, stderr=subprocess.PIPE,stdout=subprocess.PIPE, text=True)
                        volume,note= get_cmd_info(result)
                        note= 'MENSILI - ' + note
                        logger.info(f'scaricati {volume} in {note}')
                        cur=db.cursor()

                        query=f'insert INTO Download (titolo,flow,data_aggiornamento,anno,volume,note,livello_geografico)values ("{titolo}","{flowRef}","{data_agg}","{a}","{volume}","{note}","{geo}");'
                        cur.execute(query)  

                        logger.info(f'Aggiornata osservazione in db - DATI MENSILI')
                        db.close()
                        gspreadAPI='python C:\\Users\\riccie\\Desktop\\Progetti\\gspreadAPI\\gspreadAPI.py'  
                        subprocess.run(gspreadAPI, stderr=subprocess.PIPE,stdout=subprocess.PIPE, text=True)
                        logger.info(f'gspreadAPI')


                
                except Exception as e:

                    logger.error(e)
            
            query=f'UPDATE Monitor SET download=True WHERE flow="{flowRef}" and data_aggiornamento="{data_agg}";'            
            cur=db.cursor()
            cur.execute(query)  
            db.close()

        else:

            logger.info(f'livello geografico: {geo}. \b non verrà eseguito il download')
            
            try:
                cur=db.cursor()
                    
                query=f'UPDATE Monitor SET  note = "Livello geografico {geo}" , download=True WHERE flow="{flowRef}" and data_aggiornamento="{data_agg}";'
                cur.execute(query)  
                db.close()
            
            except Exception as e:

                logger.error(e)
    
    logger.info('*** stop***') 


    time.sleep(5)

except Exception as e:

    logger.error(e)

