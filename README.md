# Retail Store Analytics System

## Overview

This project implements an AI-powered retail analytics pipeline for customer journey tracking and behavioral analysis using store surveillance footage.

The system detects customers, tracks them across frames, performs person re-identification (ReID), maps movement to store zones, and generates analytics events in JSONL format.

## Features

* Person Detection using RT-DETR
* Multi-Object Tracking using ByteTrack
* Customer Re-Identification using OSNet
* Zone Entry and Dwell Time Analytics
* Session Tracking
* Event Logging in JSONL format
* Queue Analytics Framework
* POS Integration Framework

## Architecture

Video Input
→ RT-DETR Detection
→ ByteTrack Tracking
→ ReID (OSNet)
→ Zone Mapping
→ Event Generation
→ JSONL Event Log

## Generated Events

* ENTRY
* EXIT
* REENTRY
* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* BILLING_QUEUE_ABANDON

## Installation

pip install ultralytics
pip install supervision
pip install torch torchvision
pip install torchreid
pip install opencv-python
pip install scipy shapely pillow

## Running

python run_pipeline.py

## Output

Generated analytics events are written to:

events.jsonl

## Example Event

{
"visitor_id": "VIS_854d10ad",
"event_type": "ZONE_DWELL",
"zone_id": "RIGHT_WALL",
"dwell_ms": 30563
}
