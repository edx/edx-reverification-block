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
            errors.push(gettext("The Verification Checkpoint Name field cannot be empty."));
        }
        if ( !validators.number(data.attempts) ) {
            errors.push(gettext("You must select a value other than 0 for the Verification Attempts field."));
        } else {
            data.attempts = Math.floor(Number(data.attempts));
        }
        if ( !validators.number(data.grace_period) ) {
            errors.push(gettext("Please enter a valid number for the Grace Period field."));
        } else {
            data.grace_period = Math.floor(Number(data.grace_period));
        }
        return errors;
    }


    $(element).find('.save-button').bind('click', function () {
        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

        var data = {
            related_assessment: $(element).find('input[name=related_assessment]').val().trim(),
            attempts: $(element).find('select[name=attempts]').val().trim(),
            grace_period: $(element).find('input[name=grace_period]').val().trim()
        };

        var validation_errors = validate(data);
        if ( validation_errors.length === 0 ) {
            runtime.notify('save', {state: 'start'});
            $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
                if (response.result === "success") {
                    runtime.notify('save', {state: 'end'});
                } else {
                    runtime.notify('error', {
                        title: gettext('Verification Checkpoint Save Error'),
                        message: gettext('An unexpected error occurred. Select Save to try again.')
                    });
                }
            });
        } else {
            var message = '<br>' + validation_errors.join(' <br>');
            runtime.notify('error', {title: gettext('Verification Checkpoint Save Error'), message: message});
        }
    });

    $(element).find('.cancel-button').bind('click', function () {
        runtime.notify('cancel', {});
    });
}
