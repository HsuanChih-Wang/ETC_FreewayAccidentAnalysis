freewayNo1_2020_all <- read.csv("C:/Users/WangRabbit/Documents/GitHub/ETC_FreewayAccidentAnalysis/output/fw1_2020_north_final(afterSQL).csv", sep=",")

# remove columns which either contain same value or are unused
freewayNo1_2020_all <- subset(freewayNo1_2020_all, 
                            select = -c(num, pavement, cement, remark, minradiuslength, one, 
                                        Var_windspeed, Var_rain, Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, 
                                        startkilo, endkilo, starttime, startTime_millionSec, endtime, endTime_millionSec, 
                                        speedlimit, fw1_northcol, index))

## remove highly correlated coefficients
freewayNo1_2020_all <- subset(freewayNo1_2020_all, 
                              select = -c(totalwidth, lanewidth, maxdownslope, volume, volume_S, volume_L, volume_T))

freewayNo1_2020_all <- subset(freewayNo1_2020_all, 
                              select = -c(Speed_volume, Speed_PCU))

freewayNo1_2020_all <- subset(freewayNo1_2020_all, 
                              select = -c(year, date))

# convert crash values to 1
freewayNo1_2020_all$crash[freewayNo1_2020_all$crash > 1] <- 1

#find na values and remove them
freewayNo1_2020_all$rain <- as.numeric(freewayNo1_2020_all$rain)
freewayNo1_2020_all$windspeed <- as.numeric(freewayNo1_2020_all$windspeed)

summary(freewayNo1_2020_all)

# convert numeric features into factor features
freewayNo1_2020_all$crash <- factor(freewayNo1_2020_all$crash)
# freewayNo1_2020_all$lane <- factor(freewayNo1_2020_all$lane)
freewayNo1_2020_all$minlane <- factor(freewayNo1_2020_all$minlane)
freewayNo1_2020_all$addlane <- factor(freewayNo1_2020_all$addlane)
freewayNo1_2020_all$continuouscurve <- factor(freewayNo1_2020_all$continuouscurve)
freewayNo1_2020_all$interchange <- factor(freewayNo1_2020_all$interchange)
freewayNo1_2020_all$tunnelin <- factor(freewayNo1_2020_all$tunnelin)
freewayNo1_2020_all$tunnelout <- factor(freewayNo1_2020_all$tunnelout)
freewayNo1_2020_all$shouderoallow <- factor(freewayNo1_2020_all$shouderoallow)
freewayNo1_2020_all$camera <- factor(freewayNo1_2020_all$camera)
freewayNo1_2020_all$service <- factor(freewayNo1_2020_all$service)
freewayNo1_2020_all$crash <- factor(freewayNo1_2020_all$crash)
freewayNo1_2020_all$DayType <- factor(freewayNo1_2020_all$DayType)
freewayNo1_2020_all$PeakHour <- factor(freewayNo1_2020_all$PeakHour)
freewayNo1_2020_all$Hour <- factor(freewayNo1_2020_all$Hour)

# 
hasCrash <- which(freewayNo1_2020_all$crash == 1)
hasNoCrash <- which(freewayNo1_2020_all$crash == 0)
noCrash.downsample <- sample(hasNoCrash, length(hasCrash) * 10)
freewayNo1_2020.down <- freewayNo1_2020_all[c(noCrash.downsample, hasCrash),]


# formulate logistic regression

fw_logistic_No1_2020_all <- glm(formula = crash ~ lane + minlane + addlane + inshoulder + outshoulder + upslope + downslope
                                + upslopelength + downslopelength + maxupslope + curvelength + minradius + continuouscurve
                                + interchange + tunnellength + tunnelin + tunnelout + shouderoallow + camera + service + windspeed
                                + rain + PCU + heavy_rate + DayType + PeakHour, data = freewayNo1_2020_all, family = binomial(link = "logit"))

summary(fw_logistic_No1_2020_all)

fw_logistic_No1_2020_all.down <- glm(formula = crash ~ lane + minlane + addlane + inshoulder + outshoulder + upslope + downslope
                                               + upslopelength + downslopelength + maxupslope + curvelength + minradius + continuouscurve
                                               + interchange + tunnellength + tunnelin + tunnelout + shouderoallow + camera + service + windspeed
                                               + rain + PCU + heavy_rate + DayType + PeakHour
                                               , data = freewayNo1_2020.down, family = binomial(link = "logit"))

summary(fw_logistic_No1_2020_all.down)


