# test_pipeline.py

from run_pipeline import StorePipeline
from config import ENTRY_VIDEO

pipeline = StorePipeline()

pipeline.run(
    ENTRY_VIDEO
)