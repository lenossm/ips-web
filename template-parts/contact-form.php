<?php
/* contact form — FormSubmit */

if (!defined('ABSPATH')) {
	exit;
}

$email = ips_t('email');
$ok = ips_is_en() ? 'Thanks — we got your message.' : 'გმადლობთ — შეტყობინება მიღებულია.';
$err = ips_is_en() ? 'Something went wrong. Try again.' : 'რაღაც გაფუჭდა. სცადეთ თავიდან.';
?>
<form class="contact-form" data-contact-form action="https://formsubmit.co/ajax/<?php echo esc_attr($email); ?>" method="POST">
	<input type="hidden" name="_subject" value="IPS website">
	<input type="text" name="_honey" tabindex="-1" autocomplete="off" class="contact-form__honey" aria-hidden="true">

	<div class="contact-form__row">
		<label>
			<?php echo esc_html(ips_is_en() ? 'Name' : 'სახელი'); ?>
			<input type="text" name="name" required autocomplete="name">
		</label>
		<label>
			<?php echo esc_html(ips_is_en() ? 'Email' : 'ელ-ფოსტა'); ?>
			<input type="email" name="email" required autocomplete="email">
		</label>
	</div>
	<label>
		<?php echo esc_html(ips_is_en() ? 'Phone' : 'ტელეფონი'); ?>
		<input type="tel" name="phone" autocomplete="tel">
	</label>
	<label>
		<?php echo esc_html(ips_is_en() ? 'Message' : 'შეტყობინება'); ?>
		<textarea name="message" required rows="5"></textarea>
	</label>
	<button class="btn btn--metal" type="submit"><?php echo esc_html(ips_t('cta_contact')); ?></button>
	<p class="contact-form__status" data-form-status data-ok="<?php echo esc_attr($ok); ?>" data-err="<?php echo esc_attr($err); ?>" aria-live="polite"></p>
</form>
