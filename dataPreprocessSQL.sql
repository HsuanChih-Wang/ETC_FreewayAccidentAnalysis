/*
LOAD DATA INFILE 'D:/freewayData/fw1_north_new.csv' INTO TABLE fw1_north
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES */

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

/*
Create Index
ALTER TABLE fw1_north ADD INDEX startTime_index(startTime_millionSec)
*/



/*快速方法: 資料匯出成csv*/
/*
SELECT * INTO OUTFILE 'D:/freewayData/fw1_north_new_1.csv'
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY ''
  LINES TERMINATED BY '\n'
  FROM fw1_north; 
*/


