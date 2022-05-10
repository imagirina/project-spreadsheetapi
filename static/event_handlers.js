'use strict';

// When user clicks on Copy button, the text should be copied into clipboard
const btnCopy = document.querySelector('#btnCopy');
/* Get the text field */

function copyToClipboard() {    
    const copySheetId = document.getElementById("SheetId");
    copySheetId.ariaSelected;
    copySheetId.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
    navigator.clipboard.writeText(copySheetId.value);
    alert("Copied the text: " + copySheetId.value);

}

btnCopy.addEventListener('click', copyToClipboard);


