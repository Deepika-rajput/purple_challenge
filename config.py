from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

STORE1_DIR = BASE_DIR / "Store 1-20260602T101818Z-3-001ec38db8" / "Store 1"

ENTRY_VIDEO = STORE1_DIR / "CAM 3 - entry.mp4"
ZONE1_VIDEO = STORE1_DIR / "CAM 1 - zone.mp4"
ZONE2_VIDEO = STORE1_DIR / "CAM 2 - zone.mp4"
BILLING_VIDEO = STORE1_DIR / "CAM 5 - billing.mp4"

LAYOUT_IMAGE = STORE1_DIR / "Store 1-layout.png"

POS_FILE = BASE_DIR / "POS - sample transactionsb1e826f.csv"

OUTPUT_EVENTS = BASE_DIR / "events.jsonl"

ZONE_CONFIG = BASE_DIR / "zones.json"

# ==========================================
# STORE CONFIG
# ==========================================

STORE_ID = "STORE_1"

# ==========================================
# MODELS
# ==========================================

RTDETR_MODEL = "rtdetr-l.pt"

OSNET_MODEL = "osnet_x0_25_msmt17.pt"

# ==========================================
# TRACKING
# ==========================================

TRACK_MAX_AGE = 30

MIN_CONFIDENCE = 0.30

REID_THRESHOLD = 0.80

# ==========================================
# ENTRY CAMERA
# ==========================================

ENTRY_LINE_X = 1050

# ==========================================
# DWELL
# ==========================================

DWELL_THRESHOLD_SECONDS = 30

DWELL_REPEAT_SECONDS = 30

# ==========================================
# QUEUE
# ==========================================

QUEUE_JOIN_THRESHOLD = 1

QUEUE_TIMEOUT_SECONDS = 300

# ==========================================
# STAFF
# ==========================================

STAFF_DWELL_SECONDS = 1800

STAFF_VISITS_THRESHOLD = 5

# ==========================================
# POS
# ==========================================

PURCHASE_LOOKBACK_MINUTES = 5

# ==========================================
# EVENT TYPES
# ==========================================

ENTRY = "ENTRY"
EXIT = "EXIT"
REENTRY = "REENTRY"

ZONE_ENTER = "ZONE_ENTER"
ZONE_EXIT = "ZONE_EXIT"
ZONE_DWELL = "ZONE_DWELL"

BILLING_QUEUE_JOIN = "BILLING_QUEUE_JOIN"
BILLING_QUEUE_ABANDON = "BILLING_QUEUE_ABANDON"
PURCHASE = "PURCHASE"