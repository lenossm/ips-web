<?php
/* IPS theme — setup, assets, helpers */

declare(strict_types=1);

if (!defined('ABSPATH')) {
	exit;
}

define('IPS_VERSION', '1.4.0');
define('IPS_DIR', get_template_directory());
define('IPS_URI', get_template_directory_uri());

require_once IPS_DIR . '/inc/content.php';
require_once IPS_DIR . '/inc/demo-import.php';

/* basic theme supports + menus */
function ips_setup(): void {
	load_theme_textdomain('ips', IPS_DIR . '/languages');

	add_theme_support('title-tag');
	add_theme_support('post-thumbnails');
	add_theme_support('html5', [
		'search-form',
		'comment-form',
		'comment-list',
		'gallery',
		'caption',
		'style',
		'script',
	]);
	add_theme_support('custom-logo', [
		'height'      => 80,
		'width'       => 240,
		'flex-height' => true,
		'flex-width'  => true,
	]);
	add_theme_support('responsive-embeds');
	add_theme_support('align-wide');

	register_nav_menus([
		'primary' => __('Primary Menu', 'ips'),
		'footer'  => __('Footer Menu', 'ips'),
	]);

	/* custom sizes so project cards look sharp */
	add_image_size('ips-hero', 1920, 1080, true);
	add_image_size('ips-project', 900, 1200, true);
	add_image_size('ips-card', 800, 600, true);
}
add_action('after_setup_theme', 'ips_setup');

/* css + js */
function ips_assets(): void {
	wp_enqueue_style(
		'ips-fonts',
		'https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@400;500;600;700&family=Noto+Serif+Georgian:wght@500;600;700&display=swap',
		[],
		null
	);

	wp_enqueue_style(
		'ips-main',
		IPS_URI . '/assets/css/main.css',
		['ips-fonts'],
		IPS_VERSION
	);

	wp_enqueue_style(
		'ips-pages',
		IPS_URI . '/assets/css/pages.css',
		['ips-main'],
		IPS_VERSION
	);

	wp_enqueue_script(
		'ips-main',
		IPS_URI . '/assets/js/main.js',
		[],
		IPS_VERSION,
		true
	);

	wp_enqueue_script(
		'ips-filters',
		IPS_URI . '/assets/js/preview-nav.js',
		[],
		IPS_VERSION,
		true
	);

	wp_enqueue_script(
		'ips-transitions',
		IPS_URI . '/assets/js/transitions.js',
		[],
		IPS_VERSION,
		true
	);

	wp_localize_script('ips-main', 'ipsTheme', [
		'homeUrl' => home_url('/'),
	]);
}
add_action('wp_enqueue_scripts', 'ips_assets');

function ips_widgets(): void {
	register_sidebar([
		'name'          => __('Footer Column', 'ips'),
		'id'            => 'footer-1',
		'before_widget' => '<div class="footer-widget">',
		'after_widget'  => '</div>',
		'before_title'  => '<h3 class="footer-widget__title">',
		'after_title'   => '</h3>',
	]);
}
add_action('widgets_init', 'ips_widgets');

/* projects post type */
function ips_register_cpts(): void {
	register_post_type('project', [
		'labels' => [
			'name'          => __('Projects', 'ips'),
			'singular_name' => __('Project', 'ips'),
			'add_new_item'  => __('Add New Project', 'ips'),
			'edit_item'     => __('Edit Project', 'ips'),
		],
		'public'       => true,
		'has_archive'  => true,
		'rewrite'      => ['slug' => 'project'],
		'menu_icon'    => 'dashicons-building',
		'supports'     => ['title', 'editor', 'thumbnail', 'excerpt'],
		'show_in_rest' => true,
	]);

	register_taxonomy('project_type', 'project', [
		'labels' => [
			'name'          => __('Project Types', 'ips'),
			'singular_name' => __('Project Type', 'ips'),
		],
		'public'       => true,
		'hierarchical' => true,
		'rewrite'      => ['slug' => 'project-type'],
		'show_in_rest' => true,
	]);
}
add_action('init', 'ips_register_cpts');

/* language helpers — works with polylang/wpml if theyre installed */
function ips_lang(): string {
	if (function_exists('pll_current_language')) {
		$code = pll_current_language('slug');
		return is_string($code) ? $code : 'ka';
	}

	if (defined('ICL_LANGUAGE_CODE') && is_string(ICL_LANGUAGE_CODE)) {
		return ICL_LANGUAGE_CODE;
	}

	$locale = determine_locale();
	return str_starts_with($locale, 'en') ? 'en' : 'ka';
}

function ips_is_en(): bool {
	return ips_lang() === 'en';
}

