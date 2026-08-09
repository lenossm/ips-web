<?php
/* helpers for reading site.json */

declare(strict_types=1);

if (!defined('ABSPATH')) {
	exit;
}

function ips_site_content(): array {
	static $cache = null;
	if ($cache !== null) {
		return $cache;
	}

	$path = IPS_DIR . '/content/site.json';
	if (!is_readable($path)) {
		$cache = [];
		return $cache;
	}

	$data = json_decode((string) file_get_contents($path), true);
	$cache = is_array($data) ? $data : [];
	return $cache;
}

/* home / about / services for current language */
function ips_content_section(string $section): array {
	$site = ips_site_content();
	$lang = ips_is_en() ? 'en' : 'ka';
	$bucket = $site[$section][$lang] ?? $site[$section]['en'] ?? [];
	return is_array($bucket) ? $bucket : [];
}

function ips_content_projects(): array {
	$site = ips_site_content();
	return is_array($site['projects'] ?? null) ? $site['projects'] : [];
}

function ips_content_brands(): array {
	$site = ips_site_content();
	return is_array($site['brands'] ?? null) ? $site['brands'] : [];
}

function ips_content_posts(): array {
	$site = ips_site_content();
	return is_array($site['posts'] ?? null) ? $site['posts'] : [];
}

function ips_project_title(array $project): string {
	$lang = ips_is_en() ? 'en' : 'ka';
	$title = $project['title'][$lang] ?? $project['title']['en'] ?? $project['slug'] ?? '';
	return (string) $title;
}

/* turns content/images/... into a real url */
function ips_content_image_url(?string $path): string {
	if (!$path) {
		return '';
	}
	if (str_starts_with($path, 'http://') || str_starts_with($path, 'https://')) {
		return $path;
	}
	return trailingslashit(IPS_URI) . ltrim(str_replace('\\', '/', $path), '/');
}
