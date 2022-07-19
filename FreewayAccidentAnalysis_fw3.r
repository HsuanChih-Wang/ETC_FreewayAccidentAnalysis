freewayNo3_2020_all <- read.csv("C:/Users/WangRabbit/Documents/GitHub/ETC_FreewayAccidentAnalysis/output/STEP3. after_add_density/FW3_North_All(afterSQL).csv", sep=",")


# remove columns which either contain same value or are unused
freewayNo3_2020_all <- subset(freewayNo3_2020_all, 
                              select = -c(other, num, pavement, cement, remark, minradiuslength, one, 
                                          Var_windspeed, Var_rain, Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, 
                                          startkilo, endkilo, starttime, endtime, 
                                          speedlimit, index))

## remove highly correlated coefficients
freewayNo3_2020_all <- subset(freewayNo3_2020_all, 
                              select = -c(maxupslope, maxdownslope, volume, volume_S, volume_L, volume_T))

freewayNo3_2020_all <- subset(freewayNo3_2020_all, 
                              select = -c(Speed_volume, Speed_PCU))

freewayNo3_2020_all <- subset(freewayNo3_2020_all, 
                              select = -c(year, date))

# convert crash values to 1
freewayNo3_2020_all$crash[freewayNo3_2020_all$crash > 1] <- 1

#find na values and remove them
freewayNo3_2020_all$rain <- as.numeric(freewayNo3_2020_all$rain)
freewayNo3_2020_all$windspeed <- as.numeric(freewayNo3_2020_all$windspeed)

summary(freewayNo3_2020_all)

# convert numeric features into factor features
freewayNo3_2020_all$crash <- factor(freewayNo3_2020_all$crash)
freewayNo3_2020_all$minlane <- factor(freewayNo3_2020_all$minlane)
freewayNo3_2020_all$addlane <- factor(freewayNo3_2020_all$addlane)
freewayNo3_2020_all$continuouscurve <- factor(freewayNo3_2020_all$continuouscurve)
freewayNo3_2020_all$interchange <- factor(freewayNo3_2020_all$interchange)
freewayNo3_2020_all$tunnelin <- factor(freewayNo3_2020_all$tunnelin)
freewayNo3_2020_all$tunnelout <- factor(freewayNo3_2020_all$tunnelout)
freewayNo3_2020_all$shouderoallow <- factor(freewayNo3_2020_all$shouderoallow)
freewayNo3_2020_all$camera <- factor(freewayNo3_2020_all$camera)
freewayNo3_2020_all$service <- factor(freewayNo3_2020_all$service)
freewayNo3_2020_all$date <- factor(freewayNo3_2020_all$date)
freewayNo3_2020_all$crash <- factor(freewayNo3_2020_all$crash)
freewayNo3_2020_all$DayType <- factor(freewayNo3_2020_all$DayType)
freewayNo3_2020_all$PeakHour <- factor(freewayNo3_2020_all$PeakHour)
freewayNo3_2020_all$Hour <- factor(freewayNo3_2020_all$Hour)
freewayNo3_2020_all$CrashType <- factor(freewayNo3_2020_all$CrashType)


# 
hasCrash <- which(freewayNo3_2020_all$crash == 1)
hasNoCrash <- which(freewayNo3_2020_all$crash == 0)
noCrash.downsample <- sample(hasNoCrash, length(hasCrash) * 1)
freewayNo3_2020.down <- freewayNo3_2020_all[c(noCrash.downsample, hasCrash),]


# formulate logistic regression
fw_logistic_No3_2020_all <- glm(formula = crash ~ lane + minlane + addlane + totalwidth + lanewidth
                                + inshoulder + outshoulder + upslope + downslope + upslopelength + downslopelength
                                + curvelength + minradius + continuouscurve + interchange + windspeed + rain
                                + PCU + heavy_rate + DayType + Hour, data = freewayNo3_2020_all, family = binomial(link = "logit"))

summary(fw_logistic_No3_2020_all)

#
fw_logistic_No3_2020_all.down <- glm(formula = crash ~ lane + minlane + addlane + inshoulder + outshoulder + upslope + downslope
                                     + upslopelength + downslopelength + curvelength + minradius + continuouscurve
                                     + interchange + shouderoallow + camera + service + windspeed
                                     + rain + PCU + Density_byVehicle_S_Speed + heavy_rate + DayType + PeakHour, data = freewayNo3_2020.down, family = binomial(link = "logit"))

summary(fw_logistic_No3_2020_all.down)

# 
library(pscl)
pR2(fw_logistic_No3_2020_all.down)





