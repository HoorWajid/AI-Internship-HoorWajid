# Cybersecurity Attacks Dataset – Data Analysis Mini Project

## 1. Overview
This project performs an end-to-end exploratory data analysis (EDA) on a
40,000-record simulated network attack log using Pandas, NumPy,
Matplotlib, and SciPy (for statistical significance testing). It
loads the raw log, cleans missing values, generates summary statistics, and
tests — rather than just visualizes — whether the fields in the dataset are
actually related to one another.

## 2. Dataset
- Name: Cybersecurity Attacks (network intrusion / attack event log)
- File: cybersecurity_attacks.csv
- Size: 40,000 rows × 25 columns
- Key columns:
  - Timestamp – Date/time of the event
  - Source / Destination IP, Port – Network endpoints
  - Protocol – ICMP / UDP / TCP
  - Packet Length – Size of the network packet
  - Packet Type, Traffic Type – Data vs Control; HTTP / DNS / FTP
  - Malware Indicators – Whether an Indicator of Compromise (IoC) was flagged
  - Anomaly Scores – 0–100 anomaly detection score
  - Alerts/Warnings – Whether an alert was triggered
  - Attack Type – DDoS / Malware / Intrusion
  - Attack Signature – Known Pattern A / B
  - Action Taken – Blocked / Logged / Ignored
  - Severity Level – Low / Medium / High
  - Proxy Information, Firewall Logs, IDS/IPS Alerts – Security tooling metadata
  - Geo-location Data – City, State of the event
  - User Information, Device Information, Payload Data – Free-text / high-cardinality fields

## 3. Data Cleaning Process
Cleaning went beyond filling missing values — it validated the data end to
end and reported what it found at every step.

a) Missing values. Five columns were roughly 50% missing:
Malware Indicators, Alerts/Warnings, Proxy Information,
Firewall Logs, IDS/IPS Alerts. Inspection showed these are not
missing data in the usual sense — a NaN means the event (detection,
alert, proxy use, log entry) simply did not occur. Mean/median
imputation would have been wrong here, so:
1. Malware Indicators → filled with "No Detection" (vs "IoC Detected")
2. Alerts/Warnings → filled with "No Alert" (vs "Alert Triggered")
3. Firewall Logs → filled with "No Log" (vs "Log Data")
4. IDS/IPS Alerts → filled with "No Alert Data" (vs "Alert Data")
5. Proxy Information → the raw proxy IP itself is not analytically useful
   (20,148 near-unique values), so it was converted into a binary
   Proxy Used (Yes/No) flag, and the original column dropped.

b) Duplicate records. Checked with df.duplicated() before dropping —
0 exact duplicate rows were found in the raw 40,000-row file.

c) Timestamp validity. Parsed with pd.to_datetime(df["Timestamp"]).
Note: this call has no errors="coerce" argument, so a genuinely
unparseable timestamp would raise an exception and stop the pipeline
rather than silently becoming NaT — in this dataset all 40,000
timestamps parsed cleanly, so the distinction didn't surface, but it's
worth knowing for anyone reusing this function on a messier log file.
Valid timestamps were then split into Year, Month, Hour, DayOfWeek.

d) Categorical text standardization. Every text/object column was
stripped of stray leading/trailing whitespace (a common artifact of
different logging sources writing to the same field). City and State
— the two fields derived from free-form Geo-location Data — were also
title-cased for consistent display, since they're split out of raw text
rather than arriving as clean pre-set categories.

e) Port range validation. Source Port and Destination Port were
checked against the physically valid 0–65535 range; any row failing the
check would be dropped outright (treated as a corrupted log entry, not
recoverable/imputable data). All 40,000 rows passed — zero rows dropped.

f) Negative-value check. Packet Length and Anomaly Scores can't
legitimately be negative, so any row with a negative value in either
column would be dropped. All rows passed — zero rows dropped.

g) Feature engineering. Geo-location Data was split into City /
State; Source Port / Destination Port were bucketed into standard
port-range classes (Well-Known / Registered / Dynamic).

h) Dropped columns. Source/Destination IP, User Information
(personal names), Device Information (raw user-agent strings), and
Payload Data (randomized placeholder text) were dropped — these are
either privacy-sensitive (PII), extremely high-cardinality, or contain no
genuine signal, so keeping them would add noise and risk without
analytical benefit.

Result: 0 missing values, 0 duplicates, 0 range/validity violations in
the final cleaned dataset (cybersecurity_attacks_cleaned.csv), 40,000
rows × 27 columns.

## 4. Analysis Performed
- Descriptive statistics on all numeric fields (ports, packet length,
  anomaly scores).
