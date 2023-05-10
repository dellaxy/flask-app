function openRegistration() {
    window.location.href = "/registration";
}

function openLogin() {
    window.location.href = "/login";
}


function registerValidation() {
    var form = $("#registration-form");
    var password = form.find("#password").val();
    var confirmPassword = form.find("#confirm-password").val();
    if (password != confirmPassword) {
        $("#error-message").text("Passwords do not match");
        return false;
    }
    return true;
}
