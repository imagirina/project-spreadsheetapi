'use strict';

$(function() {
    $('button[data-bs-toggle="tab"]').on("shown.bs.tab", function(e) {
        localStorage.setItem('lastActiveTab', e.target.id);
    });
    // go to the latest tab, if it exists:
    var lastActiveTab = localStorage.getItem('lastActiveTab');
    if (lastActiveTab !== null) {
        $(`button#${lastActiveTab}`).tab('show');
    }

    // Enabling/disabling switch accordeon
    $('.form-check-input').on('change', function (event) {
        if (event.target.checked) {
            event.target.parentElement.parentElement.querySelector('.badge').classList.remove('disabled');
            event.target.parentElement.querySelector('.form-check-label').innerText = "Enabled";
        } else {
            event.target.parentElement.parentElement.querySelector('.badge').classList.add('disabled');
            event.target.parentElement.querySelector('.form-check-label').innerText = "Disabled";
        }
    });
});

function copyToClipboard(btn) {
    // https://developer.mozilla.org/en-US/docs/Web/API/Document/execCommand
    // Obsolete but wider browser coverage, Clipboard API is not widespread yet
    btn.parentElement.parentElement.firstElementChild.select();
    document.execCommand('copy');
}

function updateApiAction(checkbox, sheet_id) {
    let url = "http://localhost:5000/update_api_action"

    const action_name = checkbox.getAttribute('api-action-name');

    fetch(url, {
        method: 'POST',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify({action_name: action_name, sheet_id: sheet_id})
    })
}

// Update Showcase Category Text
function updateCategory(id) {
    // String interpolation
    let url_update = `http://localhost:5000/api/sheets/1-Z-kDYHlpt_vRfaScTJ-WzCR6DPkuLRuumSISpBSzvI/${id}`;
    let item_text;
    const item_id = id;
    if (item_id == 2) {
        item_text = document.getElementById("text-about").value;
    }
    else if (item_id == 3) {
        item_text = document.getElementById("text-contacts").value;
    }
    let body = {
        "Text" : item_text,
    }
    fetch(url_update, {
        method: 'PUT',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then((responce) => responce.json())
    .then(json => {
        document.location = "/showcases/manage";
    })
}

// Delete Showcase Schedule Item
function deleteItem(id) {
    let url = `http://localhost:5000/api/sheets/1M4SwxMxOGsJSh_FIZBxktitoQhM2xrbRgQQszrriD1M/${id}`;

    fetch(url, {
        method: 'DELETE',
    })
    .then((response) => response.json())
    .then(() => {
        console.log('Object deleted');
    });
    document.location = "/showcases/manage";
}

// Update Showcase Schedule Text
function updateSchedule(id) {
    // String interpolation
    let url_update = `http://localhost:5000/api/sheets/1M4SwxMxOGsJSh_FIZBxktitoQhM2xrbRgQQszrriD1M/${id}`;

    let week_day = document.getElementById("week-day").innerHTML;
    let time = document.querySelector(".time").value;
    let class_name = document.querySelector(".class-name").value;
    let teacher = document.querySelector(".teacher").value;
    
    let body = {
      "Day": week_day,
      "Time": time,
      "Class Name": class_name,
      "Teacher": teacher,
    }

    fetch(url_update, {
        method: 'PUT',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then((responce) => responce.json())
    .then(json => {
        document.location = "/showcases/manage"
    })
}

// Add to schedule using API POST (Showcase Studio)
function addToSchedule() {
    let url_add_to_schedule = 'http://localhost:5000/api/sheets/1M4SwxMxOGsJSh_FIZBxktitoQhM2xrbRgQQszrriD1M'
    var week_day = document.getElementById("week-day");
    var week_day_text = week_day.options[week_day.selectedIndex].text;

    let body = {
        "Day": week_day_text,
        "Time": document.querySelector('#time').value,
        "Class Name": document.querySelector('#class-name').value,
        "Teacher": document.querySelector('#teacher').value
    }
    fetch(url_add_to_schedule, {
        method: 'POST',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then((response) => response.json())
    .then(json => {
        document.location = "/showcases/manage";
    });
}