<?php
/* fallback template — blog list, archives, search */

get_header();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<?php if (is_home() && !is_front_page()) : ?>
				<h1 class="page-hero__title"><?php echo esc_html(ips_t('nav_news')); ?></h1>
			<?php elseif (is_archive()) : ?>
				<h1 class="page-hero__title"><?php the_archive_title(); ?></h1>
			<?php elseif (is_search()) : ?>
				<h1 class="page-hero__title"><?php printf(esc_html__('Search: %s', 'ips'), esc_html(get_search_query())); ?></h1>
			<?php else : ?>
				<h1 class="page-hero__title"><?php the_title(); ?></h1>
			<?php endif; ?>
		</div>
	</div>

	<div class="container content-wrap">
		<?php if (have_posts()) : ?>
			<div class="post-list">
				<?php while (have_posts()) : the_post(); ?>
					<article <?php post_class('post-card'); ?>>
						<?php if (has_post_thumbnail()) : ?>
							<a class="post-card__media" href="<?php the_permalink(); ?>">
								<?php the_post_thumbnail('ips-card'); ?>
							</a>
						<?php endif; ?>
						<div class="post-card__body">
							<h2 class="post-card__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
							<div class="post-card__excerpt"><?php the_excerpt(); ?></div>
							<a class="text-link" href="<?php the_permalink(); ?>"><?php echo esc_html(ips_t('read_more')); ?></a>
						</div>
					</article>
				<?php endwhile; ?>
			</div>
			<?php the_posts_pagination(); ?>
		<?php else : ?>
			<p><?php echo esc_html(ips_is_en() ? 'No content found.' : 'კონტენტი ვერ მოიძებნა.'); ?></p>
		<?php endif; ?>
	</div>
</main>

<?php
get_footer();
