function SkipReverifcation(runtime, element) {
  $(element).find('#skip').bind('click', function() {
      $(element).find('#skip-reverification-modal').show();
  });

  $(element).find("#close-modal").bind('click', function(){
      $(element).find('#skip-reverification-modal').hide();
  });

  $(element).find("#opt-out").bind('click', function(){
      var handlerUrl = runtime.handlerUrl(element, 'skip_verification');
      var data = {
        course_id: $(element).find('input[name=course_id]').val(),
        user_id: $(element).find('input[name=user_id]').val(),
        checkpoint: $(element).find('input[name=checkpoint]').val()
      };
      $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
        $(element).find('#skip-reverification-modal').hide();
      });
  });

  $(element).find("#opt-out-cancel").bind('click', function(){
      $(element).find('#skip-reverification-modal').hide();
  });
}