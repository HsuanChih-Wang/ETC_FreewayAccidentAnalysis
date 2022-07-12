freewayNo3_2020_all <- read.csv("C:/Users/WangRabbit/Documents/GitHub/ETC_FreewayAccidentAnalysis/output/fw3_2020_north_final(afterSQL).csv", sep=",")

# remove columns which either contain same value or are unused
freewayNo3_2020_all <- subset(freewayNo3_2020_all, 
                            select = -c(num, pavement, cement, remark, minradiuslength, one, 
                                        Var_windspeed, Var_rain, Var_volume, Var_PCU, Var_Speed_volume, Var_Speed_PCU, 
                                        startkilo, endkilo, starttime, endtime, 
                                        speedlimit, index))

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

# formulate logistic regression

fw_logistic_No3_2020_all <- glm(formula = crash ~ lane + minlane + addlane + totalwidth + inshoulder + outshoulder + shouderoallow + upslopelength 
                                        + downslopelength + maxupslope + maxdownslope + curvelength + minradius + continuouscurve + camera + service + interchange 
                                        + PCU + heavy_rate + volume  + windspeed + rain + DayType + PeakHour, data = freewayNo3_2020_all, family = binomial(link = "logit"))

summary(fw_logistic_No3_2020_all)
