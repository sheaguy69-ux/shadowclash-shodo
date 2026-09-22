#!/usr/bin/env python3
"""Regression check for subset coverage assertions and the removed Form-1 vanish."""
from copy import deepcopy
from audit_move_coverage import assert_measured, BTN, DIRS, ORDER


def main():
    row = dict(box='light', proj=0, state='ATTACK_SPECIAL', touched=[], err=None)
    matrix = {name: {f'{st}.{d}.{b}': dict(row) for st in ('gnd', 'air')
                     for d in DIRS for b in BTN} for name in ORDER}
    for rows in matrix.values():
        rows['gnd.neutral.M']['box'] = 'medium'
    matrix['Shin']['gnd.down.S']['proj'] = 1
    matrix['Kael']['gnd.back.H']['touched'] = ['parryFlashTimer']
    for name in ('Kael', 'Ember'):
        matrix[name]['gnd.back.S']['state'] = 'PARRY_STANCE'
    # No vanishTimer: the current first-form kit must reach the Medium check anyway.
    assert_measured(matrix, range(9))
    for i, name in enumerate(ORDER):
        assert_measured({name: matrix[name]}, [i])
    bad = []
    partial = {'Executioner': deepcopy(matrix['Executioner'])}
    partial['Executioner'].pop('air.up.M')
    bad.append(partial)
    partial = {'Executioner': deepcopy(matrix['Executioner'])}
    partial['Executioner']['air.down.H']['err'] = 'broken route'
    bad.append(partial)
    partial = {'Executioner': deepcopy(matrix['Executioner'])}
    partial['Executioner']['gnd.neutral.M']['box'] = 'light'
    bad.append(partial)
    bad.append({'Executioner': matrix['Executioner'], 'Shin': matrix['Shin']})
    for malformed in bad:
        try:
            assert_measured(malformed, [0])
        except AssertionError:
            pass
        else:
            raise AssertionError('subset accepted missing/error/Medium/foreign data')
    print('PASS: full roster, 9 subsets, 4 malformed subsets; no obsolete vanish required')


if __name__ == '__main__':
    main()
