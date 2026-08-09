<?php
/* normal page */

get_header();
?>

<main id="main" class="site-main">
	<?php while (have_posts()) : the_post(); ?>
		<div class="page-hero">
			<div class="container">
				<h1 class="page-hero__title"><?php the_title(); ?></h1>
			</div>
		</div>
		<div class="container content-wrap prose">
			<?php the_content(); ?>
		</div>
	<?php endwhile; ?>
</main>

<?php
get_footer();
