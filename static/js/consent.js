  document.addEventListener('DOMContentLoaded', function () {
    const modal = new bootstrap.Modal(document.getElementById('cookieConsentModal'));
    const checkbox = document.getElementById('acceptCookiesCheckbox');
    const acceptBtn = document.getElementById('acceptCookiesBtn');

    // Check if the user already accepted cookies
    if (!localStorage.getItem('cookieConsent')) {
      modal.show();
    }

    // Enable the accept button only if checkbox is checked
    checkbox.addEventListener('change', function () {
      acceptBtn.disabled = !checkbox.checked;
    });

    // When user clicks accept
    acceptBtn.addEventListener('click', function () {
      localStorage.setItem('cookieConsent', 'accepted');
      modal.hide();
    });

    // Optional: handle decline
    document.querySelector('.modal-footer .btn-dark').addEventListener('click', function () {
      localStorage.setItem('cookieConsent', 'declined');
    });
  });