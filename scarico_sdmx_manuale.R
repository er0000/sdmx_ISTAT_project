library(tidyverse)
library(rsdmx)

source("F:/DIREZIONE-GENERALE/DATA/DB_SDMX/altro/Common.R")
istatFlows <- readSDMX(providerId = "ISTAT", resource = "dataflow") %>% as.data.frame()


ref='183_277'

dsdRef=istatFlows %>% filter(id==ref) %>% pull(dsdRef)

dsd <- readSDMX(providerId = "ISTAT", resource = "datastructure", resourceId=dsdRef)

dimensioni<-slot(slot(slot(dsd,'datastructures'), "datastructures")[[1]], "Components") %>% as.data.frame() %>% 
  filter(component == "Dimension") 


#as.data.frame(slot(dsd, "codelists"), codelistId = dimensioni$codelist[2]) %>% as.data.frame() #%>% write.csv('codelists.csv')

#slot(dsd,"codelists") %>% View()

cod_dimensioni<-NULL

for (i in 1:nrow(dimensioni)){
  cod_dimensioni[[i]]<- as.data.frame(slot(dsd, "codelists"), codelistId = dimensioni$codelist[i]) %>% select(id,label.it) %>% as.data.frame()
  names(cod_dimensioni)[i]<-dimensioni$conceptRef[i]
}


                                             


DT<-NULL
temp<-NULL
#tic()
for (i in altro){
  temp <- readSDMX(providerId = "ISTAT",
                   resource = "data",
                   flowRef  = ref,                
                   key=get_keys(i,'A',dsdRef ),
                   start = '2019',
                   end='2019',
                   dsd = T)  %>% 
    as.data.frame(labels = TRUE)
  DT<-rbind(DT,temp)
}

DT<-DT %>% select(-ends_with('.en')) 
toc()
DT %>% write.csv('DCIS_POPSTRRES1_2021_2021_A.csv',row.names = F)


DT<-readSDMX(providerId = "ISTAT",
         resource = "data",
         flowRef  = ref,                
         key= list("A", NULL, NULL, NULL, NULL, NULL, NULL, NULL),
         start = '2020',
         end='2020',
         dsd = F)  %>% 
  as.data.frame(labels = TRUE)
DT<-rbind(DT,temp)