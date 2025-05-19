
// Time In Button Click
document.getElementById('timeInBtn').addEventListener('click', function() {
    const btn = this;
    btn.disabled = true;
    
    fetch('{% url "time_in" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Check if a row for today already exists
            const table = document.querySelector('#attendanceMenu table tbody');
            const today = new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
            let existingRow = null;
            
            // Find existing row for today
            Array.from(table.rows).forEach(row => {
                const rowDate = row.cells[0].textContent.trim();
                if (rowDate === today) {
                    existingRow = row;
                }
            });
            
            if (existingRow) {
                // Update existing row
                existingRow.cells[1].textContent = data.time_in.toLowerCase();
                existingRow.cells[2].textContent = '--';
            } else {
                // Create new row
                const newRow = document.createElement('tr');
                newRow.innerHTML = `
                    <td>${data.date}</td>
                    <td>${data.time_in.toLowerCase()}</td>
                    <td>--</td>
                `;
                
                // Insert at the top of the table
                if (table.rows.length > 0) {
                    table.insertBefore(newRow, table.rows[0]);
                } else {
                    table.appendChild(newRow);
                }
            }
            
            alert('Successfully timed in at ' + data.time_in);
        } else {
            alert(data.message || 'Error timing in');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to time in. Please try again.');
    })
    .finally(() => {
        btn.disabled = false;
    });
});

