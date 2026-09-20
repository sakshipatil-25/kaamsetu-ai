import matplotlib.pyplot as plt
import numpy as np

# Data from your experiments
setups = ['Centralized\n(1 worker)', 'Static Distributed\n(3 workers)', 'Adaptive Distributed\n(3 workers)']

# Latency data (ms)
avg_latency = [21.10, 23.71, 24.65]
max_latency = [40.0, 123.18, 119.13]

# CPU data (%)
avg_cpu = [100.0, 501.05, 411.53]
max_cpu = [100.0, 945.80, 767.80]

# Load imbalance (%)
imbalance = [0, 3.2, 4.1]

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Latency comparison
x = np.arange(len(setups))
width = 0.35
axes[0].bar(x - width/2, avg_latency, width, label='Avg Latency', color='steelblue')
axes[0].bar(x + width/2, max_latency, width, label='Max Latency', color='coral')
axes[0].set_ylabel('Latency (ms)')
axes[0].set_title('Latency Comparison')
axes[0].set_xticks(x)
axes[0].set_xticklabels(setups)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)

# Plot 2: CPU comparison
axes[1].bar(x - width/2, avg_cpu, width, label='Avg CPU', color='mediumseagreen')
axes[1].bar(x + width/2, max_cpu, width, label='Max CPU', color='orange')
axes[1].set_ylabel('CPU Usage (%)')
axes[1].set_title('CPU Utilization')
axes[1].set_xticks(x)
axes[1].set_xticklabels(setups)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

# Plot 3: Load imbalance
axes[2].bar(setups, imbalance, color=['gray', 'salmon', 'gold'])
axes[2].set_ylabel('Load Imbalance (%)')
axes[2].set_title('Load Imbalance Across Workers')
axes[2].grid(axis='y', alpha=0.3)
for i, v in enumerate(imbalance):
    axes[2].text(i, v + 0.1, f'{v}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('results/comparison_plots.png', dpi=150, bbox_inches='tight')
print("Saved comparison_plots.png to results/")
plt.show()