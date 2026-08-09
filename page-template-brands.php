<?php
/*
Template Name: Content — Brands
brand grid + the interior/facade filter
*/

get_header();
$brands = ips_content_brands();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html(ips_is_en() ? 'Brands' : 'ბრენდები'); ?></h1>
			<p class="page-hero__lead"><?php echo esc_html(count($brands) . (ips_is_en() ? ' brands from ips.ge' : ' ბრენდი ips.ge-დან')); ?></p>
		</div>
	</div>

	<div class="filter-bar container" data-filter-bar>
		<button type="button" class="filter-bar__btn is-active" data-filter="all"><?php echo esc_html(ips_is_en() ? 'All' : 'ყველა'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="interior"><?php echo esc_html(ips_is_en() ? 'Interior' : 'ინტერიერი'); ?></button>
		<button type="button" class="filter-bar__btn" data-filter="facade"><?php echo esc_html(ips_is_en() ? 'Facade' : 'ფასადი'); ?></button>
	</div>

	<div class="container brand-grid" data-filter-grid>
		<?php foreach ($brands as $brand) :
			$logo = ips_content_image_url($brand['logo'] ?? null);
			$cats = implode(' ', $brand['categories'] ?? []);
			?>
			<article class="brand-card" data-types="<?php echo esc_attr($cats); ?>">
				<div class="brand-card__logo">
					<?php if ($logo) : ?>
						<img src="<?php echo esc_url($logo); ?>" alt="<?php echo esc_attr((string) ($brand['name'] ?? '')); ?>" loading="lazy">
					<?php endif; ?>
				</div>
				<h3 class="brand-card__name"><?php echo esc_html((string) ($brand['name'] ?? '')); ?></h3>
				<p class="brand-card__cats"><?php echo esc_html(implode(', ', $brand['categories'] ?? [])); ?></p>
			</article>
		<?php endforeach; ?>
	</div>
</main>

<?php
get_footer();
