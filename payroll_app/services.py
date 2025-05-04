from decimal import Decimal
from .models import Adjustment, Deduction, Payroll
from django.db import models

def calculate_payroll(employee, cutoff_start, cutoff_end, total_hours_worked):
    # Get overtime and absences
    overtime = Adjustment.objects.filter(
        employee=employee, adjustment_type='Overtime',
        cutoff_start=cutoff_start, cutoff_end=cutoff_end
    ).aggregate(total_hours=models.Sum('hours'))['total_hours'] or 0

    absence = Adjustment.objects.filter(
        employee=employee, adjustment_type='Absence',
        cutoff_start=cutoff_start, cutoff_end=cutoff_end
    ).aggregate(total_hours=models.Sum('hours'))['total_hours'] or 0

    # Base pay calculation
    regular_hours = Decimal(employee.standard_hours)
    hourly_rate = employee.hourly_rate

    adjusted_hours = total_hours_worked + Decimal(overtime) - Decimal(absence)
    gross_pay = adjusted_hours * hourly_rate

    # Sample deductions (flat rates or percentages can vary based on actual rules)
    tax = gross_pay * Decimal('0.1')  # 10% tax
    sss = gross_pay * Decimal('0.05')  # 5% SSS
    pagibig = Decimal('100.00')  # Flat rate

    total_deductions = tax + sss + pagibig
    net_pay = gross_pay - total_deductions

    return {
        'gross_pay': round(gross_pay, 2),
        'deductions': round(total_deductions, 2),
        'net_pay': round(net_pay, 2),
        'breakdown': {
            'tax': round(tax, 2),
            'sss': round(sss, 2),
            'pagibig': round(pagibig, 2),
            'overtime_hours': Decimal(overtime),
            'absence_hours': Decimal(absence)
        }
    }
def save_payroll(employee, gross_pay, total_deductions, net_pay, breakdown, cutoff_start, cutoff_end):
    payroll = Payroll(
        employee=employee,
        gross_pay=gross_pay,
        total_deductions=total_deductions,
        net_pay=net_pay,
        tax=breakdown['tax'],
        sss=breakdown['sss'],
        pagibig=breakdown['pagibig'],
        overtime_hours=breakdown['overtime_hours'],
        absence_hours=breakdown['absence_hours'],
        cutoff_start=cutoff_start,
        cutoff_end=cutoff_end
    )
    payroll.save()
