// Common JS utilities
function showPopup(html) {
  $('#popup-content').html(html);
  $('#popup').show();
}
function hidePopup() {
  $('#popup').hide();
}
function attachClose() {
  $('#closePopup').off('click').on('click', hidePopup);
}