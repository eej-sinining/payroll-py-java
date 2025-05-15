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

// Handle process payroll button
$("#processPayroll").click(function() {
    alert("Payroll ni Aybol");
});