import java.time.Duration;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

public class service {
    
    public static void main(String[] args) {
        if (args.length < 5) {
            System.out.println("Error: Insufficient arguments");
            System.out.println("Usage: java service <employeeId> <hourlyRate> <bonusRate> <deduction> <attendanceData>");
            System.exit(1);
        }

        try {
            String employeeId = args[0];
            double hourlyRate = Double.parseDouble(args[1]);
            double bonusRate = Double.parseDouble(args[2]);
            double deduction = Double.parseDouble(args[3]);
            String attendanceData = args[4];

            // Parse attendance data (format: date1,timeIn1,timeOut1;date2,timeIn2,timeOut2;...)
            List<AttendanceRecord> records = parseAttendanceData(attendanceData);

            // Calculate payroll
            PayrollResult result = calculatePayroll(records, hourlyRate, bonusRate, deduction);

            // Output result in format that Django can parse
            System.out.println(String.format(
                "employeeId:%s,totalHours:%.2f,overallPay:%.2f,deductions:%.2f",
                employeeId,
                result.totalHours,
                result.overallPay,
                result.deductions
            ));
            
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }

    private static List<AttendanceRecord> parseAttendanceData(String data) throws Exception {
        List<AttendanceRecord> records = new ArrayList<>();
        String[] entries = data.split(";");
        
        for (String entry : entries) {
            String[] parts = entry.split(",");
            if (parts.length != 3) {
                throw new Exception("Invalid attendance data format");
            }
            
            LocalTime timeIn = parts[1].isEmpty() ? null : LocalTime.parse(parts[1]);
            LocalTime timeOut = parts[2].isEmpty() ? null : LocalTime.parse(parts[2]);
            
            records.add(new AttendanceRecord(parts[0], timeIn, timeOut));
        }
        
        return records;
    }

    private static PayrollResult calculatePayroll(List<AttendanceRecord> records, double hourlyRate, double bonusRate, double deduction) {
        double totalHours = 0;
        double overallPay = 0;
        
        for (AttendanceRecord record : records) {
            if (record.timeIn != null && record.timeOut != null) {
                
                double hours = Duration.between(record.timeIn, record.timeOut).toMinutes() / 60.0;
                totalHours += hours;
                
                
                double dailyPay = hours * hourlyRate;
                
                
                if (hours > 8) {
                    dailyPay += (hours - 8) * bonusRate;
                }
                
                overallPay += dailyPay;
            }
        }
        
        
        overallPay -= deduction;
        
        return new PayrollResult(totalHours, overallPay, deduction);
    }

    static class AttendanceRecord {
        String date;
        LocalTime timeIn;
        LocalTime timeOut;

        public AttendanceRecord(String date, LocalTime timeIn, LocalTime timeOut) {
            this.date = date;
            this.timeIn = timeIn;
            this.timeOut = timeOut;
        }
    }

    static class PayrollResult {
        double totalHours;
        double overallPay;
        double deductions;

        public PayrollResult(double totalHours, double overallPay, double deductions) {
            this.totalHours = totalHours;
            this.overallPay = overallPay;
            this.deductions = deductions;
        }
    }
}