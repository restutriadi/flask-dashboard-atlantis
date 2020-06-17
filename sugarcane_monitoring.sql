-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 17, 2020 at 11:29 AM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sugarcane_monitoring`
--

-- --------------------------------------------------------

--
-- Table structure for table `citra_cwsi`
--

CREATE TABLE `citra_cwsi` (
  `id` int(50) UNSIGNED NOT NULL,
  `filename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `path` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `red_pixel` int(10) DEFAULT NULL,
  `orange_pixel` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `citra_cwsi`
--

INSERT INTO `citra_cwsi` (`id`, `filename`, `path`, `red_pixel`, `orange_pixel`) VALUES
(11, '20190720', '/static/assets/img/cwsi/20190720.png', 259, 540),
(12, '20190805', '/static/assets/img/cwsi/20190805.png', 222, 753),
(13, '20190618', '/static/assets/img/cwsi/20190618.png', 67, 277);

-- --------------------------------------------------------

--
-- Table structure for table `cwsi`
--

CREATE TABLE `cwsi` (
  `id` int(50) UNSIGNED NOT NULL,
  `filename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `a1` float DEFAULT NULL,
  `a2` float DEFAULT NULL,
  `b1` float DEFAULT NULL,
  `b2` float DEFAULT NULL,
  `c1` float DEFAULT NULL,
  `c2` float DEFAULT NULL,
  `d1` float DEFAULT NULL,
  `d2` float DEFAULT NULL,
  `e1` float DEFAULT NULL,
  `e2` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `cwsi`
--

INSERT INTO `cwsi` (`id`, `filename`, `a1`, `a2`, `b1`, `b2`, `c1`, `c2`, `d1`, `d2`, `e1`, `e2`) VALUES
(1, '20171018', 0.181988, 0.181715, 0.180378, 0.181364, 0.180641, 0.180525, 0.184656, 0.18089, 0.180214, 0.18139),
(2, '20171103', 0.841346, 0.779892, 0.994949, 0.788383, 0.813462, 0.91689, 0.813094, 0.911515, 0.502561, 0.570813),
(3, '20171205', 0.363805, 0.264566, 0.680498, 0.240383, 0.718929, 0.700683, 0.447426, 0.783088, 0.327239, 0.288875),
(4, '20180106', 0.590791, 0.534253, 0.570987, 0.651257, 0.282136, 0.251513, 0.198656, 0.121154, 0.419949, 0.252692),
(5, '20180223', 0.131798, 0.0995526, 0.211321, 0.550464, 0.254183, 0.30453, 0.104676, 0.426122, 0.278644, 0.391104),
(6, '20180327', 0.423558, 0.412565, 0.901572, 0.481898, 0.65368, 0.638086, 0.671422, 0.705999, 0.51257, 0.432011),
(7, '20180428', 0.780204, 0.332082, 0.496755, 0.53133, 0.454626, 0.654665, 0.305357, 0.57826, 0.311569, 0.309938),
(8, '20180530', 0.39951, 0.283926, 0.472616, 0.417678, 0.455197, 0.269406, 0.321665, 0.355887, 0.267006, 0.28237),
(9, '20180615', 0.371378, 0.284006, 0.84395, 0.351024, 0.478738, 0.330588, 0.549555, 0.689732, 0.512908, 0.315893),
(10, '20180701', 0.387946, 0.335721, 0.798738, 0.344409, 0.891587, 0.459014, 0.538887, 0.79018, 0.954538, 0.454193),
(11, '20180818', 0.563337, 0.387549, 0.598461, 0.405876, 0.814276, 0.82948, 0.724023, 0.777451, 0.676035, 0.647334),
(12, '20180903', 0.631618, 0.486569, 0.584977, 0.454236, 0.787479, 0.889524, 0.791486, 0.738239, 0.77389, 0.485409),
(13, '20181005', 0.753059, 0.733475, 0.691124, 0.502857, 0.677532, 0.762086, 0.551507, 0.492448, 0.892188, 0.636731),
(14, '20181122', 0.772172, 0.751926, 0.710544, 0.66261, 0.679988, 0.769667, 0.648029, 0.612115, 0.784172, 0.78875),
(15, '20181208', 0.604561, 0.649711, 0.481126, 0.806279, 0.407477, 0.26756, 0.36288, 0.299295, 0.579851, 0.39881);

-- --------------------------------------------------------

--
-- Table structure for table `ndvi`
--

CREATE TABLE `ndvi` (
  `id` int(50) UNSIGNED NOT NULL,
  `filename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `a1` float DEFAULT NULL,
  `a2` float DEFAULT NULL,
  `b1` float DEFAULT NULL,
  `b2` float DEFAULT NULL,
  `c1` float DEFAULT NULL,
  `c2` float DEFAULT NULL,
  `d1` float DEFAULT NULL,
  `d2` float DEFAULT NULL,
  `e1` float DEFAULT NULL,
  `e2` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `citra_cwsi`
--
ALTER TABLE `citra_cwsi`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `cwsi`
--
ALTER TABLE `cwsi`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ndvi`
--
ALTER TABLE `ndvi`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `citra_cwsi`
--
ALTER TABLE `citra_cwsi`
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `cwsi`
--
ALTER TABLE `cwsi`
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `ndvi`
--
ALTER TABLE `ndvi`
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
