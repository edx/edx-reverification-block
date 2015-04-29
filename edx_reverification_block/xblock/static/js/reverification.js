function Reverification(runtime, element) {
  var $el = $(element);

  var setSkipConfirmVisible = function(isVisible) {
    var skipConfirm = $el.find('.reverify-skip-confirm-wrapper'),
        reverifyMsg = $el.find('.reverify-now-wrapper');
    if (isVisible) {
      reverifyMsg.addClass('hidden');
      skipConfirm.removeClass('hidden');
    } else {
      skipConfirm.addClass('hidden');
      reverifyMsg.removeClass('hidden');
    }
  };

  $el.find('.reverify-skip-link').on('click', function() {
    setSkipConfirmVisible(true);
  });

  $el.find('.reverify-skip-cancel-button').on('click', function() {
    setSkipConfirmVisible(false);
  });

  $el.find('.reverify-now-button').on('click', function() {
    var href = $(this).data('href');
    window.location.href = href;
  });

  $el.find('.reverify-skip-confirm-button').on('click', function(){
      var handlerUrl = runtime.handlerUrl(element, 'skip_verification');
      $.post(handlerUrl, JSON.stringify('')).done(function (response) {
        window.location.reload();
      });
  });
}
