<?php
/*
Template Name: Content — About
mission, history, team, csr, contact
*/

get_header();
$about = ips_content_section('about');
$contact = $about['contact'] ?? [];
?>

<main id="main" class="site-main">
	<div class="page-hero">
		<div class="container">
			<h1 class="page-hero__title"><?php echo esc_html($about['title'] ?? ips_t('nav_about')); ?></h1>
		</div>
	</div>

	<section class="content-section" id="mission">
		<div class="container prose">
			<h2><?php echo esc_html((string) ($about['mission_title'] ?? '')); ?></h2>
			<?php foreach (($about['mission'] ?? []) as $p) : ?>
				<p><?php echo esc_html((string) $p); ?></p>
			<?php endforeach; ?>

			<h2><?php echo esc_html(ips_is_en() ? 'History' : 'ისტორია'); ?></h2>
			<ol class="history-list">
				<?php foreach (($about['history'] ?? []) as $row) : ?>
					<li>
						<strong><?php echo esc_html((string) ($row['year'] ?? '')); ?></strong>
						<span><?php echo esc_html((string) ($row['label'] ?? '')); ?></span>
						<p><?php echo esc_html((string) ($row['text'] ?? '')); ?></p>
					</li>
				<?php endforeach; ?>
			</ol>
		</div>
	</section>

	<section class="content-section" id="team">
		<div class="container prose">
			<h2><?php echo esc_html((string) ($about['team_title'] ?? '')); ?></h2>
			<?php foreach (($about['team'] ?? []) as $p) : ?>
				<p><?php echo esc_html((string) $p); ?></p>
			<?php endforeach; ?>
			<ul class="values">
				<?php foreach (($about['values'] ?? []) as $i => $value) : ?>
					<li class="values__item">
						<span><?php echo esc_html(str_pad((string) ($i + 1), 2, '0', STR_PAD_LEFT)); ?></span>
						<?php echo esc_html((string) $value); ?>
					</li>
				<?php endforeach; ?>
			</ul>
		</div>
	</section>

	<section class="content-section" id="social">
		<div class="container prose">
			<h2><?php echo esc_html((string) ($about['csr_title'] ?? '')); ?></h2>
			<?php foreach (($about['csr'] ?? []) as $p) : ?>
				<p><?php echo esc_html((string) $p); ?></p>
			<?php endforeach; ?>
		</div>
	</section>

	<section class="content-section" id="contact">
		<div class="container">
			<h2><?php echo esc_html(ips_t('nav_contact')); ?></h2>
			<address class="contact-block">
				<p><?php echo esc_html((string) ($contact['address'] ?? ips_t('address'))); ?></p>
				<p><a href="tel:+995322252424"><?php echo esc_html((string) ($contact['phone'] ?? ips_t('phone'))); ?></a></p>
				<p><a href="mailto:<?php echo esc_attr((string) ($contact['email'] ?? ips_t('email'))); ?>"><?php echo esc_html((string) ($contact['email'] ?? ips_t('email'))); ?></a></p>
			</address>
		</div>
	</section>
</main>

<?php
get_footer();
