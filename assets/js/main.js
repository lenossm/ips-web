/* main interactions — menu, scroll reveals, hero letters, parallax */

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

	/* sticky header — hides on desktop when scrolling down, stays put on phones */
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
		const pct = Math.min(Math.max((window.scrollY / max) * 100, 0), 100);
		progress.style.width = `${pct}%`;
	};

	const onScroll = () => {
		onScrollHeader();
		onScrollProgress();
	};

	onScroll();
	window.addEventListener("scroll", onScroll, { passive: true });
	window.addEventListener("resize", onScrollHeader, { passive: true });

	/* mobile menu */
	if (toggle && mobileNav && header) {
		const closeNav = () => {
			header.classList.remove("is-open");
			toggle.setAttribute("aria-expanded", "false");
			mobileNav.classList.remove("is-visible");
			window.setTimeout(() => {
				if (!header.classList.contains("is-open")) mobileNav.hidden = true;
			}, 420);
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
			const open = toggle.getAttribute("aria-expanded") === "true";
			if (open) closeNav();
			else openNav();
		});

		mobileNav.querySelectorAll("a").forEach((link) => {
			link.addEventListener("click", closeNav);
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

	/* split IPS letters so they can animate one by one */
	const brand = document.querySelector(".hero__brand");
	if (brand && !reduce) {
		const text = brand.textContent.trim();
		brand.textContent = "";
		[...text].forEach((letter, i) => {
			const span = document.createElement("span");
			span.className = "char";
			span.textContent = letter;
			span.style.transitionDelay = `${0.1 + i * 0.09}s`;
			brand.appendChild(span);
		});
	}

	/* stagger delays for tiles / cards inside a reveal section */
	const stampDelays = (root) => {
		const items = root.querySelectorAll(
			"[data-reveal-item], .project-tile, .post-card, .brand-card, .service-card, .values__item, .history-list li"
		);
		items.forEach((item, i) => {
			if (!item.style.transitionDelay) {
				item.style.transitionDelay = `${Math.min(i * 0.06, 0.54)}s`;
			}
		});
	};

	/* fade stuff in when it enters the viewport */
	const revealNodes = [
		...document.querySelectorAll("[data-reveal]"),
		...document.querySelectorAll(".hero"),
		...document.querySelectorAll(".project-single"),
	];

	revealNodes.forEach(stampDelays);

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
			{ threshold: isNarrow() ? 0.08 : 0.14, rootMargin: "0px 0px -6% 0px" }
		);

		revealNodes.forEach((node) => observer.observe(node));
		if (hero) requestAnimationFrame(() => hero.classList.add("is-in"));
	}

	/* soft parallax on the hero photo — lighter on phones so it stays smooth */
	if (hero && heroImage && !reduce) {
		let ticking = false;
		window.addEventListener(
			"scroll",
			() => {
				if (ticking) return;
				ticking = true;
				requestAnimationFrame(() => {
					const rect = hero.getBoundingClientRect();
					const progressY = Math.min(Math.max(-rect.top / Math.max(rect.height, 1), 0), 1);
					const scaleAmt = isNarrow() ? 0.08 : 0.16;
					const shiftAmt = isNarrow() ? 6 : 12;
					heroImage.style.transform = `scale(${1.22 - progressY * scaleAmt}) translate3d(0, ${progressY * shiftAmt}%, 0)`;
					ticking = false;
				});
			},
			{ passive: true }
		);
	}

	/* buttons that follow the cursor a tiny bit — desktop only */
	if (!reduce && finePointer) {
		document.querySelectorAll(".btn").forEach((btn) => {
			btn.addEventListener("pointermove", (event) => {
				const rect = btn.getBoundingClientRect();
				const x = event.clientX - rect.left - rect.width / 2;
				const y = event.clientY - rect.top - rect.height / 2;
				btn.style.transform = `translate(${x * 0.16}px, ${y * 0.22}px)`;
			});
			btn.addEventListener("pointerleave", () => {
				btn.style.transform = "";
			});
		});
	}

	/* tiny tilt on project tiles when the mouse moves over them */
	if (!reduce && finePointer) {
		document.querySelectorAll(".project-tile").forEach((tile) => {
			tile.addEventListener("pointermove", (event) => {
				const rect = tile.getBoundingClientRect();
				const x = (event.clientX - rect.left) / rect.width - 0.5;
				const y = (event.clientY - rect.top) / rect.height - 0.5;
				tile.style.transform = `perspective(700px) rotateY(${x * 4}deg) rotateX(${-y * 4}deg)`;
			});
			tile.addEventListener("pointerleave", () => {
				tile.style.transform = "";
			});
		});
	}
})();
