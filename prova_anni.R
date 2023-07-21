library(rsdmx)
library(dplyr)
library("optparse")
library(readr)
source('./Common.R')
library(tictoc)
#lista_comuni <- read_csv("C:/Users/riccie/Desktop/sdmx_ISTAT_project")

tic()

option_list = list(

  make_option(c("-s", "--start"), type="character", default=NULL, 
              help="inizio periodo temporale relativo al dato richiesto", metavar="character")
  ,
  make_option(c("-e", "--end"), type="character", default=NULL, 
              help="fine periodo temporale relativo al dato richiesto", metavar="character"))



opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)


anni=c(as.numeric(opt$start):as.numeric(opt$end))

for (i in anni){
  print(i)
}