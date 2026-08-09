<?php
/* projects archive */

get_header();
$content_projects = ips_content_projects();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html(ips_t('nav_projects')); ?></h1>
			<p class="page-hero__lead"><?php echo esc_html(ips_t('projects_lead')); ?></p>
		</div>
	</div>

	<div class="filter-bar container" data-filter-bar>
		<button type="button" class="filter-bar__btn is-active" data-filter="all"><?php echo esc_html(ips_is_en() ? 'All' : 'ყველა'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="interior"><?php echo esc_html(ips_is_en() ? 'Interior' : 'ინტერიერი'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="facade"><?php echo esc_html(ips_is_en() ? 'Facade' : 'ფასადი'); ?></button>
	</div>

	<div class="container project-grid" data-filter-grid>
		<?php if (have_posts()) : ?>
			<?php while (have_posts()) : the_post();
				$terms = get_the_terms(get_the_ID(), 'project_type');
				$type_slugs = [];
				if ($terms && !is_wp_error($terms)) {
					foreach ($terms as $term) {
						$type_slugs[] = $term->slug;
					}
				}
				$type_attr = implode(' ', array_unique($type_slugs));
				$type_label = $terms && !is_wp_error($terms)
					? implode(', ', wp_list_pluck($terms, 'name'))
					: '';
				?>
				<a class="project-tile" href="<?php the_permalink(); ?>" data-types="<?php echo esc_attr($type_attr); ?>">
					<span class="project-tile__media">
						<?php if (has_post_thumbnail()) : ?>
							<?php the_post_thumbnail('ips-project'); ?>
						<?php else : ?>
							<span class="project-tile__placeholder" aria-hidden="true"></span>
						<?php endif; ?>
					</span>
					<span class="project-tile__meta">
						<?php if ($type_label) : ?>
							<span class="project-tile__type"><?php echo esc_html($type_label); ?></span>
						<?php endif; ?>
						<span class="project-tile__title"><?php the_title(); ?></span>
					</span>
				</a>
			<?php endwhile; ?>
		<?php else : ?>
			<?php foreach ($content_projects as $project) :
				$img = ips_content_image_url($project['image'] ?? null);
				$types = $project['types'] ?? [];
				$slug = (string) ($project['slug'] ?? '');
				$href = $slug !== '' ? home_url('/project/' . $slug . '/') : '#';
				?>
				<a class="project-tile" href="<?php echo esc_url($href); ?>" data-types="<?php echo esc_attr(implode(' ', $types)); ?>">
					<span class="project-tile__media">
						<?php if ($img) : ?>
							<img src="<?php echo esc_url($img); ?>" alt="<?php echo esc_attr(ips_project_title($project)); ?>" loading="lazy">
						<?php else : ?>
							<span class="project-tile__placeholder" aria-hidden="true"></span>
						<?php endif; ?>
					</span>
					<span class="project-tile__meta">
						<span class="project-tile__type"><?php echo esc_html(implode(', ', $types)); ?></span>
						<span class="project-tile__title"><?php echo esc_html(ips_project_title($project)); ?></span>
					</span>
				</a>
			<?php endforeach; ?>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
