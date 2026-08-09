/* menu, light reveals, hero */

(() => {
	const header = document.querySelector("[data-header]");
	const toggle = document.querySelector("[data-nav-toggle]");
	const mobileNav = document.querySelector("[data-mobile-nav]");
	const hero = document.querySelector(".hero");
	const progress = document.querySelector("[data-scroll-progress]");
	const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
	const isNarrow = () => window.matchMedia("(max-width: 899px)").matches;

	let lastY = 0;
	const onScroll = () => {
		const y = window.scrollY || 0;
		if (header) {
			header.classList.toggle("is-scrolled", y > 12);
			if (!isNarrow() && y > 200 && y > lastY && !header.classList.contains("is-open")) {
				header.classList.add("is-hidden");
			} else {
				header.classList.remove("is-hidden");
			}
			lastY = y;
		}
		if (progress) {
			const max = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
			progress.style.width = `${Math.min((y / max) * 100, 100)}%`;
		}
	};
	onScroll();
	window.addEventListener("scroll", onScroll, { passive: true });

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
			mobileNav.hidden = true;
			document.body.style.overflow = "";
		};

		const openNav = () => {
			header.classList.add("is-open");
			toggle.setAttribute("aria-expanded", "true");
			mobileNav.hidden = false;
			mobileNav.classList.add("is-visible");
			document.body.style.overflow = "hidden";
		};

		toggle.addEventListener("click", () => {
			if (toggle.getAttribute("aria-expanded") === "true") closeNav();
			else openNav();
		});

		mobileNav.querySelectorAll(".has-children, .menu-item-has-children").forEach((item) => {
			const link = item.querySelector(":scope > a");
			const sub = item.querySelector(":scope > .sub-menu");
			if (!link || !sub) return;
			link.setAttribute("aria-expanded", "false");
			link.addEventListener("click", (event) => {
				event.preventDefault();
				const open = item.classList.contains("is-open");
				mobileNav.querySelectorAll(".has-children.is-open, .menu-item-has-children.is-open").forEach((other) => {
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
			link.addEventListener("click", () => {
				const parent = link.parentElement;
				if (parent?.classList.contains("has-children") || parent?.classList.contains("menu-item-has-children")) {
					return;
				}
				if (link.getAttribute("href") === "#") return;
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
			span.style.transitionDelay = `${0.05 + i * 0.05}s`;
			brand.appendChild(span);
		});
	}

	const revealNodes = [
		...document.querySelectorAll("[data-reveal]"),
		...document.querySelectorAll(".hero"),
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
			{ threshold: 0.08, rootMargin: "0px 0px -4% 0px" }
		);
		revealNodes.forEach((node) => observer.observe(node));
		if (hero) requestAnimationFrame(() => hero.classList.add("is-in"));
	}
})();
