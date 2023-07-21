#Common
from conf import conf
import os

os.chdir(conf['db'][conf['env']]['working_directory'])


#Common
def Get_box_info(box):

    ######################## REGEX ##############################
    import re
    start_regex=re.compile('(?<=<query:StartTime>)(.*)(?=</query:StartTime>)')
    end_regex=re.compile('(?<=<query:EndTime>)(.*)(?=</query:EndTime>)')
    id_regex=re.compile('(?<=<ID>)(.*)(?=</ID>)')
    ##############################################################
    
    titolo=box.find(class_='title').text
    
    data=box.find(class_='date').text
    
    text=box.find('textarea').text
    
    start=start_regex.findall(text)[0]
    end=end_regex.findall(text)[0]
    
    ID=id_regex.findall(text)[0]
    
    return dict(titolo=titolo,
                data_aggiornamento=data,
                start_periodo=start,
                end_periodo=end,
                flow=ID)



def get_constraint(flowref):
    import subprocess
    cmd=f'curl --location --request GET "http://sdmx.istat.it/SDMXWS/rest/availableconstraint/{flowref}">"./constraint/constraint_{flowref}.xml"'
    out=subprocess.run(cmd,shell=True,  stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    
    return(out)

def parse_constraint(flowref):
    import xml.etree.ElementTree as ET

    
    tree = ET.parse(f'./constraint/constraint_{flowref}.xml')
    root=tree.getroot()

    keys=[]
    dim=[]

    for child in root[1][0][0][3]:

      values=[]
      keys.append(child.attrib['id'])

      for item in child:
         values.append(item.text)

      dim.append(values)

    constraint=dict(zip(keys,dim))
    return constraint

def get_geo_level(constraint):
    
    geo_test=['037001','ITD55','ITD5','ITD','IT']
    geo_level=['Comunale','Provinciale','Regionale','Areale','Nazionale']
    
    for geo_t,geo_l in zip(geo_test,geo_level):
        res=[]
        for i in constraint.values():
            res.append((geo_t in i))

        if any(res):
            geo=geo_l
            return geo

    
def min_geo_level(geo):
    import re

    geo_reg=re.compile('Comunale|Provinciale')
    
    if geo_reg.findall(geo):
        return True
    else:
        return False


def get_cmd_info(result):
    import re
    size=re.compile('"(\d.*\d* Mb|Kb)"')
    sec=re.compile('"\n(.* sec) elapsed')
    #err=re.compile('.*(HTTP 404).*')

    try:
        volume=size.findall(result.stdout)[0]
        time=sec.findall(result.stdout)[0]
    except:
        volume=None
        err=result.stderr
        #.removeprefix('\nCaricamento pacchetto: \'dplyr\'\n\nI seguenti oggetti sono mascherati da \'package:stats\':\n\n    filter, lag\n\nI seguenti oggetti sono mascherati da \'package:base\':\n\n    intersect, setdiff, setequal, union\n\nMessaggio di avvertimento:\nil pacchetto \'optparse\' è stato creato con R versione 4.1.2 \n')
        time=err.replace('"','')
    return volume,time
