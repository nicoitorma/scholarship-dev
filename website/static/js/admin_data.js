function renderBarChart(divId, data) {
  var ctx = document.getElementById(divId).getContext("2d");
  var labels = Object.keys(data);
  var values = Object.values(data);

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Beneficiaries count",
          data: values,
          backgroundColor: "#36b9cc",
          hoverBackgroundColor: "#36b9cc",
          borderColor: "#4e73df",
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      legend: {
        display: false,
      },
      tooltips: {
        titleMarginBottom: 10,
        titleFontColor: "#6e707e",
        titleFontSize: 14,
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: "#dddfeb",
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
      },
    },
  });
}

// Handle Accept and Reject click on Applicants table
// script.js

var currentApplicantId;
var currentAction;
var applicantEmail;

function showConfirmation(applicantId, email, action) {
  currentApplicantId = applicantId;
  applicantEmail = email;
  currentAction = action;

  // Update the text in the modal based on the action
  document.getElementById(
    "confirmationModalLabel"
  ).innerHTML = `Confirm ${action}`;
  document.getElementById(
    "confirmationModalBody"
  ).innerHTML = `Are you sure you want to ${action.toLowerCase()} this applicant?`;

  // Open the confirmation modal
  $("#confirmationModal").modal("show");
}

function showRemoveConfirmation(email, action) {
  applicantEmail = email;
  currentAction = action;

  // Update the text in the modal based on the action
  document.getElementById(
    "confirmationRemoveModalLabel"
  ).innerHTML = `Confirm ${action}`;
  document.getElementById(
    "confirmationRemoveModalBody"
  ).innerHTML = `Are you sure you want to ${action.toLowerCase()} this beneficiary?`;

  // Open the confirmation modal
  $("#confirmationRemoveModal").modal("show");
}

function performAction() {
  // Make an AJAX request to the Flask route with the applicant ID and action
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/process", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      console.log("Action performed successfully:", currentAction);

      // Close the confirmation modal
      $("#confirmationModal").modal("hide");
    }
  };

  var data = JSON.stringify({
    id: currentApplicantId,
    email: applicantEmail,
    action: currentAction,
  });
  xhr.send(data);
}

// Attach event listener to the Confirm button in the modal
document
  .getElementById("confirmActionButton")
  .addEventListener("click", performAction);

  // Attach event listener to the Confirm button in the modal
document
.getElementById("confirmRemoveActionButton")
  .addEventListener("click", removeBeneficiary);

  function removeBeneficiary() {
    // Make an AJAX request to the Flask route with the applicant ID and action
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/remove", true);
    xhr.setRequestHeader("Content-Type", "application/json");
  
    xhr.onreadystatechange = function () {
      if (xhr.readyState == 4 && xhr.status == 200) {
        console.log("Action performed successfully:", currentAction);
  
        // Close the confirmation modal
        $("#confirmationRemoveModal").modal("hide");
      }
    };
  
    var data = JSON.stringify({
      id: currentApplicantId,
      email: applicantEmail,
      action: currentAction,
    });
    xhr.send(data);
  }


// For QR Code
function domReady(fn) { 
  if ( 
      document.readyState === "complete" || 
      document.readyState === "interactive"
  ) { 
      setTimeout(fn, 1000); 
  } else { 
      document.addEventListener("DOMContentLoaded", fn); 
  } 
} 

domReady(function () {
  let htmlscanner;

  function startScanner() {
    htmlscanner = new Html5QrcodeScanner(
      "my-qr-reader",
      { fps: 10, qrbos: 250 }
    );
    
    htmlscanner.render(onScanSuccess);
  }

  function onScanSuccess(decodeText, decodeResult) {
    // Remove event listeners to stop the scanner
    htmlscanner.pause();
    
    // Send the QR code data to the Flask server
    fetch('/payout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ qrCodeData: decodeText }),
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        else if (response.status === 404) {
          throw new Error('Beneficiary not found!');
        }
        else {
          throw new Error('Unexpected error');
        }
      })
      .then(data => {
        const userDetails = document.getElementById("userDetails");
        userDetails.innerHTML = `
        <h1 class="h5 mb-4 font-weight-bold text-primary">Beneficiary Informations</h1>
        <h1 class="h6 text-dark" ><b>Name</b>: ${data.name}</h5>
        <h1 class="h6 text-dark" ><b>Email</b>: ${data.email}</h1>
        <h1 class="h6 text-dark" ><b>Municipality</b>: ${data.municipality}</h1>
        <hr />
        <h1 class="h6 text-dark" ><b>School</b>: ${data.school}</h1>
        <h1 class="h6 text-dark" ><b>Program</b>: ${data.program}</h1>
        <h1 class="h6 text-dark" ><b>Year level</b>: ${data.year_level}</h1>
        <hr/>
        <h1 class="h6 text-dark" ><b>Scholarship</b>: ${data.scholarship}</h>
        <h1 class="h6 text-dark" ><b>Scholarship status</b>: ${data.status}</h1>
        `;

        if (data.gwa == "Error: Document not found for email.") {
          const gwaTable = document.getElementById("gwaTable");
          gwaTable.innerHTML = ``;
        }
        else {
      // Display GWA in the table
      const gwaTable = document.getElementById("gwaTable");
          gwaTable.innerHTML = `
        <h1 class="h5 mb-2 font-weight-bold text-warning">GWA Records</h1>
      <table class="table table-bordered"
      id="dataTable"
      width="100%"
      cellspacing="0">
        <tr>
          <th><b>School Year</b></th>
          <th><b>Semester</b></th>
          <th><b>GWA</b></th>
        </tr>
        ${data.gwa.map(item =>
          `
          <tr>
            <td>${item.school_year}</td>
            <td>${item.semester}</td>
            <td>${item.gwa !== null ? item.gwa.toFixed(2) : 'No record'}</td>
          </tr>
        `).join('')}
      </table>
    `;
        }

        // Check if the status is Beneficiary
        if (data.status === "Beneficiary") {
          const payoutButtonContainer = document.getElementById("payoutButton");

          // Create a button element
          const payoutButton = document.createElement("button");
          payoutButton.className = "btn btn-primary btn-warning";
          payoutButton.textContent = "Release Payout";

          // Append the button to the container
          payoutButtonContainer.appendChild(payoutButton);
        } 
        else {
          const payoutButtonContainer = document.getElementById("payoutButton");
          payoutButtonContainer.innerHTML = ``;
        }
        // Restart the scanner after a successful scan
        setTimeout(startScanner, 3000);
      })
      .catch(error => {
        if (error.message === 'Beneficiary not found!')
        {
          const userDetails = document.getElementById("userDetails");
          userDetails.innerHTML = `
          <h1 class="h3 mb-4 font-weight-bold text-danger">Beneficiary not found!</h1>`;
        }

        // Restart the scanner after an error
        setTimeout(startScanner, 3000);
      })
  }

  // Start the initial scanner
  startScanner();
});
