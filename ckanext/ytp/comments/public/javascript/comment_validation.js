function hideFormErrors()
{
    jQuery('#comment_form_errors').addClass('hidden');
    jQuery('#comment_form_errors li').addClass('hidden');
}

function showFormErrors()
{
    jQuery('#comment_form_errors').removeClass('hidden');
}

function showFormError(id, error_name)
{
    jQuery('#' + id + ' .error-' + error_name).removeClass('hidden');
}

function showEditFormErrors(id)
{
    jQuery('#' + id + ' .edit_form_errors').removeClass('hidden');
}

jQuery(document).ready(function() {

    jQuery('.module-content input[type="submit"]').on('click', function(e) {
        if (jQuery(this).hasClass('btn-primary')) {
            var form = jQuery(this).closest('form');
            var comment = form.find('textarea[name="comment"]').val();
            var display_errors = false;

            hideFormErrors();

            if (!comment) {
                jQuery('#comment_form_errors .error-comment').removeClass('hidden');
                display_errors = true;
            }
            if (display_errors) {
                showFormErrors();
                return false;
            }
        }
    });

    if (window.location.hash) {
        var hash = window.location.hash;
        var hash_no_hash = hash.substring(1); //Puts hash in variable, and removes the # character
        if (hash_no_hash == 'comment_form') {
            //  Regex the flash-messages for 'subject' 'comment' and 'profanity'
            if (jQuery('#content .flash-messages').children().length > 0) {
                var error_message = jQuery('#content .flash-messages').text()
                //  Check for profanity error message
                if (error_message.search("profanity") !== -1) {
                    jQuery('#comment_form_errors .error-profanity').removeClass('hidden');
                    showFormErrors();
                }
            }
        }
        else if (hash_no_hash.indexOf('edit_') !== -1) {
            var form_wrapper_id = 'comment_form_' + hash_no_hash;
            jQuery(hash).removeClass('hidden');
            document.getElementById(form_wrapper_id).scrollIntoView();
            //  Regex the flash-messages for 'subject' 'comment' and 'profanity'
            if (jQuery('#content .flash-messages').children().length > 0) {
                var error_message = jQuery('#content .flash-messages').text()
                //  Check for profanity error message
                if (error_message.search("profanity") !== -1) {
                    showFormError(form_wrapper_id, 'profanity');
                    showEditFormErrors(form_wrapper_id);
                }
            }
        }
    }

});