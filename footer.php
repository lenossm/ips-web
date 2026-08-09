<?php
/* footer */

$about = function_exists('ips_content_section') ? ips_content_section('about') : [];
$contact = $about['contact'] ?? [];
?>

<footer class="site-footer">
	<div class="site-footer__grain" aria-hidden="true"></div>
	<div class="container site-footer__grid">
		<div class="site-footer__brand">
			<p class="site-footer__logo">IPS</p>
			<p class="site-footer__tag"><?php echo esc_html(ips_t('hero_title')); ?></p>
			<p class="site-footer__since"><?php echo esc_html(ips_t('since')); ?></p>
		</div>

		<div class="site-footer__nav">
			<p class="site-footer__label"><?php echo esc_html(ips_is_en() ? 'Navigate' : 'ნავიგაცია'); ?></p>
			<ul class="footer-nav">
				<li><a href="<?php echo esc_url(home_url('/services/')); ?>"><?php echo esc_html(ips_t('nav_services')); ?></a></li>
				<li><a href="<?php echo esc_url(get_post_type_archive_link('project') ?: home_url('/project/')); ?>"><?php echo esc_html(ips_t('nav_projects')); ?></a></li>
				<li><a href="<?php echo esc_url(home_url('/brands/')); ?>"><?php echo esc_html(ips_is_en() ? 'Brands' : 'ბრენდები'); ?></a></li>
				<li><a href="<?php echo esc_url(home_url('/about-us/')); ?>"><?php echo esc_html(ips_t('nav_about')); ?></a></li>
				<li><a href="<?php echo esc_url(home_url('/news-blogs/')); ?>"><?php echo esc_html(ips_t('nav_news')); ?></a></li>
				<li><a href="<?php echo esc_url(home_url('/about-us/#contact')); ?>"><?php echo esc_html(ips_t('nav_contact')); ?></a></li>
			</ul>
		</div>

		<div class="site-footer__contact">
			<p class="site-footer__label"><?php echo esc_html(ips_t('nav_contact')); ?></p>
			<address class="site-footer__address">
				<?php echo esc_html($contact['address'] ?? ips_t('address')); ?><br>
				<a href="tel:+995322252424"><?php echo esc_html($contact['phone'] ?? ips_t('phone')); ?></a><br>
				<a href="mailto:<?php echo esc_attr($contact['email'] ?? ips_t('email')); ?>"><?php echo esc_html($contact['email'] ?? ips_t('email')); ?></a>
			</address>
		</div>

		<div class="site-footer__social">
			<p class="site-footer__label"><?php echo esc_html(ips_t('social')); ?></p>
			<ul class="social-list">
				<li><a href="https://www.facebook.com/" rel="noopener noreferrer" target="_blank">Facebook</a></li>
				<li><a href="https://www.instagram.com/" rel="noopener noreferrer" target="_blank">Instagram</a></li>
				<li><a href="https://www.linkedin.com/company/ips-interior-facade" rel="noopener noreferrer" target="_blank">LinkedIn</a></li>
			</ul>
		</div>
	</div>

	<div class="container site-footer__bottom">
		<p>&copy; <?php echo esc_html(gmdate('Y')); ?> IPS. <?php echo esc_html(ips_t('rights')); ?></p>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
