<?php
/* header — logo, nav, language switch */

?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo('charset'); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<a class="skip-link" href="#main"><?php echo esc_html(ips_is_en() ? 'Skip to content' : 'გადასვლა კონტენტზე'); ?></a>

<div class="scroll-progress" data-scroll-progress aria-hidden="true"></div>
<div class="page-transition" data-page-transition aria-hidden="true"></div>

<header class="site-header" data-header>
	<div class="site-header__inner">
		<?php if (has_custom_logo()) : ?>
			<div class="brand brand--logo"><?php the_custom_logo(); ?></div>
		<?php else : ?>
			<a class="brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="IPS">
				<span class="brand__mark" aria-hidden="true">
					<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
						<rect x="4" y="4" width="40" height="40" stroke="currentColor" stroke-width="2"/>
						<path d="M14 34V14h8.2c4.4 0 7.2 2.4 7.2 6.2 0 3.8-2.8 6.2-7.2 6.2H18.5V34H14zm4.5-11.4h3.4c2.1 0 3.3-1 3.3-2.6s-1.2-2.6-3.3-2.6h-3.4v5.2zM36 14v4h-6.5v16H25V14h11z" fill="currentColor"/>
					</svg>
				</span>
				<span class="brand__text">IPS</span>
			</a>
		<?php endif; ?>

		<nav class="site-nav" data-nav aria-label="<?php echo esc_attr(ips_t('menu')); ?>">
			<?php
			wp_nav_menu([
				'theme_location' => 'primary',
				'container'      => false,
				'menu_class'     => 'nav-list',
				'fallback_cb'    => 'ips_fallback_menu',
				'depth'          => 2,
			]);
			?>
		</nav>

		<div class="site-header__actions">
			<?php
			$langs = ips_language_urls();
			$current = ips_lang();
			?>
			<div class="lang-switch" aria-label="Language">
				<a class="lang-switch__link<?php echo $current === 'ka' ? ' is-active' : ''; ?>" href="<?php echo esc_url($langs['ka']); ?>" hreflang="ka" lang="ka">ქარ</a>
				<span class="lang-switch__sep" aria-hidden="true"></span>
				<a class="lang-switch__link<?php echo $current === 'en' ? ' is-active' : ''; ?>" href="<?php echo esc_url($langs['en']); ?>" hreflang="en" lang="en">EN</a>
			</div>

			<button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="mobile-nav">
				<span class="nav-toggle__label"><?php echo esc_html(ips_t('menu')); ?></span>
				<span class="nav-toggle__icon" aria-hidden="true">
					<span></span>
					<span></span>
				</span>
			</button>
		</div>
	</div>

	<div class="mobile-nav" id="mobile-nav" data-mobile-nav hidden>
		<?php
		wp_nav_menu([
			'theme_location' => 'primary',
			'container'      => false,
			'menu_class'     => 'nav-list',
			'fallback_cb'    => 'ips_fallback_menu',
			'depth'          => 2,
		]);
		?>
		<a class="btn btn--light mobile-nav__cta" href="<?php echo esc_url(home_url('/about-us/#contact')); ?>">
			<?php echo esc_html(ips_t('cta_contact')); ?>
		</a>
	</div>
</header>
