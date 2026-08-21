// Collapses the "PDF may be available at these external sources" notes
// that follow each unavailable PDF link, and lets the preceding [ PDF ]
// button toggle them back open.
//
// The links themselves always exist in the page's HTML (so they're
// crawlable and screen-reader accessible even without this script);
// this only adds the show/hide behavior on top.

function initPdfWidgets() {
	var buttons = document.querySelectorAll('.pdf-toggle');
	for (var i = 0; i < buttons.length; i++) {
		var button = buttons[i];
		var panel = document.getElementById(button.getAttribute('aria-controls'));
		if (!panel) { continue; }

		panel.hidden = true;
		button.setAttribute('aria-expanded', 'false');

		button.addEventListener('click', (function (button, panel) {
			return function () {
				var expanded = button.getAttribute('aria-expanded') === 'true';
				button.setAttribute('aria-expanded', String(!expanded));
				panel.hidden = expanded;
			};
		})(button, panel));
	}
}

if (window.addEventListener) {
	window.addEventListener('DOMContentLoaded', initPdfWidgets, false);
} else if (window.attachEvent) {
	window.attachEvent('onload', initPdfWidgets);
}
