<?php
/* single project page */

get_header();
?>

<main id="main" class="site-main">
	<?php while (have_posts()) : the_post(); ?>
		<article <?php post_class('project-single'); ?>>
			<div class="project-single__hero">
				<?php if (has_post_thumbnail()) : ?>
					<?php the_post_thumbnail('ips-hero'); ?>
				<?php else : ?>
					<div class="project-single__fallback" aria-hidden="true"></div>
				<?php endif; ?>
				<div class="project-single__overlay">
					<div class="container">
						<?php
						$types = get_the_terms(get_the_ID(), 'project_type');
						if ($types && !is_wp_error($types)) :
							?>
							<p class="project-single__type"><?php echo esc_html($types[0]->name); ?></p>
						<?php endif; ?>
						<h1 class="project-single__title"><?php the_title(); ?></h1>
					</div>
				</div>
			</div>
			<div class="container content-wrap prose">
				<?php the_content(); ?>
			</div>
		</article>
	<?php endwhile; ?>
</main>

<?php
get_footer();
