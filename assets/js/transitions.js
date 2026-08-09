/* page curtain + contact form */

(() => {
	const curtain = document.querySelector("[data-page-transition]");
	const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

	if (curtain && !reduce) {
		curtain.classList.add("is-covering");
		requestAnimationFrame(() => {
			requestAnimationFrame(() => {
				curtain.classList.remove("is-covering");
				curtain.classList.add("is-revealing");
				window.setTimeout(() => curtain.classList.remove("is-revealing"), 620);
			});
		});
	}

	const goTo = (href) => {
		if (!curtain || reduce) {
			window.location.href = href;
			return;
		}
		curtain.classList.remove("is-revealing");
		curtain.classList.add("is-covering");
		window.setTimeout(() => {
			window.location.href = href;
		}, 560);
	};

	document.addEventListener("click", (event) => {
		const link = event.target.closest("a[href]");
		if (!link) return;

		const href = link.getAttribute("href");
		if (!href) return;
		if (href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) return;
		if (link.target === "_blank" || link.hasAttribute("download")) return;
		if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

		let url;
		try {
			url = new URL(href, window.location.href);
		} catch (error) {
			return;
		}

		if (url.origin !== window.location.origin) return;
		if (url.pathname === window.location.pathname && url.hash) return;

		event.preventDefault();
		goTo(url.href);
	});

	document.querySelectorAll("[data-contact-form]").forEach((form) => {
		form.addEventListener("submit", async (event) => {
			event.preventDefault();

			const status = form.querySelector("[data-form-status]");
			const btn = form.querySelector('button[type="submit"]');
			const ok = status?.getAttribute("data-ok") || "Sent";
			const err = status?.getAttribute("data-err") || "Error";

			if (status) {
				status.textContent = "";
				status.classList.remove("is-ok", "is-error");
			}
			if (btn) btn.disabled = true;

			try {
				const data = new FormData(form);
				const res = await fetch(form.action, {
					method: "POST",
					body: data,
					headers: { Accept: "application/json" },
				});
				if (!res.ok) throw new Error("send failed");
				form.reset();
				if (status) {
					status.textContent = ok;
					status.classList.add("is-ok");
				}
			} catch (error) {
				if (status) {
					status.textContent = err;
					status.classList.add("is-error");
				}
			} finally {
				if (btn) btn.disabled = false;
			}
		});
	});
})();
