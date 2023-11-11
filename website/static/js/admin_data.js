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
          label: "Student with scholarship",
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

function renderPieChart(divId, data) {
  var ctx = document.getElementById(divId).getContext("2d");
  var labels = Object.keys(data);
  var values = Object.values(data);

  var myPieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: values,
          backgroundColor: ["#F9F301", "#1cc88a"],
          hoverBackgroundColor: ["#F9F301", "#1cc88a"],
          hoverBorderColor: "rgba(234, 236, 244, 1)",
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      tooltips: {
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: "#dddfeb",
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
      },
      legend: {
        display: false,
      },
      cutoutPercentage: 80,
    },
  });
}

// Handle Accept and Reject click on Applicants table
// script.js

var currentApplicantId;
var currentAction;

function showConfirmation(applicantId, action) {
    currentApplicantId = applicantId;
    currentAction = action;

    // Update the text in the modal based on the action
    document.getElementById('confirmationModalLabel').innerHTML = `Confirm ${action}`;
    document.getElementById('confirmationModalBody').innerHTML = `Are you sure you want to ${action.toLowerCase()} this applicant?`;

    // Open the confirmation modal
    $('#confirmationModal').modal('show');
}

function performAction() {
    // Make an AJAX request to the Flask route with the applicant ID and action
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/process_action", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log('Action performed successfully:', currentAction);

            // Close the confirmation modal
            $('#confirmationModal').modal('hide');
        }
    };

    var data = JSON.stringify({ id: currentApplicantId, action: currentAction });
    xhr.send(data);
}

// Attach event listener to the Confirm button in the modal
document.getElementById('confirmActionButton').addEventListener('click', performAction);
 