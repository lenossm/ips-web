<?php
/* one click import — dumps everything from site.json into wordpress
   appearance → IPS Demo Import → press the button, go make coffee */

declare(strict_types=1);

if (!defined('ABSPATH')) {
	exit;
}

/* brands post type, same as the old site had */
function ips_register_brand_cpt(): void {
	register_post_type('brand', [
		'labels' => [
			'name'          => __('Brands', 'ips'),
			'singular_name' => __('Brand', 'ips'),
			'add_new_item'  => __('Add New Brand', 'ips'),
			'edit_item'     => __('Edit Brand', 'ips'),
		],
		'public'       => true,
		'has_archive'  => true,
		'rewrite'      => ['slug' => 'brand'],
		'menu_icon'    => 'dashicons-awards',
		'supports'     => ['title', 'editor', 'thumbnail', 'excerpt'],
		'show_in_rest' => true,
	]);
}
add_action('init', 'ips_register_brand_cpt');

/* puts the importer under Appearance */
function ips_demo_admin_menu(): void {
	add_theme_page(
		__('IPS Demo Import', 'ips'),
		__('IPS Demo Import', 'ips'),
		'manage_options',
		'ips-demo-import',
		'ips_demo_admin_page'
	);
}
add_action('admin_menu', 'ips_demo_admin_menu');

/* the admin screen itself */
function ips_demo_admin_page(): void {
	if (!current_user_can('manage_options')) {
		return;
	}

	$done = isset($_GET['ips_imported']) && $_GET['ips_imported'] === '1';
	$site = ips_site_content();
	$stats = $site['stats'] ?? [];
	?>
	<div class="wrap">
		<h1><?php esc_html_e('IPS Demo Import', 'ips'); ?></h1>
		<p><?php esc_html_e('One click and it fills the whole site — pages, projects, brands, blog. No building things one by one.', 'ips'); ?></p>

		<?php if ($done) : ?>
			<div class="notice notice-success is-dismissible"><p><?php esc_html_e('Import finished. Open the site front page to review.', 'ips'); ?></p></div>
		<?php endif; ?>

		<div class="card" style="max-width:640px;padding:1.25rem;">
			<p><strong><?php esc_html_e('Will import:', 'ips'); ?></strong></p>
			<ul>
				<li><?php echo esc_html(($stats['projects'] ?? 0) . ' projects'); ?></li>
				<li><?php echo esc_html(($stats['brands'] ?? 0) . ' brands'); ?></li>
				<li><?php echo esc_html(($stats['posts'] ?? 0) . ' blog posts'); ?></li>
				<li><?php esc_html_e('Core pages: Home, Services, About, Brands, News + menus + front page settings', 'ips'); ?></li>
			</ul>
			<form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
				<?php wp_nonce_field('ips_demo_import', 'ips_demo_nonce'); ?>
				<input type="hidden" name="action" value="ips_run_demo_import">
				<p>
					<button type="submit" class="button button-primary button-hero" onclick="return confirm('<?php echo esc_js(__('This may take a minute and will create many posts. Continue?', 'ips')); ?>');">
						<?php esc_html_e('Import entire site now', 'ips'); ?>
					</button>
				</p>
			</form>
			<p class="description"><?php esc_html_e('Safe to re-run: existing IPS demo items are updated by slug, not duplicated blindly.', 'ips'); ?></p>
		</div>
	</div>
	<?php
}

/* runs when the button is pressed */
function ips_handle_demo_import(): void {
	if (!current_user_can('manage_options')) {
		wp_die(esc_html__('Forbidden', 'ips'));
	}
	check_admin_referer('ips_demo_import', 'ips_demo_nonce');

	@set_time_limit(0);
	ips_run_demo_import();

	wp_safe_redirect(add_query_arg('ips_imported', '1', admin_url('themes.php?page=ips-demo-import')));
	exit;
}
add_action('admin_post_ips_run_demo_import', 'ips_handle_demo_import');

