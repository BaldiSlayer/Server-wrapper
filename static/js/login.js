function auth() {
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const formData = {
            "username": username,
            "password": password
        };

        fetch('/login', {
            method: 'POST',
            body: JSON.stringify(formData),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (response.redirected) {
                    // выполнить редирект на новый URL
                    window.location.replace(response.url);
                }
            })
            .catch(error => {
                // обработать ошибку
                console.error(error);
            });

    }