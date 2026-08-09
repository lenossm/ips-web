<?php
/* homepage */

get_header();

$home     = ips_content_section('home');
$about    = ips_content_section('about');
$projects = ips_content_projects();
$posts    = ips_content_posts();
$featured = array_slice($projects, 0, 8);
$news     = array_slice($posts, 0, 3);

$projects_url = get_post_type_archive_link('project') ?: home_url('/project/');
$about_url    = home_url('/about-us/');
$services_url = home_url('/services/');
$news_url     = home_url('/news-blogs/');
?>

<main id="main" class="site-main">

	<section class="hero" data-reveal="hero">
		<div class="hero__media" aria-hidden="true">
			<div class="hero__image"></div>
			<div class="hero__veil"></div>
			<div class="hero__grid"></div>
		</div>
		<div class="hero__frame" aria-hidden="true"></div>

		<div class="hero__content">
			<p class="hero__brand">IPS</p>
			<div class="hero__rule" aria-hidden="true"></div>
			<h1 class="hero__title" data-reveal-item>
				<?php echo esc_html($home['hero_title'] ?? ips_t('hero_title')); ?>
			</h1>
			<p class="hero__lead" data-reveal-item>
				<?php echo esc_html($home['hero_lead'] ?? ips_t('hero_lead')); ?>
			</p>
			<div class="hero__actions" data-reveal-item>
				<a class="btn btn--light" href="<?php echo esc_url($projects_url); ?>">
					<?php echo esc_html($home['cta_projects'] ?? ips_t('cta_projects')); ?>
				</a>
				<a class="btn btn--ghost" href="<?php echo esc_url($services_url); ?>">
					<?php echo esc_html(ips_t('nav_services')); ?>
				</a>
			</div>
		</div>

		<div class="hero__meta" aria-hidden="true">
			<span><?php echo esc_html(ips_is_en() ? 'Tbilisi' : 'თბილისი'); ?></span>
			<span>2016</span>
		</div>
		<div class="hero__scroll" aria-hidden="true"><span></span></div>
	</section>

	<section class="directions" id="directions">
		<div class="directions__pair">
			<a class="direction direction--interior" href="<?php echo esc_url($services_url); ?>#interior" data-reveal>
				<span class="direction__bg" aria-hidden="true"></span>
				<span class="direction__shade" aria-hidden="true"></span>
				<span class="direction__body">
					<span class="direction__eyebrow"><?php echo esc_html(ips_t('nav_interior')); ?></span>
					<span class="direction__title"><?php echo esc_html($home['interior_title'] ?? ips_t('interior_title')); ?></span>
					<span class="direction__lead"><?php echo esc_html($home['interior_lead'] ?? ips_t('interior_lead')); ?></span>
					<span class="direction__cta"><?php echo esc_html(ips_t('nav_services')); ?></span>
				</span>
			</a>
			<a class="direction direction--facade" href="<?php echo esc_url($services_url); ?>#facade" data-reveal>
				<span class="direction__bg" aria-hidden="true"></span>
				<span class="direction__shade" aria-hidden="true"></span>
				<span class="direction__body">
					<span class="direction__eyebrow"><?php echo esc_html(ips_t('nav_facade')); ?></span>
					<span class="direction__title"><?php echo esc_html($home['facade_title'] ?? ips_t('facade_title')); ?></span>
					<span class="direction__lead"><?php echo esc_html($home['facade_lead'] ?? ips_t('facade_lead')); ?></span>
					<span class="direction__cta"><?php echo esc_html(ips_t('nav_services')); ?></span>
				</span>
			</a>
		</div>
	</section>

	<section class="mission" data-reveal>
		<div class="container mission__grid">
			<div class="mission__copy">
				<?php
				$mission = $about['mission'] ?? [];
				$mission_title = $mission[2] ?? ($about['mission_title'] ?? ips_t('mission_title'));
				$mission_text  = trim(implode(' ', array_slice($mission, 0, 2)));
				?>
				<h2 class="mission__title"><?php echo esc_html((string) $mission_title); ?></h2>
				<p class="mission__text"><?php echo esc_html($mission_text !== '' ? $mission_text : ips_t('mission_text')); ?></p>
				<a class="text-link" href="<?php echo esc_url($about_url); ?>"><?php echo esc_html(ips_t('nav_about')); ?></a>
			</div>
			<ul class="values">
				<?php foreach (($about['values'] ?? []) as $i => $value) : ?>
					<li class="values__item" data-reveal-item>
						<span><?php echo esc_html(str_pad((string) ($i + 1), 2, '0', STR_PAD_LEFT)); ?></span>
						<?php echo esc_html((string) $value); ?>
					</li>
				<?php endforeach; ?>
			</ul>
		</div>
	</section>

	<section class="projects-strip" data-reveal>
		<div class="container projects-strip__head">
			<h2 class="section-title"><?php echo esc_html(ips_t('projects_title')); ?></h2>
			<p class="section-lead">
				<?php echo esc_html(count($projects) . (ips_is_en() ? ' projects' : ' პროექტი')); ?>
			</p>
			<a class="text-link" href="<?php echo esc_url($projects_url); ?>"><?php echo esc_html(ips_t('view_all')); ?></a>
		</div>
		<div class="container projects-strip__track">
			<?php foreach ($featured as $project) :
				$img = ips_content_image_url($project['image'] ?? null);
				$types = implode(', ', $project['types'] ?? []);
				$slug = (string) ($project['slug'] ?? '');
				$href = $slug !== '' ? home_url('/project/' . $slug . '/') : $projects_url;
				?>
				<a class="project-tile" href="<?php echo esc_url($href); ?>" data-reveal-item>
					<span class="project-tile__media">
						<?php if ($img) : ?>
							<img src="<?php echo esc_url($img); ?>" alt="<?php echo esc_attr(ips_project_title($project)); ?>" loading="lazy">
						<?php else : ?>
							<span class="project-tile__placeholder" aria-hidden="true"></span>
						<?php endif; ?>
					</span>
					<span class="project-tile__meta">
						<?php if ($types) : ?><span class="project-tile__type"><?php echo esc_html($types); ?></span><?php endif; ?>
						<span class="project-tile__title"><?php echo esc_html(ips_project_title($project)); ?></span>
					</span>
				</a>
			<?php endforeach; ?>
		</div>
	</section>

	<?php if ($news) : ?>
	<section class="news-strip" data-reveal>
		<div class="container projects-strip__head">
			<h2 class="section-title"><?php echo esc_html(ips_t('nav_news')); ?></h2>
			<a class="text-link" href="<?php echo esc_url($news_url); ?>"><?php echo esc_html(ips_t('read_more')); ?></a>
		</div>
		<div class="container post-list">
			<?php foreach ($news as $post_item) :
				$img = ips_content_image_url($post_item['image'] ?? null);
				$slug = (string) ($post_item['slug'] ?? '');
				$href = $slug !== '' ? home_url('/' . $slug . '/') : $news_url;
				$title = ips_is_en()
					? (string) ($post_item['title']['en'] ?? $post_item['title']['ka'] ?? '')
					: (string) ($post_item['title']['ka'] ?? $post_item['title']['en'] ?? '');
				?>
				<article class="post-card" data-reveal-item>
					<?php if ($img) : ?>
						<a class="post-card__media" href="<?php echo esc_url($href); ?>">
							<img src="<?php echo esc_url($img); ?>" alt="<?php echo esc_attr($title); ?>" loading="lazy">
						</a>
					<?php endif; ?>
					<div class="post-card__body">
						<h3 class="post-card__title"><a href="<?php echo esc_url($href); ?>"><?php echo esc_html($title); ?></a></h3>
						<a class="text-link" href="<?php echo esc_url($href); ?>"><?php echo esc_html(ips_t('read_more')); ?></a>
					</div>
				</article>
			<?php endforeach; ?>
		</div>
	</section>
	<?php endif; ?>

	<section class="cta-band" id="contact" data-reveal>
		<div class="container cta-band__inner">
			<h2 class="cta-band__title"><?php echo esc_html(ips_t('cta_contact')); ?></h2>
			<p class="cta-band__text">
				<?php
				$contact = $about['contact'] ?? [];
				echo esc_html(($contact['address'] ?? ips_t('address')) . ' · ' . ($contact['phone'] ?? ips_t('phone')));
				?>
			</p>
			<?php get_template_part('template-parts/contact', 'form'); ?>
		</div>
	</section>

</main>

<?php
get_footer();
