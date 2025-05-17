// ---------Responsive-navbar-active-animation-----------
function test() {
    var tabsNewAnim = $('#navbarSupportedContent');
    var selectorNewAnim = $('#navbarSupportedContent').find('li').length;
    var activeItemNewAnim = tabsNewAnim.find('.active');
    var activeWidthNewAnimHeight = activeItemNewAnim.innerHeight();
    var activeWidthNewAnimWidth = activeItemNewAnim.innerWidth();
    var itemPosNewAnimTop = activeItemNewAnim.position();
    var itemPosNewAnimLeft = activeItemNewAnim.position();
    
    $(".hori-selector").css({
        "top": itemPosNewAnimTop.top + "px",
        "left": itemPosNewAnimLeft.left + "px",
        "height": activeWidthNewAnimHeight + "px",
        "width": activeWidthNewAnimWidth + "px"
    });
    
    $("#navbarSupportedContent").on("click", "li", function (e) {
        $('#navbarSupportedContent ul li').removeClass("active");
        $(this).addClass('active');
        var activeWidthNewAnimHeight = $(this).innerHeight();
        var activeWidthNewAnimWidth = $(this).innerWidth();
        var itemPosNewAnimTop = $(this).position();
        var itemPosNewAnimLeft = $(this).position();
        
        $(".hori-selector").css({
            "top": itemPosNewAnimTop.top + "px",
            "left": itemPosNewAnimLeft.left + "px",
            "height": activeWidthNewAnimHeight + "px",
            "width": activeWidthNewAnimWidth + "px"
        });
    });
}
// Handle admin dropdown
$(document).ready(function() {
    // Close dropdown when clicking outside
    $(document).click(function(e) {
        if (!$(e.target).closest('.dropdown').length) {
            $('.dropdown-menu').removeClass('show');
        }
    });
    
    // Keep dropdown open when clicking inside
    $('.dropdown-menu').click(function(e) {
        e.stopPropagation();
    });
    
    // Make sure dropdown works on mobile
    $('.admin-dropdown').click(function() {
        var dropdown = $(this).next('.dropdown-menu');
        $('.dropdown-menu').not(dropdown).removeClass('show');
        dropdown.toggleClass('show');
    });
});
$(document).ready(function () {
    setTimeout(function () {
        test();
    });
    
    // Hide the default content
    $(".content").hide();
    // Show only employee records content since it's active
    $("#employeeRecordsContent").show();
    
    // Handle menu item clicks
    $("#navbarSupportedContent li").click(function() {
        var navText = $(this).find("a").text();
        
        // Hide all content sections
        $(".content, #employeeRecordsContent, #attendanceContent, #salarySetupContent, #payrollContent").hide();
        
        // Show appropriate content based on clicked item
        if(navText.includes("Employee Records")) {
            $("#employeeRecordsContent").show();
        } else if(navText.includes("Attendance")) {
            $("#attendanceContent").show();
        } else if(navText.includes("Salary Setup")) {
            $("#salarySetupContent").show();
        } else if(navText.includes("Payroll")) {
            $("#payrollContent").show();
        } else {
            // For other menu items, show the default content
            $(".content").show();
        }
    });
});

$(window).on('resize', function () {
    setTimeout(function () {
        test();
    }, 500);
});

$(".navbar-toggler").click(function () {
    $(".navbar-collapse").slideToggle(300);
    setTimeout(function () {
        test();
    });
});

// Handle attendance report generation
$("#generateAttendanceReport").click(function() {
    var selectedDate = $("#attendanceDate").val();
    alert("Attendance ni Aybol: " + selectedDate);
});

// Handle generate employee button click
$("#generateEmployeeBtn").click(function() {
    $('#employeeModal').modal('show');
});