/* little dictionary so i dont hardcode strings everywhere */
function ips_t(string $key): string {
	$strings = [
		'nav_interior'    => ['ka' => 'IPS ინტერიერი', 'en' => 'IPS Interior'],
		'nav_facade'      => ['ka' => 'IPS ფასადი', 'en' => 'IPS Facade'],
		'nav_services'    => ['ka' => 'სერვისები', 'en' => 'Services'],
		'nav_projects'    => ['ka' => 'პროექტები', 'en' => 'Projects'],
		'nav_about'       => ['ka' => 'ჩვენ შესახებ', 'en' => 'About us'],
		'nav_news'        => ['ka' => 'სიახლე და ბლოგი', 'en' => 'News & Blog'],
		'nav_contact'     => ['ka' => 'კონტაქტი', 'en' => 'Contact'],
		'cta_projects'    => ['ka' => 'ნახეთ ჩვენი პროექტები', 'en' => 'See our projects'],
		'cta_video'       => ['ka' => 'ნახეთ ვიდეო', 'en' => 'Watch the video'],
		'cta_contact'     => ['ka' => 'დაგვიკავშირდით', 'en' => 'Get in touch'],
		'hero_title'      => ['ka' => 'სამშენებლო სერვისები & მასალები', 'en' => 'Building Services & Materials'],
		'hero_lead'       => [
			'ka' => 'ინტერიერი და ფასადი — ცოდნით დაწყებული, ოსტატობით დასრულებული.',
			'en' => 'Interior and facade — started with knowledge, finished with mastery.',
		],
		'interior_title'  => ['ka' => 'ინტერიერის მასალები და სერვისები', 'en' => 'Interior materials and services'],
		'interior_lead'   => ['ka' => 'შერჩევა | მიწოდება | მონტაჟი', 'en' => 'Selection | Delivery | Installation'],
		'facade_title'    => ['ka' => 'საფასადო მასალები და სერვისები', 'en' => 'Facade materials and services'],
		'facade_lead'     => ['ka' => 'პროექტირება | მიწოდება | მონტაჟი', 'en' => 'Projecting | Delivery | Installation'],
		'mission_title'   => ['ka' => 'ყველა პროექტს ვიწყებთ და ვასრულებთ ცოდნით', 'en' => 'We start and finish every project with knowledge'],
		'mission_text'    => [
			'ka' => 'ნაშენების ხარისხს განსაზღვრავს კვალიფიკაცია და არა მხოლოდ მასალის ფასი. IPS-ში პროექტების სწორად დაგეგმარებას პროცესების და მასალების სიღრმისეული ცოდნა განაპირობებს.',
			'en' => 'Building quality is determined by qualification — not only the price of materials. At IPS, proper project planning depends on deep knowledge of processes and materials.',
		],
		'values_title'    => ['ka' => 'ჩვენი ღირებულებები', 'en' => 'Our values'],
		'value_mastery'   => ['ka' => 'ოსტატობა', 'en' => 'Mastery'],
		'value_confidence'=> ['ka' => 'თავდაჯერებულობა', 'en' => 'Confidence'],
		'value_curiosity' => ['ka' => 'ცნობისმოყვარეობა', 'en' => 'Curiosity'],
		'value_accuracy'  => ['ka' => 'სიზუსტე', 'en' => 'Accuracy'],
		'projects_title'  => ['ka' => 'შერჩეული პროექტები', 'en' => 'Selected projects'],
		'projects_lead'   => [
			'ka' => 'ინტერიერის და ფასადის პროექტები მთელი საქართველოდან.',
			'en' => 'Interior and facade projects across Georgia.',
		],
		'view_all'        => ['ka' => 'ყველა პროექტი', 'en' => 'All projects'],
		'since'           => ['ka' => '2016-დან', 'en' => 'Since 2016'],
		'address'         => ['ka' => 'თბილისი, ჭავჭავაძის გამზ. 49დ', 'en' => 'Tbilisi, Chavchavadze Ave. 49d'],
		'phone'           => ['ka' => '+995 32 225 24 24', 'en' => '+995 32 225 24 24'],
		'email'           => ['ka' => 'info@ips.ge', 'en' => 'info@ips.ge'],
		'social'          => ['ka' => 'სოციალური მედია', 'en' => 'Social media'],
		'rights'          => ['ka' => 'ყველა უფლება დაცულია', 'en' => 'All rights reserved'],
		'menu'            => ['ka' => 'მენიუ', 'en' => 'Menu'],
		'close'           => ['ka' => 'დახურვა', 'en' => 'Close'],
		'read_more'       => ['ka' => 'ვრცლად', 'en' => 'Read more'],
	];

	$lang = ips_is_en() ? 'en' : 'ka';
	if (!isset($strings[$key])) {
		return $key;
	}
	return $strings[$key][$lang];
}

function ips_language_urls(): array {
	if (function_exists('pll_home_url')) {
		return [
			'ka' => pll_home_url('ka'),
			'en' => pll_home_url('en'),
		];
	}

	$home = home_url('/');
	return [
		'ka' => $home,
		'en' => trailingslashit($home) . 'en/',
	];
}

function ips_body_classes(array $classes): array {
	$classes[] = 'lang-' . ips_lang();
	if (is_front_page()) {
		$classes[] = 'is-front';
	}
	return $classes;
}
add_filter('body_class', 'ips_body_classes');

/* fallback menu if nothing is assigned yet */
function ips_fallback_menu(): void {
	$services = home_url('/services/');
	$items = [
		['nav_interior', $services . '#interior'],
		['nav_facade', $services . '#facade'],
		['nav_services', $services],
		['nav_projects', get_post_type_archive_link('project') ?: home_url('/project/')],
		['nav_about', home_url('/about-us/')],
		['nav_news', home_url('/news-blogs/')],
	];

	echo '<ul class="nav-list">';
	foreach ($items as [$key, $url]) {
		printf(
			'<li><a href="%s">%s</a></li>',
			esc_url($url),
			esc_html(ips_t($key))
		);
	}
	echo '</ul>';
}

/* so desktop dropdown css can target wp menus too */
function ips_menu_item_classes(array $classes, $item, $args, int $depth = 0): array {
	if (in_array('menu-item-has-children', $classes, true)) {
		$classes[] = 'has-children';
	}
	return $classes;
}
add_filter('nav_menu_css_class', 'ips_menu_item_classes', 10, 4);

function ips_excerpt_length(int $length): int {
	return 22;
}
add_filter('excerpt_length', 'ips_excerpt_length');

function ips_excerpt_more(string $more): string {
	return '…';
}
add_filter('excerpt_more', 'ips_excerpt_more');
