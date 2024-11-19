
function register(type, url) {
    // Using fetch
    fetch("https://localhost:5002/register/" + map + "/" + url)
        .then(function (response) {
            if (response.ok) {
                // Success
                return response.json();
            } else {
                // Error
                throw new Error(response.statusText);
            }
            }
        );
}