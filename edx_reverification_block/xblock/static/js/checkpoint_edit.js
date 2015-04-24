function CheckpointEditBlock(runtime, element) {
    var validators = {
        'number': function (value) {
            if ( isNaN(Number(value)) || Number(value) < 0){
                return false;
            }
            return true;
        },
        'string': function (value) {
            if ( value != '' ) {
                return true;
            }
            return false;
        }
    }

    function validate(data) {
        var errors = [];
        if ( !validators.string(data.related_assessment) ) {
            errors.push("Related Assessment field cannot be empty.");
        }
        if ( !validators.number(data.attempts) ) {
            errors.push("Attempts field should be a positive number.");
        }
        return errors;
    }


    $(element).find('.save-button').bind('click', function () {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

        var data = {
            related_assessment: $(element).find('input[name=related_assessment]').val().trim(),
            attempts: $(element).find('input[name=attempts]').val().trim()
        };

        var validation_errors = validate(data);
        if ( validation_errors.length == 0 ) {
            runtime.notify('save', {state: 'start'});
            $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
                runtime.notify('save', {state: 'end'});
            });
        } else {
            var message = "Validation Error[s]:<br>" + validation_errors.join(' <br>')
            runtime.notify('error', {title: 'Re-Verification Save Error', message: message});
        }
    });

    $(element).find('.cancel-button').bind('click', function () {
        runtime.notify('cancel', {});
    });
}
