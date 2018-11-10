def get_working_days(start_date, end_date):
    number_of_days = (end_date - start_date).days + 1
    number_of_weeks = number_of_days // 7
    reminder_days = number_of_days % 7
    number_of_days -= number_of_weeks * 2
    if reminder_days:
        weekdays = set(range(end_date.isoweekday(), end_date.isoweekday() - reminder_days, -1))
        number_of_days -= len(weekdays.intersection([7, 6, 0, -1]))
    return number_of_days
