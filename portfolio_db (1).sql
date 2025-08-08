-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 08, 2025 at 03:10 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.4.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `portfolio_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `judul` varchar(255) NOT NULL,
  `klien` varchar(255) NOT NULL,
  `deskripsi` text NOT NULL,
  `fitur_utama` text NOT NULL,
  `durasi` varchar(255) NOT NULL,
  `video_path` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` (`id`, `judul`, `klien`, `deskripsi`, `fitur_utama`, `durasi`, `video_path`, `created_at`) VALUES
(11, 'APLIKASI E-SPTPD', 'Pemerintah Kabupaten Sleman', 'Aplikasi E-SPTPD (Elektronik Surat Pemberitahuan Pajak Daerah) adalah sistem digital untuk memudahkan wajib pajak dalam melaporkan dan membayar pajak daerah secara online. Sistem ini mengintegrasikan berbagai jenis pajak daerah dalam satu platform yang user-friendly.', 'Authentikasi\nSign Up\nSign In', '5 Bulan ( Maret - Desember 2024 )', 'assets/videos/Aplikasi-ESPTPD-Web-Kab-Sleman.mp4', '2025-08-07 09:46:02');

-- --------------------------------------------------------

--
-- Table structure for table `project_technologies`
--

CREATE TABLE `project_technologies` (
  `id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `nama_teknologi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `project_technologies`
--

INSERT INTO `project_technologies` (`id`, `project_id`, `nama_teknologi`) VALUES
(15, 11, 'Pyhton'),
(16, 11, 'PostgreSQL'),
(17, 11, 'Redis');

-- --------------------------------------------------------

--
-- Table structure for table `provinces`
--

CREATE TABLE `provinces` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `provinces`
--

INSERT INTO `provinces` (`id`, `name`, `logo`, `is_enabled`) VALUES
(3, 'Jawa Barat', 'assets/client/Logo-Provinsi-Jawa-Barat.png', 1),
(4, 'Banten', 'assets/client/Logo-Provinsi-Banten.png', 1),
(5, 'Kalimantan Tengah', 'assets/client/Logo-Provinsi-Kalimantan-Tengah.png', 1);

-- --------------------------------------------------------

--
-- Table structure for table `regions`
--

CREATE TABLE `regions` (
  `id` int(11) NOT NULL,
  `province_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` enum('Kota','Kabupaten') NOT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `is_enabled` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `regions`
--

INSERT INTO `regions` (`id`, `province_id`, `name`, `type`, `logo`, `is_enabled`) VALUES
(2, 3, 'Kota Bekasi', 'Kota', 'assets/client/Logo-Kota-Bekasi.png', 1),
(4, 3, 'Kota Banjar', 'Kota', 'assets/client/Logo-Kota-Banjar.png', 1),
(5, 3, 'Kota Bogor', 'Kota', 'assets/client/Logo-Kota-Bogor.png', 1),
(6, 3, 'Kota Cimahi', 'Kota', 'assets/client/Logo-Kota-Cimahi.png', 1),
(7, 3, 'Kota Depok', 'Kota', 'assets/client/Logo-Kota-Depok.png', 1),
(8, 3, 'Kota Sukabumi', 'Kota', 'assets/client/Logo-Kota-Sukabumi.png', 1),
(9, 3, 'Kota Tasikmalaya', 'Kota', 'assets/client/Logo-Kota-Tasikmalaya.png', 1),
(10, 3, 'Kabupaten Cirebon', 'Kabupaten', 'assets/client/Lambang_Kabupaten_Cirebon.gif', 1),
(11, 3, 'Kabupaten Kuningan', 'Kabupaten', 'assets/client/Logo_Kabupaten_kuningan.jpg', 1),
(12, 3, 'Kabupaten Majalengka', 'Kabupaten', 'assets/client/Logo-Kab-Majalengka.png', 1),
(13, 3, 'Kabupaten Pangandaran', 'Kabupaten', 'assets/client/Logo-Kab-Pangandaran.png', 1),
(14, 3, 'Kabupaten Subang', 'Kabupaten', 'assets/client/Logo-Kab-Subang.png', 1),
(15, 3, 'Kabupaten Sukabumi', 'Kabupaten', 'assets/client/Logo-Kab-Sukabumi.png', 1),
(16, 3, 'Kabupaten Sumedang', 'Kabupaten', 'assets/client/Logo-Kab-Sumedang.png', 1),
(17, 4, 'Kota Cilegon', 'Kota', 'assets/client/Logo-Kota-Cilegon.png', 1),
(18, 4, 'Kota Serang', 'Kota', 'assets/client/Logo-Kota-Serang.jpg', 1),
(19, 4, 'Kota Tanggerang', 'Kota', 'assets/client/Logo-Kota-Tangerang.png', 1),
(20, 4, 'Kota Tanggerang Selatan', 'Kota', 'assets/client/Logo-Kota-Tangerang-Selatan.png', 1),
(21, 4, 'Kabupaten Lebak', 'Kabupaten', 'assets/client/Logo-Kab-Lebak.png', 1),
(22, 4, 'Kabupaten Serang', 'Kabupaten', 'assets/client/Logo-Kab-Serang.png', 1),
(23, 4, 'Kabupaten Tanggerang', 'Kabupaten', 'assets/client/Logo-Kab-Tangerang.png', 1),
(24, 5, 'Kota Palangkaraya', 'Kota', 'assets/client/Logo-Kota-Palangkaraya.png', 1),
(25, 3, 'Kabupaten Bandung', 'Kabupaten', 'assets/client/Logo-Kab-Bandung.png', 1),
(26, 3, 'Kabupaten Tasikmalaya', 'Kabupaten', 'assets/client/Logo-Kab-Tasikmalaya.png', 1),
(27, 3, 'Kabupaten Ciamis', 'Kabupaten', 'assets/client/Logo-Kab-Ciamis.png', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `project_technologies`
--
ALTER TABLE `project_technologies`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`);

--
-- Indexes for table `provinces`
--
ALTER TABLE `provinces`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `regions`
--
ALTER TABLE `regions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `province_id` (`province_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `project_technologies`
--
ALTER TABLE `project_technologies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `provinces`
--
ALTER TABLE `provinces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `regions`
--
ALTER TABLE `regions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `project_technologies`
--
ALTER TABLE `project_technologies`
  ADD CONSTRAINT `project_technologies_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `regions`
--
ALTER TABLE `regions`
  ADD CONSTRAINT `regions_ibfk_1` FOREIGN KEY (`province_id`) REFERENCES `provinces` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
