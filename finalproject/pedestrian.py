#!/usr/bin/env python3

import cv2
import numpy as np

import multiprocessing as mp

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


def cam_process(cam_q):
    try:
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

            def cb(packet: TwoStagePacket):
                id_data = {}
                visualizer = packet.visualizer
                for det, rec in zip(packet.detections, packet.nnData):
                    reid_result = rec.getFirstLayerFp16()
                    id = reid.new_result(reid_result)
                    id_data[id] = (*det.top_left, *det.bottom_right)

                    visualizer.add_text(f"ID: {id}",
                                        bbox=(*det.top_left, *det.bottom_right),
                                        position=TextPosition.MID)
                frame = visualizer.draw(packet.frame)
                #cv2.imshow('Person reidentification', frame)
                cam_q.put(id_data)

            oak.visualize(nn_reid, callback=cb, fps=True)
            #oak.show_graph()
            oak.start(blocking=True)

    except KeyboardInterrupt:
        print('Stopped camera process')


if __name__ == '__main__':
    mp.set_start_method('spawn')
    cam_q = mp.Queue()
    cam_p = mp.Process(target = cam_process, args = (cam_q,))
    cam_p.start()
    print('Started main camera process')
    try:
        while True:
            while not cam_q.empty():
                print(cam_q.get())
    except KeyboardInterrupt:
        print('Stopped main camera process')