// Handle position change to update hourly rate
$(document).ready(function() {
    // Handle position change to update hourly rate and standard hours
    $("#position").change(function() {
        const selectedOption = $(this).find('option:selected');
        const hourlyRate = selectedOption.data('hourly-rate');
        const standardHours = selectedOption.data('standard-hours');
        
        $("#hourlyRate").val(hourlyRate);
        
        // Only set standard hours if it exists in the data attribute
        if (standardHours) {
            $("#standardHours").val(standardHours);
        }
    });

    // Handle form submission via AJAX
    $(document).ready(function() {
    $('#employeeForm').submit(function(e) {
        e.preventDefault();
        
        // Validate password complexity
        const password = $('#password').val();
        if (!/(?=.*\d)(?=.*[!@#$%^&*])/.test(password)) {
            alert('Password must contain at least 1 number and 1 special character');
            return;
        }

        $.ajax({
            url: '/create-employee/',
            method: 'POST',
            data: $(this).serialize(),
            headers: {
                "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if(response.success) {
                    location.reload(); // Refresh to show new employee
                } else {
                    alert('Error: ' + response.error);
                }
            },
            error: function(xhr) {
                alert('Server error: ' + xhr.statusText);
            }
        });
    });
});
});

// Delete button functionality in employee page
$(document).on('click', '.delete-employee', function() {
    if (confirm('Are you sure you want to delete this employee and their user account?')) {
        var employeeId = $(this).data('employee-id');
        var $row = $(this).closest('tr');
        
        $.ajax({
            type: "POST",
            url: `/delete_employee/${employeeId}/`,
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    $row.fadeOut(400, function() {
                        $(this).remove();
                        // If no rows left, show the empty message
                        if ($('tbody tr').not('.empty-row').length === 0) {
                            $('tbody').html('<tr class="empty-row"><td colspan="7" class="text-center">No employees found</td></tr>');
                        }
                    });
                } else {
                    alert("Error: " + response.error);
                }
            },
            error: function(xhr, errmsg, err) {
                alert("An error occurred while deleting the employee.");
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }
});

$(document).ready(function() {
    // Handle add salary structure button click
    $('#addSalaryStructure').click(function() {
        $('#salaryModal').modal('show');
    });

    // Handle form submission
    $('#salaryForm').submit(function(e) {
        e.preventDefault();
        
        $.ajax({
            url: '/add-salary-structure/',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if(response.success) {
                    // Add the new position to the table
                    addPositionToTable(response.position);
                    $('#salaryModal').modal('hide');
                    showSuccessAlert('Salary structure added successfully!');
                    // Reset form
                    $('#salaryForm')[0].reset();
                } else {
                    showErrorAlert(response.error);
                }
            },
            error: function(xhr) {
                showErrorAlert('An error occurred: ' + xhr.responseText);
            }
        });
    });

    // Function to add new position to table
    function addPositionToTable(position) {
    const formattedId = 'P' + String(position.id).padStart(3, '0');
    const newRow = $(`
        <tr>
            <td>${formattedId}</td>
            <td>${position.name}</td>
            <td>${position.standard_hours} hrs</td>
            <td>₱ ${position.base_salary}</td>
            <td>₱ ${position.bonus}</td>
            <td>₱ ${position.deduction}</td>
            <td>
                <button class="btn btn-sm btn-primary"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-danger"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `);
    
    // Find the correct position to insert (alphabetical by name)
    let inserted = false;
    $('#positionsTableBody tr').each(function() {
        if ($(this).find('td:nth-child(2)').text().localeCompare(position.name) > 0) {
            $(this).before(newRow);
            inserted = true;
            return false; // break loop
        }
    });
    
    // If not inserted yet, append to end
    if (!inserted) {
        $('#positionsTableBody').append(newRow);
    }
}
});

// Handle process payroll button
$("#processPayroll").click(function() {
    alert("Payroll ni Aybol");
});

//create employee
$(document).ready(function() {
    // Update hourly rate and standard hours when position changes
    $('#position').change(function() {
        const selectedOption = $(this).find('option:selected');
        $('#hourlyRate').val(selectedOption.data('hourly-rate'));
        $('#standardHours').val(selectedOption.data('standard-hours'));
    });

    // Handle employee form submission
    $('#employeeForm').submit(function(e) {
        e.preventDefault();
        
        $.ajax({
            url: '/create-employee/',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if(response.success) {
                    // Add new employee to table
                    addEmployeeToTable(response.employee);
                    $('#employeeModal').modal('hide');
                    showSuccessAlert('Employee created successfully!');
                    // Reset form
                    $('#employeeForm')[0].reset();
                } else {
                    showErrorAlert(response.error);
                }
            },
            error: function(xhr) {
                showErrorAlert('Error: ' + xhr.responseText);
            }
        });
    });

    // Function to add new employee row
    function addEmployeeToTable(employee) {
    const statusClass = employee.is_active ? 'bg-success' : 'bg-secondary';
    const statusText = employee.is_active ? 'Active' : 'Inactive';
    
    // Fix undefined names and format data properly
    const firstName = employee.first_name || '';
    const lastName = employee.last_name || '';
    const positionName = employee.position?.name || 'No Position';
    const hourlyRate = employee.hourly_rate ? `₱${parseFloat(employee.hourly_rate).toFixed(2)}` : 'N/A';
    const standardHours = employee.standard_hours ? `${employee.standard_hours} hrs` : 'N/A';
    const contact = employee.contact || 'N/A';

    const newRow = `
        <tr>
            <td>E${String(employee.id).padStart(3, '0')}</td>
            <td>${firstName} ${lastName}</td>
            <td>${positionName}</td>
            <td>${hourlyRate}</td>
            <td>${standardHours}</td>
            <td><span class="badge ${statusClass}">${statusText}</span></td>
            <td>${contact}</td>
            <td>
                <button class="btn btn-sm btn-primary edit-employee" 
                        data-employee-id="${employee.id}"
                        data-bs-toggle="modal" 
                        data-bs-target="#editEmployeeModal">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-employee" 
                        data-employee-id="${employee.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `;
    
    $('tbody tr td[colspan="9"]').parent().remove();
    $('table tbody').prepend(newRow);
}
});

// Alert functions
function showSuccessAlert(message) {
    const alert = `<div class="alert alert-success alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
    $('#alertsContainer').append(alert);
    setTimeout(() => $('.alert').alert('close'), 3000);
}

function showErrorAlert(message) {
    const alert = `<div class="alert alert-danger alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
    $('#alertsContainer').append(alert);
}

// Fetch and display employees (if not using Django template rendering)
$(document).ready(function() {
    $.ajax({
        url: '/api/employees/',  // You need an API endpoint for this
        method: 'GET',
        success: function(data) {
            // Loop through data and append rows to the table
            data.forEach(employee => {
                $('tbody').append(`
                    <tr>
                        <td>E${employee.id.toString().padStart(3, '0')}</td>
                        <td>${employee.first_name} ${employee.last_name}</td>
                        <td>${employee.position?.name || '<span class="text-muted">No Position</span>'}</td>
                        <td>${employee.position ? '₱' + employee.position.base_salary : '<span class="text-muted">N/A</span>'}</td>
                        <td>${employee.position ? employee.position.standard_hours + ' hrs' : '<span class="text-muted">N/A</span>'}</td>
                        <td><span class="badge ${employee.is_active ? 'bg-success' : 'bg-secondary'}">${employee.is_active ? 'Active' : 'Inactive'}</span></td>
                        <td>${employee.contact}</td>
                        <td>
                            <button class="btn btn-sm btn-primary edit-employee" data-employee-id="${employee.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger delete-employee" data-employee-id="${employee.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `);
            });
        },
        error: function(error) {
            console.error("Error fetching employees:", error);
        }
    });
});