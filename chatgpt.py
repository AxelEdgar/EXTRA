# Create realistic datasets for CPU and GPU measurements, compute errors, and plot each equation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Create dataset
events = np.arange(1, 11)
t_pattern = np.array([0.5, 0.8, 1.2, 1.6, 2.0, 2.5, 3.0, 3.6, 4.2, 5.0])  # seconds

# Simulated CPU and GPU detection times
t_cpu = t_pattern + np.random.normal(0.05, 0.015, size=len(t_pattern))
t_gpu = t_pattern + np.random.normal(0.02, 0.008, size=len(t_pattern))

# Errors
err_abs_cpu = np.abs(t_cpu - t_pattern)
err_abs_gpu = np.abs(t_gpu - t_pattern)

err_rel_cpu = err_abs_cpu / t_pattern
err_rel_gpu = err_abs_gpu / t_pattern

err_pct_cpu = err_rel_cpu * 100
err_pct_gpu = err_rel_gpu * 100

# DataFrame
df = pd.DataFrame({
    "Evento": events,
    "t_patron_s": t_pattern,
    "t_cpu_s": t_cpu,
    "t_gpu_s": t_gpu,
    "err_abs_cpu_s": err_abs_cpu,
    "err_abs_gpu_s": err_abs_gpu,
    "err_pct_cpu": err_pct_cpu,
    "err_pct_gpu": err_pct_gpu
})

df
# Plot 1: Pattern vs CPU vs GPU
plt.figure()
plt.plot(events, t_pattern, label="Patron")
plt.plot(events, t_cpu, label="CPU")
plt.plot(events, t_gpu, label="GPU")
plt.xlabel("Evento")
plt.ylabel("Tiempo (s)")
plt.legend()
plt.show()

# Plot 2: Absolute Error CPU
plt.figure()
plt.plot(events, err_abs_cpu)
plt.xlabel("Evento")
plt.ylabel("Error Absoluto CPU (s)")
plt.show()

# Plot 3: Absolute Error GPU
plt.figure()
plt.plot(events, err_abs_gpu)
plt.xlabel("Evento")
plt.ylabel("Error Absoluto GPU (s)")
plt.show()

# Plot 4: Percentage Error CPU
plt.figure()
plt.plot(events, err_pct_cpu)
plt.xlabel("Evento")
plt.ylabel("Error Porcentual CPU (%)")
plt.show()

# Plot 5: Percentage Error GPU
plt.figure()
plt.plot(events, err_pct_gpu)
plt.xlabel("Evento")
plt.ylabel("Error Porcentual GPU (%)")
plt.show()
