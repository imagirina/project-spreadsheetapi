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


// function deleteSheet(btn) {
//     console.log("My event handler")
// }


function copyToClipboard(btn) {
    // console.log(btn.parentElement.parentElement.firstElementChild);
    btn.parentElement.parentElement.firstElementChild.select();
    document.execCommand('copy');
}

// function copyToClipboard2(btn) {
//     const textToClipboard = $(btn).parent().find('input[type=text]');
//     console.log("textToClipboard (dom element) = ", textToClipboard);
//     urlLink = textToClipboard.context.parentElement.previousElementSibling.ariaLabel;
//     console.log("urlLink (textToClipboard.context.parentElement.previousElementSiblin) = ", urlLink);

//     textFromDomEl = document.getElementById("SheetId");
//     console.log("textFromDomEl" + "(typeof is " + typeof(textFromDomEl) + ") ====>", textFromDomEl);
//     value = textFromDomEl.value;
//     console.log("value (dom element) = ", value);

//     textInput = textFromDomEl.parentElement.firstChild;
    
//     console.log("textInput" + "(typeof is " + typeof(textInput) + ") ====>", textInput);
    
//     apiUrl = textInput.nextElementSibling.ariaLabel;
//     console.log("apiUrl (.nextElementSibling) =", apiUrl);

//     var text = textFromDomEl.select();
//     document.execCommand('copy');

//     // ===================================

//     // var text = document.getElementById('SheetId').select();
//     // document.execCommand('copy');
// }

// function copyToClipboard() {
//     copyText = document.getElementById("SheetId");

//     /* Select the text field */
//     copyText.select();
//     copyText.setSelectionRange(0, 99999); /* For mobile devices */

//     // navigator.clipboard.writeText("test string");
//     navigator.clipboard.writeText(String(copyText.value));

// }