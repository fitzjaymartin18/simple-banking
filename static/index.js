document.getElementById('pinForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const pin = document.getElementById('pin').value;
    const confirmPin = document.getElementById('confirmPin').value;
    const errorMessage = document.getElementById('errorMessage');

    if (pin.length !== 4 || confirmPin.length !== 4) {
        errorMessage.textContent = "PIN must be 4 digits long.";
    } else if (pin !== confirmPin) {
        errorMessage.textContent = "PINs do not match. Please try again.";
    } else {
        errorMessage.textContent = "";
        alert("PIN created successfully!");
        // Submit the form or handle PIN creation logic
    }
});

// Deposit
document.getElementById('depositForm').addEventListener('submit', function(event) {
    const depositAmount = document.getElementById('depositAmount').value;
    const errorMessage = document.getElementById('errorMessage');

    if (depositAmount < 500.00 || depositAmount > 999999999.00) {
        errorMessage.textContent = 'Deposit must be between 500.00 and 999,999,999.00';
        event.preventDefault(); // Prevent form submission
    } else {
        errorMessage.textContent = ''; // Clear any previous errors
    }
});

// Withdraw
document.getElementById('withdrawForm').addEventListener('submit', function(event) {
    const withdrawAmount = parseFloat(document.getElementById('withdrawAmount').value);
    const errorMessage = document.getElementById('errorMessage');

    // Ensure at least 100 is left in the account
    if (userBalance - withdrawAmount < 100) {
        errorMessage.textContent = 'You must leave at least 100 in your account.';
        event.preventDefault(); // Prevent form submission
    } else if (withdrawAmount <= 0 || isNaN(withdrawAmount)) {
        errorMessage.textContent = 'Please enter a valid amount.';
        event.preventDefault(); // Prevent form submission
    } else if (withdrawAmount > userBalance) {
        errorMessage.textContent = 'Please enter a valid amount.';
        event.preventDefault(); // Prevent form submission
    } else {
        errorMessage.textContent = ''; // Clear previous errors
    }
});


// Transfer
document.getElementById('transferForm').addEventListener('submit', function(event) {
    const transferAmount = parseFloat(document.getElementById('transferAmount').value);
    const errorMessage = document.getElementById('errorMessage');

    // Check if transfer leaves at least 100 in the user's account
    if (userBalance - transferAmount < 100) {
        errorMessage.textContent = 'You must leave at least 100 in your account.';
        event.preventDefault(); // Prevent form submission
    }
    // Check if transfer amount exceeds user balance
    else if (transferAmount > userBalance) {
        errorMessage.textContent = 'Transfer amount exceeds your balance.';
        event.preventDefault(); // Prevent form submission
    }
    // Check if transfer amount is invalid
    else if (transferAmount <= 0 || isNaN(transferAmount)) {
        errorMessage.textContent = 'Please enter a valid amount.';
        event.preventDefault(); // Prevent form submission
    } 
    else {
        errorMessage.textContent = ''; // Clear any previous error messages
    }
});

