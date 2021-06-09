-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Hôte : mariadb
-- Généré le : mer. 09 juin 2021 à 13:01
-- Version du serveur :  10.5.9-MariaDB-1:10.5.9+maria~focal
-- Version de PHP : 7.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `vaccincovid`
--

-- --------------------------------------------------------

--
-- Structure de la table `vc_center`
--

CREATE TABLE `vc_center` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `slots` int(11) NOT NULL,
  `doctolib_id` int(11) NOT NULL,
  `doctolib_name` text NOT NULL,
  `doctolib_practice` int(11) NOT NULL,
  `doctolib_url` text NOT NULL,
  `doctolib_data` longtext NOT NULL,
  `last_fetch` datetime NOT NULL,
  `update_hash` varchar(64) NOT NULL DEFAULT 'blank',
  `cache_expire` datetime NOT NULL,
  `city` varchar(254) NOT NULL,
  `zip_code` char(5) NOT NULL,
  `address` text NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `place_name` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `vc_channel`
--

CREATE TABLE `vc_channel` (
  `channel` varchar(254) NOT NULL,
  `center_id` int(11) NOT NULL,
  `last_update` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `vc_setting`
--

CREATE TABLE `vc_setting` (
  `id` int(11) NOT NULL,
  `param` varchar(255) NOT NULL,
  `param_value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `vc_center`
--
ALTER TABLE `vc_center`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `vc_channel`
--
ALTER TABLE `vc_channel`
  ADD PRIMARY KEY (`channel`,`center_id`),
  ADD KEY `channelmodel_center_id` (`center_id`);

--
-- Index pour la table `vc_setting`
--
ALTER TABLE `vc_setting`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `vc_center`
--
ALTER TABLE `vc_center`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `vc_setting`
--
ALTER TABLE `vc_setting`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `vc_channel`
--
ALTER TABLE `vc_channel`
  ADD CONSTRAINT `vc_channel_ibfk_1` FOREIGN KEY (`center_id`) REFERENCES `vc_center` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
