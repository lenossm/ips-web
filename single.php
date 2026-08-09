<?php
/* single blog post */

get_header();
?>

<main id="main" class="site-main">
	<?php while (have_posts()) : the_post(); ?>
		<article <?php post_class(); ?>>
			<div class="page-hero">
				<div class="container">
					<p class="page-hero__meta"><?php echo esc_html(get_the_date()); ?></p>
					<h1 class="page-hero__title"><?php the_title(); ?></h1>
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
		</article>
	<?php endwhile; ?>
</main>

<?php
get_footer();
