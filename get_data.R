##### GET DATA
  ##### Aggiunta gestione parametri query da chiamata bash
    #### TODO: aggiungere gestione path per scarico (valutare di farlo nel main py)
suppressWarnings({
      suppressMessages({

            library(rsdmx)
            library(dplyr)
            library("optparse")
            library(readr)
            source('./Common.R')
            library(tictoc)
            #lista_comuni <- read_csv("C:/Users/riccie/Desktop/sdmx_ISTAT_project")
      })

      tic()

      option_list = list(
        make_option(c("-r", "--flowref"), type="character", default=NULL, 
                    help="dataset file name", metavar="character"),
                    make_option(c("-f", "--frequence"), type="character", default=NULL, 
                          help="frequenza del dato richiesta ", metavar="character")
                          ,
                    make_option(c("-s", "--start"), type="character", default=NULL, 
                          help="inizio periodo temporale relativo al dato richiesto", metavar="character")
                          ,
                    make_option(c("-e", "--end"), type="character", default=NULL, 
                          help="fine periodo temporale relativo al dato richiesto", metavar="character")
                          ,
                    make_option(c("-g", "--geo"), type="character", default=NULL, 
                          help="livello geografico su cui richiedere i dati", metavar="character")
                          ,
                    make_option(c("-d", "--down_dir"), type="character", default=NULL, 
                          help="path per il download", metavar="character")

      )

      opt_parser = OptionParser(option_list=option_list)
      opt = parse_args(opt_parser)



      ref=opt$flowref
      istatFlows <- readSDMX(providerId = "ISTAT", resource = "dataflow") %>% as.data.frame()
      dsdRef=istatFlows %>% filter(id==ref) %>% pull(dsdRef)
      name=istatFlows %>% filter(id==ref) %>% pull(Name.it)

      dsd <- readSDMX(providerId = "ISTAT", resource = "datastructure", resourceId=dsdRef)

      dimensioni<-slot(slot(slot(dsd,'datastructures'), "datastructures")[[1]], "Components") %>% as.data.frame() %>% 
        filter(component == "Dimension") 



      dt<-NULL
      temp<-NULL

      if (opt$geo=='Comunale'){
        for (i in geo){
          temp <- readSDMX(providerId = "ISTAT",
                                   resource = "data",
                                   flowRef  = opt$flowref,                
                                   key=get_keys(i,opt$frequence,dimensioni$codelist),
                                   start = opt$start,
                                   end=opt$end,
                                   dsd = T)  %>% 
            as.data.frame(labels = TRUE)
          dt<-rbind(dt,temp)
        }

          
      }else{
            i=altro
            dt <- readSDMX(providerId = "ISTAT",
                                   resource = "data",
                                   flowRef  = opt$flowref,                
                                   key=get_keys(i,opt$frequence,dimensioni$codelist),
                                   start = opt$start,
                                   end=opt$end,
                                   dsd = T)  %>% 
            as.data.frame(labels = TRUE)
            
            
            if ("ITTER107" %in% colnames(dt)) {geos<-dt %>% distinct(ITTER107)%>% pull()} else{geos<-dt %>% distinct(REF_AREA)%>% pull()}
            if(!('ITD55' %in% geos)){stop('Aggiornamento non su base provinciale')}
      }

      dt<-dt %>% select(-ends_with('.en')) 
      dt<-dt %>% mutate(data_download=format(Sys.time(), "%d-%m-%Y"))
      
      geo=ifelse(opt$geo=='Comunale','Com','CM')

  

      dt %>% write.csv(paste0(opt$down_dir,dsdRef,'__',name,'__',substr(opt$end,1, 4),'_',geo ,'_',opt$frequence,'.csv'),row.names = F)

      print(utils:::format.object_size(file.size(paste0(opt$down_dir,dsdRef,'__',name,'__',substr(opt$end,1, 4),'_',geo ,'_',opt$frequence,'.csv')), "auto"))

      toc()
})