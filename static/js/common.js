// Common JS utilities
// Track last clicked element for popup origin
window._lastPopupSource = null;

function showPopup(html) {
    // populate popup content
    $('#popup-content').html(html);
    const $popup = $('#popup');
    const $dialog = $popup.find('.modal-dialog');
    // show overlay hidden for measurement
    $popup.css({ display: 'flex', visibility: 'hidden' });
    // compute transform-origin for animation
    let originX = '50%', originY = '50%';
    if (window._lastPopupSource) {
        const $btn = $(window._lastPopupSource);
        const btnOff = $btn.offset();
        const btnCX = btnOff.left + $btn.outerWidth() / 2;
        const btnCY = btnOff.top + $btn.outerHeight() / 2;
        const dialogOff = $dialog.offset();
        originX = `${btnCX - dialogOff.left}px`;
        originY = `${btnCY - dialogOff.top}px`;
    }
    // set initial transform origin and scale
    $dialog.css({ 'transform-origin': `${originX} ${originY}`, transform: 'scale(0)' });
    // reveal then animate
    $popup.css('visibility', 'visible');
    requestAnimationFrame(() => { $dialog.css('transform', 'scale(1)'); });
}

function hidePopup() {
    const $popup = $('#popup');
    const $dialog = $popup.find('.modal-dialog');
    // compute transform-origin for hide animation
    let originX = '50%', originY = '50%';
    if (window._lastPopupSource) {
        const $btn = $(window._lastPopupSource);
        const btnOff = $btn.offset();
        const btnCX = btnOff.left + $btn.outerWidth() / 2;
        const btnCY = btnOff.top + $btn.outerHeight() / 2;
        const dialogOff = $dialog.offset();
        originX = `${btnCX - dialogOff.left}px`;
        originY = `${btnCY - dialogOff.top}px`;
    }
    $dialog.css('transform-origin', `${originX} ${originY}`);
    // animate scale down
    requestAnimationFrame(() => {
        $dialog.css('transform', 'scale(0)');
    });
    $dialog.one('transitionend', () => {
        $popup.css({ display: 'none', visibility: '' });
        $dialog.css({ transform: '', 'transform-origin': '' });
        window._lastPopupSource = null;
    });
}

function attachClose() {
    $('#closePopup').off('click').on('click', hidePopup);
}