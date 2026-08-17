import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
warnings.filterwarnings('ignore')


class TransformerAnalyzer:
    def __init__(self):
        # Transformer config
        self.summer_data = None
        self.winter_data = None
        self.festival_data = None

        # Raw transformer A,B,C data (per season)
        self.trans_a = {}
        self.trans_b = {}
        self.trans_c = {}

        self.TRANSFORMER_KVA = 200
        self.PF = 0.8
        self.capacity_kW = self.TRANSFORMER_KVA * self.PF
        self.nominal_voltage = 230
        self.voltage_tolerance = 0.05
        self.vuf_threshold = 2.0
        self.cuf_threshold = 10.0

        # Setup GUI
        self.setup_gui()

    # ---------------- GUI ----------------
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Transformer Data Analyzer")
        self.root.geometry("1400x900")

        # Section 2: Transformer Files (New workflow)
        t_frame = ttk.LabelFrame(self.root, text="Transformer Raw Data (A,B,C per Season)", padding=10)
        t_frame.pack(fill=tk.X, pady=(0, 10))

        # Status labels make it immediately clear whether A/B/C data were loaded
        # and whether a merged load dataset was created for each season.
        self.season_status = {}

        # Create a separate frame for each season's buttons
        for season in ["summer", "winter", "festival"]:
            season_frame = ttk.Frame(t_frame)
            season_frame.pack(fill=tk.X, pady=2)

            ttk.Label(season_frame, text=f"{season.capitalize()}:", width=10).pack(side=tk.LEFT, padx=5)
            status = ttk.Label(season_frame, text="A ✗  B ✗  C ✗  | Data: ✗", foreground="#aa0000")
            status.pack(side=tk.RIGHT, padx=10)
            self.season_status[season] = status

            ttk.Button(season_frame, text="Load Transformer A",
                       command=lambda s=season: self.load_transformer_file(s, 'A')).pack(side=tk.LEFT, padx=5)
            ttk.Button(season_frame, text="Load Transformer B",
                       command=lambda s=season: self.load_transformer_file(s, 'B')).pack(side=tk.LEFT, padx=5)
            ttk.Button(season_frame, text="Load Transformer C",
                       command=lambda s=season: self.load_transformer_file(s, 'C')).pack(side=tk.LEFT, padx=5)

        # Analysis frame
        analysis_frame = ttk.LabelFrame(self.root, text="Analysis Options", padding=10)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))

        # Row 1: Original analyses
        row1_frame = ttk.Frame(analysis_frame)
        row1_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(row1_frame, text="📊 Peak/Off-Peak Analysis",
                   command=self.peak_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="📈 Voltage Analysis",
                   command=self.voltage_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="⚡ Energy Consumption",
                   command=self.energy_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="📅 Daily Load Profiles",
                   command=self.load_curves).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="📈 Active Power Curve", 
                   command=self.power_vs_time_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="📈 Reactive Power Curve", 
                   command=self.reactive_power_vs_time_graph).pack(side=tk.LEFT, padx=5)


        # Row 2: Unbalance analyses
        row2_frame = ttk.Frame(analysis_frame)
        row2_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(row2_frame, text="📊 VUF/CUF Charts",
                   command=self.unbalance_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="📈 Unbalance Trends",
                   command=self.unbalance_trends).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="📋 Generate Full PDF Report",
                   command=self.generate_full_report).pack(side=tk.LEFT, padx=5)

        # Row 3: Hourly-averaged distribution analyses
        row3_frame = ttk.Frame(analysis_frame)
        row3_frame.pack(fill=tk.X, pady=2)

        ttk.Button(row3_frame, text="📊 Hourly Avg Active Power Distribution",
                   command=self.hourly_avg_active_power_distribution).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="📊 Hourly Avg VUF Distribution",
                   command=self.hourly_avg_vuf_distribution).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="📊 Hourly Avg CUF Distribution",
                   command=self.hourly_avg_cuf_distribution).pack(side=tk.LEFT, padx=5)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Text report tab
        self.text_tab = ttk.Frame(self.notebook)
        self.text_area = tk.Text(self.text_tab, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.text_tab, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(self.text_tab, text="Text Report")

        # Chart tab
        self.chart_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_tab, text="Charts")

    # ---------------- Data Loading ----------------
    def load_season_data(self, dtype):
        """Load old-style seasonal load data"""
        file_path = filedialog.askopenfilename(
            title=f"Select {dtype.capitalize()} Data File",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")]
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith('.csv'):
                data = pd.read_csv(file_path)
            else:
                data = pd.read_excel(file_path)

            data = self.preprocess(data)

            if dtype == 'summer':
                self.summer_data = data
                self.summer_status.config(text="Summer: Loaded ✓", foreground="green")
            elif dtype == 'winter':
                self.winter_data = data
                self.winter_status.config(text="Winter: Loaded ✓", foreground="green")
            else:
                self.festival_data = data
                self.festival_status.config(text="Festival: Loaded ✓", foreground="green")

            messagebox.showinfo("Success", f"{dtype.capitalize()} data loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def load_transformer_file(self, season, tname):
        """Load raw transformer A,B,C files"""
        file_path = filedialog.askopenfilename(
            title=f"Select {season.capitalize()} Transformer {tname} File",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx;*.xls")]
        )
        if not file_path:
            return
        try:
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            # Validate/prepare the file here so an unsupported column layout
            # produces a clear message instead of silently causing 'No Data'.
            prepared = self._prepare_phase_data(df, tname)
            if prepared is None or prepared.empty:
                raise ValueError(
                    'No valid Time/Voltage/Current data found in this file. '
                    f'Found columns: {list(df.columns)}'
                )

            # IMPORTANT: store the cleaned/normalized phase dataframe, not the
            # original dataframe. This guarantees every downstream analysis sees
            # the same DateTime / Voltage_X / Current_X columns.
            if season not in self.trans_a:
                self.trans_a[season] = None
                self.trans_b[season] = None
                self.trans_c[season] = None
            if tname == 'A':
                self.trans_a[season] = prepared
            elif tname == 'B':
                self.trans_b[season] = prepared
            else:
                self.trans_c[season] = prepared

            # Refresh the seasonal load dataset whenever transformer files are loaded.
            # This keeps the original load-based analyses (Peak/Off-Peak, Energy,
            # Daily Load Profiles, Active Power Curve, Reactive Power Curve, and
            # Hourly Avg Active Power Distribution) compatible with the new
            # Transformer A/B/C loading workflow.
            self.update_seasonal_load_data(season)
            self.update_season_status(season)

            messagebox.showinfo("Success", f"{season.capitalize()} Transformer {tname} data loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")

    def update_season_status(self, season):
        a_ok = self.trans_a.get(season) is not None
        b_ok = self.trans_b.get(season) is not None
        c_ok = self.trans_c.get(season) is not None
        data_ok = self._get_cached_or_built_load_data(season)
        text = f"A {'✓' if a_ok else '✗'}  B {'✓' if b_ok else '✗'}  C {'✓' if c_ok else '✗'}  | Data: {'✓' if data_ok else '✗'}"
        self.season_status[season].configure(
            text=text, foreground=("#008000" if data_ok else "#aa0000")
        )

    def _get_cached_or_built_load_data(self, season):
        df = {'summer': self.summer_data, 'winter': self.winter_data, 'festival': self.festival_data}.get(season)
        return df is not None and not df.empty and 'Load_kW' in df.columns

    def update_seasonal_load_data(self, season):
        """Build/update seasonal load data from the loaded A/B/C phase files."""
        merged = self.get_merged_unbalance_data(season)
        if merged is None or merged.empty:
            return False
        df = merged.copy()
        target = {'summer':'summer_data','winter':'winter_data','festival':'festival_data'}[season]
        setattr(self, target, df)
        return True

    def preprocess(self, df):
        # Handle Time column
        if 'Time' in df.columns:
            df['DateTime'] = pd.to_datetime(df['Time'])
        elif 'DateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['DateTime'])
        else:
            raise ValueError("Missing 'Time' or 'DateTime' column!")

        # If Load_kW is missing, try to compute it from other available columns
        if 'Load_kW' not in df.columns:
            if 'Power' in df.columns:
                df['Load_kW'] = df['Power'] / 1000.0  # Assume power is in W
            elif all(c in df.columns for c in ['Main_Transformer_a', 'Main_Transformer_b', 'Main_Transformer_c']):
                df['Load_kW'] = df['Main_Transformer_a'] + df['Main_Transformer_b'] + df['Main_Transformer_c']
            else:
                raise ValueError("No 'Load_kW', 'Power', or transformer phase columns found!")

        # Add extra time-based columns
        df['Date'] = df['DateTime'].dt.date
        df['Hour'] = df['DateTime'].dt.hour
        df['Weekday'] = df['DateTime'].dt.weekday
        df['DayType'] = np.where(df['Weekday'] < 5, 'Weekday', 'Weekend')
        return df

    # ---------------- Helper functions ----------------
    def calculate_vuf(self, r, y, b):
        avg = (r + y + b) / 3
        if avg == 0: return 0
        return (max(abs(r - avg), abs(y - avg), abs(b - avg)) / avg) * 100

    def calculate_cuf(self, r, y, b):
        avg = (r + y + b) / 3
        if avg == 0: return 0
        return (max(abs(r - avg), abs(y - avg), abs(b - avg)) / avg) * 100

    def display_report(self, txt):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, txt)
        self.notebook.select(self.text_tab)

    def display_chart(self, fig):
        for widget in self.chart_tab.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, self.chart_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.notebook.select(self.chart_tab)

    def save_figure_as_jpg(self, fig, default_name="chart_output.jpg"):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            initialfile=default_name,
            filetypes=[("JPEG Files", "*.jpg")]
        )
        if save_path:
            fig.savefig(save_path, dpi=300, format='jpg')
            messagebox.showinfo("Image Saved", f"Chart saved as {save_path}")
            return save_path
        return None

    def _prepare_phase_data(self, data, phase_name):
        """Normalize one phase file to DateTime, Voltage_<phase>, Current_<phase>."""
        if data is None or data.empty:
            return None
        df = data.copy()
        df.columns = [str(c).strip() for c in df.columns]
        import re

        def norm(col):
            return re.sub(r'[^a-z0-9]+', '', str(col).lower())

        normalized = {norm(c): c for c in df.columns}

        def find_col(exact, contains=()):
            for c in exact:
                if norm(c) in normalized:
                    return normalized[norm(c)]
            for k, original in normalized.items():
                if any(term in k for term in contains):
                    return original
            return None

        time_col = find_col(
            ['Time','DateTime','Datetime','Timestamp','TimeStamp','Date'],
            ('datetime','timestamp','time')
        )
        voltage_col = find_col(
            ['Voltage','VoltageV','V','Vrms','RMSVoltage','VoltageRMS'],
            ('voltage','vrms')
        )
        current_col = find_col(
            ['Current','CurrentA','I','Irms','RMSCurrent','CurrentRMS'],
            ('current','irms')
        )

        if time_col is None or voltage_col is None or current_col is None:
            return None

        out = pd.DataFrame({
            'DateTime': pd.to_datetime(df[time_col], errors='coerce'),
            f'Voltage_{phase_name}': pd.to_numeric(df[voltage_col], errors='coerce'),
            f'Current_{phase_name}': pd.to_numeric(df[current_col], errors='coerce')
        })
        out = out.dropna().sort_values('DateTime').reset_index(drop=True)
        return None if out.empty else out

    def get_merged_unbalance_data(self, season):
        """Return a reliable A/B/C dataset for a season."""
        A = self.trans_a.get(season)
        B = self.trans_b.get(season)
        C = self.trans_c.get(season)
        if A is None or B is None or C is None:
            return None

        a = self._prepare_phase_data(A, 'A')
        b = self._prepare_phase_data(B, 'B')
        c = self._prepare_phase_data(C, 'C')
        if any(x is None or x.empty for x in (a,b,c)):
            return None

        # First preference: row-by-row pairing when files are synchronized
        # exports. This is deterministic and avoids timestamp-format issues.
        if len(a) == len(b) == len(c):
            merged = pd.DataFrame({
                'DateTime': a['DateTime'].to_numpy(),
                'Voltage_A': a['Voltage_A'].to_numpy(), 'Current_A': a['Current_A'].to_numpy(),
                'Voltage_B': b['Voltage_B'].to_numpy(), 'Current_B': b['Current_B'].to_numpy(),
                'Voltage_C': c['Voltage_C'].to_numpy(), 'Current_C': c['Current_C'].to_numpy(),
            })
        else:
            # Otherwise use nearest timestamp matching with a generous 1-hour
            # window for independently exported phase files.
            merged = pd.merge_asof(
                a.sort_values('DateTime'), b.sort_values('DateTime'),
                on='DateTime', direction='nearest', tolerance=pd.Timedelta(hours=1)
            )
            merged = pd.merge_asof(
                merged.dropna(subset=['Voltage_B','Current_B']).sort_values('DateTime'),
                c.sort_values('DateTime'), on='DateTime', direction='nearest',
                tolerance=pd.Timedelta(hours=1)
            )
            merged = merged.dropna(subset=[
                'Voltage_A','Current_A','Voltage_B','Current_B','Voltage_C','Current_C'
            ]).reset_index(drop=True)

        if merged.empty:
            return None

        merged['VUF'] = merged.apply(lambda r: self.calculate_vuf(
            r['Voltage_A'], r['Voltage_B'], r['Voltage_C']), axis=1)
        merged['CUF'] = merged.apply(lambda r: self.calculate_cuf(
            r['Current_A'], r['Current_B'], r['Current_C']), axis=1)
        merged['Load_kW'] = (
            merged['Voltage_A']*merged['Current_A'] +
            merged['Voltage_B']*merged['Current_B'] +
            merged['Voltage_C']*merged['Current_C']
        ) * self.PF / 1000.0
        merged['Hour'] = merged['DateTime'].dt.hour
        merged['Date'] = merged['DateTime'].dt.date
        merged['Weekday'] = merged['DateTime'].dt.weekday
        merged['DayType'] = np.where(merged['Weekday'] < 5, 'Weekday', 'Weekend')
        return merged

    # ---------------- Analyses ----------------
    def _refresh_all_seasonal_load_data(self):
        for season in ['summer', 'winter', 'festival']:
            self.update_seasonal_load_data(season)
            self.update_season_status(season)

    def peak_analysis(self):
        self._refresh_all_seasonal_load_data()
        txt = "PEAK/OFF-PEAK ANALYSIS\n\n"

        fig, ax = plt.subplots(figsize=(12, 8))

        for name, df in {'Summer': self.summer_data,
                         'Winter': self.winter_data,
                         'Festival': self.festival_data}.items():
            if df is None or 'Load_kW' not in df.columns:
                continue

            txt += f"{name} (Overall):\n"
            avg_by_hour = df.groupby("Hour")['Load_kW'].mean()
            peak_hour = avg_by_hour.idxmax()
            offpeak_hour = avg_by_hour.idxmin()
            peak_load = df['Load_kW'].max()
            overload_days = (df.groupby("Date")['Load_kW'].max() > self.capacity_kW).sum()

            # Calculate hours in peak and off-peak condition
            peak_condition_hours = df[df['Load_kW'] >= avg_by_hour[peak_hour]]['Hour'].nunique()
            offpeak_condition_hours = df[df['Load_kW'] <= avg_by_hour[offpeak_hour]]['Hour'].nunique()

            txt += f"  Average Peak Hour: {peak_hour}:00, Off-Peak Hour: {offpeak_hour}:00\n"
            txt += f"  Max Recorded Load: {peak_load:.2f} kW\n"
            txt += f"  Overload Days (> {self.capacity_kW:.1f} kW): {overload_days}\n"
            txt += f"  Hours in Peak Load Condition: {peak_condition_hours} hours\n"
            txt += f"  Hours in Off-Peak Load Condition: {offpeak_condition_hours} hours\n\n"

            hours = np.arange(0, 24, 1)
            hourly_avg = [avg_by_hour.get(h, 0) for h in hours]

            ax.plot(hours, hourly_avg, marker='o', linewidth=2, markersize=4, label=f"{name} Avg Load")
            ax.scatter(peak_hour, avg_by_hour[peak_hour], color="red", s=150, zorder=5,
                       label=f"{name} Peak {peak_hour}:00")
            ax.scatter(offpeak_hour, avg_by_hour[offpeak_hour], color="blue", s=150, zorder=5,
                       label=f"{name} Off-Peak {offpeak_hour}:00")

        ax.axhline(self.capacity_kW, color="orange", linestyle="--", linewidth=2,
                   label=f"Transformer Capacity ({self.capacity_kW:.0f} kW)")

        ax.set_title("Peak vs Off-Peak Load Analysis (Hourly)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hour of Day", fontsize=12)
        ax.set_ylabel("Average Load (kW)", fontsize=12)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_xlim(-0.5, 23.5)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.display_report(txt)
        self.save_figure_as_jpg(fig, "Peak_Offpeak_Analysis.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def voltage_analysis(self):
        """
        CORRECTED: This function now reads voltage from the Transformer Raw Data (A,B,C) files.
        """
        txt = "VOLTAGE ANALYSIS (TEXT REPORT)\n(from Transformer Raw Data)\n\n"
        vmin = self.nominal_voltage * (1 - self.voltage_tolerance)
        vmax = self.nominal_voltage * (1 + self.voltage_tolerance)
        
        season_map = {'Summer': 'summer', 'Winter': 'winter', 'Festival': 'festival'}
        
        # --- Text Report Generation ---
        has_any_data_for_report = False
        for name, season_key in season_map.items():
            df = self.get_merged_unbalance_data(season_key)
            if df is None or df.empty:
                continue
                
            has_any_data_for_report = True
            txt += f"{name}:\n"
            # Use corrected phase names from the merged dataframe
            for phase in ['Voltage_A', 'Voltage_B', 'Voltage_C']:
                if phase in df.columns:
                    uv_days = (df.groupby("Date")[phase].min() < vmin).sum()
                    ov_days = (df.groupby("Date")[phase].max() > vmax).sum()
                    txt += f"  Phase {phase[-1]}: Undervoltage Days={uv_days}, Overvoltage Days={ov_days}\n"
            txt += "\n"
        
        if not has_any_data_for_report:
            txt += "No complete Transformer Raw Data (A, B, C) loaded for any season."
        self.display_report(txt)

        # --- Graph Generation ---
        fig, ax = plt.subplots(figsize=(12, 8))
        # Use corrected phase names and colors
        phase_colors = {'Voltage_A': 'red', 'Voltage_B': 'orange', 'Voltage_C': 'blue'}
        season_styles = {'Summer': '-', 'Winter': '--', 'Festival': ':'}
        
        has_any_data_for_graph = False
        
        for name, season_key in season_map.items():
            df = self.get_merged_unbalance_data(season_key)
            if df is None or df.empty:
                continue

            has_any_data_for_graph = True
            for phase, color in phase_colors.items():
                if phase in df.columns:
                    avg_by_hour = df.groupby("Hour")[phase].mean()
                    hours = np.arange(0, 24, 1)
                    hourly_avg = [avg_by_hour.get(h, np.nan) for h in hours] # Use nan for missing hours
                    # Use corrected label
                    ax.plot(hours, hourly_avg, color=color, linestyle=season_styles[name], 
                                    label=f"{name} Phase {phase[-1]}")

        if not has_any_data_for_graph:
            messagebox.showwarning("No Data", "No voltage data found in the loaded Transformer Raw Files to generate a graph.")
            plt.close(fig)
            return

        ax.axhline(vmax, color="black", linestyle="--", linewidth=2, label=f"Upper Limit ({vmax:.1f} V)")
        ax.axhline(vmin, color="black", linestyle="--", linewidth=2, label=f"Lower Limit ({vmin:.1f} V)")

        ax.set_title("Average Hourly Voltage Profile by Season and Phase", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hour of Day", fontsize=12)
        ax.set_ylabel("Average Voltage (V)", fontsize=12)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_xlim(-0.5, 23.5)
        ax.legend(title="Legend", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend

        self.save_figure_as_jpg(fig, "Voltage_Profile.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def energy_analysis(self):
        self._refresh_all_seasonal_load_data()
        fig, ax = plt.subplots(figsize=(10, 6))
        datasets = {'Summer': self.summer_data,
                    'Winter': self.winter_data,
                    'Festival': self.festival_data}
        for name, df in datasets.items():
            if df is not None and 'Load_kW' in df.columns:
                if len(df) > 1:
                    delta_t = (df['DateTime'].iloc[1] - df['DateTime'].iloc[0]).total_seconds() / 3600.0
                else:
                    delta_t = 1
                df['Energy_kWh'] = df['Load_kW'] * delta_t

                monthly = df.groupby(df['DateTime'].dt.month)['Energy_kWh'].sum()
                ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, markersize=6, label=name)

        ax.set_title("Monthly Energy Consumption (kWh)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Energy (kWh)", fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Monthly_Energy_Consumption.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def load_curves(self):
        self._refresh_all_seasonal_load_data()
        fig, ax = plt.subplots(figsize=(12, 8))
        datasets = {'Summer': self.summer_data,
                    'Winter': self.winter_data,
                    'Festival': self.festival_data}

        colors = {'Overall': 'blue', 'Weekday': 'green', 'Weekend': 'red'}
        styles = {'Summer': '-', 'Winter': '--', 'Festival': ':'}

        for name, df in datasets.items():
            if df is not None:
                for d_type in ["Overall", "Weekday", "Weekend"]:
                    if d_type == "Overall":
                        sub = df
                    else:
                        sub = df[df['DayType'] == d_type]
                    if sub.empty:
                        continue

                    avg_curve = sub.groupby("Hour")['Load_kW'].mean()
                    hours = np.arange(0, 24, 1)
                    hourly_loads = [avg_curve.get(h, 0) for h in hours]

                    ax.plot(hours, hourly_loads, linestyle=styles[name], color=colors[d_type],
                            linewidth=2, label=f"{name} - {d_type}")

        ax.set_title("Average Daily Load Profiles (Hourly)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hour of Day", fontsize=12)
        ax.set_ylabel("Load (kW)", fontsize=12)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_xlim(-0.5, 23.5)
        ax.legend(title="Legend", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout(rect=[0, 0, 0.85, 1])

        self.save_figure_as_jpg(fig, "Daily_Load_Profiles.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def power_vs_time_graph(self):
        self._refresh_all_seasonal_load_data()
        """Generates a plot of average active power (kW) vs. time for each season."""
        fig, ax = plt.subplots(figsize=(12, 8))
        datasets = {'Summer': self.summer_data, 'Winter': self.winter_data, 'Festival': self.festival_data}
        
        has_data = False
        for name, df in datasets.items():
            if df is not None and 'Load_kW' in df.columns:
                has_data = True
                avg_by_hour = df.groupby("Hour")['Load_kW'].mean()
                hours = np.arange(0, 24, 1)
                hourly_avg = [avg_by_hour.get(h, 0) for h in hours]
                ax.plot(hours, hourly_avg, marker='.', linewidth=2, label=f"{name} Average Load")

        if not has_data:
            messagebox.showwarning("No Data", "No load data available to generate power curve.")
            plt.close(fig)
            return

        ax.axhline(self.capacity_kW, color="red", linestyle="--", linewidth=2,
                   label=f"Transformer Capacity ({self.capacity_kW:.0f} kW)")
        
        ax.set_title("Average Active Power Curve", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hour of Day", fontsize=12)
        ax.set_ylabel("Average Active Power (kW)", fontsize=12)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_xlim(-0.5, 23.5)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Active_Power_Curve.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def hourly_avg_active_power_distribution(self):
        self._refresh_all_seasonal_load_data()
        """Generate a histogram of hourly-averaged active power for each season.

        The existing seasonal Load_kW data are used when available. If those
        files are not loaded, active power is calculated directly from the
        already-loaded Transformer A, B and C files using the existing PF.
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        datasets = {'Summer': self.summer_data, 'Winter': self.winter_data, 'Festival': self.festival_data}
        season_keys = {'Summer': 'summer', 'Winter': 'winter', 'Festival': 'festival'}
        has_data = False

        all_values = []
        season_values = {}

        for name, df in datasets.items():
            # First use the original Load_kW seasonal data if they are loaded.
            if df is not None and 'Load_kW' in df.columns:
                hourly_avg = df.groupby('Hour')['Load_kW'].mean().dropna()
                if not hourly_avg.empty:
                    season_values[name] = hourly_avg.values
                    all_values.extend(hourly_avg.values)
                    has_data = True
                    continue

            # Otherwise calculate active power from Transformer A/B/C files.
            merged_df = self.get_merged_unbalance_data(season_keys[name])
            if merged_df is not None and not merged_df.empty:
                required_cols = [
                    'Voltage_A', 'Current_A',
                    'Voltage_B', 'Current_B',
                    'Voltage_C', 'Current_C'
                ]
                if all(col in merged_df.columns for col in required_cols):
                    # Per-phase active power: P = V * I * PF.
                    # Sum the three phases and convert W to kW.
                    merged_df['ActivePower_kW'] = (
                        (merged_df['Voltage_A'] * merged_df['Current_A']) +
                        (merged_df['Voltage_B'] * merged_df['Current_B']) +
                        (merged_df['Voltage_C'] * merged_df['Current_C'])
                    ) * self.PF / 1000.0

                    hourly_avg = merged_df.groupby('Hour')['ActivePower_kW'].mean().dropna()
                    if not hourly_avg.empty:
                        season_values[name] = hourly_avg.values
                        all_values.extend(hourly_avg.values)
                        has_data = True

        if not has_data:
            messagebox.showwarning(
                "No Data",
                "No active power data available. Load the seasonal data or Transformer A, B and C files first."
            )
            plt.close(fig)
            return

        bins = np.histogram_bin_edges(all_values, bins='auto')
        for name, values in season_values.items():
            ax.hist(values, bins=bins, alpha=0.55, edgecolor='black', label=name)

        ax.axvline(self.capacity_kW, color="red", linestyle="--", linewidth=2,
                   label=f"Transformer Capacity ({self.capacity_kW:.0f} kW)")
        ax.set_title("Distribution of Hourly-Averaged Active Power", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hourly-Averaged Active Power (kW)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Hourly_Averaged_Active_Power_Distribution.jpg")
        self.display_chart(fig)
        plt.close(fig)
    def hourly_avg_vuf_distribution(self):
        """Generate a histogram of hourly-averaged VUF for each season."""
        fig, ax = plt.subplots(figsize=(12, 8))
        seasons = {'Summer': 'summer', 'Winter': 'winter', 'Festival': 'festival'}
        has_data = False

        all_values = []
        season_values = {}
        for name, season_key in seasons.items():
            df = self.get_merged_unbalance_data(season_key)
            if df is not None and not df.empty and 'VUF' in df.columns:
                hourly_avg = df.groupby('Hour')['VUF'].mean().dropna()
                if not hourly_avg.empty:
                    has_data = True
                    season_values[name] = hourly_avg.values
                    all_values.extend(hourly_avg.values)

        if not has_data:
            messagebox.showwarning("No Data", "No complete Transformer A, B, C data available to generate the hourly-averaged VUF distribution.")
            plt.close(fig)
            return

        bins = np.histogram_bin_edges(all_values, bins='auto')
        for name, values in season_values.items():
            ax.hist(values, bins=bins, alpha=0.55, edgecolor='black', label=name)

        ax.axvline(self.vuf_threshold, color="red", linestyle="--", linewidth=2,
                   label=f"VUF Limit ({self.vuf_threshold}%)")
        ax.set_title("Distribution of Hourly-Averaged VUF", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hourly-Averaged VUF (%)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Hourly_Averaged_VUF_Distribution.jpg")
        self.display_chart(fig)
        plt.close(fig)
    def hourly_avg_cuf_distribution(self):
        """Generate a histogram of hourly-averaged CUF for each season."""
        fig, ax = plt.subplots(figsize=(12, 8))
        seasons = {'Summer': 'summer', 'Winter': 'winter', 'Festival': 'festival'}
        has_data = False

        all_values = []
        season_values = {}
        for name, season_key in seasons.items():
            df = self.get_merged_unbalance_data(season_key)
            if df is not None and not df.empty and 'CUF' in df.columns:
                hourly_avg = df.groupby('Hour')['CUF'].mean().dropna()
                if not hourly_avg.empty:
                    has_data = True
                    season_values[name] = hourly_avg.values
                    all_values.extend(hourly_avg.values)

        if not has_data:
            messagebox.showwarning("No Data", "No complete Transformer A, B, C data available to generate the hourly-averaged CUF distribution.")
            plt.close(fig)
            return

        bins = np.histogram_bin_edges(all_values, bins='auto')
        for name, values in season_values.items():
            ax.hist(values, bins=bins, alpha=0.55, edgecolor='black', label=name)

        ax.axvline(self.cuf_threshold, color="red", linestyle="--", linewidth=2,
                   label=f"CUF Limit ({self.cuf_threshold}%)")
        ax.set_title("Distribution of Hourly-Averaged CUF", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hourly-Averaged CUF (%)", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Hourly_Averaged_CUF_Distribution.jpg")
        self.display_chart(fig)
        plt.close(fig)
    def reactive_power_vs_time_graph(self):
        self._refresh_all_seasonal_load_data()
        """Calculates and plots average reactive power (kVAR) vs. time."""
        fig, ax = plt.subplots(figsize=(12, 8))
        datasets = {'Summer': self.summer_data, 'Winter': self.winter_data, 'Festival': self.festival_data}
        
        # Q = P * tan(arccos(PF))
        try:
            tan_phi = np.tan(np.arccos(self.PF))
        except ValueError:
            messagebox.showerror("Error", "Invalid Power Factor. Must be between -1 and 1.")
            return

        has_data = False
        for name, df in datasets.items():
            if df is not None and 'Load_kW' in df.columns:
                has_data = True
                df['Load_kVAR'] = df['Load_kW'] * tan_phi
                avg_by_hour = df.groupby("Hour")['Load_kVAR'].mean()
                hours = np.arange(0, 24, 1)
                hourly_avg = [avg_by_hour.get(h, 0) for h in hours]
                ax.plot(hours, hourly_avg, marker='.', linewidth=2, label=f"{name} Average Reactive Power")

        if not has_data:
            messagebox.showwarning("No Data", "No load data available to calculate reactive power.")
            plt.close(fig)
            return

        ax.set_title("Average Reactive Power Curve", fontsize=14, fontweight='bold')
        ax.set_xlabel("Hour of Day", fontsize=12)
        ax.set_ylabel(f"Average Reactive Power (kVAR) @ PF={self.PF}", fontsize=12)
        ax.set_xticks(np.arange(0, 24, 1))
        ax.set_xlim(-0.5, 23.5)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()

        self.save_figure_as_jpg(fig, "Reactive_Power_Curve.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def unbalance_charts(self):
        seasons_with_data = []
        for season in ["summer", "winter", "festival"]:
            df = None
            try:
                df = self.get_merged_unbalance_data(season)
            except Exception:
                pass
            if df is not None:
                seasons_with_data.append(season)

        if not seasons_with_data:
            messagebox.showwarning("No Data", "No transformer A,B,C data available for unbalance analysis!")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        colors = {'summer': 'red', 'winter': 'blue', 'festival': 'green'}

        vuf_data_list = []
        cuf_data_list = []
        labels_list = []

        for season in seasons_with_data:
            try:
                df = self.get_merged_unbalance_data(season)
                ax1.scatter(df['VUF'], df['CUF'], alpha=0.6, c=colors[season], label=season.capitalize(), s=20)

                hourly_vuf = df.groupby('Hour')['VUF'].mean()
                hours = np.arange(0, 24, 1)
                vuf_values = [hourly_vuf.get(h, 0) for h in hours]
                ax2.plot(hours, vuf_values, marker='o', linewidth=2, markersize=4, color=colors[season], label=season.capitalize())

                hourly_cuf = df.groupby('Hour')['CUF'].mean()
                cuf_values = [hourly_cuf.get(h, 0) for h in hours]
                ax3.plot(hours, cuf_values, marker='o', linewidth=2, markersize=4, color=colors[season], label=season.capitalize())

                vuf_data_list.append(df['VUF'].values)
                cuf_data_list.append(df['CUF'].values)
                labels_list.append(season.capitalize())

            except Exception as e:
                messagebox.showerror("Error", f"Error processing {season} data: {e}")

        ax1.axvline(x=self.vuf_threshold, color='red', linestyle='--', alpha=0.7, linewidth=2, label=f'VUF Limit ({self.vuf_threshold}%)')
        ax1.axhline(y=self.cuf_threshold, color='red', linestyle='--', alpha=0.7, linewidth=2, label=f'CUF Limit ({self.cuf_threshold}%)')
        ax1.set_xlabel('Voltage Unbalance Factor (%)', fontweight='bold')
        ax1.set_ylabel('Current Unbalance Factor (%)', fontweight='bold')
        ax1.set_title('VUF vs CUF Correlation', fontweight='bold')
        
        # Set CUF y-axis scale to 5% intervals
        cuf_max = max([df['CUF'].max() for season in seasons_with_data 
                      for df in [self.get_merged_unbalance_data(season)] if df is not None])
        ax1.set_yticks(np.arange(0, cuf_max + 5, 5))
        
        ax1.legend(loc='best', framealpha=0.9)
        ax1.grid(True, alpha=0.3)

        ax2.axhline(y=self.vuf_threshold, color='red', linestyle='--', alpha=0.7, label=f'VUF Limit ({self.vuf_threshold}%)')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Average VUF (%)')
        ax2.set_title('Hourly Voltage Unbalance Factor')
        ax2.set_xticks(np.arange(0, 24, 2))
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.axhline(y=self.cuf_threshold, color='red', linestyle='--', alpha=0.7, label=f'CUF Limit ({self.cuf_threshold}%)')
        ax3.set_xlabel('Hour of Day')
        ax3.set_ylabel('Average CUF (%)')
        ax3.set_title('Hourly Current Unbalance Factor')
        ax3.set_xticks(np.arange(0, 24, 2))
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        if vuf_data_list and cuf_data_list and labels_list:
            # Create bar chart with error bars for clearer comparison
            x_pos = np.arange(len(seasons_with_data))
            width = 0.35
            
            vuf_means = [np.mean(data) for data in vuf_data_list]
            vuf_stds = [np.std(data) for data in vuf_data_list]
            cuf_means = [np.mean(data) for data in cuf_data_list]
            cuf_stds = [np.std(data) for data in cuf_data_list]
            
            bars1 = ax4.bar(x_pos - width/2, vuf_means, width, yerr=vuf_stds, 
                           capsize=5, alpha=0.8, color='skyblue', 
                           edgecolor='darkblue', linewidth=1.5, label='VUF')
            bars2 = ax4.bar(x_pos + width/2, cuf_means, width, yerr=cuf_stds, 
                           capsize=5, alpha=0.8, color='lightcoral', 
                           edgecolor='darkred', linewidth=1.5, label='CUF')
            
            # Add value labels on bars
            for i, (vuf_m, cuf_m) in enumerate(zip(vuf_means, cuf_means)):
                ax4.text(i - width/2, vuf_m + vuf_stds[i] + 0.5, f'{vuf_m:.1f}%', 
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
                ax4.text(i + width/2, cuf_m + cuf_stds[i] + 0.5, f'{cuf_m:.1f}%', 
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(labels_list, fontweight='bold')
            ax4.set_ylabel('Unbalance Factor (%)', fontweight='bold')
            ax4.set_title('VUF and CUF Distribution by Season\n(Mean ± Std Dev)', fontweight='bold')
            ax4.legend(loc='upper left', framealpha=0.9)
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add reference lines for thresholds
            ax4.axhline(y=self.vuf_threshold, color='blue', linestyle='--', 
                       alpha=0.5, linewidth=1, label=f'VUF Limit ({self.vuf_threshold}%)')
            ax4.axhline(y=self.cuf_threshold, color='red', linestyle='--', 
                       alpha=0.5, linewidth=1, label=f'CUF Limit ({self.cuf_threshold}%)')

        plt.tight_layout()
        self.save_figure_as_jpg(fig, "VUF_CUF_Charts.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def unbalance_trends(self):
        seasons_with_data = []
        for season in ["summer", "winter", "festival"]:
            df = None
            try:
                df = self.get_merged_unbalance_data(season)
            except Exception:
                pass
            if df is not None:
                seasons_with_data.append(season)

        if not seasons_with_data:
            messagebox.showwarning("No Data", "No transformer A,B,C data available for trend analysis!")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        colors = {'summer': 'red', 'winter': 'blue', 'festival': 'green'}

        for season in seasons_with_data:
            df = self.get_merged_unbalance_data(season)
            if len(df) > 1000:
                df_sample = df.sample(n=1000).sort_values('DateTime')
            else:
                df_sample = df.sort_values('DateTime')

            ax1.plot(df_sample['DateTime'], df_sample['VUF'],
                     color=colors[season], alpha=0.7, linewidth=1,
                     label=f'{season.capitalize()} VUF')
            ax2.plot(df_sample['DateTime'], df_sample['CUF'],
                     color=colors[season], alpha=0.7, linewidth=1,
                     label=f'{season.capitalize()} CUF')

        ax1.axhline(y=self.vuf_threshold, color='red', linestyle='--', alpha=0.8,
                    label=f'VUF Limit ({self.vuf_threshold}%)')
        ax1.set_ylabel('Voltage Unbalance Factor (%)')
        ax1.set_title('VUF Time Series Trend')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.axhline(y=self.cuf_threshold, color='red', linestyle='--', alpha=0.8,
                    label=f'CUF Limit ({self.cuf_threshold}%)')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Current Unbalance Factor (%)')
        ax2.set_title('CUF Time Series Trend')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        self.save_figure_as_jpg(fig, "Unbalance_Trends.jpg")
        self.display_chart(fig)
        plt.close(fig)

    def generate_full_report(self):
        try:
            filename = "Energy_Analytics_Report.pdf"
            pdf = PdfPages(filename)

            datasets = {'Summer': self.summer_data,
                        'Winter': self.winter_data,
                        'Festival': self.festival_data}

            seasons_with_unbalance = []
            for season in ["summer", "winter", "festival"]:
                if self.get_merged_unbalance_data(season) is not None:
                    seasons_with_unbalance.append(season)

            if seasons_with_unbalance:
                # Page 1: Unbalance Text Summary
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis("off")
                unbalance_text = ["UNBALANCE ANALYSIS SUMMARY", "", ""]
                for season in seasons_with_unbalance:
                    df = self.get_merged_unbalance_data(season)
                    unbalance_text.extend([
                        f"{season.capitalize()}:",
                        f"  Average VUF: {df['VUF'].mean():.2f}% (Limit: {self.vuf_threshold}%)",
                        f"  Maximum VUF: {df['VUF'].max():.2f}%",
                        f"  Average CUF: {df['CUF'].mean():.2f}% (Limit: {self.cuf_threshold}%)",
                        f"  Maximum CUF: {df['CUF'].max():.2f}%",
                        f"  VUF Violations: {(df['VUF'] > self.vuf_threshold).sum()} readings",
                        f"  CUF Violations: {(df['CUF'] > self.cuf_threshold).sum()} readings",
                        ""
                    ])
                plt.text(0.05, 0.95, "\n".join(unbalance_text), va="top", fontsize=11,
                         transform=ax.transAxes, family='monospace')
                plt.title("Unbalance Analysis Report", fontsize=16, fontweight='bold', pad=20)
                pdf.savefig(fig)
                plt.close(fig)

                # Page 2: Unbalance Charts
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
                colors = {'summer': 'red', 'winter': 'blue', 'festival': 'green'}

                for season in seasons_with_unbalance:
                    df = self.get_merged_unbalance_data(season)
                    ax1.scatter(df['VUF'], df['CUF'], alpha=0.6, c=colors[season],
                                label=season.capitalize(), s=15)
                ax1.axvline(x=self.vuf_threshold, color='red', linestyle='--', alpha=0.7)
                ax1.axhline(y=self.cuf_threshold, color='red', linestyle='--', alpha=0.7)
                ax1.set_xlabel('VUF (%)')
                ax1.set_ylabel('CUF (%)')
                ax1.set_title('VUF vs CUF')
                ax1.legend()
                ax1.grid(True, alpha=0.3)

                for season in seasons_with_unbalance:
                    df = self.get_merged_unbalance_data(season)
                    hourly_vuf = df.groupby('Hour')['VUF'].mean()
                    ax2.plot(hourly_vuf.index, hourly_vuf.values, marker='o',
                             color=colors[season], label=season.capitalize())
                ax2.axhline(y=self.vuf_threshold, color='red', linestyle='--', alpha=0.7)
                ax2.set_xlabel('Hour')
                ax2.set_ylabel('VUF (%)')
                ax2.set_title('Hourly VUF')
                ax2.legend()
                ax2.grid(True, alpha=0.3)

                for season in seasons_with_unbalance:
                    df = self.get_merged_unbalance_data(season)
                    hourly_cuf = df.groupby('Hour')['CUF'].mean()
                    ax3.plot(hourly_cuf.index, hourly_cuf.values, marker='o',
                             color=colors[season], label=season.capitalize())
                ax3.axhline(y=self.cuf_threshold, color='red', linestyle='--', alpha=0.7)
                ax3.set_xlabel('Hour')
                ax3.set_ylabel('CUF (%)')
                ax3.set_title('Hourly CUF')
                ax3.legend()
                ax3.grid(True, alpha=0.3)

                vuf_data, cuf_data, labels = [], [], []
                for season in seasons_with_unbalance:
                    df = self.get_merged_unbalance_data(season)
                    vuf_data.append(df['VUF'].values)
                    cuf_data.append(df['CUF'].values)
                    labels.append(season.capitalize())
                x_pos = np.arange(len(seasons_with_unbalance))
                ax4.boxplot(vuf_data, positions=x_pos - 0.2, widths=0.3, patch_artist=True,
                            boxprops=dict(facecolor='lightblue'))
                ax4.boxplot(cuf_data, positions=x_pos + 0.2, widths=0.3, patch_artist=True,
                            boxprops=dict(facecolor='lightgreen'))
                ax4.set_xticks(x_pos)
                ax4.set_xticklabels(labels)
                ax4.set_ylabel('Unbalance (%)')
                ax4.set_title('VUF & CUF Distribution')
                ax4.grid(True, alpha=0.3)
                plt.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)

            # Subsequent Pages: Load Analysis per Season/DayType
            for name, df in datasets.items():
                if df is None:
                    continue
                for d_type in ["Overall", "Weekday", "Weekend"]:
                    if d_type == "Overall":
                        sub = df
                    else:
                        sub = df[df['DayType'] == d_type]
                    if sub.empty:
                        continue

                    # Summary Table
                    fig, ax = plt.subplots(figsize=(8, 3))
                    ax.axis("off")
                    peak = sub['Load_kW'].max()
                    overload_days = (sub.groupby("Date")['Load_kW'].max() > self.capacity_kW).sum()
                    table_data = [[f"{name} {d_type}", f"{peak:.1f} kW", f"{overload_days} days"]]
                    ax.table(cellText=table_data,
                             colLabels=["Subset", "Peak Load", "Overload Days"],
                             loc="center").scale(1.2, 1.2)
                    ax.set_title(f"{name} - {d_type} Summary", fontsize=12, pad=20)
                    pdf.savefig(fig)
                    plt.close(fig)

                    # Critical Day Load Curve
                    daily_max = sub.groupby("Date")['Load_kW'].max()
                    if not daily_max.empty:
                        crit_day = daily_max.idxmax()
                        crit_df = sub[sub['Date'] == crit_day]

                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(crit_df['Hour'], crit_df['Load_kW'], marker='o', color='purple', label='Load')
                        ax.axhline(self.capacity_kW, color='red', linestyle='--', label=f'Capacity ({self.capacity_kW} kW)')
                        ax.set_title(f"Critical Day Load Curve ({name} - {d_type} | Date: {crit_day})")
                        ax.set_xlabel("Hour of Day")
                        ax.set_ylabel("Load (kW)")
                        ax.set_xticks(np.arange(0, 24, 1))
                        ax.legend()
                        ax.grid(True)
                        plt.tight_layout()
                        pdf.savefig(fig)
                        plt.close(fig)

            pdf.close()
            messagebox.showinfo("Report Generated", f"Report saved as {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF report: {str(e)}")


if __name__ == "__main__":
    analyzer = TransformerAnalyzer()
    analyzer.root.mainloop()