/* copies an image from the theme folder into the media library */
function ips_sideload_theme_image(?string $relative, int $parent_id = 0): int {
	if (!$relative) {
		return 0;
	}

	$relative = ltrim(str_replace('\\', '/', $relative), '/');
	$path = IPS_DIR . '/' . $relative;
	if (!is_readable($path)) {
		// try docs copy path variants
		$path = IPS_DIR . '/content/images/' . basename($relative);
	}
	if (!is_readable($path)) {
		return 0;
	}

	$filename = basename($path);
	$existing = get_posts([
		'post_type'      => 'attachment',
		'name'           => sanitize_title(pathinfo($filename, PATHINFO_FILENAME)),
		'posts_per_page' => 1,
		'post_status'    => 'inherit',
		'fields'         => 'ids',
	]);
	if ($existing) {
		return (int) $existing[0];
	}

	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';
	require_once ABSPATH . 'wp-admin/includes/image.php';

	$upload = wp_upload_bits($filename, null, (string) file_get_contents($path));
	if (!empty($upload['error'])) {
		return 0;
	}

	$filetype = wp_check_filetype($filename, null);
	$attach_id = wp_insert_attachment([
		'post_mime_type' => $filetype['type'] ?? 'image/jpeg',
		'post_title'     => sanitize_file_name(pathinfo($filename, PATHINFO_FILENAME)),
		'post_content'   => '',
		'post_status'    => 'inherit',
	], $upload['file'], $parent_id);

	if (is_wp_error($attach_id) || !$attach_id) {
		return 0;
	}

	$meta = wp_generate_attachment_metadata($attach_id, $upload['file']);
	wp_update_attachment_metadata($attach_id, $meta);
	return (int) $attach_id;
}

/* create it, or update it if the slug already exists — so re-running is safe */
function ips_upsert_post(array $args): int {
	$slug = $args['post_name'] ?? '';
	$type = $args['post_type'] ?? 'post';
	$existing = get_page_by_path($slug, OBJECT, $type);
	if ($existing instanceof WP_Post) {
		$args['ID'] = $existing->ID;
		return (int) wp_update_post($args, true);
	}
	$id = wp_insert_post($args, true);
	return is_wp_error($id) ? 0 : (int) $id;
}

/* turns the json blocks back into normal html */
function ips_content_to_html(array $content): string {
	if (!empty($content['html'])) {
		return (string) $content['html'];
	}
	$html = '';
	foreach ($content['paragraphs'] ?? [] as $p) {
		$html .= '<p>' . esc_html((string) $p) . '</p>';
	}
	foreach ($content['lists'] ?? [] as $list) {
		$html .= '<ul>';
		foreach ($list as $li) {
			$html .= '<li>' . esc_html((string) $li) . '</li>';
		}
		$html .= '</ul>';
	}
	return $html;
}

