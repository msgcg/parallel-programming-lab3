import os
import sys
import subprocess
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BOINC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boinc")
BIN_DIR = os.path.join(BOINC_DIR, "bin")
DATA_DIR = os.path.join(BOINC_DIR, "data")
BOINC_EXE = os.path.join(BIN_DIR, "boinc.exe")
BOINCCMD_EXE = os.path.join(BIN_DIR, "boinccmd.exe")
STATE_XML = os.path.join(DATA_DIR, "client_state.xml")
AUTH_CFG = os.path.join(DATA_DIR, "gui_rpc_auth.cfg")

def get_rpc_password():
    if os.path.exists(AUTH_CFG):
        with open(AUTH_CFG, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def load_hardware_telemetry():
    telemetry = {
        "computer_name": "MSIZ690Pro",
        "cpu_model": "12th Gen Intel(R) Core(TM) i5-12600KF",
        "num_cpus": 16,
        "fp_mips": 7921.0,
        "int_mips": 26104.0,
        "ram_gb": 31.86,
        "disk_total_gb": 953.87,
        "disk_free_gb": 212.86,
        "gpu_name": "NVIDIA GeForce RTX 3050",
        "gpu_vram_gb": 8.0,
        "gpu_peak_gflops": 9098.0,
        "os_name": "Microsoft Windows 11 Professional x64"
    }

    if os.path.exists(STATE_XML):
        try:
            tree = ET.parse(STATE_XML)
            root = tree.getroot()
            host_info = root.find("host_info")
            if host_info is not None:
                d_name = host_info.findtext("domain_name")
                if d_name: telemetry["computer_name"] = d_name
                p_model = host_info.findtext("p_model")
                if p_model: telemetry["cpu_model"] = p_model
                ncpus = host_info.findtext("p_ncpus")
                if ncpus: telemetry["num_cpus"] = int(ncpus)
                fpops = host_info.findtext("p_fpops")
                if fpops: telemetry["fp_mips"] = float(fpops) / 1e6
                iops = host_info.findtext("p_iops")
                if iops: telemetry["int_mips"] = float(iops) / 1e6
                m_bytes = host_info.findtext("m_nbytes")
                if m_bytes: telemetry["ram_gb"] = round(float(m_bytes) / (1024**3), 2)
                d_total = host_info.findtext("d_total")
                if d_total: telemetry["disk_total_gb"] = round(float(d_total) / (1024**3), 2)
                d_free = host_info.findtext("d_free")
                if d_free: telemetry["disk_free_gb"] = round(float(d_free) / (1024**3), 2)
                os_name = host_info.findtext("os_name")
                os_ver = host_info.findtext("os_version")
                if os_name: telemetry["os_name"] = f"{os_name} {os_ver}"
        except Exception:
            pass

    return telemetry

def calculate_metrics(telemetry):
    cpu_gflops = telemetry["fp_mips"] / 1000.0
    num_cpus = telemetry["num_cpus"]

    credits_per_core_hour = (100.0 / 24.0) * cpu_gflops

    project_name = "Einstein@Home (Поиск гравитационных волн и радиопульсаров)"
    task_count = 24
    input_mb_per_task = 12.5
    output_mb_per_task = 1.2
    task_flops = 2.5e13

    total_in_traffic_mb = task_count * input_mb_per_task
    total_out_traffic_mb = task_count * output_mb_per_task

    efficiency = 0.85
    effective_core_gflops = cpu_gflops * efficiency
    task_seconds = task_flops / (effective_core_gflops * 1e9)
    task_minutes = task_seconds / 60.0

    boinc_daemon_ram_mb = 28.5
    slot_ram_mb = 210.0
    total_ram_mb = boinc_daemon_ram_mb + (num_cpus * slot_ram_mb)

    project_binaries_disk_mb = 145.0
    slots_temp_disk_mb = num_cpus * 35.0
    total_disk_used_mb = project_binaries_disk_mb + slots_temp_disk_mb

    session_hours = 8.0
    total_session_credits = num_cpus * session_hours * credits_per_core_hour
    total_user_flops = num_cpus * (session_hours * 3600.0) * (cpu_gflops * 1e9)
    total_user_pflops = total_user_flops / 1e15

    return {
        "project_name": project_name,
        "cpu_gflops": cpu_gflops,
        "credits_per_core_hour": credits_per_core_hour,
        "task_count": task_count,
        "total_in_traffic_mb": total_in_traffic_mb,
        "total_out_traffic_mb": total_out_traffic_mb,
        "task_seconds": task_seconds,
        "task_minutes": task_minutes,
        "total_ram_mb": total_ram_mb,
        "total_disk_used_mb": total_disk_used_mb,
        "session_hours": session_hours,
        "total_session_credits": total_session_credits,
        "total_user_flops": total_user_flops,
        "total_user_pflops": total_user_pflops
    }

def print_report(t, m):
    print("=" * 80)
    print("  РАСЧЕТ ХАРАКТЕРИСТИК ГРИД-СИСТЕМЫ BOINC НА РЕАЛЬНОМ АППАРАТНОМ УЗЛЕ")
    print("=" * 80)
    print(f"  Вычислительный узел: {t['computer_name']}")
    print(f"  Процессор:           {t['cpu_model']} ({t['num_cpus']} логических ядер)")
    print(f"  Оперативная память:  {t['ram_gb']} ГБ физической памяти")
    print(f"  Накопитель:          {t['disk_total_gb']} ГБ всего, {t['disk_free_gb']} ГБ свободно")
    print(f"  Видеокарта (GPU):    {t['gpu_name']} ({t['gpu_vram_gb']} ГБ VRAM, {t['gpu_peak_gflops']} GFLOPS peak)")
    print(f"  Операционная система:{t['os_name']}")
    print("-" * 80)
    print("  АППАРАТНЫЕ ТЕСТЫ BOINC (DHRYSTONE & WHETSTONE):")
    print(f"    Whetstone FP OPS:  {t['fp_mips']:.2f} MIPS ({m['cpu_gflops']:.3f} GFLOPS на ядро)")
    print(f"    Dhrystone INT OPS: {t['int_mips']:.2f} MIPS на ядро")
    print("=" * 80)
    print(f"  ЦЕЛЕВОЙ НАУЧНЫЙ ПРОЕКТ: {m['project_name']}")
    print("-" * 80)
    print("  1. СЕТЕВОЙ ТРАФИК:")
    print(f"     Объем входного пакета задачи:      12.50 МБ")
    print(f"     Объем выходного пакета результата: 1.20 МБ")
    print(f"     Количество расчетных заданий (WU): {m['task_count']} шт.")
    print(f"     Суммарный входящий трафик:         {m['total_in_traffic_mb']:.1f} МБ")
    print(f"     Суммарный исходящий трафик:        {m['total_out_traffic_mb']:.1f} МБ")
    print(f"     Общий объем сетевого трафика:      {m['total_in_traffic_mb'] + m['total_out_traffic_mb']:.1f} МБ")
    print("-" * 80)
    print("  2. ВРЕМЯ ВЫЧИСЛЕНИЯ И ЗАТРАТЫ СИСТЕМНЫХ РЕСУРСОВ:")
    print(f"     Сложность расчетного блока (WU):   25.0 TFLOP")
    print(f"     Среднее время расчета 1 блока:     {m['task_seconds']:.0f} сек ({m['task_minutes']:.1f} мин)")
    print(f"     Затраты оперативной памяти:        {m['total_ram_mb']:.1f} МБ (демон + {t['num_cpus']} слотов)")
    print(f"     Затраты дискового пространства:    {m['total_disk_used_mb']:.1f} МБ (бинарники и буфер слотов)")
    print("-" * 80)
    print("  3. ОЧКИ (COBBLESTONES) И ОБЪЕМ ВЫЧИСЛЕНИЙ ПОЛЬЗОВАТЕЛЯ:")
    print(f"     Формула Cobblestone:               (GFLOPS * 3600 * 100) / 86400")
    print(f"     Средний объем очков на 1 ядро/час: {m['credits_per_core_hour']:.2f} очков/(ядро*час)")
    print(f"     Время непрерывного сеанса:         {m['session_hours']:.1f} часов")
    print(f"     Суммарно начислено очков:          {m['total_session_credits']:.2f} Cobblestones")
    print(f"     Суммарный объем вычислений:        {m['total_user_pflops']:.3f} PFLOP ({m['total_user_flops']:.2e} FLOP)")
    print("=" * 80)

def main():
    telemetry = load_hardware_telemetry()
    metrics = calculate_metrics(telemetry)
    print_report(telemetry, metrics)

if __name__ == "__main__":
    main()
