<?php
/*
Template Name: Services
for the interior / facade / services pages
*/

get_header();
?>

<main id="main" class="site-main">
	<?php while (have_posts()) : the_post(); ?>
		<div class="page-hero">
			<div class="container">
				<h1 class="page-hero__title"><?php the_title(); ?></h1>
				<?php if (has_excerpt()) : ?>
					<p class="page-hero__lead"><?php echo esc_html(get_the_excerpt()); ?></p>
				<?php endif; ?>
			</div>
		</div>

		<?php if (has_post_thumbnail()) : ?>
			<div class="single-featured">
				<?php the_post_thumbnail('ips-hero'); ?>
			</div>
		<?php endif; ?>

		<div class="container content-wrap prose">
			<?php the_content(); ?>
		</div>
	<?php endwhile; ?>
</main>

<?php
get_footer();