/* the actual import — pages, projects, brands, posts, menus */
function ips_run_demo_import(): array {
	$site = ips_site_content();
	$report = ['pages' => 0, 'projects' => 0, 'brands' => 0, 'posts' => 0];

	$lang = 'ka';
	$about = $site['about'][$lang] ?? [];
	$services = $site['services'][$lang] ?? [];

	// --- Pages ---
	$home_id = ips_upsert_post([
		'post_title'   => 'IPS',
		'post_name'    => 'home',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '',
	]);

	$services_body = '';
	foreach (['interior', 'facade'] as $key) {
		$block = $services[$key] ?? null;
		if (!$block) {
			continue;
		}
		$services_body .= '<h2 id="' . esc_attr($key) . '">' . esc_html((string) ($block['title'] ?? '')) . '</h2>';
		foreach ($block['items'] ?? [] as $item) {
			$services_body .= '<h3>' . esc_html((string) ($item['title'] ?? '')) . '</h3><ul>';
			foreach ($item['points'] ?? [] as $point) {
				$services_body .= '<li>' . esc_html((string) $point) . '</li>';
			}
			$services_body .= '</ul>';
		}
	}

	$services_id = ips_upsert_post([
		'post_title'   => (string) ($services['title'] ?? 'სერვისები'),
		'post_name'    => 'services',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => $services_body,
	]);
	if ($services_id) {
		update_post_meta($services_id, '_wp_page_template', 'page-template-services.php');
	}

	$about_body = '';
	foreach ($about['all_paragraphs'] ?? ($about['mission'] ?? []) as $p) {
		$about_body .= '<p>' . esc_html((string) $p) . '</p>';
	}
	$about_id = ips_upsert_post([
		'post_title'   => (string) ($about['title'] ?? 'ჩვენ შესახებ'),
		'post_name'    => 'about-us',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => $about_body,
	]);
	if ($about_id) {
		update_post_meta($about_id, '_wp_page_template', 'page-template-about.php');
	}

	$brands_page_id = ips_upsert_post([
		'post_title'   => 'ბრენდები',
		'post_name'    => 'brands',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '',
	]);
	if ($brands_page_id) {
		update_post_meta($brands_page_id, '_wp_page_template', 'page-template-brands.php');
	}

	$news_id = ips_upsert_post([
		'post_title'   => 'სიახლე და ბლოგი',
		'post_name'    => 'news-blogs',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '',
	]);

	$interior_id = ips_upsert_post([
		'post_title'   => 'IPS ინტერიერი',
		'post_name'    => 'interior',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '<p>' . esc_html((string) (($site['home'][$lang]['interior_title'] ?? '') . ' — ' . ($site['home'][$lang]['interior_lead'] ?? ''))) . '</p>',
	]);

	$facade_id = ips_upsert_post([
		'post_title'   => 'IPS ფასადი',
		'post_name'    => 'facade',
		'post_status'  => 'publish',
		'post_type'    => 'page',
		'post_content' => '<p>' . esc_html((string) (($site['home'][$lang]['facade_title'] ?? '') . ' — ' . ($site['home'][$lang]['facade_lead'] ?? ''))) . '</p>',
	]);

	$report['pages'] = 7;

	// Front page settings
	if ($home_id) {
		update_option('show_on_front', 'page');
		update_option('page_on_front', $home_id);
	}
	if ($news_id) {
		update_option('page_for_posts', $news_id);
	}

	// Project types
	foreach (['interior' => 'Interior', 'facade' => 'Facade'] as $slug => $name) {
		if (!term_exists($slug, 'project_type')) {
			wp_insert_term($name, 'project_type', ['slug' => $slug]);
		}
	}

	// Projects
	foreach ($site['projects'] ?? [] as $project) {
		$slug = (string) ($project['slug'] ?? '');
		if ($slug === '') {
			continue;
		}
		$title = (string) (($project['title']['ka'] ?? null) ?: ($project['title']['en'] ?? $slug));
		$content = ips_content_to_html(($project['content']['ka'] ?? null) ?: ($project['content']['en'] ?? []));
		$fields = ($project['fields']['ka'] ?? null) ?: ($project['fields']['en'] ?? []);
		$meta_html = '';
		foreach ($fields as $k => $v) {
			if ($v) {
				$meta_html .= '<p><strong>' . esc_html((string) $k) . ':</strong> ' . esc_html((string) $v) . '</p>';
			}
		}
		$id = ips_upsert_post([
			'post_title'   => $title,
			'post_name'    => $slug,
			'post_status'  => 'publish',
			'post_type'    => 'project',
			'post_content' => $meta_html . $content,
			'post_excerpt' => (string) (($project['excerpt']['ka'] ?? null) ?: ($project['excerpt']['en'] ?? '')),
		]);
		if (!$id) {
			continue;
		}
		$types = $project['types'] ?? [];
		if ($types) {
			wp_set_object_terms($id, $types, 'project_type');
		}
		foreach ($fields as $k => $v) {
			update_post_meta($id, 'ips_' . sanitize_key((string) $k), $v);
		}
		$img = ips_sideload_theme_image($project['image'] ?? ($project['featured_image'] ?? null), $id);
		if ($img) {
			set_post_thumbnail($id, $img);
		}
		$report['projects']++;
	}

	// Brands
	foreach ($site['brands'] ?? [] as $brand) {
		$slug = (string) ($brand['slug'] ?? '');
		if ($slug === '') {
			continue;
		}
		$title = (string) ($brand['name'] ?? ($brand['title']['en'] ?? ($brand['title']['ka'] ?? $slug)));
		$content = ips_content_to_html(($brand['content']['ka'] ?? null) ?: ($brand['content']['en'] ?? []));
		$id = ips_upsert_post([
			'post_title'   => $title,
			'post_name'    => $slug,
			'post_status'  => 'publish',
			'post_type'    => 'brand',
			'post_content' => $content,
			'post_excerpt' => (string) (($brand['excerpt']['ka'] ?? null) ?: ($brand['excerpt']['en'] ?? '')),
		]);
		if (!$id) {
			continue;
		}
		$img = ips_sideload_theme_image($brand['logo'] ?? ($brand['featured_image'] ?? null), $id);
		if ($img) {
			set_post_thumbnail($id, $img);
		}
		$report['brands']++;
	}

	// Blog posts (prefer KA, also import EN as separate if different slug)
	$seen_post_slugs = [];
	foreach ($site['posts'] ?? [] as $post) {
		foreach (['ka', 'en'] as $plang) {
			$title = (string) (($post['title'][$plang] ?? '') ?: '');
			if ($title === '') {
				continue;
			}
			$slug = (string) ($post['slug'] ?? '');
			if ($slug === '' || isset($seen_post_slugs[$slug])) {
				continue;
			}
			$seen_post_slugs[$slug] = true;
			$content = ips_content_to_html($post['content'][$plang] ?? []);
			$id = ips_upsert_post([
				'post_title'   => $title,
				'post_name'    => $slug,
				'post_status'  => 'publish',
				'post_type'    => 'post',
				'post_content' => $content,
				'post_excerpt' => (string) ($post['excerpt'][$plang] ?? ''),
				'post_date'    => !empty($post['date']) ? sanitize_text_field((string) $post['date']) : current_time('mysql'),
			]);
			if (!$id) {
				continue;
			}
			$img = ips_sideload_theme_image($post['image'] ?? ($post['featured_image'] ?? null), $id);
			if ($img) {
				set_post_thumbnail($id, $img);
			}
			$report['posts']++;
		}
	}

	// Menus
	$menu_name = 'IPS Primary';
	$menu = wp_get_nav_menu_object($menu_name);
	$menu_id = $menu ? (int) $menu->term_id : (int) wp_create_nav_menu($menu_name);

	// Clear existing items
	$items = wp_get_nav_menu_items($menu_id);
	if (is_array($items)) {
		foreach ($items as $item) {
			wp_delete_post($item->ID, true);
		}
	}

	$add = static function (int $menu_id, string $title, string $url, int $parent = 0) : int {
		return (int) wp_update_nav_menu_item($menu_id, 0, [
			'menu-item-title'  => $title,
			'menu-item-url'    => $url,
			'menu-item-status' => 'publish',
			'menu-item-parent-id' => $parent,
			'menu-item-type'   => 'custom',
		]);
	};

	$parent_int = $add($menu_id, 'IPS ინტერიერი', '#');
	$add($menu_id, 'სერვისები', get_permalink($services_id) . '#interior', $parent_int);
	$add($menu_id, 'ბრენდები', get_permalink($brands_page_id) ?: home_url('/brands/'), $parent_int);
	$add($menu_id, 'პროექტები', get_post_type_archive_link('project') ?: home_url('/project/'), $parent_int);

	$parent_fac = $add($menu_id, 'IPS ფასადი', '#');
	$add($menu_id, 'სერვისები', get_permalink($services_id) . '#facade', $parent_fac);
	$add($menu_id, 'ბრენდები', get_permalink($brands_page_id) ?: home_url('/brands/'), $parent_fac);
	$add($menu_id, 'პროექტები', get_post_type_archive_link('project') ?: home_url('/project/'), $parent_fac);

	$add($menu_id, 'სერვისები', get_permalink($services_id) ?: home_url('/services/'));
	$parent_proj = $add($menu_id, 'პროექტები', get_post_type_archive_link('project') ?: home_url('/project/'));
	$add($menu_id, 'ყველა პროექტი', get_post_type_archive_link('project') ?: home_url('/project/'), $parent_proj);

	$parent_about = $add($menu_id, 'ჩვენ შესახებ', get_permalink($about_id) ?: home_url('/about-us/'));
	$add($menu_id, 'კონტაქტი', (get_permalink($about_id) ?: home_url('/about-us/')) . '#contact', $parent_about);
	$add($menu_id, 'სიახლე და ბლოგი', get_permalink($news_id) ?: home_url('/news-blogs/'));

	$locations = get_theme_mod('nav_menu_locations', []);
	if (!is_array($locations)) {
		$locations = [];
	}
	$locations['primary'] = $menu_id;
	$locations['footer']  = $menu_id;
	set_theme_mod('nav_menu_locations', $locations);

	flush_rewrite_rules();
	update_option('ips_demo_imported_at', current_time('mysql'));
	update_option('ips_demo_import_report', $report);

	return $report;
}
