CREATE DATABASE  IF NOT EXISTS `judiciary_case_management` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `judiciary_case_management`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: judiciary_case_management
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '72ae2940-af9c-11f0-9800-74d4dd6eaf35:1-528';

--
-- Table structure for table `case`
--

DROP TABLE IF EXISTS `case`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case` (
  `case_id` int NOT NULL AUTO_INCREMENT,
  `case_number` varchar(50) NOT NULL,
  `case_type` varchar(50) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `filing_date` date NOT NULL,
  `priority_level` varchar(20) NOT NULL DEFAULT 'Medium',
  `description` text NOT NULL,
  `judge_id` int NOT NULL,
  `clerk_id` int NOT NULL,
  PRIMARY KEY (`case_id`),
  UNIQUE KEY `case_number` (`case_number`),
  KEY `idx_case_status` (`status`),
  KEY `idx_case_type` (`case_type`),
  KEY `idx_case_filing_date` (`filing_date`),
  KEY `idx_case_priority` (`priority_level`),
  KEY `idx_case_judge` (`judge_id`),
  KEY `idx_case_clerk` (`clerk_id`),
  CONSTRAINT `fk_case_clerk` FOREIGN KEY (`clerk_id`) REFERENCES `clerk` (`clerk_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_case_judge` FOREIGN KEY (`judge_id`) REFERENCES `judge` (`judge_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_case_status` CHECK ((`status` in (_utf8mb4'Pending',_utf8mb4'In Progress',_utf8mb4'Hearing Scheduled',_utf8mb4'Under Review',_utf8mb4'Closed',_utf8mb4'Dismissed',_utf8mb4'Settled'))),
  CONSTRAINT `chk_case_type` CHECK ((`case_type` in (_utf8mb4'Civil',_utf8mb4'Criminal',_utf8mb4'Family',_utf8mb4'Constitutional',_utf8mb4'Tax',_utf8mb4'Labor',_utf8mb4'Property'))),
  CONSTRAINT `chk_priority_level` CHECK ((`priority_level` in (_utf8mb4'Low',_utf8mb4'Medium',_utf8mb4'High',_utf8mb4'Urgent')))
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `case`
--

LOCK TABLES `case` WRITE;
/*!40000 ALTER TABLE `case` DISABLE KEYS */;
INSERT INTO `case` VALUES (1,'CIV/2024/001','Civil','In Progress','2024-01-15','High','Property dispute between two neighbors regarding boundary wall construction',1,1),(2,'CRM/2024/002','Criminal','In Progress','2024-01-20','Urgent','Theft case involving electronic goods worth 5 lakhs',2,2),(3,'FAM/2024/003','Family','Hearing Scheduled','2024-02-01','Medium','Divorce petition with child custody dispute',3,3),(4,'CIV/2024/004','Civil','In Progress','2024-02-10','Low','Contract breach case between business partners',4,1),(5,'CRM/2024/005','Criminal','Hearing Scheduled','2024-02-15','High','Assault case with multiple witnesses',5,2),(6,'PRO/2024/006','Property','Pending','2024-02-20','Medium','Land acquisition dispute with government',1,6),(7,'TAX/2024/007','Tax','Hearing Scheduled','2024-03-01','High','Tax evasion case involving corporate entity',6,4),(8,'LAB/2024/008','Labor','Pending','2024-03-05','Medium','Unfair termination and compensation claim',7,5),(9,'CIV/2024/009','Civil','Closed','2024-01-10','Low','Debt recovery case settled through mediation',8,1),(10,'CRM/2024/010','Criminal','Dismissed','2024-01-25','Medium','False accusation case dismissed due to lack of evidence',2,2),(11,'FAM/2024/011','Family','Settled','2024-02-05','Low','Property division among siblings settled amicably',9,3),(12,'CIV/2024/012','Civil','In Progress','2024-03-10','High','Medical negligence claim against hospital',10,6),(13,'CRM/2024/013','Criminal','Hearing Scheduled','2024-03-15','Urgent','Fraud case involving financial transactions',5,2),(14,'PRO/2024/014','Property','Hearing Scheduled','2024-03-20','Medium','Tenant eviction case due to non-payment of rent',1,1),(15,'CON/2024/015','Constitutional','Under Review','2024-03-25','High','PIL regarding environmental protection',6,4),(16,'CIV/2026/999','Civil','Closed','2026-03-10','Medium','This is a test case to demonstrate a successful multi-table ACID transaction.',1,1);
/*!40000 ALTER TABLE `case` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_case_status_audit` AFTER UPDATE ON `case` FOR EACH ROW BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO CASE_STATUS_HISTORY (status, update_date, remarks, case_id)
        VALUES (NEW.status, CURDATE(), CONCAT('Status changed from ', OLD.status, ' to ', NEW.status), NEW.case_id);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `case_lawyer`
