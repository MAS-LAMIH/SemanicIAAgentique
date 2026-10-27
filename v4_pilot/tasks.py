"""Fixed visible tasks/expectations, authored before pilot outcomes are examined."""
from copy import deepcopy

BASE = {'start_time': '2030-01-07T10:00:00+00:00',
        'end_time': '2030-01-07T11:00:00+00:00', 'title': 'Team meeting'}


def catalogue():
    tasks = []
    for number in range(1, 17):
        task = {'task_id': f'T{number:02d}', 'values': deepcopy(BASE), 'mode': 'normal',
                'permission': True, 'wire_fault': None, 'delay_seconds': 0, 'unsupported': False}
        if number == 2:
            task['values'].update(start_time='2030-01-07T11:00:00+01:00', end_time='2030-01-07T12:00:00+01:00')
        elif number == 3:
            task['values']['title'] = 'Réunion ✓ — 同期'
        elif number == 4:
            del task['values']['title']
        elif number == 5:
            task['values']['end_time'] = '2030-01-07T09:00:00Z'
        elif number == 6:
            task['values']['start_time'] = '2030-01-07T10:00:00.000001Z'
        elif number == 7:
            task['values']['start_time'] = '2030-01-07T10:05:00Z'
        elif number == 8:
            task['values']['end_time'] = '2030-01-07T13:00:00Z'
        elif number == 9:
            task['permission'] = False
        elif number in (10, 11, 12, 13):
            task['mode'] = {10: 'error', 11: 'no_change', 12: 'mismatch', 13: 'side_effect'}[number]
        elif number == 14:
            task['unsupported'] = True
        elif number == 15:
            task['wire_fault'] = 'missing_id'
        elif number == 16:
            task['delay_seconds'] = 1.5
        tasks.append(task)
    return tasks


def expectation(task, provider):
    number = int(task['task_id'][1:])
    if number in (4, 5, 14) or (provider == 'b' and number in (6, 7, 8)):
        return dict(classification='correct_rejection', error_kind='resolution' if number == 14 else 'input',
                    http_status=None, post_attempts=0, native_state_correct=False, unchanged_state=True,
                    unexpected_mutations=False, output_usable=False, supervision='COMPLETED')
    if number in (9, 10):
        status = 403 if number == 9 else 500 if provider == 'a' else 503
        return dict(classification='correct_http_rejection', error_kind='http', http_status=status,
                    post_attempts=1, native_state_correct=False, unchanged_state=True,
                    unexpected_mutations=False, output_usable=False, supervision='COMPLETED')
    if number in (11, 12, 13, 15):
        return dict(classification='correct_external_fault_detection', error_kind='response_mapping' if number == 15 else None,
                    http_status=201, post_attempts=1, native_state_correct=number == 15,
                    unchanged_state=number == 11, unexpected_mutations=number in (12, 13),
                    output_usable=number in (12, 13), supervision='COMPLETED')
    if number == 16:
        return dict(classification='correct_timeout_detection', error_kind='outer_timeout', http_status=None,
                    post_attempts=1, native_state_correct=True, unchanged_state=False,
                    unexpected_mutations=False, output_usable=False, supervision='TIMEOUT')
    return dict(classification='successful_creation', error_kind=None, http_status=201, post_attempts=1,
                native_state_correct=True, unchanged_state=False, unexpected_mutations=False,
                output_usable=True, supervision='COMPLETED')
