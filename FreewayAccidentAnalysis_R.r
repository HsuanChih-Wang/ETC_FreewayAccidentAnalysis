freeway_no1_north <-read.csv("C:/Users/WangRabbit/Documents/GitHub/ETC_FreewayAccidentAnalysis/data/2020/freeway_no1_north.csv", sep=",")
freeway_no3_north <-read.csv("C:/Users/WangRabbit/Documents/GitHub/FreewayAccidentAnalysis/data/freeway_no3_north.csv", sep=",")
freeway_500000_withheavyrate <- read.csv("C:/Users/WangRabbit/Documents/GitHub/ETC_FreewayAccidentAnalysis/data/500000_heavyrate.csv", sep=",")


freeway_no1_north <- subset(freeway_no1_north, 
                           select = -c(pavement, cement, remark, upslope
                           ,downslope, minradiuslength, one, Var_windspeed, Var_rain, 
                           Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, startkilo, 
                           endkilo, year, date, starttime, endtime, speedlimit))

# remove rows 
freeway_no1_north <- freeway_no1_north[-c(44401:nrow(freeway_no1_north)), ]


freeway_no3_north <- subset(freeway_no3_north, 
                            select = -c(pavement, cement, remark, upslope
                                        ,downslope, minradiuslength, one, Var_windspeed, Var_rain, volume, 
                                        Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, startkilo, 
                                        endkilo, year, date, starttime, endtime, speedlimit))

freeway_500000_withheavyrate <- subset(freeway_500000_withheavyrate, 
                            select = -c(startTime_millionSec, endTime_millionSec, pavement, cement, remark, upslope
                                        ,downslope, minradiuslength, one, Var_windspeed, Var_rain, 
                                        Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, startkilo, 
                                        endkilo, year, date, starttime, endtime, speedlimit, Speed_volume, Speed_PCU, index))


# convert crash values to 1
freeway_no1_north$crash[freeway_no1_north$crash > 1] <- 1
freeway_no3_north$crash[freeway_no3_north$crash > 1] <- 1
freeway_500000_withheavyrate$crash[freeway_500000_withheavyrate$crash > 1] <- 1


#find na values and remove them
freeway_no1_north$rain <- as.numeric(freeway_no1_north$rain)
freeway_no1_north$windspeed <- as.numeric(freeway_no1_north$windspeed)

freeway_no3_north$rain <- as.numeric(freeway_no3_north$rain)
freeway_no3_north$windspeed <- as.numeric(freeway_no3_north$windspeed)

freeway_500000_withheavyrate$rain <- as.numeric(freeway_500000_withheavyrate$rain)
freeway_500000_withheavyrate$windspeed <- as.numeric(freeway_500000_withheavyrate$windspeed)

summary(freeway_500000_withheavyrate)

#is.character(freeway_no1_north$windspeed)
#which(is.na(as.numeric(freeway_no1_north$rain))) 


# 將部分變數轉換為類別型態(factor)
freeway_no1_north$crash <- factor(freeway_no1_north$crash)
freeway_no1_north$minlane <- factor(freeway_no1_north$minlane)
freeway_no1_north$addlane <- factor(freeway_no1_north$addlane)
freeway_no1_north$continuouscurve <- factor(freeway_no1_north$continuouscurve)
freeway_no1_north$interchange <- factor(freeway_no1_north$interchange)
freeway_no1_north$tunnelin <- factor(freeway_no1_north$tunnelin)
freeway_no1_north$tunnelout <- factor(freeway_no1_north$tunnelout)
freeway_no1_north$shouderoallow <- factor(freeway_no1_north$shouderoallow)
freeway_no1_north$camera <- factor(freeway_no1_north$camera)
freeway_no1_north$service <- factor(freeway_no1_north$service)

