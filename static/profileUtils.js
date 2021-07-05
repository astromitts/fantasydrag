function hasLowerCase(str) {
    return (/[a-z]/.test(str));
}

function hasUpperCase(str) {
    return (/[A-Z]/.test(str));
}

function hasNumber(str) {
    return (/[0-9]/.test(str));
}

function hasLength(str, minLength) {
    return str.length >= minLength;
}

function hasSpecial(str) {
    return (/[~`!#$%\^&*+=\-\[\]\\';,/{}|\\":<>\?]/g.test(str));
}

function getPasswordErrors(str) {
    var errors = [];
    if (!hasLowerCase(str)) {
        errors.push('Password must contain at least one lowercase letter');
    }
    if (!hasUpperCase(str)) {
        errors.push('Password must contain at least one uppercase letter');
    }
    if (!hasNumber(str)) {
        errors.push('Password must contain at least one number');
    }
    if (!hasSpecial(str)) {
        errors.push('Password must contain at least one special character');
    }
    if (!hasLength(str, 9)) {
        errors.push('Password must contain at least 9 characters');
    }
    if (errors.length == 0){
        return false;
    }
    return errors;
}