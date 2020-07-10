-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 10, 2020 at 09:27 AM
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
(18, '20171018', '/static/assets/img/cwsi/20171018.png', 1, 0),
(19, '20171103', '/static/assets/img/cwsi/20171103.png', 752, 1458),
(20, '20171205', '/static/assets/img/cwsi/20171205.png', 95, 418),
(21, '20180106', '/static/assets/img/cwsi/20180106.png', 57, 834),
(22, '20180223', '/static/assets/img/cwsi/20180223.png', 53, 328),
(23, '20180327', '/static/assets/img/cwsi/20180327.png', 188, 1242),
(24, '20180428', '/static/assets/img/cwsi/20180428.png', 8, 271),
(25, '20180530', '/static/assets/img/cwsi/20180530.png', 14, 113),
(28, '20180615', '/static/assets/img/cwsi/20180615.png', 80, 373),
(29, '20180701', '/static/assets/img/cwsi/20180701.png', 203, 499),
(30, '20180818', '/static/assets/img/cwsi/20180818.png', 387, 1339),
(31, '20180903', '/static/assets/img/cwsi/20180903.png', 489, 1748),
(32, '20181005', '/static/assets/img/cwsi/20181005.png', 246, 1829);

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
(16, '20171018', 0.181988, 0.181715, 0.180378, 0.181364, 0.180641, 0.180525, 0.180214, 0.18139, 0.184656, 0.18089),
(17, '20171103', 0.840401, 0.780648, 0.996091, 0.784576, 0.80974, 0.918879, 0.482898, 0.548934, 0.798689, 0.911956),
(18, '20171205', 0.348379, 0.235564, 0.658077, 0.216392, 0.711037, 0.696591, 0.307236, 0.300286, 0.425136, 0.757926),
(19, '20180106', 0.577991, 0.520639, 0.558323, 0.637549, 0.27819, 0.244827, 0.415384, 0.246354, 0.201467, 0.124178),
(20, '20180223', 0.139529, 0.105166, 0.216489, 0.546305, 0.258825, 0.310578, 0.285482, 0.383039, 0.0980687, 0.427738),
(21, '20180327', 0.423558, 0.412565, 0.901572, 0.481898, 0.65368, 0.638086, 0.51257, 0.432011, 0.671422, 0.705999),
(22, '20180428', 0.780204, 0.332082, 0.496755, 0.53133, 0.454626, 0.654665, 0.311569, 0.309938, 0.305357, 0.57826),
(23, '20180530', 0.39951, 0.283926, 0.472616, 0.417678, 0.455197, 0.269406, 0.267006, 0.28237, 0.321665, 0.355887),
(26, '20180615', 0.371378, 0.284006, 0.84395, 0.351024, 0.478738, 0.330588, 0.512908, 0.315893, 0.549555, 0.689732),
(27, '20180701', 0.387946, 0.335721, 0.798738, 0.344409, 0.891587, 0.459014, 0.954538, 0.454193, 0.538887, 0.79018),
(28, '20180818', 0.563337, 0.387549, 0.598461, 0.405876, 0.814276, 0.82948, 0.676035, 0.647334, 0.724023, 0.777451),
(29, '20180903', 0.631618, 0.486569, 0.584977, 0.454236, 0.787479, 0.889524, 0.77389, 0.485409, 0.791486, 0.738239),
(30, '20181005', 0.753059, 0.733475, 0.691124, 0.502857, 0.677532, 0.762086, 0.892188, 0.636731, 0.551507, 0.492448);

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
-- Dumping data for table `ndvi`
--

INSERT INTO `ndvi` (`id`, `filename`, `a1`, `a2`, `b1`, `b2`, `c1`, `c2`, `d1`, `d2`, `e1`, `e2`) VALUES
(1, '20171018', 0.220375, 0.279253, 0.3542, 0.325849, 0.387497, 0.478545, 0.499481, 0.322889, 0.145705, 0.380078),
(2, '20171103', 0.27224, 0.298192, 0.225077, 0.341428, 0.305733, 0.347136, 0.494859, 0.462199, 0.15362, 0.176756),
(3, '20171205', 0.465177, 0.520823, 0.198055, 0.619471, 0.287153, 0.264872, 0.589229, 0.251569, 0.388299, 0.189788),
(4, '20180106', 0.466387, 0.510611, 0.515452, 0.515702, 0.540742, 0.567809, 0.562012, 0.579524, 0.523729, 0.548508),
(5, '20180223', 0.217951, 0.29893, 0.352183, 0.383538, 0.244427, 0.206512, 0.252438, 0.35684, 0.286696, 0.321381),
(6, '20180327', 0.64415, 0.62015, 0.212154, 0.572078, 0.335878, 0.337803, 0.613485, 0.693479, 0.675918, 0.580661),
(7, '20180428', 0.419122, 0.56014, 0.500774, 0.523504, 0.485973, 0.478152, 0.570993, 0.625717, 0.646022, 0.493608),
(8, '20180530', 0.509279, 0.59153, 0.146807, 0.526099, 0.614916, 0.735721, 0.558335, 0.653836, 0.444778, 0.167277),
(11, '20180615', 0.514773, 0.58202, 0.153656, 0.500113, 0.527862, 0.679027, 0.4886, 0.615438, 0.396107, 0.18684),
(12, '20180701', 0.523639, 0.55935, 0.165759, 0.511198, 0.45262, 0.634997, 0.213868, 0.632132, 0.574596, 0.259759),
(13, '20180818', 0.314388, 0.351024, 0.294829, 0.380431, 0.194989, 0.160342, 0.296765, 0.271578, 0.258959, 0.357136),
(14, '20180903', 0.309849, 0.133919, 0.0752644, 0.212519, 0.211285, 0.211741, 0.221614, 0.156859, 0.22147, 0.337988),
(15, '20181005', 0.189883, 0.230362, 0.215909, 0.265646, 0.238869, 0.235512, 0.176822, 0.337671, 0.237223, 0.368732);

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
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `cwsi`
--
ALTER TABLE `cwsi`
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `ndvi`
--
ALTER TABLE `ndvi`
  MODIFY `id` int(50) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
