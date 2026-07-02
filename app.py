import streamlit as st

# Main Title & Professional Branding
st.title("🎲 bin-go")
st.subheader("UVM Testbench Functional Coverage Generator")
st.caption("🤖 Developed by **Ashish Memane** | *Verification Engineer*")
st.write("---")

# 1. Covergroup Name configuration
cv_name = st.text_input("Covergroup Name", placeholder="e.g., register_bank")

# 2. Dynamic Slider for number of coverpoints
num_signals = st.slider("How many coverpoints do you need?", min_value=1, max_value=20, value=3)

st.write("---")
st.write("### Enter Coverpoint Details")

# Collect inputs dynamically inside a list
signals_data = []
for i in range(num_signals):
    st.write(f"#### Coverpoint {i+1}")
    
    # 5-column layout to fit the dynamic manual/auto selectors cleanly side-by-side
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1.5, 2.5, 1])
    
    with col1:
        sig_name = st.text_input(f"Signal Name", key=f"name_{i}", placeholder="e.g., current_reg")
    with col2:
        sig_width = st.number_input(f"Bit Width", min_value=1, max_value=64, value=8, key=f"width_{i}")
    
    # 💡 New Choice: Auto vs Manual Mode Selection
    with col3:
        bin_type = st.radio(f"Bin Type", ["Auto", "Manual"], key=f"type_{i}", horizontal=True)
    
    # Dynamic Column 4: Changes entirely based on the selection in Column 3!
    with col4:
        if bin_type == "Auto":
            strategy = st.selectbox(f"Auto Strategy", ["All Coverage", "Uniform with Min-Max", "Uniform without Min-Max"], key=f"strat_{i}")
            bin_count = 8  # Default default chunk count for auto uniform modes
            include_min_max = "With Min-Max" if "with Min-Max" in strategy else "Without"
        else:
            # For Manual, we draw a dynamic internal sub-layout inside Column 4!
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                bin_count = st.number_input(f"Count", min_value=1, max_value=1024, value=16, key=f"bins_{i}")
            with sub_col2:
                include_min_max = st.selectbox(f"Edges", ["With Min-Max", "Without Min-Max"], key=f"edges_{i}")
            strategy = "Manual"
            
    with col5:
        hit_count = st.number_input(f"At Least", min_value=1, max_value=10000, value=1, key=f"hit_{i}")
        
    signals_data.append({
        "name": sig_name, 
        "width": sig_width, 
        "bin_type": bin_type,
        "strategy": strategy,
        "bin_count": bin_count,
        "include_min_max": include_min_max,
        "hit_count": hit_count
    })

st.write("---")
st.write("### 🔀 Cross Coverage Configuration")

# Gather all valid signal names the user typed in
valid_signals = [sig["name"] for sig in signals_data if sig["name"]]

if len(valid_signals) < 2:
    st.info("Type at least 2 signal names above to enable cross-coverage options.")
    selected_crosses = []
else:
    selected_crosses = st.multiselect(
        "Select coverpoints to cross multiply:",
        options=valid_signals,
        default=None,
    )

st.write("---")

# 3. Code Generation Engine
if st.button("Generate SystemVerilog Code", type="primary"):
    if not cv_name:
        st.error("Please enter a Covergroup Name first!")
    else:
        sv_code = f"covergroup cg_{cv_name} @(posedge clk);\n"
        
        # Build individual coverpoints
        for sig in signals_data:
            if not sig["name"]:
                continue
                
            name = sig["name"]
            width = sig["width"]
            b_type = sig["bin_type"]
            strat = sig["strategy"]
            b_num = sig["bin_count"]
            edges = sig["include_min_max"]
            hit = sig["hit_count"]
            max_val = (2 ** width) - 1
            
            sv_code += f"  cp_{name}: coverpoint {name} {{\n"
            
            if hit > 1:
                sv_code += f"    option.at_least = {hit};\n"
            
            # --- CODE MATH LOGIC GENERATOR ---
            if b_type == "Auto" and strat == "All Coverage":
                sv_code += f"    bins all_vals[] = {{[0 : {max_val}]}};\n"
                
            elif (b_type == "Auto" and strat == "Uniform with Min-Max") or (b_type == "Manual" and edges == "With Min-Max"):
                sv_code += f"    bins min_val = {{0}};\n"
                sv_code += f"    bins max_val = {{{max_val}}};\n"
                # Avoid calculating negative bounds if max_val is tiny
                chunk_end = max_val - 1 if max_val > 1 else 1
                sv_code += f"    bins chunks[{b_num}] = {{[1 : {chunk_end}]}};\n"
                
            elif (b_type == "Auto" and strat == "Uniform without Min-Max") or (b_type == "Manual" and edges == "Without Min-Max"):
                sv_code += f"    bins chunks[{b_num}] = {{[0 : {max_val}]}};\n"
                
            sv_code += "  }\n"
        
        # Build dynamic cross-coverage block
        if len(selected_crosses) >= 2:
            sv_code += "\n  // Cross Coverage Blocks\n"
            
            total_cross_bins = 1
            has_exploded_signal = False
            
            for sig in signals_data:
                if sig["name"] in selected_crosses:
                    if sig["strategy"] == "All Coverage":
                        sig_bins = (2 ** sig["width"])
                        if sig["width"] > 4:
                            has_exploded_signal = True
                    else:
                        sig_bins = sig["bin_count"]
                    
                    total_cross_bins *= sig_bins
            
            if total_cross_bins > 1000000 or has_exploded_signal:
                sv_code += "  // ⚠️ WARNING: HIGH SIMULATION MEMORY RISK DETECTED!\n"
                sv_code += f"  // This cross statement calculates to approx. {total_cross_bins:,} total bins.\n"
                sv_code += "  // RECOMMENDATION: Switch large crossed signal bit-widths to an optimized bin strategy.\n"

            cross_id = "_X_".join(selected_crosses)
            cross_targets = ", ".join([f"cp_{sig}" for sig in selected_crosses])
            sv_code += f"  X_{cross_id}: cross {cross_targets};\n"
            
        sv_code += "endgroup"
        
        st.success("SystemVerilog Code Generated!")
        st.code(sv_code, language="systemverilog")