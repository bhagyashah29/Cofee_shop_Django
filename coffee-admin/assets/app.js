/* Simple client-side auth and UI script for Café Admin */
(function () {
	'use strict';

	const DEFAULT_AUTH = { username: 'admin', password: 'coffee123' };
	const SESSION_KEY = 'coffeeAdminSession';
	const PRODUCTS_KEY = 'coffeeAdminProducts';
	const THEME_KEY = 'coffeeAdminTheme';

	function getSessionStoragePayload() {
		try {
			return JSON.parse(sessionStorage.getItem(SESSION_KEY)) || JSON.parse(localStorage.getItem(SESSION_KEY)) || null;
		} catch (_) {
			return null;
		}
	}

	function setSessionStoragePayload(session, remember) {
		const payload = JSON.stringify(session);
		if (remember) {
			localStorage.setItem(SESSION_KEY, payload);
			sessionStorage.removeItem(SESSION_KEY);
		} else {
			sessionStorage.setItem(SESSION_KEY, payload);
			localStorage.removeItem(SESSION_KEY);
		}
	}

	function clearSession() {
		localStorage.removeItem(SESSION_KEY);
		sessionStorage.removeItem(SESSION_KEY);
	}

	function handleLoginPage() {
		const form = document.getElementById('loginForm');
		if (!form) return;

		// If already logged in, redirect to dashboard
		if (getSessionStoragePayload()) {
			window.location.replace('dashboard.html');
			return;
		}

		const usernameInput = document.getElementById('username');
		const passwordInput = document.getElementById('password');
		const rememberInput = document.getElementById('remember');
		const errorEl = document.getElementById('loginError');
		const togglePassword = document.getElementById('togglePassword');

		togglePassword?.addEventListener('click', () => {
			const isHidden = passwordInput.type === 'password';
			passwordInput.type = isHidden ? 'text' : 'password';
			togglePassword.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
		});

		form.addEventListener('submit', (event) => {
			event.preventDefault();

			const username = String(usernameInput.value || '').trim();
			const password = String(passwordInput.value || '').trim();
			const remember = Boolean(rememberInput.checked);

			if (!username || !password) {
				errorEl.textContent = 'Please enter both username and password.';
				return;
			}

			const isValid = username === DEFAULT_AUTH.username && password === DEFAULT_AUTH.password;
			if (!isValid) {
				errorEl.textContent = 'Invalid credentials. Hint: admin / coffee123';
				return;
			}

			setSessionStoragePayload({ user: username, ts: Date.now() }, remember);
			window.location.assign('dashboard.html');
		});
	}

	function handleDashboardPage() {
		const logoutButton = document.getElementById('logoutButton');
		const ordersList = document.getElementById('ordersList');
		const productForm = document.getElementById('productForm');
		const productsList = document.getElementById('productsList');
		const yearEl = document.getElementById('year');
		const themeToggle = document.getElementById('themeToggle');

		if (!logoutButton || !ordersList || !productForm || !productsList) return;

		// Guard auth
		if (!getSessionStoragePayload()) {
			window.location.replace('index.html');
			return;
		}

		yearEl.textContent = String(new Date().getFullYear());

		// Seed some demo orders
		const demoOrders = [
			{ id: 'ORD-1024', item: 'Latte', customer: 'Sam', status: 'Completed' },
			{ id: 'ORD-1025', item: 'Cappuccino', customer: 'Alex', status: 'Preparing' },
			{ id: 'ORD-1026', item: 'Espresso', customer: 'Lee', status: 'Completed' },
			{ id: 'ORD-1027', item: 'Mocha', customer: 'Taylor', status: 'Pending' }
		];
		ordersList.innerHTML = '';
		demoOrders.forEach((order) => {
			const li = document.createElement('li');
			const statusClass = order.status === 'Completed' ? 'success' : (order.status === 'Pending' ? 'pending' : 'pending');
			li.innerHTML = `
				<span>${order.id} — ${order.customer} · ${order.item}</span>
				<span class="pill ${statusClass}">${order.status}</span>
			`;
			ordersList.appendChild(li);
		});

		// Products persistence
		function getProducts() {
			try {
				return JSON.parse(localStorage.getItem(PRODUCTS_KEY)) || [];
			} catch (_) {
				return [];
			}
		}
		function setProducts(products) {
			localStorage.setItem(PRODUCTS_KEY, JSON.stringify(products));
		}
		function renderProducts() {
			const products = getProducts();
			productsList.innerHTML = '';
			products.forEach((p, index) => {
				const li = document.createElement('li');
				li.innerHTML = `
					<span>${p.name} — $${Number(p.price).toFixed(2)}</span>
					<button class="secondary-button" data-index="${index}">Remove</button>
				`;
				productsList.appendChild(li);
			});
		}

		renderProducts();

		productForm.addEventListener('submit', (event) => {
			event.preventDefault();
			const name = String(document.getElementById('productName').value || '').trim();
			const price = Number(document.getElementById('productPrice').value || '0');
			if (!name || Number.isNaN(price) || price < 0) return;
			const products = getProducts();
			products.push({ name, price });
			setProducts(products);
			productForm.reset();
			renderProducts();
		});

		productsList.addEventListener('click', (event) => {
			const target = event.target;
			if (target instanceof HTMLElement && target.matches('button[data-index]')) {
				const index = Number(target.getAttribute('data-index'));
				const products = getProducts();
				products.splice(index, 1);
				setProducts(products);
				renderProducts();
			}
		});

		logoutButton.addEventListener('click', () => {
			clearSession();
			window.location.replace('index.html');
		});

		// Theme toggle
		function applyTheme(theme) {
			if (theme === 'light') {
				document.documentElement.classList.add('light');
			} else {
				document.documentElement.classList.remove('light');
			}
		}
		const savedTheme = localStorage.getItem(THEME_KEY) || 'dark';
		applyTheme(savedTheme);
		themeToggle.addEventListener('click', () => {
			const next = document.documentElement.classList.contains('light') ? 'dark' : 'light';
			localStorage.setItem(THEME_KEY, next);
			applyTheme(next);
		});
	}

	// Initialize per page
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', () => {
			handleLoginPage();
			handleDashboardPage();
		});
	} else {
		handleLoginPage();
		handleDashboardPage();
	}
})();

