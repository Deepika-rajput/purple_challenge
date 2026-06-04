# DESIGN DOCUMENT

## System Design

The solution follows a modular computer vision pipeline.

### Detection Layer

RT-DETR is used for person detection because of its strong detection accuracy and transformer-based architecture.

### Tracking Layer

ByteTrack is used to maintain stable identities across frames while remaining lightweight enough for CPU execution.

### Re-Identification Layer

OSNet (TorchReID) generates appearance embeddings for each tracked person.

Embeddings are matched using cosine similarity to maintain visitor identities.

### Analytics Layer

Customer positions are mapped into predefined store zones.

The analytics engine generates:

* Zone Entry Events
* Zone Exit Events
* Zone Dwell Events
* Queue Events
* Session Events

### Event Storage

Events are stored as JSONL records to support scalable downstream analytics.

## AI-Assisted Decisions

AI assistance was used to:

* Compare detection models
* Evaluate tracking architectures
* Design JSONL schema
* Optimize CPU execution
* Generate boilerplate pipeline code
* Review integration issues

All AI-generated code was manually reviewed, tested, and modified during implementation.
