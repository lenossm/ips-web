<?php
/*
Template Name: Content — Brands
*/

get_header();
$brands = ips_content_brands();
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html(ips_is_en() ? 'Brands' : 'ბრენდები'); ?></h1>
			<p class="page-hero__lead">
				<?php echo esc_html(count($brands) . (ips_is_en() ? ' partner brands' : ' პარტნიორი ბრენდი')); ?>
			</p>
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
			$types = $brand['types'] ?? [];
			$cats = $brand['categories'] ?? [];
			$cat_labels = [];
			foreach ($cats as $cat) {
				if (is_array($cat)) {
					$cat_labels[] = (string) ($cat['name'] ?? '');
				} else {
					$cat_labels[] = (string) $cat;
				}
			}
			$cat_labels = array_values(array_filter($cat_labels));
			$name = (string) ($brand['name'] ?? $brand['title']['ka'] ?? $brand['title']['en'] ?? '');
			$slug = (string) ($brand['slug'] ?? '');
			$href = $slug !== '' ? home_url('/brand/' . $slug . '/') : '';
			?>
			<?php if ($href !== '') : ?>
				<a class="brand-card" href="<?php echo esc_url($href); ?>" data-types="<?php echo esc_attr(implode(' ', $types)); ?>">
			<?php else : ?>
				<article class="brand-card" data-types="<?php echo esc_attr(implode(' ', $types)); ?>">
			<?php endif; ?>
					<div class="brand-card__logo">
						<?php if ($logo) : ?>
							<img src="<?php echo esc_url($logo); ?>" alt="<?php echo esc_attr($name); ?>" loading="lazy">
						<?php endif; ?>
					</div>
					<h3 class="brand-card__name"><?php echo esc_html($name); ?></h3>
					<?php if ($cat_labels) : ?>
						<p class="brand-card__cats"><?php echo esc_html(implode(', ', $cat_labels)); ?></p>
					<?php elseif ($types) : ?>
						<p class="brand-card__cats"><?php echo esc_html(implode(', ', $types)); ?></p>
					<?php endif; ?>
			<?php if ($href !== '') : ?>
				</a>
			<?php else : ?>
				</article>
			<?php endif; ?>
		<?php endforeach; ?>
	</div>
</main>

<?php
get_footer();
