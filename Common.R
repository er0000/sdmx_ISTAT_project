get_keys<-function(i,freq,conceptRef){

  if (is.null(i)){
    for (j in 1:length(dimensioni$conceptRef)){
    
    keys=ifelse(dimensioni$codelist=='CL_FREQ',freq,list(NULL))
    
  } 
  }else{
  
    for (j in 1:length(dimensioni$conceptRef)){

      keys=ifelse(dimensioni$codelist=='CL_FREQ',freq,ifelse(
        dimensioni$codelist=='CL_ITTER107',i,list(NULL)))

    } 
  }

  return(keys)
}


lista_comuni<-NULL
lista_comuni$Comuni=c(037001,
037002,
037003,
037005,
037006,
037007,
037008,
037009,
037010,
037011,
037012,
037013,
037014,
037015,
037016,
037017,
037019,
037020,
037021,
037022,
037024,
037025,
037026,
037027,
037028,
037030,
037031,
037032,
037033,
037034,
037035,
037036,
037037,
037038,
037039,
037040,
037041,
037042,
037044,
037045,
037046,
037047,
037048,
037050,
037051,
037052,
037053,
037054,
037055,
037056,
037057,
037059,
037060,
037061,
037062
)

lista_comuni<-lista_comuni %>%as.data.frame() %>% mutate(Comuni=paste0(0,Comuni))

#geo1<-paste(lista_comuni$Comuni[1:11],collapse = '+')
#geo2<-paste(lista_comuni$Comuni[12:22],collapse = '+')
#geo3<-paste(lista_comuni$Comuni[23:33],collapse = '+')
#geo4<-paste(lista_comuni$Comuni[34:44],collapse = '+')
#geo5<-paste(lista_comuni$Comuni[45:55],collapse = '+')
#geo<-c(geo1,geo2,geo3,geo4,geo5)
#
geo1<-paste(lista_comuni$Comuni[1:27],collapse = '+')
geo2<-paste(lista_comuni$Comuni[28:55],collapse = '+')
geo<-c(geo1,geo2)

#altro=NULL
altro=c('IT','ITD5','ITF42','ITD55','ITG27','ITG17','ITE14','ITC33','ITG13','ITC45','ITF33','ITG12','ITF65','ITE43','ITC11','ITD35')
altro=paste(altro,collapse = '+')
