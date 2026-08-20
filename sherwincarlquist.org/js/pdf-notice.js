// Shows a notice when a PDF link is clicked, since the referenced PDFs
// are not hosted on this site. Call from a link's onclick handler:
//   onclick="return pdfNotAvailable(event);"
// A second argument can carry extra HTML (e.g. a link to where the
// publication is available elsewhere) once that detail is known:
//   onclick="return pdfNotAvailable(event, 'Available at <a href=&quot;...&quot;>...</a>');"

function pdfNotAvailable(event, details) {
	if (event && event.preventDefault) { event.preventDefault(); }

	var message = document.getElementById('pdfNoticeMessage');
	if (message) {
		message.innerHTML = 'This PDF is not hosted on this site.' + (details ? '<br /><br />' + details : '');
	}

	var overlay = document.getElementById('pdfNoticeOverlay');
	var box = document.getElementById('pdfNoticeBox');
	if (overlay) { overlay.style.display = 'block'; }
	if (box) { box.style.display = 'block'; }

	return false;
}

function closePdfNotice() {
	var overlay = document.getElementById('pdfNoticeOverlay');
	var box = document.getElementById('pdfNoticeBox');
	if (overlay) { overlay.style.display = 'none'; }
	if (box) { box.style.display = 'none'; }
}

function buildPdfNotice() {
	var overlay = document.createElement('div');
	overlay.id = 'pdfNoticeOverlay';
	overlay.onclick = closePdfNotice;
	document.body.appendChild(overlay);

	var box = document.createElement('div');
	box.id = 'pdfNoticeBox';

	var message = document.createElement('p');
	message.id = 'pdfNoticeMessage';
	box.appendChild(message);

	var closeLink = document.createElement('a');
	closeLink.href = '#';
	closeLink.id = 'pdfNoticeClose';
	closeLink.innerHTML = 'Close';
	closeLink.onclick = function () { closePdfNotice(); return false; };
	box.appendChild(closeLink);

	document.body.appendChild(box);
}

if (window.addEventListener) {
	window.addEventListener('load', buildPdfNotice, false);
} else if (window.attachEvent) {
	window.attachEvent('onload', buildPdfNotice);
}
