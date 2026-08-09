<?php
/* projects archive — uses wp posts, falls back to site.json */

get_header();
$content_projects = ips_content_projects();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html(ips_t('nav_projects')); ?></h1>
			<p class="page-hero__lead">
				<?php
				echo esc_html(
					have_posts()
						? ips_t('projects_lead')
						: (count($content_projects) . (ips_is_en() ? ' projects from ips.ge' : ' პროექტი ips.ge-დან'))
				);
				?>
			</p>
		</div>
	</div>

	<div class="filter-bar container" data-filter-bar>
		<button type="button" class="filter-bar__btn is-active" data-filter="all"><?php echo esc_html(ips_is_en() ? 'All' : 'ყველა'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="interior"><?php echo esc_html(ips_is_en() ? 'Interior' : 'ინტერიერი'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="facade"><?php echo esc_html(ips_is_en() ? 'Facade' : 'ფასადი'); ?></button>
	</div>

	<div class="container project-grid" data-filter-grid>
		<?php if (have_posts()) : ?>
			<?php while (have_posts()) : the_post(); ?>
				<a class="project-tile" href="<?php the_permalink(); ?>" data-types="project">
					<span class="project-tile__media">
						<?php if (has_post_thumbnail()) : ?>
							<?php the_post_thumbnail('ips-project'); ?>
						<?php else : ?>
							<span class="project-tile__placeholder" aria-hidden="true"></span>
						<?php endif; ?>
					</span>
					<span class="project-tile__meta">
						<span class="project-tile__title"><?php the_title(); ?></span>
					</span>
				</a>
			<?php endwhile; ?>
		<?php else : ?>
			<?php foreach ($content_projects as $project) :
				$img = ips_content_image_url($project['image'] ?? null);
				$types = implode(' ', $project['types'] ?? []);
				?>
				<article class="project-tile" data-types="<?php echo esc_attr($types); ?>">
					<span class="project-tile__media">
						<?php if ($img) : ?>
							<img src="<?php echo esc_url($img); ?>" alt="<?php echo esc_attr(ips_project_title($project)); ?>" loading="lazy">
						<?php else : ?>
							<span class="project-tile__placeholder" aria-hidden="true"></span>
						<?php endif; ?>
					</span>
					<span class="project-tile__meta">
						<span class="project-tile__type"><?php echo esc_html(implode(', ', $project['types'] ?? [])); ?></span>
						<span class="project-tile__title"><?php echo esc_html(ips_project_title($project)); ?></span>
					</span>
				</article>
			<?php endforeach; ?>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
