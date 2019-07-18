function ShowCommentForm(id){
    $("#" + id).removeClass('hidden');
}

jQuery(document).ready(function() {

    jQuery('.comment-container form .btn-cancel').on('click', function(e) {
        var form = jQuery(this).closest('form');
        if (form) {
            form.addClass('hidden');
        }
    });
});