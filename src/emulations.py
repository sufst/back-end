import math
import random

__x = 0


def get_next_emulation():
    global __x
    
    next_emulation = {
        "rpm": int(5000 * math.sin(math.radians(__x * 10)) + 5000),
        "water_temp_c": random.randint(80, 100),
        "tps_perc": int(50*math.sin(math.radians(__x*10))+50),
        "battery_mv": random.randint(11900, 12100),
        "ext_5v_mv": random.randint(4900, 5100),
        "fuel_flow": int(25 * math.sin(math.radians(__x * 10)) + 25),
        "lambda": int(25 * math.sin(math.radians(__x * 10)) + 50),
        "speed_kph": int(150 * math.sin(math.radians(__x * 10)) + 150),
        "evo_scan_1": int(10 * math.sin(math.radians(__x * 10)) + 10),
        "evo_scan_2": int(15 * math.sin(math.radians(__x * 10)) + 15),
        "evo_scan_3": int(15 * math.sin(math.radians(__x * 10)) + 20),     
        "evo_scan_4": int(15 * math.sin(math.radians(__x * 10)) + 25),    
        "evo_scan_5": int(15 * math.sin(math.radians(__x * 10)) + 30),    
        "evo_scan_6": int(15 * math.sin(math.radians(__x * 10)) + 35),      
        "evo_scan_7": int(15 * math.sin(math.radians(__x * 10)) + 40),    
        "status_ecu_connected": 1,
        "status_engine": 1,
        "status_battery": 2, 
        "status_logging": 1,
        "inj_time": random.randint(6, 10),
        "inj_duty_cycle": random.randint(70, 80),
        "lambda_pid_adj": random.randint(10, 20),
        "lambda_pid_target": random.randint(95, 105),
        "advance": random.randint(0, 5),
        "ride_height_fl_cm": int(5 * math.cos(math.radians(__x * 15)) + 8),
        "ride_height_fr_cm": int(5 * math.sin(math.radians(__x * 15)) + 8),
        "ride_height_flw_cm": int(5 * math.cos(math.radians(__x * 5)) + 8),
        "ride_height_rear_cm": int(5 * math.sin(math.radians(__x * 5)) + 8),
        "lap_time_s": __x,
        "accel_fl_x_mg": int(500 * math.sin(math.radians(__x * 10 + 1)) + 1000),
        "accel_fl_y_mg": int(500 * math.sin(math.radians(__x * 10 + 0.5)) + 1000),
        "accel_fl_z_mg": int(500 * math.sin(math.radians(__x * 10)) + 1000) 
    }

    __x += 1
    
    return next_emulation
