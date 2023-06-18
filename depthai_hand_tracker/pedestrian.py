#!/usr/bin/env python3

import cv2
import numpy as np

from depthai_sdk import OakCamera
from depthai_sdk.classes import TwoStagePacket
from depthai_sdk.visualize.configs import TextPosition

class PedestrianReId:
    def __init__(self) -> None:
        self.results = []

    def _cosine_dist(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def new_result(self, vector_result) -> int:
        vector_result = np.array(vector_result)
        for i, vector in enumerate(self.results):
            dist = self._cosine_dist(vector, vector_result)
            if dist > 0.7:
                self.results[i] = vector_result
                return i
        else:
            self.results.append(vector_result)
            return len(self.results) - 1


with OakCamera() as oak:
    color = oak.create_camera('color', fps=10)
    color._rotation = 180

    person_det = oak.create_nn('person-detection-retail-0013', color)
    person_det.node.setNumInferenceThreads(2)
    person_det.config_nn(resize_mode='crop')

    nn_reid = oak.create_nn('person-reidentification-retail-0287', input=person_det)
    nn_reid.node.setNumInferenceThreads(2)

    reid = PedestrianReId()
    results = []
    id_count = {}
    id_coordinates = {}
    real_id = 0
    counter = 0

    def cb(packet: TwoStagePacket):
        global counter
        global real_id
        visualizer = packet.visualizer
        for det, rec in zip(packet.detections, packet.nnData):
            reid_result = rec.getFirstLayerFp16()
            id = reid.new_result(reid_result)

            if id in id_count:
                id_count[id] += 1
            else:
                id_count[id] = 1

            # If this ID has been seen more than 20 times, save the coordinates
            if id_count[id] > 20:
                counter += 1
                if (counter == 1):
                    real_id = id
            if(counter > 0 and id == real_id):
                id_coordinates[real_id] = (det.top_left, det.bottom_right)
                print(id_coordinates)

            visualizer.add_text(f"ID: {id}",
                               bbox=(*det.top_left, *det.bottom_right),
                               position=TextPosition.MID)
            print(id)

        frame = visualizer.draw(packet.frame)
        #cv2.imshow('Person reidentification', frame)

    oak.visualize(nn_reid, callback=cb, fps=True)
    #oak.show_graph()
    oak.start(blocking=True)