- Frequency distributions for Attack Type and Severity Level (pie charts).
- Chi-square tests of independence between key categorical pairs
  (Attack Type ↔ Severity, Severity ↔ Action Taken, Attack Type ↔ Malware
  Indicator) to check whether visually-different category counts represent
  a real statistical relationship or just natural sampling noise —
  visualized as annotated heatmaps rather than grouped bar charts, so the
  exact count/percentage and the p-value sit in one figure.
- Time-pattern analysis: attack volume by hour of day and by year (line
  charts, since these are trends over an ordered axis).
- Anomaly score distribution compared across attack types (KDE plot) and
  across severity levels (boxplot, to show median/quartile spread directly).
- Geographic breakdown: top 10 states by attack count (horizontal bar —
  the one place a bar chart is the right tool, since it's a ranking).
- Correlation heatmap across numeric features (ports, packet length,
  anomaly score).
- Malware indicator detection rate broken down by actual attack type
  (annotated percentage heatmap).

## 5. Key Findings

The single most important finding: this dataset shows no statistically
significant relationship between an attack's severity, its actual type, or
the response action taken against it. Every chi-square test between
these fields returned a large p-value (all p > 0.4, far above the 0.05
significance threshold), meaning severity level does not predict
whether an attack gets Blocked, Logged, or Ignored, and a detected
"Malware Indicator" does not predict whether the attack is actually
classified as Malware, DDoS, or Intrusion.

Supporting evidence:

1. Category balance is near-perfectly uniform. Attack Type splits
   ~33.6% DDoS / 33.3% Malware / 33.2% Intrusion; Severity splits ~33.6%
   Medium / 33.5% High / 33.0% Low; Action Taken splits ~33.8% Blocked /
   33.2% Ignored / 33.0% Logged. Real-world attack logs are almost never
   this evenly split — this pattern is the signature of randomly/
   synthetically generated data rather than organically captured
   telemetry.
2. High-severity attacks are just as likely to be Ignored as low-severity
   ones (chi-square p = 0.49). In a real security operations pipeline
   this would be alarming — it would mean incident response isn't
   risk-prioritized — but combined with finding #1, the more accurate
   read is that severity and response were assigned independently in this
   dataset.
3. The "Malware Indicators" flag is unrelated to the actual Attack Type
   (chi-square p = 0.45) — an IoC is flagged in ~50% of DDoS attacks and
   ~50% of Malware attacks alike, so it cannot be used as a real detector
   of malware activity here.
4. Anomaly Scores do not differ meaningfully by attack type or severity
   — mean scores cluster tightly around 50 (range ~49.8–50.3) with nearly
   identical spread (std ≈ 28.8–28.9) across all groups, so the anomaly
   score in this dataset carries no discriminative signal for triage.
5. No time-based attack pattern exists. Attack volume is flat across
   all 24 hours (±3% of the mean) and across all 7 days of the week,
   unlike real-world attack telemetry which usually shows clustering
   around business hours or automated bot schedules.
6. Geographic spread is broad and even across 28 Indian states with no
   dominant hotspot (top state accounts for only ~3.7% of events).

What this means for anyone using this dataset: it is well-suited for
practicing data cleaning, dashboarding, and pipeline-building — but it
cannot be used as-is to train a model that predicts severity, response
action, or attack type from other fields, because those relationships do
not exist in the data. Anyone building a "smart" alert-prioritization or
attack-classification model on top of this dataset without first validating
real-world label correlation would be learning noise, not signal.

## 6. Project Structure
```
cyberattack_project/
├── README.md                              # This file
├── cyberattack_analysis.ipynb             # Full notebook (executed, with outputs & charts)
├── cybersecurity_attacks.csv              # Raw dataset
├── cybersecurity_attacks_cleaned.csv      # Cleaned dataset produced by the pipeline
└── charts/                                 # Saved PNG charts from the EDA
    ├── distribution_overview.png           # Attack Type & Severity (pie charts)
    ├── attacktype_vs_severity_heatmap.png  # Annotated heatmap + chi2 p-value
    ├── severity_vs_action_heatmap.png      # Annotated heatmap + chi2 p-value
    ├── attacks_by_hour.png                 # Line chart
    ├── attacks_by_year.png                 # Line chart
    ├── anomaly_score_by_attacktype.png     # KDE plot
    ├── anomaly_score_boxplot_by_severity.png # Boxplot
    ├── top_states.png                      # Horizontal bar (ranking)
    ├── correlation_heatmap.png             # Heatmap
    └── malware_indicator_heatmap.png       # Annotated % heatmap + chi2 p-value
```

## 7. How to Run
```bash
pip install pandas numpy matplotlib scipy jupyter
jupyter notebook cyberattack_analysis.ipynb
```
Run all cells; the pipeline reloads the raw CSV, cleans it, prints summary
statistics and chi-square test results, and regenerates all charts in
charts/.

## 8. Uploading to GitHub
```bash
cd cyberattack_project
git init
git add .
git commit -m "Cybersecurity attacks EDA mini project"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
