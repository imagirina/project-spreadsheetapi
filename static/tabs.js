'use strict';

// $(function() { ... }); is a jQuery short-hand for $(document).ready(function() {...});
// Will be called once all the DOM elements on the page are ready to be used
// Reference Error : we are trying to access a variable or call a function that has not been defined yet
$(function() {
    // alert('I am in the $ function');
    // $('td').css('color', 'red'); 
    $('button[data-bs-toggle="tab"]').on("shown.bs.tab", function(e) {
        // console.log("switched tab ", e.target.id);
        localStorage.setItem('lastActiveTab', e.target.id);
    });
    // go to the latest tab, if it exists:
    var lastActiveTab = localStorage.getItem('lastActiveTab');
    if (lastActiveTab !== null) {
        $(`button#${lastActiveTab}`).tab('show');
    }
});