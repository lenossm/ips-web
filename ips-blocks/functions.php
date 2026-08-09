<?php
/* IPS Blocks — block theme, everything is editable in the site editor */

declare(strict_types=1);

if (!defined('ABSPATH')) {
	exit;
}

add_action('after_setup_theme', static function (): void {
	add_theme_support('wp-block-styles');
	add_theme_support('editor-styles');
	add_editor_style('assets/css/editor.css');
	register_nav_menus([
		'primary' => __('Primary', 'ips-blocks'),
	]);
});

add_action('init', static function (): void {
	register_block_pattern_category('ips', [
		'label' => __('IPS sections', 'ips-blocks'),
	]);
});

add_action('wp_enqueue_scripts', static function (): void {
	wp_enqueue_style(
		'ips-blocks-fonts',
		'https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@400;500;600;700&family=Noto+Serif+Georgian:wght@500;600;700&display=swap',
		[],
		null
	);
	wp_enqueue_style(
		'ips-blocks-theme',
		get_stylesheet_uri(),
		['ips-blocks-fonts'],
		wp_get_theme()->get('Version')
	);
});
