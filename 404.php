<?php
/* 404 */

get_header();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title">404</h1>
			<p class="page-hero__lead">
				<?php echo esc_html(ips_is_en() ? 'Page not found.' : 'გვერდი ვერ მოიძებნა.'); ?>
			</p>
			<a class="btn btn--dark" href="<?php echo esc_url(home_url('/')); ?>">IPS</a>
		</div>
	</div>
</main>

<?php
get_footer();
