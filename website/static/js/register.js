function validateFirstName() {
    var firstName = document.getElementById("FirstName").value;
    var containsNumbers = /\d/.test(firstName);
    var error = document.getElementById("fNameError");
    if (firstName === "") {
        error.textContent = "Please enter your Last Name.";
    }
    if (containsNumbers) {
        error.textContent = "Firstname cannot contain numbers.";
    } else {
        error.textContent = "";
    }
}

function validateLastName() {
    var lastName = document.getElementById("LastName").value;
    var containsNumbers = /\d/.test(lastName);
    var error = document.getElementById("lNameError");
    if (lastName === "") {
        error.textContent = "Please enter your Last Name.";
    }
    if (containsNumbers) {
        error.textContent = "Lastname cannot contain numbers.";
    } else {
        error.textContent = "";
    }
}

function validateEmail() {
    var email = document.getElementById("Email").value;
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    var error = document.getElementById("emailError");
    if (!emailRegex.test(email)) {
        error.textContent = "Please enter a valid email address.";
    }else {
        error.textContent = "";
    }
}

function validatePassword() {
    var password = document.getElementById("Password").value;
    var error = document.getElementById("passwordError");
    if (password.length < 8) {
        error.textContent = "Password must be at least 8 characters long.";
    }
    else {
        error.textContent = "";
    }
}

function validateConfirmPassword() {
    var password = document.getElementById("RepeatPassword").value;
    var confirmPassword = document.getElementById("confirmPassword").value;
    var error = document.getElementById("confPassError");
    if (password !== confirmPassword) {
        error.textContent = "Password and Confirm Password do not match.";
    }else {
        error.textContent = "";
    }
}
 