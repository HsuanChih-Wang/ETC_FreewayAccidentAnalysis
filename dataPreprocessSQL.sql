/*
LOAD DATA INFILE 'D:/freewayData/2020_fw1_north_All.csv' INTO TABLE fw1_2020_north_all_new
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES 
*/


/*
DELETE FROM accident_2020_no1_north WHERE right(發生日期,4) not in ('2020'); 
*/

/* concencate the data
UPDATE freeway.accident_2020_no1_north SET 發生日期 = concat(right(發生日期,4), '-',SUBSTRING_INDEX(發生日期, "-", 2)); 
UPDATE freeway.accident_2020 SET 發生日期 = concat(right(發生日期,4), '-',SUBSTRING_INDEX(發生日期, "-", 2));
*/

/*
LOAD DATA INFILE 'D:/freewayData/accidentData.csv' INTO TABLE accident
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES;
*/

/* Delete the column which the direction is not North 刪除方向非"北"的欄位
DELETE FROM accident_2020_no1_north WHERE 方向 not in ('北'); 
*/

/*
DELETE FROM accident_2020_no1_north WHERE 道路 not in ('國道1號'); 
*/

/*
CREATE TABLE fw1_north_new
AS
SELECT 
  * 
FROM fw1_north;
*/
 
/* Convert datetime to millionSecond 將日期時間轉換為毫秒格式
UPDATE accident_2020_no1_north as A SET A.millionSec=UNIX_TIMESTAMP(CONCAT(發生日期,' ' ,時,':' , 分));
UPDATE fw1_north as A SET A.startTime_millionSec = left(UNIX_TIMESTAMP(CONCAT(year,'/' ,date,' ' , starttime)), 10) ;
UPDATE fw1_north as A SET A.endTime_millionSec = left(UNIX_TIMESTAMP(CONCAT(year,'/' ,date,' ' , endtime)), 10) ;
*/

/*CREATE INDEX FOR THE TABLE (TO ACCELERATE SEARCHING PERFORMANCE)*/
/*
Create Index
ALTER TABLE fw1_north ADD INDEX startTime_index(startTime_millionSec)
Create Index dateIndex on fw1_2020_north_all(date);
*/



/*快速方法: 資料匯出成csv*/
SELECT * INTO OUTFILE 'D:/freewayData/fw1_north_new_1.csv'
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY ''
  LINES TERMINATED BY '\n'
  FROM fw1_north; 


/*CREATE A NEW TABLE WITH STRUCTURE THAT IS SIMILAR TO ANOTHER TABLE*/
/*
CREATE TABLE `fw1_2020_north_all` LIKE `fw1_north`;
*/


/*  Set DayType  0 = Workweek, 1 = Weekend, 2 = Holiday */ 
UPDATE freeway.fw1_2020_north_all as A SET A.DayType = 2 where A.date in ('01/01', '01/23', '01/24', '01/25', '01/26', '01/27', '01/28', '01/29',
				   '02/28', '02/29', '03/01', '04/02', '04/03', '04/04', '04/05',
                   '06/25', '06/26', '06/27', '06/28', '10/01', '10/02', '10/03', '10/04',
                   '10/09', '10/10', '10/11');

UPDATE freeway.fw1_2020_north_all as A SET A.DayType = 1 where A.date not in ('01/01', '01/24', '01/25', '01/26', '01/27', '01/28', '01/29',
				   '02/28', '02/29', '03/01', '04/02', '04/03', '04/04', '04/05',
                   '06/25', '06/26', '06/27', '06/28', '10/01', '10/02', '10/03', '10/04',
                   '10/09', '10/10', '10/11') and WEEKDAY(CONCAT(A.year,'/' , A.date)) > 4;
                   
UPDATE freeway.fw1_2020_north_all as A SET A.DayType = 0 where A.date not in ('01/01', '01/24', '01/25', '01/26', '01/27', '01/28', '01/29',
				   '02/28', '02/29', '03/01', '04/02', '04/03', '04/04', '04/05',
                   '06/25', '06/26', '06/27', '06/28', '10/01', '10/02', '10/03', '10/04',
                   '10/09', '10/10', '10/11') and WEEKDAY(CONCAT(A.year,'/' , A.date)) < 5;

/* Set Peakhour: Workweek */
UPDATE freeway.fw1_2020_north_all as A SET A.PeakHour = 1 
where A.DayType = 0 -- Workweek
	and (left(A.starttime,1) in (7,8) or left(A.starttime,2) in (17,18)); 
	-- Peakhour: 07:00~09:00 and 17:00~19:00 

/* Set Peakhour: Weekend*/ 
UPDATE freeway.fw1_2020_north_all as A SET A.PeakHour = 1 
where A.DayType = 1 -- Weekend
	and (left(A.starttime,2) in (10,12) or left(A.starttime,2) in (14,16)); 
	-- Peakhour: 10:00~12:00 and 14:00~16:00 
    

/* Find peak 5 min (i.e. MAX PCU) of each road segment on a specific day*/ 
SELECT a.startkilo, a.endkilo, a.year, a.date, a.starttime, a.endtime, a.volume, a.PCU
FROM freeway.fw1_2020_north_all as a
INNER JOIN (
    SELECT startkilo, endkilo, year, date, starttime, endtime, volume, max(PCU) PCU
    FROM freeway.fw1_2020_north_all
    where date in ('01/02')
    GROUP BY startkilo, endkilo
) b ON a.startkilo = b.startkilo AND a.endkilo = b.endkilo AND a.PCU = b.PCU AND a.date = b.date;

