function CheckpointEditBlock(runtime, element) {
    var validators = {
        'number': function (value) {
            if ( isNaN(Number(value)) || Number(value) < 0){
                return false;
            }
            return true;
        },
        'string': function (value) {
            if ( value !== '' ) {
                return true;
            }
            return false;
        }
    };

    function validate(data) {
        var errors = [];
        if ( !validators.string(data.related_assessment) ) {
            errors.push(gettext("Related Assessment field cannot be empty."));
        }
        if ( !validators.number(data.attempts) ) {
            errors.push(gettext("Attempts field should be a positive number."));
        } else {
            data.attempts = Math.floor(Number(data.attempts));
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
        if ( validation_errors.length === 0 ) {
            runtime.notify('save', {state: 'start'});
            $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
                if (response.result === "success") {
                    runtime.notify('save', {state: 'end'});
                } else {
                    runtime.notify('error', {
                        title: gettext('Re-Verification Save Error'),
                        message: gettext('An unexpected error occurred while saving.')
                    });
                }
            });
        } else {
            var message = gettext("Validation Error[s]:") + "<br>" + validation_errors.join(' <br>');
            runtime.notify('error', {title: gettext('Re-Verification Save Error'), message: message});
        }
    });

    $(element).find('.cancel-button').bind('click', function () {
        runtime.notify('cancel', {});
    });
}
