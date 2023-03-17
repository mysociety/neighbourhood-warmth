import $ from '../jquery/jquery.esm.js'
import { Modal, Tab } from '../bootstrap/bootstrap.esm.min.js'
import party from '../party/party.min.js'
import Typewriter from '../typewriter-effect/core.esm.js'

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
});
