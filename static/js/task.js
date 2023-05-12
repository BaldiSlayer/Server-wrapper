
function selectItem(item) {
    document.getElementById('dropdownMenuButton').innerText = item;
}

function do_a_notification(text) {
    // TODO сделай красивее
    alert(text)
}

function sendRequest() {
    const apiUrl = window.location.href + '/submit';

    let code = document.getElementById("Code").value
    let language = document.getElementById('dropdownMenuButton').innerText

    const codeAlert = document.getElementById("codeAlert");
    if (!code.trim()) {
        codeAlert.classList.remove("d-none");
        return;
    } else {
        codeAlert.classList.add("d-none");
    }

    const languageAlert = document.getElementById("languageAlert")
    if (language == 'Select an language ') {
        languageAlert.classList.remove("d-none");
        return;
    } else {
        languageAlert.classList.add("d-none");
    }

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "code": code,
            "language": language,
        })
    })
        .then(response => {
            location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
        });
}