import uuid
import numpy as np

from PIL import Image
from scipy.spatial.distance import cosine

import torch
import torchvision.transforms as T

import torchreid

from config import REID_THRESHOLD


class ReIDManager:

    def __init__(self):

        self.device = "cpu"

        print(
            f"[INFO] ReID running on {self.device}"
        )

        self.model = torchreid.models.build_model(
            name="osnet_x0_25",
            num_classes=1000,
            pretrained=True
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        self.transform = T.Compose([
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize(
                mean=[0.485,0.456,0.406],
                std=[0.229,0.224,0.225]
            )
        ])

        # visitor_id -> embedding
        self.visitor_embeddings = {}

        # track_id -> visitor_id
        self.track_mapping = {}

        # exited visitors
        self.exited_visitors = set()

    def extract_embedding(
        self,
        crop
    ):

        if crop is None:
            return None

        image = Image.fromarray(
            crop[:,:,::-1]
        )

        image = self.transform(
            image
        ).unsqueeze(0)

        image = image.to(
            self.device
        )

        with torch.no_grad():

            embedding = self.model(
                image
            )

        embedding = (
            embedding
            .cpu()
            .numpy()
            .flatten()
        )

        return embedding

    def similarity(
        self,
        emb1,
        emb2
    ):

        return 1 - cosine(
            emb1,
            emb2
        )

    def generate_visitor_id(
        self
    ):

        uid = str(
            uuid.uuid4()
        )[:8]

        return f"VIS_{uid}"

    def find_match(
        self,
        embedding
    ):

        if embedding is None:
            return None

        best_id = None
        best_score = 0

        for visitor_id, stored_emb in \
            self.visitor_embeddings.items():

            score = self.similarity(
                embedding,
                stored_emb
            )

            if score > best_score:

                best_score = score
                best_id = visitor_id

        if best_score >= REID_THRESHOLD:

            return best_id

        return None

    def assign_visitor(
        self,
        track_id,
        embedding
    ):

        # Track already mapped
        if track_id in self.track_mapping:

            return self.track_mapping[
                track_id
            ]

        # Try matching
        matched = self.find_match(
            embedding
        )

        if matched:

            self.track_mapping[
                track_id
            ] = matched

            return matched

        # New visitor
        visitor_id = (
            self.generate_visitor_id()
        )

        self.track_mapping[
            track_id
        ] = visitor_id

        self.visitor_embeddings[
            visitor_id
        ] = embedding

        return visitor_id

    def update_embedding(
        self,
        visitor_id,
        embedding
    ):

        if embedding is None:
            return

        self.visitor_embeddings[
            visitor_id
        ] = embedding

    def mark_exit(
        self,
        visitor_id
    ):

        self.exited_visitors.add(
            visitor_id
        )

    def is_reentry(
        self,
        visitor_id
    ):

        return (
            visitor_id
            in self.exited_visitors
        )

    def get_crop(
        self,
        frame,
        bbox
    ):

        x1,y1,x2,y2 = bbox

        h,w = frame.shape[:2]

        x1 = max(0,x1)
        y1 = max(0,y1)

        x2 = min(w,x2)
        y2 = min(h,y2)

        if x2 <= x1:
            return None

        if y2 <= y1:
            return None

        return frame[
            y1:y2,
            x1:x2
        ]

    def process_track(
        self,
        frame,
        track
    ):

        bbox = track["bbox"]

        track_id = track[
            "track_id"
        ]

        crop = self.get_crop(
            frame,
            bbox
        )

        embedding = (
            self.extract_embedding(
                crop
            )
        )

        visitor_id = (
            self.assign_visitor(
                track_id,
                embedding
            )
        )

        self.update_embedding(
            visitor_id,
            embedding
        )

        return visitor_id