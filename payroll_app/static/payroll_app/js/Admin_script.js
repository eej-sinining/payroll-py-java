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
document.getElementById('generateAttendanceReport').addEventListener('click', function() {
    if (confirm('Generate payroll report for all employees?')) {
        const btn = this;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
        
        fetch('/generate-payroll-report/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let message = `Processed ${data.processed} of ${data.total} employees`;
                if (data.warning) {
                    message += ` (${data.warning})`;
                    if (data.errors) {
                        message += '\n\n' + data.errors.join('\n');
                    }
                }
                alert(message);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate report');
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = 'Generate Report';
        });
    }
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
    $("#employeeForm").submit(function(e) {
        e.preventDefault();
        
        // Basic validation
        if (!$("#position").val()) {
            alert("Please select a position");
            return false;
        }
        
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if(response.success) {
                    $('#employeeModal').modal('hide');                
                    location.reload();
                } else {
                    alert("Error: " + response.error);
                }
            },
            error: function(xhr, errmsg, err) {
                alert("An error occurred while saving the employee.");
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    });
});

// Handle edit employee button click
$(document).on('click', '.edit-employee', function() {
    var employeeId = $(this).data('employee-id');
    
    // Show loading state
    $('#editEmployeeModal .modal-body').addClass('loading');
    $('#editEmployeeModal').modal('show');
    
    // Fetch employee data via AJAX
    $.ajax({
        url: `/get_employee_data/${employeeId}/`,
        type: 'GET',
        success: function(response) {
            $('#editEmployeeModal .modal-body').removeClass('loading');
            
            if (response.success) {
                // Populate the form with employee data
                $('#editEmployeeId').val(response.employee.id);
                $('#editFirstName').val(response.employee.first_name);
                $('#editLastName').val(response.employee.last_name);
                $('#editContact').val(response.employee.contact);
                
                // Set position and related fields
                if (response.employee.position) {
                    $('#editPosition').val(response.employee.position.id);
                    $('#editHourlyRate').val(response.employee.hourly_rate);
                    $('#editStandardHours').val(response.employee.position.standard_hours);
                } else {
                    $('#editPosition').val('');
                    $('#editHourlyRate').val('');
                    $('#editStandardHours').val('');
                }
                
                // Set account information
                $('#editUsername').val(response.user.username);
                $('#editIsActive').prop('checked', response.user.is_active);
                
                // Set the form action URL
                $('#editEmployeeForm').attr('action', `/update_employee/${employeeId}/`);
            } else {
                alert('Error: ' + response.error);
                $('#editEmployeeModal').modal('hide');
            }
        },
        error: function(xhr, errmsg, err) {
            $('#editEmployeeModal .modal-body').removeClass('loading');
            alert('An error occurred while fetching employee data');
            $('#editEmployeeModal').modal('hide');
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});

// Handle edit form submission
$("#editEmployeeForm").submit(function(e) {
    e.preventDefault();
    
    // Clear previous error messages
    $('.username-error').remove();
    
    $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function(response) {
            if(response.success) {
                $('#editEmployeeModal').modal('hide');
                location.reload();  // Refresh the page
            } else {
                // Show specific error for username
                if (response.error && response.error.includes('Username')) {
                    $('#editUsername').after(
                        `<div class="text-danger username-error mt-1">${response.error}</div>`
                    );
                } else {
                    alert("Error: " + response.error);
                }
            }
        },
        error: function(xhr, errmsg, err) {
            alert("An error occurred while updating the employee.");
            console.log(xhr.status + ": " + xhr.responseText);
        }
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


// Handle salary structure button to show modal
$("#addSalaryStructure").click(function() {
    $('#salaryStructureModal').modal('show');
});

// Handle salary structure form submission
$("#salaryStructureForm").submit(function(e) {
    e.preventDefault();
    
    $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function(response) {
            if(response.success) {
                $('#salaryStructureModal').modal('hide');
                // Show success message
                alert("Salary structure added successfully!");
                // Refresh the page to show the new structure
                location.reload();
            } else {
                alert("Error: " + response.error);
            }
        },
        error: function(xhr, errmsg, err) {
            alert("An error occurred while saving the salary structure.");
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});

// Handle edit salary structure button click
$(document).on('click', '.edit-salary-structure', function() {
    var positionId = $(this).data('position-id');
    
    // Show loading state
    $('#editSalaryStructureModal .modal-body').addClass('loading');
    $('#editSalaryStructureModal').modal('show');
    
    // Fetch position data via AJAX
    $.ajax({
        url: `/get_position_data/${positionId}/`,
        type: 'GET',
        success: function(response) {
            $('#editSalaryStructureModal .modal-body').removeClass('loading');
            
            if (response.success) {
                // Populate the form with position data
                $('#editPositionId').val(response.position.id);
                $('#editPositionName').val(response.position.name);
                $('#editStandardHours').val(response.position.standard_hours);
                $('#editBaseSalary').val(response.position.base_salary);
                $('#editBonus').val(response.position.bonus);
                $('#editDeduction').val(response.position.deduction);
                
                // Set the form action URL
                $('#editSalaryStructureForm').attr('action', `/update_salary_structure/${positionId}/`);
            } else {
                alert('Error: ' + response.error);
                $('#editSalaryStructureModal').modal('hide');
            }
        },
        error: function(xhr, errmsg, err) {
            $('#editSalaryStructureModal .modal-body').removeClass('loading');
            alert('An error occurred while fetching position data');
            $('#editSalaryStructureModal').modal('hide');
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});

// Handle edit salary structure form submission
$("#editSalaryStructureForm").submit(function(e) {
    e.preventDefault();
    
    $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: $(this).serialize(),
        success: function(response) {
            if(response.success) {
                $('#editSalaryStructureModal').modal('hide');
                // Show success message
                alert("Salary structure updated successfully!");
                // Refresh the page to show the updated structure
                location.reload();
            } else {
                alert("Error: " + response.error);
            }
        },
        error: function(xhr, errmsg, err) {
            alert("An error occurred while updating the salary structure.");
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});

// Handle delete salary structure button click
$(document).on('click', '.delete-salary-structure', function() {
    if (confirm('Are you sure you want to delete this salary structure? This action cannot be undone.')) {
        var positionId = $(this).data('position-id');
        var $row = $(this).closest('tr');
        
        $.ajax({
            type: "POST",
            url: `/delete_salary_structure/${positionId}/`,
            data: {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    $row.fadeOut(400, function() {
                        $(this).remove();
                        // If no rows left, show the empty message
                        if ($('tbody tr').not('.empty-row').length === 0) {
                            $('tbody').html('<tr class="empty-row"><td colspan="7" class="text-center">No salary structures found</td></tr>');
                        }
                    });
                } else {
                    alert("Error: " + response.error);
                }
            },
            error: function(xhr, errmsg, err) {
                alert("An error occurred while deleting the salary structure.");
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
    }
});

// Handle salary sort form submission
$("#salarySortForm").submit(function(e) {
    e.preventDefault();
    
    const sortBy = $('input[name="salarySort"]:checked').val();
    const sortOrder = $('input[name="sortOrder"]:checked').val();
    
    $.ajax({
        type: "GET",
        url: "/sort_salary_structures/",
        data: {
            'sort_by': sortBy,
            'sort_order': sortOrder
        },
        success: function(response) {
            if(response.success) {
                // Rebuild the table with sorted data
                const tbody = $('table tbody');
                tbody.empty();
                
                response.positions.forEach(position => {
                    tbody.append(`
                        <tr>
                            <td>P${position.id.toString().padStart(3, '0')}</td>
                            <td>${position.name}</td>
                            <td>${position.standard_hours} hrs</td>
                            <td>₱ ${position.base_salary}</td>
                            <td>₱ ${position.deduction}</td>
                            <td>₱ ${position.bonus}</td>
                            <td>
                                <button class="btn btn-sm btn-primary edit-salary-structure" data-position-id="${position.id}"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-sm btn-danger delete-salary-structure" data-position-id="${position.id}"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `);
                });
                
                if (response.positions.length === 0) {
                    tbody.append('<tr class="empty-row"><td colspan="7" class="text-center">No salary structures found</td></tr>');
                }
            } else {
                alert("Error: " + response.error);
            }
        },
        error: function(xhr, errmsg, err) {
            alert("An error occurred while sorting salary structures.");
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});

// Handle process payroll button
document.addEventListener('DOMContentLoaded', function() {
  const processPayrollForm = document.getElementById('processPayrollForm');
  
  processPayrollForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get all checked payroll IDs
    const checkboxes = document.querySelectorAll('.payroll-checkbox:checked');
    const payrollIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (payrollIds.length === 0) {
      alert('Please select at least one payroll to process');
      return;
    }
    
    // Add the payroll IDs to the form data
    const formData = new FormData(processPayrollForm);
    payrollIds.forEach(id => formData.append('payroll_ids', id));
    
    // Submit the form
    fetch(processPayrollForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
      }
    })
    .then(response => {
      if (response.ok) {
        window.location.reload(); // Refresh the page to see changes
      } else {
        alert('Error processing payroll');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error processing payroll');
    });
  });
});