freeway_no3_north$crash <- factor(freeway_no3_north$crash)
freeway_no3_north$minlane <- factor(freeway_no3_north$minlane)
freeway_no3_north$addlane <- factor(freeway_no3_north$addlane)
freeway_no3_north$continuouscurve <- factor(freeway_no3_north$continuouscurve)
freeway_no3_north$interchange <- factor(freeway_no3_north$interchange)
freeway_no3_north$tunnelin <- factor(freeway_no3_north$tunnelin)
freeway_no3_north$tunnelout <- factor(freeway_no3_north$tunnelout)
freeway_no3_north$shouderoallow <- factor(freeway_no3_north$shouderoallow)
freeway_no3_north$camera <- factor(freeway_no3_north$camera)
freeway_no3_north$service <- factor(freeway_no3_north$service)

freeway_500000_withheavyrate$crash <- factor(freeway_500000_withheavyrate$crash)
freeway_500000_withheavyrate$minlane <- factor(freeway_500000_withheavyrate$minlane)
freeway_500000_withheavyrate$addlane <- factor(freeway_500000_withheavyrate$addlane)
freeway_500000_withheavyrate$continuouscurve <- factor(freeway_500000_withheavyrate$continuouscurve)
freeway_500000_withheavyrate$interchange <- factor(freeway_500000_withheavyrate$interchange)
freeway_500000_withheavyrate$tunnelin <- factor(freeway_500000_withheavyrate$tunnelin)
freeway_500000_withheavyrate$tunnelout <- factor(freeway_500000_withheavyrate$tunnelout)
freeway_500000_withheavyrate$shouderoallow <- factor(freeway_500000_withheavyrate$shouderoallow)
freeway_500000_withheavyrate$camera <- factor(freeway_500000_withheavyrate$camera)
freeway_500000_withheavyrate$service <- factor(freeway_500000_withheavyrate$service)


#切割資料集
freeway_no1_north_y <- subset(freeway_no1_north,select = c("crash"))
freeway_no1_north_x <- subset(freeway_no1_north,select = -crash)
summary(freeway_no1_north_x)

#seperate

fw500000_heavyrate_y <- subset(freeway_500000_withheavyrate,select = c("crash"))
fw500000_heavyrate_x <- subset(freeway_500000_withheavyrate,select = -crash)
summary(fw500000_heavyrate_y)


##查看資料型態
str(freeway_no1_north_x)
str(freeway_no1_north_y)

#
#  volume_S + volume_L + volume_T  + Speed_volume 
freeway_logistic_no1 <- glm(formula = crash ~ lane + minlane + addlane + totalwidth + inshoulder + outshoulder + shouderoallow + upslopelength 
                        + downslopelength + maxupslope + maxdownslope + curvelength + minradius + continuouscurve + camera + service + interchange 
                        + PCU + Speed_PCU + heavy_rate + volume + volume_S + volume_L + volume_T
                        + windspeed + rain, data = freeway_no1_north, family = binomial(link = "logit"))

#freeway_logistic <- glm(formula = crash ~ heavy_rate, data = freeway_no1_north, family = binomial(link = "logit"))

summary(freeway_logistic_no1)



freeway_logistic_no3 <- glm(formula = crash ~ lane + minlane + addlane + totalwidth + inshoulder + outshoulder + shouderoallow + upslopelength 
                            + downslopelength + maxupslope + maxdownslope + curvelength + minradius + continuouscurve + camera + service + interchange 
                            + PCU + Speed_PCU + heavy_rate 
                            + windspeed + rain, data = freeway_no3_north, family = binomial(link = "logit"))

summary(freeway_logistic_no3)


fw_logistic_500000_withheavyrate <- glm(formula = crash ~ lane + minlane + addlane + totalwidth + inshoulder + outshoulder + shouderoallow + upslopelength 
                                        + downslopelength + maxupslope + maxdownslope + curvelength + minradius + continuouscurve + camera + service + interchange 
                                        + PCU + heavy_rate + volume + volume_S + volume_L + volume_T + windspeed + rain, data = freeway_500000_withheavyrate, family = binomial(link = "logit"))

summary(fw_logistic_500000_withheavyrate)