--

DROP TABLE IF EXISTS `case_lawyer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case_lawyer` (
  `case_id` int NOT NULL,
  `lawyer_id` int NOT NULL,
  PRIMARY KEY (`case_id`,`lawyer_id`),
  KEY `fk_case_lawyer_lawyer` (`lawyer_id`),
  CONSTRAINT `fk_case_lawyer_case` FOREIGN KEY (`case_id`) REFERENCES `case` (`case_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_case_lawyer_lawyer` FOREIGN KEY (`lawyer_id`) REFERENCES `lawyer` (`lawyer_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `case_lawyer`
--

LOCK TABLES `case_lawyer` WRITE;
/*!40000 ALTER TABLE `case_lawyer` DISABLE KEYS */;
INSERT INTO `case_lawyer` VALUES (1,1),(6,1),(9,1),(16,1),(2,2),(5,2),(10,2),(3,3),(11,3),(4,4),(7,5),(15,6),(8,7),(1,8),(6,8),(14,8),(12,9),(2,10),(13,10),(3,11),(4,12),(9,13),(5,14),(7,15);
/*!40000 ALTER TABLE `case_lawyer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `case_party`
--

DROP TABLE IF EXISTS `case_party`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case_party` (
  `case_id` int NOT NULL,
  `party_id` int NOT NULL,
  PRIMARY KEY (`case_id`,`party_id`),
  KEY `fk_case_party_party` (`party_id`),
  CONSTRAINT `fk_case_party_case` FOREIGN KEY (`case_id`) REFERENCES `case` (`case_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_case_party_party` FOREIGN KEY (`party_id`) REFERENCES `party` (`party_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `case_party`
--

LOCK TABLES `case_party` WRITE;
/*!40000 ALTER TABLE `case_party` DISABLE KEYS */;
INSERT INTO `case_party` VALUES (1,1),(9,1),(16,1),(1,2),(14,2),(3,3),(12,3),(3,4),(5,5),(15,5),(2,6),(10,6),(2,7),(4,8),(9,8),(4,9),(14,9),(6,10),(11,10),(6,11),(11,11),(7,12),(13,12),(5,13),(13,13),(5,14),(8,15);
/*!40000 ALTER TABLE `case_party` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `case_status_history`
--

DROP TABLE IF EXISTS `case_status_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case_status_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `status` varchar(50) NOT NULL,
  `update_date` date NOT NULL,
  `remarks` text,
  `case_id` int NOT NULL,
  PRIMARY KEY (`history_id`),
  KEY `idx_history_case` (`case_id`),
  KEY `idx_history_date` (`update_date`),
  CONSTRAINT `fk_history_case` FOREIGN KEY (`case_id`) REFERENCES `case` (`case_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_history_status` CHECK ((`status` in (_utf8mb4'Pending',_utf8mb4'In Progress',_utf8mb4'Hearing Scheduled',_utf8mb4'Under Review',_utf8mb4'Closed',_utf8mb4'Dismissed',_utf8mb4'Settled')))
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `case_status_history`
--

LOCK TABLES `case_status_history` WRITE;
/*!40000 ALTER TABLE `case_status_history` DISABLE KEYS */;
INSERT INTO `case_status_history` VALUES (1,'Pending','2024-01-15','Case filed and registered',1),(2,'Pending','2024-01-20','Case registered under criminal procedures',2),(3,'In Progress','2024-02-15','Investigation started',2),(4,'Pending','2024-02-01','Divorce petition submitted',3),(5,'Hearing Scheduled','2024-03-10','First hearing scheduled',3),(6,'Pending','2024-02-10','Case documents submitted for review',4),(7,'Under Review','2024-03-15','Documents under judicial review',4),(8,'Pending','2024-02-15','FIR filed and case registered',5),(9,'Pending','2024-02-20','Land dispute case filed',6),(10,'In Progress','2024-03-10','Survey ordered for land measurement',6),(11,'Pending','2024-03-01','Tax case filed by revenue department',7),(12,'Hearing Scheduled','2024-03-28','Hearing date assigned',7),(13,'Pending','2024-03-05','Labor complaint registered',8),(14,'Pending','2024-01-10','Debt recovery case filed',9),(15,'In Progress','2024-02-20','Mediation process initiated',9),(16,'Closed','2024-03-15','Settlement reached between parties',9),(17,'Pending','2024-01-25','Criminal complaint registered',10),(18,'Dismissed','2024-03-10','Case dismissed due to insufficient evidence',10),(19,'Pending','2024-02-05','Property division dispute filed',11),(20,'Settled','2024-03-20','Amicable settlement reached',11),(21,'Pending','2024-03-10','Medical negligence case registered',12),(22,'In Progress','2024-03-25','Medical reports submitted for review',12),(23,'Pending','2024-03-15','Fraud case registered',13),(24,'Hearing Scheduled','2024-04-01','Court date assigned',13),(25,'Pending','2024-03-20','Eviction notice served',14),(26,'Pending','2024-03-25','PIL filed for environmental concerns',15),(27,'Under Review','2024-04-05','Expert committee report requested',15),(28,'In Progress','2026-03-14','Status automatically updated from Under Review to In Progress',4),(29,'Hearing Scheduled','2026-03-14','Status automatically updated from Pending to Hearing Scheduled',5),(30,'Pending','2026-03-14','Status automatically updated from In Progress to Pending',6),(31,'Closed','2026-03-14','Status automatically updated from Pending to Closed',16),(32,'In Progress','2026-03-14','Status automatically updated from Pending to In Progress',14),(33,'In Progress','2026-03-14','Status automatically updated from Pending to In Progress',1),(34,'In Progress','2026-03-14','Status changed from Pending to In Progress',1),(35,'Hearing Scheduled','2026-03-15','Status automatically updated from In Progress to Hearing Scheduled',14),(36,'Hearing Scheduled','2026-03-15','Status changed from In Progress to Hearing Scheduled',14);
/*!40000 ALTER TABLE `case_status_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clerk`
--

DROP TABLE IF EXISTS `clerk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clerk` (
  `clerk_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `department` varchar(50) NOT NULL,
  PRIMARY KEY (`clerk_id`),
  CONSTRAINT `chk_clerk_department` CHECK ((`department` in (_utf8mb4'Civil',_utf8mb4'Criminal',_utf8mb4'Family',_utf8mb4'Administrative',_utf8mb4'Registration'))),
  CONSTRAINT `chk_clerk_phone` CHECK (regexp_like(`phone`,_utf8mb4'^[0-9]{10,15}$'))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clerk`
--

LOCK TABLES `clerk` WRITE;
/*!40000 ALTER TABLE `clerk` DISABLE KEYS */;
INSERT INTO `clerk` VALUES (1,'Ramesh Gupta','9123456780','Civil'),(2,'Sanjay Yadav','9123456781','Criminal'),(3,'Pooja Nair','9123456782','Family'),(4,'Deepak Sharma','9123456783','Administrative'),(5,'Neha Singh','9123456784','Registration'),(6,'Arun Kumar','9123456785','Civil'),(7,'Ritu Malhotra','9123456786','Criminal'),(8,'Suresh Patil','9123456787','Family'),(9,'Anjali Reddy','9123456788','Administrative'),(10,'Manoj Tiwari','9123456789','Registration');
/*!40000 ALTER TABLE `clerk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hearing`
--

DROP TABLE IF EXISTS `hearing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hearing` (
  `hearing_id` int NOT NULL AUTO_INCREMENT,
  `hearing_date` date NOT NULL,
  `hearing_time` time NOT NULL,
  `hearing_status` varchar(50) NOT NULL DEFAULT 'Scheduled',
  `courtroom` varchar(20) NOT NULL,
  `case_id` int NOT NULL,
  PRIMARY KEY (`hearing_id`),
  UNIQUE KEY `uk_hearing_slot` (`hearing_date`,`hearing_time`,`courtroom`),
  KEY `idx_hearing_date` (`hearing_date`),
  KEY `idx_hearing_status` (`hearing_status`),
  KEY `idx_hearing_case` (`case_id`),
  CONSTRAINT `fk_hearing_case` FOREIGN KEY (`case_id`) REFERENCES `case` (`case_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_courtroom` CHECK (regexp_like(`courtroom`,_utf8mb4'^[A-Z0-9-]+$')),
  CONSTRAINT `chk_hearing_status` CHECK ((`hearing_status` in (_utf8mb4'Scheduled',_utf8mb4'In Progress',_utf8mb4'Completed',_utf8mb4'Postponed',_utf8mb4'Cancelled')))
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hearing`
--

LOCK TABLES `hearing` WRITE;
/*!40000 ALTER TABLE `hearing` DISABLE KEYS */;
INSERT INTO `hearing` VALUES (1,'2024-04-10','10:00:00','Completed','COURT-101',1),(2,'2024-04-10','11:30:00','Scheduled','COURT-102',2),(3,'2024-04-11','10:00:00','Scheduled','COURT-103',3),(4,'2024-04-11','14:00:00','Scheduled','COURT-101',4),(5,'2024-04-12','10:00:00','Scheduled','COURT-104',5),(6,'2024-04-12','11:30:00','Completed','COURT-105',6),(7,'2024-04-15','10:00:00','Scheduled','COURT-106',7),(8,'2024-04-15','14:00:00','Scheduled','COURT-107',8),(9,'2024-03-20','10:00:00','Completed','COURT-101',9),(10,'2024-03-20','11:30:00','Completed','COURT-102',9),(11,'2024-03-25','10:00:00','Completed','COURT-103',10),(12,'2024-04-05','10:00:00','Postponed','COURT-104',11),(13,'2024-04-16','10:00:00','Scheduled','COURT-108',12),(14,'2024-04-16','14:00:00','Scheduled','COURT-109',13),(15,'2024-04-17','10:00:00','Scheduled','COURT-110',14),(16,'2024-04-17','11:30:00','Scheduled','COURT-101',15),(17,'2024-04-18','10:00:00','Scheduled','COURT-102',1),(18,'2024-04-18','14:00:00','Scheduled','COURT-103',2),(19,'2024-04-19','10:00:00','Scheduled','COURT-104',12),(20,'2024-05-20','10:00:00','Scheduled','COURT-105',5),(21,'2026-03-16','02:05:00','Scheduled','COURT-104',14);
/*!40000 ALTER TABLE `hearing` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = cp850 */ ;
/*!50003 SET character_set_results = cp850 */ ;
/*!50003 SET collation_connection  = cp850_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_hearing_auto_status` AFTER INSERT ON `hearing` FOR EACH ROW BEGIN
    UPDATE `CASE` 
    SET status = 'Hearing Scheduled' 
    WHERE case_id = NEW.case_id AND status = 'Pending';
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `judge`
--

DROP TABLE IF EXISTS `judge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `judge` (
  `judge_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  `designation` varchar(50) NOT NULL,
  `court_name` varchar(100) NOT NULL,
  PRIMARY KEY (`judge_id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_judge_designation` (`designation`),
  KEY `idx_judge_court` (`court_name`),
  CONSTRAINT `chk_judge_designation` CHECK ((`designation` in (_utf8mb4'District Judge',_utf8mb4'Additional District Judge',_utf8mb4'Chief Judicial Magistrate',_utf8mb4'Civil Judge',_utf8mb4'Magistrate'))),
  CONSTRAINT `chk_judge_email` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')),
  CONSTRAINT `chk_judge_phone` CHECK (regexp_like(`phone`,_utf8mb4'^[0-9]{10,15}$'))
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `judge`
--

LOCK TABLES `judge` WRITE;
/*!40000 ALTER TABLE `judge` DISABLE KEYS */;
INSERT INTO `judge` VALUES (1,'Justice Rajesh Kumar','9876543210','rajesh.kumar@court.gov.in','District Judge','Delhi District Court'),(2,'Justice Priya Sharma','9876543211','priya.sharma@court.gov.in','Additional District Judge','Delhi District Court'),(3,'Justice Amit Patel','9876543212','amit.patel@court.gov.in','Chief Judicial Magistrate','Mumbai Magistrate Court'),(4,'Justice Sunita Verma','9876543213','sunita.verma@court.gov.in','Civil Judge','Bangalore Civil Court'),(5,'Justice Vikram Singh','9876543214','vikram.singh@court.gov.in','District Judge','Kolkata District Court'),(6,'Justice Meera Reddy','9876543215','meera.reddy@court.gov.in','Magistrate','Chennai Magistrate Court'),(7,'Justice Arjun Malhotra','9876543216','arjun.malhotra@court.gov.in','Additional District Judge','Hyderabad District Court'),(8,'Justice Kavita Joshi','9876543217','kavita.joshi@court.gov.in','Civil Judge','Pune Civil Court'),(9,'Justice Rahul Kapoor','9876543218','rahul.kapoor@court.gov.in','Chief Judicial Magistrate','Ahmedabad Magistrate Court'),(10,'Justice Anita Desai','9876543219','anita.desai@court.gov.in','District Judge','Jaipur District Court'),(12,'swaraaj krish','1234567890','swaraaj@gmail.com','district judge','civil'),(88,'aditya','2345678951','aditya@gmail.com','district judge','delhi district court');
/*!40000 ALTER TABLE `judge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lawyer`
--

DROP TABLE IF EXISTS `lawyer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lawyer` (
  `lawyer_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `email` varchar(100) NOT NULL,
  `specialization` varchar(100) NOT NULL,
  `bar_registration_number` varchar(50) NOT NULL,
  PRIMARY KEY (`lawyer_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `bar_registration_number` (`bar_registration_number`),
  KEY `idx_lawyer_specialization` (`specialization`),
  KEY `idx_lawyer_name` (`name`),
  CONSTRAINT `chk_lawyer_email` CHECK (regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')),
  CONSTRAINT `chk_lawyer_phone` CHECK (regexp_like(`phone`,_utf8mb4'^[0-9]{10,15}$')),
  CONSTRAINT `chk_lawyer_specialization` CHECK ((`specialization` in (_utf8mb4'Civil Law',_utf8mb4'Criminal Law',_utf8mb4'Family Law',_utf8mb4'Corporate Law',_utf8mb4'Tax Law',_utf8mb4'Constitutional Law',_utf8mb4'Labor Law',_utf8mb4'Property Law')))
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lawyer`
--

LOCK TABLES `lawyer` WRITE;
/*!40000 ALTER TABLE `lawyer` DISABLE KEYS */;
INSERT INTO `lawyer` VALUES (1,'Adv. Rajesh Verma','9871234560','rajesh.verma.adv@email.com','Civil Law','BAR/DL/2010/12345'),(2,'Adv. Meena Khanna','9871234561','meena.khanna.adv@email.com','Criminal Law','BAR/MH/2012/23456'),(3,'Adv. Sunil Reddy','9871234562','sunil.reddy.adv@email.com','Family Law','BAR/KA/2011/34567'),(4,'Adv. Priyanka Sharma','9871234563','priyanka.sharma.adv@email.com','Corporate Law','BAR/DL/2013/45678'),(5,'Adv. Anil Kumar','9871234564','anil.kumar.adv@email.com','Tax Law','BAR/WB/2014/56789'),(6,'Adv. Kavita Nair','9871234565','kavita.nair.adv@email.com','Constitutional Law','BAR/TN/2009/67890'),(7,'Adv. Vijay Malhotra','9871234566','vijay.malhotra.adv@email.com','Labor Law','BAR/TS/2015/78901'),(8,'Adv. Shalini Gupta','9871234567','shalini.gupta.adv@email.com','Property Law','BAR/MH/2010/89012'),(9,'Adv. Deepak Joshi','9871234568','deepak.joshi.adv@email.com','Civil Law','BAR/GJ/2016/90123'),(10,'Adv. Ritu Kapoor','9871234569','ritu.kapoor.adv@email.com','Criminal Law','BAR/RJ/2011/01234'),(11,'Adv. Harsh Patel','9871234570','harsh.patel.adv@email.com','Family Law','BAR/DL/2017/11223'),(12,'Adv. Neelam Singh','9871234571','neelam.singh.adv@email.com','Corporate Law','BAR/KA/2012/22334'),(13,'Adv. Rohit Agarwal','9871234572','rohit.agarwal.adv@email.com','Civil Law','BAR/MH/2018/33445'),(14,'Adv. Swati Desai','9871234573','swati.desai.adv@email.com','Criminal Law','BAR/WB/2013/44556'),(15,'Adv. Vikas Rao','9871234574','vikas.rao.adv@email.com','Tax Law','BAR/TN/2019/55667');
/*!40000 ALTER TABLE `lawyer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `party`
--

DROP TABLE IF EXISTS `party`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `party` (
  `party_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `party_type` varchar(50) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text NOT NULL,
  PRIMARY KEY (`party_id`),
  KEY `idx_party_type` (`party_type`),
  KEY `idx_party_name` (`name`),
  CONSTRAINT `chk_party_email` CHECK (((`email` is null) or regexp_like(`email`,_utf8mb4'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'))),
  CONSTRAINT `chk_party_phone` CHECK (((`phone` is null) or regexp_like(`phone`,_utf8mb4'^[0-9]{10,15}$'))),
  CONSTRAINT `chk_party_type` CHECK ((`party_type` in (_utf8mb4'Plaintiff',_utf8mb4'Defendant',_utf8mb4'Petitioner',_utf8mb4'Respondent',_utf8mb4'Witness',_utf8mb4'Complainant',_utf8mb4'Accused')))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `party`
--

LOCK TABLES `party` WRITE;
/*!40000 ALTER TABLE `party` DISABLE KEYS */;
INSERT INTO `party` VALUES (1,'Ramesh Kumar','Plaintiff','9988776655','ramesh.k@email.com','123 MG Road, Delhi, 110001'),(2,'Suresh Iyer','Defendant','9988776656','suresh.i@email.com','456 Brigade Road, Bangalore, 560001'),(3,'Anjali Mehta','Petitioner','9988776657','anjali.m@email.com','789 Marine Drive, Mumbai, 400001'),(4,'Vikram Chawla','Respondent','9988776658','vikram.c@email.com','321 Park Street, Kolkata, 700001'),(5,'Priya Deshmukh','Complainant','9988776659','priya.d@email.com','654 Anna Salai, Chennai, 600001'),(6,'Rahul Jain','Accused','9988776660','rahul.j@email.com','987 Jubilee Hills, Hyderabad, 500001'),(7,'Sneha Kapoor','Witness','9988776661','sneha.k@email.com','147 FC Road, Pune, 411001'),(8,'Amit Agarwal','Plaintiff','9988776662','amit.a@email.com','258 CG Road, Ahmedabad, 380001'),(9,'Kavita Saxena','Defendant','9988776663','kavita.s@email.com','369 MI Road, Jaipur, 302001'),(10,'Manish Gupta','Petitioner','9988776664','manish.g@email.com','741 Connaught Place, Delhi, 110001'),(11,'Roshni Verma','Respondent','9988776665','roshni.v@email.com','852 Lavelle Road, Bangalore, 560001'),(12,'Karan Malhotra','Complainant','9988776666','karan.m@email.com','963 Linking Road, Mumbai, 400001'),(13,'Divya Reddy','Accused','9988776667','divya.r@email.com','159 Salt Lake, Kolkata, 700001'),(14,'Arjun Pillai','Witness','9988776668','arjun.p@email.com','357 T Nagar, Chennai, 600001'),(15,'Neha Patel','Plaintiff','9988776669','neha.p@email.com','486 Banjara Hills, Hyderabad, 500001');
/*!40000 ALTER TABLE `party` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_users`
--

DROP TABLE IF EXISTS `system_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `reference_id` int NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  CONSTRAINT `chk_user_role` CHECK ((`role` in (_cp850'Clerk',_cp850'Judge',_cp850'Lawyer',_cp850'Party')))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_users`
--

LOCK TABLES `system_users` WRITE;
/*!40000 ALTER TABLE `system_users` DISABLE KEYS */;
INSERT INTO `system_users` VALUES (1,'clerk_ramesh','clerk123','Clerk',1),(2,'judge_rajesh','judge123','Judge',1),(3,'lawyer_verma','lawyer123','Lawyer',1),(4,'party_ramesh','party123','Party',1);
/*!40000 ALTER TABLE `system_users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-15  0:28:54