// Time Out Button Click
document.getElementById('timeOutBtn').addEventListener('click', function() {
    const btn = this;
    btn.disabled = true;
    
    fetch('{% url "time_out" %}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        credentials: 'include',
    })
    .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const today = new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
            const table = document.querySelector('#attendanceMenu table tbody');
            let updated = false;
            
            // Find the row for today with '--' as time-out
            Array.from(table.rows).forEach(row => {
                const rowDate = row.cells[0].textContent.trim();
                const timeOutCell = row.cells[2];
                
                if (rowDate === today && timeOutCell.textContent.trim() === '--') {
                    timeOutCell.textContent = data.time_out.toLowerCase();
                    updated = true;
                }
            });
            
            if (!updated) {
                // If no existing row found, create a new one (shouldn't normally happen)
                const newRow = document.createElement('tr');
                newRow.innerHTML = `
                    <td>${data.date}</td>
                    <td>--</td>
                    <td>${data.time_out.toLowerCase()}</td>
                `;
                table.insertBefore(newRow, table.rows[0]);
            }
            
            alert('Successfully timed out at ' + data.time_out);
        } else {
            alert(data.message || 'Error timing out');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to time out. Please try again.');
    })
    .finally(() => {
        btn.disabled = false;
    });
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
        
        // Display a page of records
        function displayPage(page) {
            currentPage = page;
            attendanceTable.innerHTML = '<tr><th>Date</th><th>Time - in</th><th>Time - out</th></tr>';
            
            const start = (page - 1) * ROWS_PER_PAGE;
            const end = start + ROWS_PER_PAGE;
            const paginatedItems = allRecords.slice(start, end);
            
            paginatedItems.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.date}</td>
                    <td>${record.timeIn}</td>
                    <td>${record.timeOut}</td>
                `;
                attendanceTable.appendChild(row);
            });
            
            setupPagination();
        }
        
        // Create pagination buttons
        function setupPagination() {
            paginationContainer.innerHTML = '';
            const pageCount = Math.ceil(allRecords.length / ROWS_PER_PAGE);
            
            if (pageCount <= 1) return;
            
            // Previous button
            const prevButton = document.createElement('button');
            prevButton.innerText = 'Previous';
            prevButton.disabled = currentPage === 1;
            prevButton.addEventListener('click', () => {
                if (currentPage > 1) displayPage(currentPage - 1);
            });
            paginationContainer.appendChild(prevButton);
            
            // Page buttons
            for (let i = 1; i <= pageCount; i++) {
                const pageButton = document.createElement('button');
                pageButton.innerText = i;
                pageButton.className = currentPage === i ? 'active' : '';
                pageButton.addEventListener('click', () => displayPage(i));
                paginationContainer.appendChild(pageButton);
            }
            
            // Next button
            const nextButton = document.createElement('button');
            nextButton.innerText = 'Next';
            nextButton.disabled = currentPage === pageCount;
            nextButton.addEventListener('click', () => {
                if (currentPage < pageCount) displayPage(currentPage + 1);
            });
            paginationContainer.appendChild(nextButton);
        }
        
        // Load attendance records from localStorage
        function loadAttendanceRecords() {
            allRecords = JSON.parse(localStorage.getItem('attendanceRecords')) || [];
            displayPage(1);
        }
        
        // Save a new attendance record
        function saveAttendanceRecord(date, timeIn, timeOut) {
            const records = JSON.parse(localStorage.getItem('attendanceRecords')) || [];
            records.unshift({ date, timeIn, timeOut });
            localStorage.setItem('attendanceRecords', JSON.stringify(records));
        }
        
        // Update an existing attendance record
        function updateAttendanceRecord(date, timeIn, timeOut) {
            let records = JSON.parse(localStorage.getItem('attendanceRecords')) || [];
            const index = records.findIndex(r => r.date === date && r.timeIn === timeIn);
            if (index !== -1) {
                records[index].timeOut = timeOut;
                localStorage.setItem('attendanceRecords', JSON.stringify(records));
            }
        }
        
        // Load records when page loads
        loadAttendanceRecords();

        // Receipt Modal Functionality
        const modal = document.getElementById('receiptModal');
        const closeModal = document.querySelector('.close-modal');
        const viewButtons = document.querySelectorAll('.btn-view');
        
        // Receipt data (in a real application, this would come from the server)
        const receiptData = {
            '{{ payroll.date|date:"Y-m-d" }}': {
                period: '{{ payroll.cutoff_start|date:"M d, Y" }} – {{ payroll.cutoff_end|date:"M d, Y" }}',
                basicPay: '{{ payroll.base_pay }}',
                overtimePay: '{{ payroll.overtime_pay }}',
				bonusPay: '{{ payroll.bonus_pay }}',
                sss: '{{ payroll.sss_deduction }}',
                philHealth: '{{ payroll.philhealth_deduction }}',
                pagibig: '{{ payroll.pagibig_deduction }}',
                tax: '{{ payroll.tax_deduction }}',
                totalDeductions: '{{ payroll.sss_deduction }} + {{ payroll.philhealth_deduction }} + {{ payroll.pagibig_deduction }} + {{ payroll.tax_deduction }}',
                netPay: '{{ payroll.net_pay }}',
            },
        };
        


// Open modal when View button is clicked
viewButtons.forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const payrollId = this.getAttribute('data-payroll-id');
        
        // Fetch payroll details from server
        fetch(`/get-payroll-details/${payrollId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Populate receipt with data
                    document.getElementById('receiptPeriod').textContent = 
                        `Pay Period: ${data.cutoff_start} – ${data.cutoff_end}`;
                    document.getElementById('receiptBasicPay').textContent = `₱${data.base_pay}`;
                    document.getElementById('receiptOvertimePay').textContent = `₱${data.overtime_pay || '0.00'}`;
                    document.getElementById('receiptHolidayPay').textContent = `₱${data.bonus_pay || '0.00'}`;
                    document.getElementById('receiptTotalEarnings').textContent = `₱${data.base_pay}`;
                    document.getElementById('receiptSSS').textContent = `₱${data.sss_deduction || '0.00'}`;
                    document.getElementById('receiptPhilHealth').textContent = `₱${data.philhealth_deduction || '0.00'}`;
                    document.getElementById('receiptPagibig').textContent = `₱${data.pagibig_deduction || '0.00'}`;
                    document.getElementById('receiptTax').textContent = `₱${data.tax_deduction || '0.00'}`;
                    document.getElementById('receiptTotalDeductions').textContent = `₱${data.deductions}`;
                    document.getElementById('receiptNetPay').textContent = `₱${data.net_pay}`;
                    
                    // Show modal
                    modal.style.display = 'block';
                } else {
                    alert('Failed to load payroll details');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to load payroll details');
            });
    });
});

    // Sidebar toggle
    let sidebar = document.getElementById("sidebar");
    let sidebarBtn = document.getElementById("menu-btn");

    sidebarBtn.addEventListener("click", () => {
        sidebar.classList.toggle("hide");
        document.getElementById("content").classList.toggle("shift");
    });

    // Content switch logic
    const links = document.querySelectorAll(".side-menu a[data-section]");
    const sections = document.querySelectorAll(".content-section");

    links.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            // Remove active class
            document.querySelectorAll(".side-menu li").forEach(li => li.classList.remove("active"));

            // Set active class on clicked
            link.parentElement.classList.add("active");

            // Hide all sections
            sections.forEach(section => section.style.display = "none");

            // Show selected section
            const targetId = link.getAttribute("data-section");
            document.getElementById(targetId).style.display = "block";
        });
    });