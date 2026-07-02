# 🎲 bin-go: UVM Testbench Functional Coverage Generator

**bin-go** is an intelligent, full-stack Python web utility designed to accelerate testbench assembly for ASIC Verification Engineers. It automates the generation of tedious SystemVerilog `covergroup` boilerplate code while introducing structural safety analysis to prevent simulation regression bottlenecks.

🚀 **Live Web App:** [PASTE YOUR STREAMLIT APP URL HERE]

---

## ✨ Features

- 🎛️ **Dynamic Scaling:** Effortlessly configure up to 20 distinct coverpoints on a highly reactive, user-friendly UI.
- 📊 **Flexible Binning Strategies:** Toggle seamlessly between **Auto-All** coverage, uniform **Chunks**, or completely tailored **Manual** edge-binning intervals (with or without min-max boundaries).
- 🔢 **Custom Hit Targets:** Explicitly declare `option.at_least` hit count thresholds per individual coverpoint.
- ⚠️ **Simulation Safety Guard:** Built-in static analysis engine dynamically calculates cross-product combinations, automatically injecting optimization alerts if a cross-matrix creates dangerous memory explosion risks.

---

## 💻 Generated Code Example

```systemverilog
covergroup cg_mem_cover @(posedge clk);
  cp_rd_addr: coverpoint rd_addr {
    option.at_least = 2;
    bins chunks[40] = {[0 : 65535]};
  }
  cp_write_read: coverpoint write_read {
    bins all_vals[] = {[0 : 1]};
  }

  // Cross Coverage Blocks
  X_write_read_X_rd_addr: cross cp_write_read, cp_rd_addr;
endgroup
