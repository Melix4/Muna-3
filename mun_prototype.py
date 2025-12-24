import math
import time
import csv
import krpc

data = []
def log_ascent():
    t = conn.space_center.ut - t0

    if t > 85:
        return
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.radius
    g = mu / (r * r)

    data.append((
        t,
        vessel.mass,
        flight.mean_altitude,
        flight.speed,
        flight.vertical_speed,
        g,
        vessel.available_thrust,
        vessel.specific_impulse
    ))

def engines_flameout():
    for eng in vessel.parts.engines:
        if eng.active and not eng.has_fuel:
            return True
    return False

def mun_manuever_node(forward, flag):
    step = 1
    temp_node = vessel.control.add_node(conn.space_center.ut + forward, prograde=860)
    ut = None
    best_pe_error = 10**6
    target_pe = 40000
    for i in range(1500//step):
        temp_node.ut += step

        mun_orbit = temp_node.orbit.next_orbit
        if not mun_orbit:
            continue
        if not mun_orbit or mun_orbit.body.name != 'Mun':
            continue
        post_orbit = mun_orbit.next_orbit
        if not post_orbit or post_orbit.body.name != 'Kerbin':
            continue
        if mun_orbit.time_to_soi_change >= temp_node.orbit.time_to_apoapsis:
            continue
        if (not flag and post_orbit.periapsis_altitude > 3000000) or post_orbit.eccentricity >= 1:
            continue
        pre_ap = temp_node.orbit.apoapsis_altitude
        post_ap = post_orbit.apoapsis_altitude
        if post_ap >= pre_ap:
            continue
        if mun_orbit.body.name == 'Mun':
            pe = mun_orbit.periapsis_altitude
            if not flag:
                if pe < 10000 or pe > 300000:
                    continue
            error = abs(target_pe - pe)
            if error < best_pe_error:
                best_pe_error = error
                ut = temp_node.ut
    temp_node.remove()
    return ut


conn = krpc.connect(name="Mun Flyby")
vessel = conn.space_center.active_vessel

ascent = True
stage1 = False
to_the_mun = False
vessel.control.throttle = 1
time.sleep(1)
vessel.control.activate_next_stage()
time.sleep(0.5)

flight = vessel.flight()

t0 = conn.space_center.ut
ap = vessel.auto_pilot
ap.engage()
while ascent:
    log_ascent()

    alt = flight.mean_altitude
    if not stage1:
        if engines_flameout():
            vessel.control.activate_next_stage()
            stage1 = True
        ap.target_pitch_and_heading(85, 90)
    if stage1:
        target_pitch = max(45, 90 - alt / 300)
        ap.target_pitch_and_heading(target_pitch, 90)
        if alt < 12000:
            vessel.control.throttle = 1.0
        else:
            vessel.control.throttle = 0.7

    if vessel.orbit.apoapsis_altitude > 80000:
        vessel.control.throttle = 0.0
        ascent = False

with open('ascent_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        't', 'mass', 'altitude', 'speed',
        'vertical_speed', 'gravity', 'thrust', 'isp'
    ])
    writer.writerows(data)

# Plan circularization burn (using vis-viva equation)
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = vessel.control.add_node(
    conn.space_center.ut + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Orientate ship
print('Orientating ship for circularization burn')

ap.disengage()
vessel.control.sas = True
vessel.control.sas_mode = conn.space_center.SASMode.prograde

# Execute burn
while vessel.orbit.time_to_apoapsis - (burn_time/2.) > 0:
    pass
vessel.control.throttle = 1.0
time.sleep(burn_time - 0.1)
vessel.control.throttle = 0.0
node.remove()
to_the_mun = True


mun = conn.space_center.bodies['Mun']
best_ut = None
fwd = 30
c = 0
while best_ut is None:
    if fwd > 5:
        best_ut = mun_manuever_node(fwd, False)
        fwd -= 5
    else:
        best_ut = mun_manuever_node(fwd, True)
    if c > 12:
        best_ut = conn.space_center.ut + 180
node = vessel.control.add_node(best_ut, prograde=860)


# Calculate burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(860 / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

lead_time = 30

burn_start_ut = node.ut - burn_time / 2
conn.space_center.warp_to(burn_start_ut - lead_time)
# Execute burn
while (node.ut - conn.space_center.ut) - (burn_time/2.) > 0:
    pass
vessel.control.throttle = 1
time.sleep(burn_time - 0.05)
vessel.control.throttle = 0.0
node.remove()
