# CHOICES DOCUMENT

## Model Selection

### RT-DETR

Selected because:

* High detection accuracy
* Good crowded-scene performance
* Transformer-based architecture
* Strong person detection capability

Alternative considered:

* YOLOv8

### ByteTrack

Selected because:

* Stable tracking
* Easy integration
* Python 3.12 compatibility
* Efficient CPU execution

Alternative considered:

* StrongSORT

StrongSORT was rejected due to dependency compatibility issues.

### ReID Model

Selected:

OSNet (TorchReID)

Reasons:

* Lightweight
* Proven ReID benchmark performance
* Good inference speed

## Schema Design

JSONL was selected because:

* Streaming friendly
* Easy validation
* Easy ingestion into analytics systems
* Human readable

Each event contains:

* Event ID
* Visitor ID
* Store ID
* Camera ID
* Timestamp
* Event Type
* Zone Information
* Metadata

## API Architecture

Pipeline modules are separated into:

* Detector
* Tracker
* ReID Manager
* Zone Manager
* Session Manager
* Queue Detector
* Event Builder

This design improves maintainability and scalability.

## Production Considerations

* Modular architecture
* Stateless event generation
* Configurable thresholds
* JSONL persistence
* CPU compatibility
