public class service {

    public static void main(String[] args) {
        
        if (args.length != 4) {
            System.out.println("Usage: java service <employee_role> <total_hours> <overtime_hours> <late_hours>");
            return;
        }

        
        String employeeRole = String.valueOf(args[0]).toLowerCase();
        int totalHours = Integer.parseInt(args[1]);
        int overtimeHours = Integer.parseInt(args[2]);
        int lateHours = Integer.parseInt(args[3]);

        
        double hourlyRate = 0;
        if (employeeRole.equals("mayor")) {
            hourlyRate = 852.00;
        } else if (employeeRole.equals("vice mayor")) {
            hourlyRate = 682.00;
        } else if (employeeRole.equals("councilor")) {
            hourlyRate = 511.00;
        } else if (employeeRole.equals("department head")) {
            hourlyRate = 398.00;
        } else if (employeeRole.equals("clerk")) {
            hourlyRate = 102.00;
        } else if (employeeRole.equals("treasurer")) {
            hourlyRate = 341.00;
        }else if (employeeRole.equals("assessor")) {
            hourlyRate = 284.00;
        }else if (employeeRole.equals("pro")) {
            hourlyRate = 199.00;
        }else if (employeeRole.equals("legal officer")) {
            hourlyRate = 455.00;
        }else if (employeeRole.equals("hr")) {
            hourlyRate = 227.00;
        }else if (employeeRole.equals("pm")) {
            hourlyRate = 341.00;
        }else if (employeeRole.equals("staff")) {
            hourlyRate = 114.00;
        }else if (employeeRole.equals("driver")) {
            hourlyRate = 85.00;
        }else if (employeeRole.equals("utility worker")) {
            hourlyRate = 74.00;
        }
        double grossPay = totalHours * hourlyRate; 
        double overtimePay = overtimeHours * hourlyRate * 1.5;
        double lateDeduction = lateHours * hourlyRate;

        grossPay += overtimePay;
        grossPay -= lateDeduction;

        // Deduct taxes 
        double tax = 0;
        if (grossPay <= 10000) {
            tax = 0;
        } else if (grossPay >= 10001 && grossPay <= 30000) {
            tax = (grossPay - 10000) * 0.20;
        } else if (grossPay >= 30001 && grossPay <= 70000) {
            tax = 2500 + (grossPay - 30000) * 0.25;
        } else if (grossPay >= 70001 && grossPay <= 140000) {
            tax = 12500 + (grossPay - 70000) * 0.30;
        } else if (grossPay >= 140001 && grossPay <= 200000) {
            tax = 32500 + (grossPay - 140000) * 0.32;
        } else if (grossPay >= 200001) {
            tax = 52000 + (grossPay - 200000) * 0.35;
        }

        // Deduct SSS & Pagibig
        double sss = 1350.00;  
        double pagibig = 100.0;  

        // Total deductions
        double totalDeductions = tax + sss + pagibig;
        
        // Calculate net pay
        double netPay = grossPay - totalDeductions;

        // trial and error / Print the results
        System.out.println("Employee Role: " + employeeRole);
        System.out.println("Total Hours Worked: " + totalHours);
        System.out.println("Overtime Hours Worked: " + overtimeHours);
        System.out.println("Late Hours Worked: " + lateHours);
        System.out.println("Gross Pay: " + grossPay);
        System.out.println("Overtime Pay: " + overtimePay);
        System.out.println("Late Deduction: " + lateDeduction);
        System.out.println("Tax Deduction: " + tax);
        System.out.println("SSS Deduction: " + sss);
        System.out.println("Pagibig Deduction: " + pagibig);
        System.out.println("Total Deductions: " + totalDeductions);
        System.out.println("Net Pay: " + netPay);
    }
}
