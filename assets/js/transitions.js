/* contact form only — no page curtain (keeps navigation fast) */

(() => {
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
