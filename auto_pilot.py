import math
import time
import csv
import krpc

def engines_flameout():
    for eng in vessel.parts.engines:
        if eng.active and not eng.has_fuel:
            return True
    return False

conn = krpc.connect(name="Mun Flyby")
vessel = conn.space_center.active_vessel

ascent = True
stage1 = False
to_the_mun = False
vessel.control.throttle = 1
time.sleep(1)
vessel.control.activate_next_stage()
t0 = conn.space_center.ut
time.sleep(0.5)

flight = vessel.flight(vessel.orbit.body.reference_frame)

altitude = conn.add_stream(getattr, flight, 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
mass = conn.add_stream(getattr, vessel, 'mass')
speed = conn.add_stream(getattr, flight, 'speed')
vspeed = conn.add_stream(getattr, flight, 'vertical_speed')
resources = conn.add_stream(getattr, vessel, 'resources')
ut = conn.add_stream(getattr, conn.space_center, 'ut')

csv_file = open('telemetry.csv', 'w', newline='')
writer = csv.writer(csv_file)

writer.writerow([
    't',
    'altitude_m',
    'apoapsis_m',
    'speed_m_s',
    'vertical_speed_m_s',
    'mass_kg',
    'throttle'
])
ap = vessel.auto_pilot
ap.engage()
while ascent:
    writer.writerow([
        ut()-t0,
        altitude(),
        apoapsis(),
        speed(),
        vspeed(),
        mass(),
        vessel.control.throttle
    ])
    csv_file.flush()
    alt = flight.mean_altitude
    if not stage1:
        if engines_flameout():
            vessel.control.activate_next_stage()
            stage1 = True
        ap.target_pitch_and_heading(90, 90)
    else:
        ap.target_pitch_and_heading(45, 90)
        if vessel.orbit.apoapsis_altitude > 80000:
            vessel.control.throttle = 0.0
            ascent = False


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

ap.disengage()
vessel.control.sas = True
vessel.control.sas_mode = conn.space_center.SASMode.prograde

# Execute burn
while vessel.orbit.time_to_apoapsis - (burn_time/2.) > 0:
    writer.writerow([
        ut()-t0,
        altitude(),
        apoapsis(),
        speed(),
        vspeed(),
        mass(),
        vessel.control.throttle
    ])
    time.sleep(0.05)

vessel.control.throttle = 1.0
burn_start = ut()

while ut() - burn_start < burn_time:
    writer.writerow([
        ut()-t0,
        altitude(),
        apoapsis(),
        speed(),
        vspeed(),
        mass(),
        vessel.control.throttle
    ])
    time.sleep(0.05)
vessel.control.throttle = 0.0
node.remove()

to_the_mun = True
