/* menu, reveals, hero, parallax */

(() => {
	const header = document.querySelector("[data-header]");
	const toggle = document.querySelector("[data-nav-toggle]");
	const mobileNav = document.querySelector("[data-mobile-nav]");
	const hero = document.querySelector(".hero");
	const heroImage = document.querySelector(".hero__image");
	const progress = document.querySelector("[data-scroll-progress]");
	const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
	const isNarrow = () => window.matchMedia("(max-width: 899px)").matches;

	let lastY = 0;
	const onScrollHeader = () => {
		if (!header) return;
		const y = window.scrollY || 0;
		header.classList.toggle("is-scrolled", y > 12);
		if (!isNarrow() && y > 180 && y > lastY && !header.classList.contains("is-open")) {
			header.classList.add("is-hidden");
		} else {
			header.classList.remove("is-hidden");
		}
		lastY = y;
	};

	const onScrollProgress = () => {
		if (!progress) return;
		const doc = document.documentElement;
		const max = Math.max(doc.scrollHeight - window.innerHeight, 1);
		progress.style.width = `${Math.min(Math.max((window.scrollY / max) * 100, 0), 100)}%`;
	};

	const onScroll = () => {
		onScrollHeader();
		onScrollProgress();
	};

	onScroll();
	window.addEventListener("scroll", onScroll, { passive: true });
	window.addEventListener("resize", onScrollHeader, { passive: true });

	if (toggle && mobileNav && header) {
		const closeNav = () => {
			header.classList.remove("is-open");
			toggle.setAttribute("aria-expanded", "false");
			mobileNav.classList.remove("is-visible");
			mobileNav.querySelectorAll(".has-children.is-open, .menu-item-has-children.is-open").forEach((item) => {
				item.classList.remove("is-open");
				const parentLink = item.querySelector(":scope > a");
				if (parentLink) parentLink.setAttribute("aria-expanded", "false");
			});
			window.setTimeout(() => {
				if (!header.classList.contains("is-open")) mobileNav.hidden = true;
			}, 400);
			document.body.style.overflow = "";
		};

		const openNav = () => {
			header.classList.add("is-open");
			toggle.setAttribute("aria-expanded", "true");
			mobileNav.hidden = false;
			requestAnimationFrame(() => mobileNav.classList.add("is-visible"));
			document.body.style.overflow = "hidden";
		};

		toggle.addEventListener("click", () => {
			if (toggle.getAttribute("aria-expanded") === "true") closeNav();
			else openNav();
		});

		/* accordion: tap parent to open kids, don't leave the page */
		mobileNav.querySelectorAll(".has-children, .menu-item-has-children").forEach((item) => {
			const link = item.querySelector(":scope > a");
			const sub = item.querySelector(":scope > .sub-menu");
			if (!link || !sub) return;

			link.setAttribute("aria-expanded", "false");
			link.addEventListener("click", (event) => {
				event.preventDefault();
				const open = item.classList.contains("is-open");
				mobileNav
					.querySelectorAll(".has-children.is-open, .menu-item-has-children.is-open")
					.forEach((other) => {
						if (other === item) return;
						other.classList.remove("is-open");
						const otherLink = other.querySelector(":scope > a");
						if (otherLink) otherLink.setAttribute("aria-expanded", "false");
					});
				item.classList.toggle("is-open", !open);
				link.setAttribute("aria-expanded", open ? "false" : "true");
			});
		});

		mobileNav.querySelectorAll("a").forEach((link) => {
			link.addEventListener("click", (event) => {
				const parent = link.parentElement;
				if (parent?.classList.contains("has-children") || parent?.classList.contains("menu-item-has-children")) {
					return;
				}
				if (link.getAttribute("href") === "#") {
					event.preventDefault();
					return;
				}
				closeNav();
			});
		});

		window.addEventListener("keydown", (event) => {
			if (event.key === "Escape") closeNav();
		});

		window.addEventListener(
			"resize",
			() => {
				if (window.matchMedia("(min-width: 1100px)").matches) closeNav();
			},
			{ passive: true }
		);
	}

	const brand = document.querySelector(".hero__brand");
	if (brand && !reduce && !brand.querySelector(".char")) {
		const text = brand.textContent.trim();
		brand.textContent = "";
		[...text].forEach((letter, i) => {
			const span = document.createElement("span");
			span.className = "char";
			span.textContent = letter;
			span.style.transitionDelay = `${0.08 + i * 0.08}s`;
			brand.appendChild(span);
		});
	}

	const revealNodes = [
		...document.querySelectorAll("[data-reveal]"),
		...document.querySelectorAll(".hero"),
		...document.querySelectorAll(".project-single"),
	];

	if (reduce) {
		revealNodes.forEach((node) => node.classList.add("is-in"));
	} else {
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (!entry.isIntersecting) return;
					entry.target.classList.add("is-in");
					observer.unobserve(entry.target);
				});
			},
			{ threshold: isNarrow() ? 0.08 : 0.12, rootMargin: "0px 0px -5% 0px" }
		);
		revealNodes.forEach((node) => observer.observe(node));
		if (hero) requestAnimationFrame(() => hero.classList.add("is-in"));
	}

	if (hero && heroImage && !reduce) {
		let ticking = false;
		window.addEventListener(
			"scroll",
			() => {
				if (ticking) return;
				ticking = true;
				requestAnimationFrame(() => {
					const rect = hero.getBoundingClientRect();
					const p = Math.min(Math.max(-rect.top / Math.max(rect.height, 1), 0), 1);
					const scaleAmt = isNarrow() ? 0.06 : 0.12;
					const shiftAmt = isNarrow() ? 4 : 10;
					heroImage.style.transform = `scale(${1.18 - p * scaleAmt}) translate3d(0, ${p * shiftAmt}%, 0)`;
					ticking = false;
				});
			},
			{ passive: true }
		);
	}

	if (!reduce && finePointer) {
		document.querySelectorAll(".btn").forEach((btn) => {
			btn.addEventListener("pointermove", (event) => {
				const rect = btn.getBoundingClientRect();
				const x = event.clientX - rect.left - rect.width / 2;
				const y = event.clientY - rect.top - rect.height / 2;
				btn.style.transform = `translate(${x * 0.12}px, ${y * 0.16}px)`;
			});
			btn.addEventListener("pointerleave", () => {
				btn.style.transform = "";
			});
		});
	}
})();
