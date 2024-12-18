import $ from '../jquery/jquery.esm.js'
import party from '../party/party.min.js'
import Typewriter from '../typewriter-effect/core.esm.js'

// Make jQuery visible to Bootstrap
window.jQuery = $;

$(function(){
    $('.js-confetti').each(function(){
        party.confetti(this, {
            count: party.variation.range(80, 100)
        });
    });

    $('[data-typewriter]').each(function(){
        var $el = $(this);
        var phrases = JSON.parse( $el.attr('data-typewriter') || '[]' );
        var pause = $el.attr('data-typewriter-pause') || 3000;
        var t = new Typewriter($el[0], {loop: true});
        $.each(phrases, function(i, phrase){
            t.deleteAll().typeString(phrase).pauseFor(pause);
        });
        t.start();
    });

    $(document).on('hide.bs.collapse show.bs.collapse', function(e){
        var id = $(e.target).attr('id');
        var $navLinks = $('.nav-link[aria-controls="' + id + '"]');
        $navLinks.toggleClass('active');
    });

    $('#postcodeModal').each(function(){
        if ( $(this).find('.is-invalid').length ) {
            var modal = bootstrap.Modal.getOrCreateInstance(this);
            modal.show()
        }
    }).on('shown.bs.modal', function(){
        $(this).find('#postcode').focus();
    });

    $('[data-copy-text]').on('click', function(e){
        e.stopPropagation();
        if (navigator.clipboard) {
            var $el = $(this);
            var $feedback = $el.find('[data-copy-feedback]');
            var copyText = $el.attr('data-copy-text');
            var successHTML = $el.attr('data-copy-success');
            var originalHTML = $feedback.html();
            navigator.clipboard.writeText(copyText).then(function(){
                $feedback.html(successHTML);
                $el.attr('data-copied', true);
                setTimeout(function(){
                    $feedback.html(originalHTML);
                    $el.removeAttr('data-copied');
                }, 2000);
            });
        }
    });
});
