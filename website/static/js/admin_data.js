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


function showAdminConfirmation(email, action) {
  adminEmail = email;
  adminAction = action;

  // Update the text in the modal based on the action
  document.getElementById(
    "confirmAdminModalLabel"
  ).innerHTML = `Confirm ${action}`;
  document.getElementById(
    "confirmAdminModalBody"
  ).innerHTML = `Are you sure you want to ${action.toLowerCase()} this admin?`;

  // Open the confirmation modal
  $("#confirmAdminModal").modal("show");
}

// For removing beneficiary
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

// For accepting or rejecting appplicant
function performAction() {
  var scholarshipType = document.querySelector('[name="scholar_type"]').value;

  if (scholarshipType === "default") {
    // Display an error message or take appropriate action
    alert("Please select a valid Scholarship Type.");
    return;
  }

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
    scholarship_type: scholarshipType,
  });
  xhr.send(data);
}

// Attach event listener to the Confirm Applicant button in the modal
document
  .getElementById("confirmActionButton")
  .addEventListener("click", performAction);

// Attach event listener to the Confirm Beneficiary button in the modal
document
  .getElementById("confirmRemoveActionButton")
  .addEventListener("click", removeBeneficiary);

document
  .getElementById("confirmAdminButton")
  .addEventListener("click", confirmAdmin); 

// For confirming or rejecting admin
function confirmAdmin() {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/users", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      console.log("Action performed successfully:", currentAction);

      // Close the confirmation modal
      $("#confirmAdminModal").modal("hide");
    }
  }

  var data = JSON.stringify({
    email: adminEmail,
    action: adminAction,
  });
  xhr.send(data);
}

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

var currentEmail;

domReady(function () {
  const scannerConfig = {
    fps: 10,
    qrbos: 250,
  };

  const userDetails = document.getElementById("userDetails");
  const gwaTable = document.getElementById("gwaTable");
  const payoutButtonContainer = document.getElementById("payoutButton");

  let htmlscanner;

  function startScanner() {
    htmlscanner = new Html5QrcodeScanner("my-qr-reader", scannerConfig);
    htmlscanner.render(onScanSuccess);
  }

  function onScanSuccess(decodeText) {
    htmlscanner.pause();
    fetchDataAndDisplayDetails(decodeText);
  }

  async function fetchDataAndDisplayDetails(decodeText) {
    try {
      const response = await fetch("/payout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ qrCodeData: decodeText }),
      });

      if (!response.ok) {
        throw new Error(response.status === 404 ? "Beneficiary not found!" : "Unexpected error");
      }

      const data = await response.json();
      displayBeneficiaryDetails(data);

      setTimeout(startScanner, 3000);
    } catch (error) {
      console.log(error);
      handleFetchError(error);
    }
  }

  function displayBeneficiaryDetails(data) {
    currentEmail = data.email;
    createReleasePayoutModal(data.fName, data.lName, data.allocation);
    userDetails.innerHTML = `
          <h1 class="h5 mb-4 font-weight-bold text-primary">Beneficiary Informations</h1>
          <h1 class="h6 text-dark" ><b>Name</b>: ${data.fName} ${data.lName}</h5>
          <h1 class="h6 text-dark" ><b>Email</b>: ${data.email}</h1>
          <h1 class="h6 text-dark" ><b>Municipality</b>: ${data.municipality}</h1>
          <hr />
          <h1 class="h6 text-dark" ><b>School</b>: ${data.school}</h1>
          <h1 class="h6 text-dark" ><b>Program</b>: ${data.program}</h1>
          <h1 class="h6 text-dark" ><b>Year level</b>: ${data.year_level}</h1>
          <hr/>
          <h1 class="h6 text-dark" ><b>Scholarship</b>: ${data.scholarship}</h>
          <h1 class="h6 text-dark" ><b>Scholarship status</b>: ${data.status}</h1>
          <h1 class="h6 text-dark" ><b>Allocation per semester</b>: ${data.allocation}</h1>
          `;

    if (data.gwa === "Error: Document not found for email.") {
      gwaTable.innerHTML = "";
    } else {
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
              ${data.gwa
                    .map(
                      (item) =>
                        `
                <tr>
                  <td>${item.school_year}</td>
                  <td>${item.semester}</td>
                  <td>${item.gwa !== null ? item.gwa.toFixed(2) : "No record"}</td>
                </tr>
              `
                    )
                    .join("")}
            </table>
          
      `;
    }

    // Check if the status is Beneficiary
    if (data.status === "Beneficiary") {
      payoutButtonContainer.innerHTML = `<button class="btn btn-primary btn-warning" id="releasePayout">Release Payout</button>`;
    } else {
      payoutButtonContainer.innerHTML = "";
    }
  }

  function handleFetchError(error) {
    userDetails.innerHTML = `<h1 class="h3 mb-4 font-weight-bold text-danger">${error.message}</h1>`;
    setTimeout(startScanner, 3000);
  }

  // Event delegation for the payout button
  payoutButtonContainer.addEventListener("click", function (event) {
    if (event.target.id === "releasePayout") {
      releasePayout();
    }
  });

  startScanner();
  
});

function releasePayout() {
  $("#myModal").modal("show");
}

function createReleasePayoutModal(fName, lName, amount) {
  const modalContainer = document.createElement("div");
  modalContainer.className = "modal fade";
  modalContainer.id = "myModal";
  modalContainer.innerHTML = `
          <div class="modal-dialog" role="document">
              <div class="modal-content">
                  <div class="modal-header">
                      <h5 class="modal-title" id="exampleModalLabel">Release Payout</h5>
                      <button type="button" class="close" data-bs-dismiss="modal" aria-label="Close">
                          <span aria-hidden="true">&times;</span>
                      </button>
                  </div>
                  <div class="modal-body">
                      <p>Are you sure you want to release the payout for <b class="text-info">${fName} ${lName}</b> amounting to <b class="text-info">${amount}</b>?</p>
                  </div>
                  <div class="modal-footer">
                      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                      <button type="button" class="btn btn-primary" id="confirmRelease">Release</button>
                  </div>
              </div>
          </div>
      `;

  document.body.appendChild(modalContainer);

  // Event listener for the "Release" button inside the modal
  document.getElementById("confirmRelease").addEventListener("click", async function () {
    try {
      const response = await fetch("/release_payout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ data: currentEmail }),
      });

      const data = await response.json();
      console.log(data);
    } catch (error) {
      console.error("Error:", error.message);
    }

    // Close the modal
    $("#myModal").modal("hide");
  });
}
