<?php
/*
Template Name: Content — Services
pulls the service lists straight from site.json
*/

get_header();
$services = ips_content_section('services');
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html($services['title'] ?? ips_t('nav_services')); ?></h1>
		</div>
	</div>

	<?php foreach (['interior' => 'interior', 'facade' => 'facade'] as $key => $anchor) :
		$block = $services[$key] ?? null;
		if (!$block) {
			continue;
		}
		?>
		<section class="content-section" id="<?php echo esc_attr($anchor); ?>">
			<div class="container">
				<h2 class="section-title"><?php echo esc_html((string) ($block['title'] ?? '')); ?></h2>
				<div class="service-grid">
					<?php foreach (($block['items'] ?? []) as $item) : ?>
						<article class="service-card">
							<h3><?php echo esc_html((string) ($item['title'] ?? '')); ?></h3>
							<?php if (!empty($item['points'])) : ?>
								<ul>
									<?php foreach ($item['points'] as $point) : ?>
										<li><?php echo esc_html((string) $point); ?></li>
									<?php endforeach; ?>
								</ul>
							<?php endif; ?>
						</article>
					<?php endforeach; ?>
				</div>
			</div>
		</section>
	<?php endforeach; ?>
</main>

<?php
get_footer();
