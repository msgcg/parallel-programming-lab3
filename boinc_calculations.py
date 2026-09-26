#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расчет ресурсных затрат, сетевого трафика и очков BOINC Credit
для лабораторной работы №3 по параллельному программированию.
"""

def calculate_boinc_metrics():
    # Параметры хоста
    cpu_cores = 12
    cpu_gflops_per_core = 21.4 # эффективная производительность ядра
    duration_hours = 8.0
    
    # Сетевой трафик (24 блока по 12.5 МБ входных, 1.2 МБ выходных)
    wu_count = 24
    inbound_mb = wu_count * 12.5
    outbound_mb = wu_count * 1.2
    
    # Очки Cobblestone (базовая ставка: 1 GFLOPS = 4.167 очков/час)
    base_rate = 100.0 / 24.0
    credit_rate_per_core_hour = base_rate * cpu_gflops_per_core
    total_credits = cpu_cores * duration_hours * credit_rate_per_core_hour
    
    # Суммарная вычислительная работа в операциях FLOP
    total_flops = cpu_cores * (duration_hours * 3600) * (cpu_gflops_per_core * 1e9)
    
    print(f"Входящий трафик: {inbound_mb:.2f} МБ")
    print(f"Исходящий трафик: {outbound_mb:.2f} МБ")
    print(f"Очки на 1 ядро за 1 час: {credit_rate_per_core_hour:.2f} очков")
    print(f"Суммарные очки ({duration_hours} ч, {cpu_cores} ядер): {total_credits:.2f} очков")
    print(f"Общий объем вычислений: {total_flops:.2e} FLOP ({total_flops / 1e15:.2f} PFLOPs)")

if __name__ == "__main__":
    calculate_boinc_metrics()
