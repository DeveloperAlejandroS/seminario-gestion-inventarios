-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: inventario_pymes
-- ------------------------------------------------------
-- Server version	8.0.44

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

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'Fusibles','Componentes de protección eléctrica (vidrio, botella, etc.)',1),(2,'Semiconductores de Protección','Diodos TVS y otros componentes de supresión de picos',1),(3,'Módulos de Relevadores','Módulos Relay para control de potencia',1),(4,'Módulos de Sensores y Comunicación','Módulos específicos de la serie 10x (Grove/Seeed u otros)',1),(5,'Módulos de Radiofrecuencia','Módulos de comunicación inalámbrica (RFM95W, LoRa, etc.)',1),(6,'Placas Arduino','Placas de desarrollo y Shields del ecosistema Arduino',1),(7,'Placas Raspberry Pi','Computadoras de placa única (SBC) y accesorios principales',1),(8,'Controladores Especializados','Controladores de motores o pantallas (Adafruit y similares)',1),(9,'Cajas y Carcasas','Estuches y protectores para placas de desarrollo',1),(10,'Cables y Conectividad','Cables de video, datos y alimentación (HDMI, USB, etc.)',1);
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos`
--

DROP TABLE IF EXISTS `movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `tipo` enum('entrada','salida') COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_movimiento` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `producto_id` (`producto_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `movimientos_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `movimientos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos`
--

LOCK TABLES `movimientos` WRITE;
/*!40000 ALTER TABLE `movimientos` DISABLE KEYS */;
INSERT INTO `movimientos` VALUES (15,36,1,'entrada','2025-12-18 02:25:47'),(16,1,1,'entrada','2025-12-18 03:03:31');
/*!40000 ALTER TABLE `movimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `categoria_id` int DEFAULT NULL,
  `stock` int DEFAULT '0',
  `stock_minimo` int DEFAULT '0',
  `activo` tinyint(1) DEFAULT '1',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  `precio` decimal(10,2) NOT NULL DEFAULT '0.00',
  `imagen` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_producto_categoria` (`categoria_id`),
  KEY `idx_productos_activo` (`activo`),
  CONSTRAINT `fk_producto_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Transistor 2N2222A','Transistor NPN de propósito general, empaque TO-92.',2,200,500,1,'2025-12-17 21:45:08',150.00,'None'),(2,'Regulador de Voltaje L7805','Regulador de voltaje lineal 5V 1.5A.',2,85,0,1,'2025-12-17 21:45:08',950.00,NULL),(3,'Sensor de Humedad DHT22','Sensor digital de temperatura y humedad de alta precisión.',4,30,0,1,'2025-12-17 21:45:08',6500.00,NULL),(4,'Módulo Joystick XY','Módulo de palanca analógica para control de robots.',4,15,0,1,'2025-12-17 21:45:08',3200.00,NULL),(5,'Sensor de Nivel de Agua','Módulo de detección de gotas de lluvia o profundidad.',4,22,0,1,'2025-12-17 21:45:08',1800.00,NULL),(6,'Raspberry Pi Pico','Microcontrolador RP2040 de doble núcleo con pines soldados.',5,40,0,1,'2025-12-17 21:45:08',9500.00,NULL),(7,'NodeMCU ESP8266','Placa de desarrollo con WiFi integrado y puerto Micro USB.',5,55,0,1,'2025-12-17 21:45:08',7200.00,NULL),(8,'Arduino Nano V3','Versión compacta del Arduino Uno con chip ATmega328P.',5,60,0,1,'2025-12-17 21:45:08',6800.00,NULL),(9,'Digispark ATTINY85','Mini placa de desarrollo USB ultra compacta.',5,25,0,1,'2025-12-17 21:45:08',4500.00,NULL),(10,'Módulo Relé 4 Canales','Módulo con optoacopladores para control de cargas AC.',3,12,0,1,'2025-12-17 21:45:08',12500.00,NULL),(11,'Driver Motor A4988','Controlador de motor paso a paso con disipador.',3,35,0,1,'2025-12-17 21:45:08',2800.00,NULL),(12,'Módulo Mosfet IRF520','Driver de potencia para control PWM de motores o LEDs.',3,20,0,1,'2025-12-17 21:45:08',3100.00,NULL),(13,'Carcasa para Arduino Uno','Caja de acrílico transparente con tornillería.',7,15,0,1,'2025-12-17 21:45:08',4200.00,NULL),(14,'Ventilador 5V 30x30mm','Cooler para Raspberry Pi o módulos de potencia.',7,28,0,1,'2025-12-17 21:45:08',2500.00,NULL),(15,'Pack Resistencias 1/4W','Kit de 600 resistencias de valores variados.',7,10,0,1,'2025-12-17 21:45:08',18500.00,NULL),(16,'Batería LiPo 3.7V 1200mAh','Batería recargable para proyectos portátiles.',7,14,0,1,'2025-12-17 21:45:08',15800.00,NULL),(17,'Sensor de Color TCS3200','Detector de color con salida de frecuencia.',4,8,0,1,'2025-12-17 21:45:08',8900.00,NULL),(18,'Módulo GPS NEO-6M','Módulo de posicionamiento global con antena cerámica.',4,11,0,1,'2025-12-17 21:45:08',24500.00,NULL),(19,'Lector RFID RC522','Módulo de lectura/escritura 13.56MHz con tarjeta y llavero.',4,24,0,1,'2025-12-17 21:45:08',9800.00,NULL),(20,'Sensor de Sonido Big Sound','Detección de intensidad sonora con salida digital/analógica.',4,19,0,1,'2025-12-17 21:45:08',2600.00,NULL),(21,'Pantalla OLED 0.96 Pulgadas','Display monocromático comunicación I2C.',6,32,0,1,'2025-12-17 21:45:08',7500.00,NULL),(22,'Shield CNC V3','Placa de expansión para máquinas CNC y grabado láser.',6,7,0,1,'2025-12-17 21:45:08',5400.00,NULL),(23,'Módulo Matriz LED 8x8 MAX7219','Display de puntos rojos en cascada.',6,18,0,1,'2025-12-17 21:45:08',6200.00,NULL),(24,'Potenciómetro 10K Ohm','Potenciómetro rotativo lineal con perilla.',2,100,0,1,'2025-12-17 21:45:08',850.00,NULL),(25,'Encoder Rotativo EC11','Sensor de rotación infinita con pulsador.',4,30,0,1,'2025-12-17 21:45:08',3800.00,NULL),(26,'Sensor de Pulso Cardiaco','Sensor óptico para monitoreo de ritmo cardiaco.',4,13,0,1,'2025-12-17 21:45:08',11500.00,NULL),(27,'Buzzer Activo 5V','Zumbador piezoeléctrico de tono continuo.',3,90,0,1,'2025-12-17 21:45:08',450.00,NULL),(28,'Teclado Matricial 4x1','Tira de 4 botones táctiles independientes.',4,40,0,1,'2025-12-17 21:45:08',1200.00,NULL),(29,'Celda de Carga 5kg','Sensor de peso con amplificador HX711 incluido.',4,6,0,1,'2025-12-17 21:45:08',18900.00,NULL),(30,'Módulo Lector MicroSD','Interfaz SPI para almacenamiento de datos.',6,25,0,1,'2025-12-17 21:45:08',2900.00,NULL),(31,'Convertidor DC-DC Buck','Módulo reductor de voltaje ajustable LM2596.',3,42,0,1,'2025-12-17 21:45:08',4800.00,NULL),(32,'Sensor de Llama','Módulo receptor infrarrojo para detección de fuego.',4,20,0,1,'2025-12-17 21:45:08',2100.00,NULL),(33,'Fotorresistencia LDR','Resistor dependiente de luz 5mm.',2,500,0,1,'2025-12-17 21:45:08',100.00,NULL),(34,'Módulo Inclinación SW-520D','Sensor de bola para detección de vibración o vuelco.',4,35,0,1,'2025-12-17 21:45:08',1600.00,NULL),(35,'Kit de Herramientas Básico','Pinzas, cautín 40W y soldadura de estaño.',7,5,0,1,'2025-12-17 21:45:08',45000.00,NULL),(36,'Fusible de Cartucho de Vidrio','Littelfuse 0217.315HXP – 315 mA, 250 V, Acción Rápida',1,5,0,1,'2025-12-17 21:45:21',1000000.00,NULL),(37,'Fusible Tipo Botella','1 Amperio 125VAC/VDC',1,10,0,1,'2025-12-17 21:45:21',500.00,NULL),(38,'Diodo TVS','Diodo TVS @ 1,5 kW pico',2,20,0,1,'2025-12-17 21:45:21',0.00,NULL),(39,'Relay Module','Modulo de Relé 5V para arduino o microcontrolador',3,25,0,1,'2025-12-17 21:45:21',0.00,NULL),(40,'Controlador ADAFR-3416','Controla hasta 16 servos mediante Raspberry Pi',3,10,0,1,'2025-12-17 21:45:21',0.00,NULL),(41,'Modulo 102010129','Seeeduino LoRaWAN RHF76-052AM con GPS',4,8,0,1,'2025-12-17 21:45:21',0.00,NULL),(42,'Modulo 101020820','Sensor de gas multicanal v2 – Grove',4,12,0,1,'2025-12-17 21:45:21',0.00,NULL),(43,'Modulo 101020052','Sensor GSR – Grove (Respuesta galvánica)',4,9,0,1,'2025-12-17 21:45:21',0.00,NULL),(44,'Modulo 113020091','Módulo inalámbrico Grove-Wio-E5 LoRaWAN',4,16,0,1,'2025-12-17 21:45:21',0.00,NULL),(45,'Adafruit RFM95W','Módulo basado en SX1276 LoRa con interfaz SPI',4,40,0,1,'2025-12-17 21:45:21',0.00,NULL),(46,'Modulo A000007','Escudo Xbee para comunicación inalámbrica',4,14,0,1,'2025-12-17 21:45:21',0.00,NULL),(47,'Modulo 103020027','Mega Shield v1.2 – Grove expansor para Arduino Mega',6,30,0,1,'2025-12-17 21:45:21',0.00,NULL),(48,'Modulo 103030000','Grove Base Shield V2.1 para Arduino',6,18,0,1,'2025-12-17 21:45:21',0.00,NULL),(49,'Modulo 103020027 v1.6','Mega Shield v1.6 – Grove expansor para Arduino Mega',6,22,0,1,'2025-12-17 21:45:21',0.00,NULL),(50,'Arduino Ethernet Shield 2','Shield de Arduino para conexión Ethernet',6,20,0,1,'2025-12-17 21:45:21',0.00,NULL),(51,'Arduino Leonardo','Microcontrolador ATmega32u4, 5V',5,35,0,1,'2025-12-17 21:45:21',0.00,NULL),(52,'Arduino UNO R4 WiFi','Mayor memoria y reloj, soporte WiFi',5,11,0,1,'2025-12-17 21:45:21',0.00,NULL),(53,'Raspberry Pi 4 1GB','Quad Core Cortex-A72, 1GB RAM',5,28,0,1,'2025-12-17 21:45:21',0.00,NULL),(54,'Estuche Argon ONE','Estuche con HDMI y ventilador para Raspberry Pi 4',7,50,0,1,'2025-12-17 21:45:21',0.00,NULL),(55,'Cable HDMI 1.5m','Cable HDMI compatible multi-dispositivo',7,60,0,1,'2025-12-17 21:45:21',0.00,NULL);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin'),(2,'operador');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rol_id` int NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `creado_en` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`),
  KEY `fk_usuario_rol` (`rol_id`),
  KEY `idx_usuarios_activo` (`activo`),
  CONSTRAINT `fk_usuario_rol` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Administrador General','admin@inventario.local','$2b$12$5bs87z7nxooLa/f.1v7/uuhAeblFTtsX8D4zTs2X/fdP5uT8SpOc.',1,1,'2025-12-17 13:44:37'),(2,'Alejandro','alejandro@inventario.local','$2b$12$K5umFkzOhbGPuvlE9C85q.GfoEq2K2ux6YBERHaTNUvrBssJP.geC',2,1,'2025-12-17 14:44:07'),(3,'Oscar David','oscard@inventario.local','$2b$12$ks9Y6OXwqP3VVaSRA0ZVM.HHaxfbtYRW4bbvGH3xLkcj.nGLruXyi',2,1,'2025-12-17 20:01:14'),(4,'Sebastian Felipe','Sebasf@inventario.local','$2b$12$IPBx4xbxP.XkgogX7McM1O2dN43uB2pSEMOwG.Gl7NlvIiupKbzwy',1,1,'2025-12-17 20:02:18'),(5,'Maria F.','mariaf@inventario.local','$2b$12$0ZJV4SmFRq.K2geJyQmQ4u2oeqFQxQVOqHP59kBAWht0VdJq9rjlC',1,1,'2025-12-17 21:37:29');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-18 11:27:20
