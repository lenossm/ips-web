/* filters on project / brand grids */

(() => {
	document.querySelectorAll("[data-filter-bar]").forEach((bar) => {
		const grid =
			bar.parentElement?.querySelector("[data-filter-grid]") ||
			document.querySelector("[data-filter-grid]");
		if (!grid) return;

		bar.addEventListener("click", (event) => {
			const btn = event.target.closest("[data-filter]");
			if (!btn) return;

			const filter = btn.getAttribute("data-filter");
			bar.querySelectorAll("[data-filter]").forEach((el) => {
				el.classList.toggle("is-active", el === btn);
			});

			grid.querySelectorAll("[data-types]").forEach((card) => {
				const types = (card.getAttribute("data-types") || "").split(/\s+/);
				const show = filter === "all" || types.includes(filter);

				if (show) {
					card.classList.remove("is-filtering-out");
					card.classList.remove("is-hidden-filter");
				} else {
					card.classList.add("is-filtering-out");
					window.setTimeout(() => {
						if (card.classList.contains("is-filtering-out")) {
							card.classList.add("is-hidden-filter");
						}
					}, 240);
				}
			});
		});
	});

	const type = new URLSearchParams(window.location.search).get("type");
	if (type) {
		const btn = document.querySelector(`[data-filter-bar] [data-filter="${type}"]`);
		if (btn) btn.click();
	}
})();
